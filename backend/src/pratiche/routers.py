from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Annotated, List

from src.auth.dipendenze import get_current_utente
from src.auth.visibilita import Visibilita, riga_di_me, visibilita_corrente
from src.database import get_db
from src.errori import CodicePraticaError, ContabilitaPraticaError
from src.notifiche.backend_invio import Mailer, get_mailer
from src.pratiche.codice import genera_codici_pratica
from src.pratiche.dopo_salvataggio import dopo_creazione
from src.pratiche.filtri import FiltriPratiche, query_filtrata
from src.pratiche.notifiche import invia_mail_nuova_pratica_ersaf, invia_mail_pratica_bozza
from src.pratiche.opzioni import router as opzioni_router
from src.pratiche.firma_rotte import router as firma_router
from src.chat_pratiche.rotte import router as chat_router
from src.pratiche.accesso import pratica_visibile
from src.pratiche.storico_stati import STATO_BOZZA_ID, STATO_CARICATA_ID, registra_stato, stato_gia_raggiunto
from src.documenti.rotte import router as documento_router
from src.pratiche.models import Pratica
from src.pratiche.schemi import ConteggioPratiche, PraticaCreate, PraticaResponse, PraticaUpdate
from src.pratiche.rinnovi import verifica_modifica_rinnovo
from src.pratiche_listini.models import PraticaListino
from src.utenti.models import Utente

# Stessa scelta di aziende/routers.py: autenticazione a livello di router,
# non di singolo endpoint, cosi' una rotta nuova la trova gia' protetta.
router = APIRouter(
    prefix="/pratiche",
    tags=["Pratiche"],
    dependencies=[Depends(get_current_utente)],
)

router.include_router(opzioni_router)
# PDF della pratica: stesso prefisso e stessa autenticazione del dettaglio.
router.include_router(documento_router)
router.include_router(firma_router)
router.include_router(chat_router)

# joinedload sulle relazioni che PraticaResponse.estrai_relazioni legge per
# popolare cliente_nome_completo / pratica_stato_descrizione / listTesta_descrizione.
# Senza, quei tre campi restano None in risposta (niente errori, ma la tabella
# del frontend mostrerebbe solo id).
_RELAZIONI_ELENCO = (
    joinedload(Pratica.cliente),
    joinedload(Pratica.stato),
    joinedload(Pratica.listino_testa),
    joinedload(Pratica.universita),
    joinedload(Pratica.tipo_corso),
    # L'emittente si mostra anche se non e' fra i clienti visibili: la scheda
    # non deve piu' chiederlo a GET /clienti/{id}. Outer join (il default):
    # l'emittente non e' garantito.
    joinedload(Pratica.cliente_emittente_aderente),
)


AZIENDA_MANCANTE = "Per creare pratiche l'utente deve avere un'azienda associata."


def _pratica_o_404(db: Session, pratica_id: int, vis: Visibilita) -> Pratica:
    return pratica_visibile(db, pratica_id, vis, opzioni=_RELAZIONI_ELENCO)


# POST
@router.post("/", response_model=PraticaResponse, status_code=status.HTTP_201_CREATED)
def crea_pratica(
    pratica_in: PraticaCreate,
    attivita: BackgroundTasks,
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
    utente: Utente = Depends(get_current_utente),
    mailer: Mailer = Depends(get_mailer),
):
    # exclude_unset=True e' OBBLIGATORIO qui, a differenza di crea_azienda:
    # molti campi di PraticaCreate (listTesta_id, cliente_id, pratica_stato_id,
    # nome_universita_id, cliente_emittente_aderente_id, pratica_prezzo, tutti
    # i missFlag/rinn...) sono Optional=None nello schema perche' a database
    # hanno un server_default. Un model_dump() completo passerebbe None
    # esplicito per i campi non inviati, e SQLAlchemy scriverebbe NULL invece
    # di lasciar agire il DEFAULT del database - lo stesso bug descritto nei
    # commenti di Cliente/Azienda sui server_default.
    dati = pratica_in.model_dump(exclude_unset=True)
    # Non e' una colonna di Pratica: si userebbe per costruire le righe di
    # pratiche_listini piu' sotto, Pratica(**dati) non lo accetterebbe.
    corsi_singoli = dati.pop("corsi_singoli", None) or []

    # Una pratica nasce sempre in Bozza: il valore eventualmente inviato non
    # conta, nemmeno per il Nazionale. Cambiare stato e' un'azione separata,
    # solo in modifica (vedi sotto).
    dati["pratica_stato_id"] = STATO_BOZZA_ID

    # Chi non e' Nazionale crea pratiche solo per la propria azienda: il valore
    # inviato non conta. 403 e non 422: il corpo e' valido, e' l'utente a non
    # poter fare l'operazione finche' non ha un'azienda.
    if not vis.nazionale:
        if vis.azienda_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=AZIENDA_MANCANTE
            )
        dati["azienda_id"] = vis.azienda_id

    # Il form non sceglie piu' l'emittente, ma le ACL chat usano ancora
    # questi riferimenti. Mai affidarsi al cliente 1 convenzionale del DB.
    if not dati.get("cliente_emittente_aderente_id"):
        emittente = riga_di_me(db, utente.utente_id)
        if emittente is None:
            raise HTTPException(status_code=403, detail="Il profilo non ha un cliente associato.")
        dati["cliente_emittente_aderente_id"] = emittente.cliente_id
    dati.setdefault("utente_id", utente.utente_id)
    nuova_pratica = Pratica(**dati)
    db.add(nuova_pratica)
    # flush+refresh, non commit: serve pratica_id e, soprattutto, i campi con
    # server_default (nome_universita_id puo' non essere stato inviato) prima
    # di generare il codice. Tutto resta nella stessa transazione: se la
    # generazione fallisce, ne' la pratica ne' l'incremento del contatore
    # vengono scritti (vedi src/pratiche/codice.py).
    db.flush()
    db.refresh(nuova_pratica)

    codice_universita = getattr(nuova_pratica.universita, "nome_universita_codice", None)
    try:
        codici = genera_codici_pratica(
            db,
            nome_universita_codice=codice_universita,
            listino_tipo_corso_id=nuova_pratica.listino_tipo_corso_id,
        )
    except CodicePraticaError as errore:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(errore)) from errore
    if codici:
        nuova_pratica.pratica_numero = codici.numero
        if codici.codice_asg:
            nuova_pratica.pratica_codiceASG = codici.codice_asg

    # Corsi Singoli: ogni corso scelto (compreso il primo, gia' in
    # listTesta_id) diventa una riga in pratiche_listini. Il prezzo e' quello
    # che il client ha gia' calcolato (vedi CorsoSingoloSelezionato): stessa
    # scelta di pratica_prezzo, il server non lo ricalcola.
    for corso in corsi_singoli:
        db.add(PraticaListino(
            pratica_id=nuova_pratica.pratica_id,
            listTesta_id=corso["listTesta_id"],
            pratica_listini_prezzo=corso.get("prezzo"),
            pratiche_listini_createdBy=utente.utente_id,
            pratiche_listini_updatedBy=utente.utente_id,
        ))

    # Codice A4U e articolo/partitario nel database dei pagamenti, nella
    # stessa transazione: se manca un dato di riferimento non si salva nulla.
    # Vedi src/pratiche/dopo_salvataggio.py.
    try:
        dopo_creazione(db, nuova_pratica, utente.utente_id, nome_universita_codice=codice_universita)
    except ContabilitaPraticaError as errore:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(errore)) from errore

    # Storico stati: una pratica nuova e' sempre "prima volta" nel suo stato
    # (sempre Bozza, vedi sopra), non serve stato_gia_raggiunto (non puo'
    # avere storico prima di esistere). Vedi src/pratiche/storico_stati.py.
    registra_stato(db, nuova_pratica, utente.utente_id)

    db.commit()
    db.refresh(nuova_pratica)
    pratica_salvata = _pratica_o_404(db, nuova_pratica.pratica_id, vis)

    # La mail parte solo DOPO il commit: un invio prima sopravviverebbe a un
    # rollback (vedi src/pratiche/notifiche.py). Solo Bozza: una pratica
    # nuova non puo' nascere Caricata (vedi sopra).
    email_cliente = (getattr(pratica_salvata.cliente, "cliente_email", None) or "").strip()
    if email_cliente:
        attivita.add_task(invia_mail_pratica_bozza, mailer, email_cliente)

    return pratica_salvata


# GET ALL
@router.get("/", response_model=List[PraticaResponse])
def lista_pratiche(
    filtri: Annotated[FiltriPratiche, Query()],
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    return (query_filtrata(db, filtri, vis).options(*_RELAZIONI_ELENCO)
            .order_by(Pratica.pratica_dataCreazione.desc(), Pratica.pratica_id.desc())
            .offset(filtri.skip).limit(filtri.limit).all())


# GET CONTEGGI: prima di /{pratica_id}, che altrimenti catturerebbe il percorso
# e risponderebbe 422.
@router.get("/conteggi", response_model=List[ConteggioPratiche])
def conteggi_pratiche(
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    """Pratiche visibili per universita', tipo di corso e stato.

    Stessa visibilita' dell'elenco, perche' passa da query_filtrata: la pagina
    Pratiche somma questi gruppi secondo le tipologie di ogni ateneo.
    """
    gruppo = (Pratica.nome_universita_id, Pratica.listino_tipo_corso_id, Pratica.pratica_stato_id)
    righe = (query_filtrata(db, FiltriPratiche(), vis)
             .with_entities(*gruppo, func.count(Pratica.pratica_id))
             .group_by(*gruppo).order_by(*gruppo).all())
    return [
        ConteggioPratiche(nome_universita_id=universita, listino_tipo_corso_id=tipo_corso,
                          pratica_stato_id=stato, totale=totale)
        for universita, tipo_corso, stato, totale in righe
    ]


# GET BY ID
@router.get("/{pratica_id}", response_model=PraticaResponse)
def dettaglio_pratica(
    pratica_id: int,
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
):
    return _pratica_o_404(db, pratica_id, vis)


# PUT
@router.put("/{pratica_id}", response_model=PraticaResponse)
def aggiorna_pratica(
    pratica_id: int,
    pratica_in: PraticaUpdate,
    attivita: BackgroundTasks,
    db: Session = Depends(get_db),
    vis: Visibilita = Depends(visibilita_corrente),
    utente: Utente = Depends(get_current_utente),
    mailer: Mailer = Depends(get_mailer),
):
    # Lettura corrente e visibilita' sotto lo stesso blocco, senza joinedload.
    # Un SELECT normale dopo il lock puo' rileggere lo snapshot precedente
    # con REPEATABLE READ, perdendo un cambio di stato o di azienda concorrente.
    pratica = pratica_visibile(db, pratica_id, vis, blocca=True)
    stato_precedente = pratica.pratica_stato_id

    # exclude_unset=True: stesso motivo di aggiorna_azienda, un campo non
    # inviato non deve essere riscritto con un default dello schema.
    modifiche = pratica_in.model_dump(exclude_unset=True)
    # L'azienda e lo stato di una pratica li cambia solo il Nazionale: per
    # l'azienda, spostarla significherebbe perderla di vista o darla a
    # un'altra; per lo stato, e' una decisione che spetta solo a lui.
    if not vis.nazionale:
        modifiche.pop("azienda_id", None)
        modifiche.pop("pratica_stato_id", None)

    try:
        verifica_modifica_rinnovo(pratica, modifiche)
    except ValueError as errore:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(errore)) from None

    for chiave, valore in modifiche.items():
        setattr(pratica, chiave, valore)

    # Storico stati + email di "prima volta": il controllo di stato_gia_raggiunto
    # va fatto PRIMA di registrare la riga di adesso, altrimenti la troverebbe
    # sempre. Vedi src/pratiche/storico_stati.py.
    stato_cambiato = pratica.pratica_stato_id != stato_precedente
    manda_bozza = manda_caricata = False
    if stato_cambiato:
        if pratica.pratica_stato_id == STATO_BOZZA_ID:
            manda_bozza = not stato_gia_raggiunto(db, pratica.pratica_id, STATO_BOZZA_ID)
        if pratica.pratica_stato_id == STATO_CARICATA_ID:
            manda_caricata = not stato_gia_raggiunto(db, pratica.pratica_id, STATO_CARICATA_ID)
        registra_stato(db, pratica, utente.utente_id)

    db.commit()
    db.refresh(pratica)
    pratica_salvata = _pratica_o_404(db, pratica_id, vis)

    if manda_bozza:
        email_cliente = (getattr(pratica_salvata.cliente, "cliente_email", None) or "").strip()
        if email_cliente:
            attivita.add_task(invia_mail_pratica_bozza, mailer, email_cliente)
    if manda_caricata:
        attivita.add_task(invia_mail_nuova_pratica_ersaf, mailer)

    return pratica_salvata
