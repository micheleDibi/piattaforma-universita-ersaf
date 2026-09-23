"""La visibilita' sulle rotte dei clienti e dei loro contatti."""

from __future__ import annotations

import pytest
from sqlalchemy import insert

from src.auth import visibilita as v
from src.clienti.models import Cliente
from src.utenti.models import Utente
from tests.support import factories as f
from tests.support.scenari import accedi, accedi_nazionale

pytestmark = pytest.mark.mariadb

CORPO_500 = {"detail": "Errore interno. Riprova, e se persiste segnala l'errore."}


def inserisci(db, persone):
    """`persone` = (utente_id, padre, ruolo, nome): un utente e una riga
    clienti con lo stesso id. Inserimento in blocco, per non fare centinaia di
    commit."""
    db.execute(insert(Utente.__table__), [
        {"utente_id": u, "utente_username": f"u{u}", "utente_password": "",
         "utente_padre": p, "utente_attivoSN": f.ATTIVO}
        for u, p, _, _ in persone
    ])
    db.execute(insert(Cliente.__table__), [
        {"cliente_id": u, "utente_id": u, "cliente_ruolo": r,
         "cliente_nome": n, "cliente_cognome": "Prova"}
        for u, _, r, n in persone
    ])
    db.commit()


def ids(risposta):
    assert risposta.status_code == 200, risposta.text
    return [riga["cliente_id"] for riga in risposta.json()]


# =============================================================================
# Elenco
# =============================================================================
def test_paginazione_con_visibili_sparsi(client, db):
    """Visibili e non visibili alternati: le due pagine da 40 devono essere
    esattamente i primi 80 visibili, senza buchi ne' ripetizioni."""
    io, sessione = accedi(client, db)
    estraneo = f.crea_utente(db)
    persone = [
        (10_000 + n, io.utente_id if n % 2 else estraneo.utente_id, f.RUOLO_SOTTOSCRITTORE, "S")
        for n in range(200)
    ]
    inserisci(db, persone)
    visibili = sorted(u for u, padre, _, _ in persone if padre == io.utente_id)

    prima = ids(client.get("/clienti/?solo_sottoscrittori=true&skip=0&limit=40", headers=sessione))
    seconda = ids(client.get("/clienti/?solo_sottoscrittori=true&skip=40&limit=40", headers=sessione))

    assert len(prima) == len(seconda) == 40
    assert prima + seconda == visibili[:80]


def test_ricerca_e_ruolo_solo_fra_i_visibili(client, db):
    azienda = f.crea_azienda(db, ragione_sociale="Formazione Rossi Srl")
    io, sessione = accedi(client, db)
    estraneo = f.crea_utente(db)
    inserisci(db, [
        (20_001, io.utente_id, f.RUOLO_ADERENTE, "Rossi"),
        (20_002, estraneo.utente_id, f.RUOLO_ADERENTE, "Rossi"),
        (20_003, io.utente_id, f.RUOLO_SOTTOSCRITTORE, "Rossi"),
        (20_004, estraneo.utente_id, f.RUOLO_SOTTOSCRITTORE, "Rossi"),
        (20_005, io.utente_id, f.RUOLO_ADERENTE, "Bianchi"),
        (20_006, estraneo.utente_id, f.RUOLO_ADERENTE, "Bianchi"),
    ])
    for cliente_id in (20_005, 20_006):
        db.get(Cliente, cliente_id).azienda_id = azienda.azienda_id
    db.commit()

    assert ids(client.get("/clienti/?ruolo_codice=Aderente&search=rossi", headers=sessione)) == [20_001]
    assert ids(client.get("/clienti/?solo_sottoscrittori=true&search=rossi", headers=sessione)) == [20_003]
    # Il ramo con l'outer join sull'azienda.
    assert ids(client.get("/clienti/?solo_attuatori=true&search=formazione", headers=sessione)) == [20_005]
    assert set(ids(client.get("/clienti/?limit=200", headers=sessione))) == {
        io.cliente_id, 20_001, 20_003, 20_005,
    }


def test_sottoscrittori_comprendono_consulenti_e_gli_operatori_sono_attuatori(client, db):
    """L'elenco Sottoscrittori raccoglie Utente e Consulente, quello degli
    Attuatori anche l'Operatore; il selettore dello studente delle pratiche
    resta sul solo ruolo Utente."""
    io, sessione = accedi(client, db)
    inserisci(db, [
        (25_001, io.utente_id, f.RUOLO_SOTTOSCRITTORE, "Utente"),
        (25_002, io.utente_id, f.RUOLO_CONSULENTE, "Consulente"),
        (25_003, io.utente_id, f.RUOLO_OPERATORE, "Operatore"),
        (25_004, io.utente_id, f.RUOLO_ADERENTE, "Aderente"),
    ])

    assert sorted(ids(client.get("/clienti/?solo_sottoscrittori=true", headers=sessione))) == [
        25_001, 25_002,
    ]
    assert ids(client.get("/clienti/?solo_utenti=true", headers=sessione)) == [25_001]
    # Chi accede e' un Regionale: fra gli attuatori che vede compare anche lui.
    assert sorted(ids(client.get("/clienti/?solo_attuatori=true", headers=sessione))) == sorted([
        io.cliente_id, 25_003, 25_004,
    ])


def test_il_nazionale_vede_tutti(client, db, mailer):
    estraneo = f.crea_utente(db)
    inserisci(db, [(30_000 + n, estraneo.utente_id, f.RUOLO_SOTTOSCRITTORE, "S") for n in range(5)])
    nazionale, sessione = accedi_nazionale(client, db, mailer)
    tutti = db.query(Cliente.cliente_id).count()
    assert len(ids(client.get("/clienti/?limit=200", headers=sessione))) == tutti


def test_un_troncamento_risponde_500_non_un_elenco_parziale(client, db, monkeypatch):
    io, sessione = accedi(client, db)
    inserisci(db, [(40_001, io.utente_id, f.RUOLO_SOTTOSCRITTORE, "C")] + [
        (40_000 + n, 40_000 + n - 1, f.RUOLO_SOTTOSCRITTORE, "C") for n in range(2, 12)
    ])
    monkeypatch.setattr(v, "MAX_ITERAZIONI", 5)
    risposta = client.get("/clienti/", headers=sessione)
    assert risposta.status_code == 500
    assert risposta.json() == CORPO_500


def test_il_limite_si_alza_solo_dove_serve(client, db, mailer, spia_sql, tabella_pratiche):
    io, sessione = accedi(client, db)
    spia_sql.clear()
    client.get("/clienti/", headers=sessione)
    # Elenco e confronto email per gli avvisi applicano entrambi la visibilita'.
    ricorsive = [s for s in spia_sql if v.NOME_CTE in s]
    assert len(ricorsive) == 2
    assert all("SET STATEMENT" in s for s in ricorsive)
    assert not any("SET STATEMENT" in s for s in spia_sql if v.NOME_CTE not in s)

    spia_sql.clear()
    client.get("/pratiche/filtri/stati", headers=sessione)
    assert not any("SET STATEMENT" in s for s in spia_sql)

    _, nazionale = accedi_nazionale(client, db, mailer)
    spia_sql.clear()
    client.get("/clienti/", headers=nazionale)
    assert not any("SET STATEMENT" in s for s in spia_sql)


# =============================================================================
# Dettaglio
# =============================================================================
def test_dettaglio_non_visibile_come_inesistente(client, db):
    io, sessione = accedi(client, db)
    figlio = f.crea_attuatore(db, email="figlio@example.org", padre=io.utente_id)
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")

    inesistente = client.get("/clienti/999999", headers=sessione)
    nascosto = client.get(f"/clienti/{estraneo.cliente_id}", headers=sessione)

    assert inesistente.status_code == nascosto.status_code == 404
    assert nascosto.json() == inesistente.json() == {"detail": "Cliente non trovato"}
    assert client.get(f"/clienti/{figlio.cliente_id}", headers=sessione).status_code == 200
    assert client.get(f"/clienti/{io.cliente_id}", headers=sessione).status_code == 200


# =============================================================================
# Modifica
# =============================================================================
NON_TROVATA = {"detail": "Anagrafica non trovata."}


def test_modifica_non_visibile_come_inesistente_e_senza_effetti(client, db, spia_sql):
    _, sessione = accedi(client, db)
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")

    inesistente = client.put("/clienti/999999", json={"cliente_citta": "X"}, headers=sessione)
    spia_sql.clear()
    nascosto = client.put(f"/clienti/{estraneo.cliente_id}", json={"cliente_citta": "X"}, headers=sessione)

    assert inesistente.status_code == nascosto.status_code == 404
    assert nascosto.json() == inesistente.json() == NON_TROVATA
    db.expire_all()
    assert db.get(Cliente, estraneo.cliente_id).cliente_citta == ""
    sospetti = [s for s in spia_sql if "FOR UPDATE" in s or s.lstrip().upper().startswith(("UPDATE CLIENTI", "DELETE"))]
    assert sospetti == []


def test_modifica_non_visibile_non_aspetta_i_lock(client, db):
    """Se la rotta prendesse il lock prima del controllo, resterebbe ferma
    finche' l'altra transazione non rilascia la riga."""
    from concurrent.futures import ThreadPoolExecutor

    from src.database import engine

    _, sessione = accedi(client, db)
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")
    con_lock = engine.connect()
    transazione = con_lock.begin()
    con_lock.exec_driver_sql(
        f"SELECT cliente_id FROM clienti WHERE cliente_id = {estraneo.cliente_id} FOR UPDATE"
    )
    try:
        with ThreadPoolExecutor(1) as esecutore:
            futuro = esecutore.submit(
                client.put, f"/clienti/{estraneo.cliente_id}",
                json={"cliente_citta": "X"}, headers=sessione,
            )
            try:
                risposta = futuro.result(timeout=5)
            finally:
                transazione.rollback()
    finally:
        con_lock.close()
    assert risposta.status_code == 404


def test_modifica_di_un_visibile(client, db):
    io, sessione = accedi(client, db)
    figlio = f.crea_attuatore(db, email="figlio@example.org", padre=io.utente_id)
    risposta = client.put(f"/clienti/{figlio.cliente_id}", json={"cliente_citta": "Torino"}, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    assert risposta.json()["cliente_citta"] == "Torino"


# =============================================================================
# Promozione a Nazionale
# =============================================================================
SOLO_NAZIONALE = {"detail": "Solo il nazionale può eseguire questa operazione."}


def _ruolo(db, cliente_id):
    db.expire_all()
    return db.get(Cliente, cliente_id).cliente_ruolo


def test_nessuno_promuove_a_nazionale_se_non_lo_e(client, db):
    io, sessione = accedi(client, db)
    figlio = f.crea_attuatore(db, email="figlio@example.org", padre=io.utente_id)

    risposta = client.put(f"/clienti/{figlio.cliente_id}", json={"cliente_ruolo": f.RUOLO_NAZIONALE}, headers=sessione)
    assert risposta.status_code == 403
    assert risposta.json() == SOLO_NAZIONALE
    assert _ruolo(db, figlio.cliente_id) == f.RUOLO_ADERENTE

    risposta = client.put(f"/clienti/{io.cliente_id}", json={"cliente_ruolo": f.RUOLO_NAZIONALE}, headers=sessione)
    assert risposta.status_code == 403
    assert _ruolo(db, io.cliente_id) == f.RUOLO_REGIONALE


def test_nessuno_cambia_il_proprio_ruolo_ma_puo_rimandarlo(client, db):
    io, sessione = accedi(client, db)
    cambio = client.put(f"/clienti/{io.cliente_id}", json={"cliente_ruolo": f.RUOLO_PROVINCIALE}, headers=sessione)
    assert cambio.status_code == 403
    assert _ruolo(db, io.cliente_id) == f.RUOLO_REGIONALE

    uguale = client.put(f"/clienti/{io.cliente_id}", json={"cliente_ruolo": f.RUOLO_REGIONALE}, headers=sessione)
    assert uguale.status_code == 200, uguale.text


def test_un_ruolo_nullo_sulla_propria_riga_e_un_cambio(client, db):
    """Con la sql_mode non strict di produzione MariaDB salva il null come 0:
    senza questo controllo si cambiava il proprio ruolo mandando null. Sul
    database di test, che e' strict, lo stesso corpo dava un 500."""
    io, sessione = accedi(client, db)
    risposta = client.put(f"/clienti/{io.cliente_id}", json={"cliente_ruolo": None}, headers=sessione)
    assert (risposta.status_code, risposta.json()) == (403, SOLO_NAZIONALE)
    assert _ruolo(db, io.cliente_id) == f.RUOLO_REGIONALE


def test_il_ruolo_su_un_non_visibile_risponde_come_un_inesistente(client, db):
    """Il controllo sul ruolo viene dopo quello di visibilita': altrimenti un
    403 rivelerebbe che il cliente esiste."""
    _, sessione = accedi(client, db)
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")
    corpo = {"cliente_ruolo": f.RUOLO_NAZIONALE}
    inesistente = client.put("/clienti/999999", json=corpo, headers=sessione)
    nascosto = client.put(f"/clienti/{estraneo.cliente_id}", json=corpo, headers=sessione)
    assert (nascosto.status_code, nascosto.json()) == (404, NON_TROVATA)
    assert nascosto.json() == inesistente.json()
    assert _ruolo(db, estraneo.cliente_id) == f.RUOLO_ADERENTE


def test_si_assegnano_ruoli_non_nazionali_ai_visibili(client, db):
    io, sessione = accedi(client, db)
    figlio = f.crea_attuatore(db, email="figlio@example.org", padre=io.utente_id,
                              ruolo=f.RUOLO_SOTTOSCRITTORE)
    risposta = client.put(f"/clienti/{figlio.cliente_id}", json={"cliente_ruolo": f.RUOLO_ADERENTE}, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    assert _ruolo(db, figlio.cliente_id) == f.RUOLO_ADERENTE


def test_con_utente_non_crea_nazionali(client, db):
    from tests.integration.test_clienti import _anagrafica

    _, sessione = accedi(client, db)
    prima = db.query(Utente).count()
    risposta = client.post("/clienti/con-utente", json=_anagrafica(cliente_ruolo=f.RUOLO_NAZIONALE), headers=sessione)
    assert risposta.status_code == 403
    assert risposta.json() == SOLO_NAZIONALE
    assert db.query(Utente).count() == prima


def test_il_nazionale_assegna_il_ruolo_nazionale(client, db, mailer):
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")
    _, sessione = accedi_nazionale(client, db, mailer)
    risposta = client.put(f"/clienti/{estraneo.cliente_id}", json={"cliente_ruolo": f.RUOLO_NAZIONALE}, headers=sessione)
    assert risposta.status_code == 200, risposta.text
    assert _ruolo(db, estraneo.cliente_id) == f.RUOLO_NAZIONALE


# =============================================================================
# Contatti
# =============================================================================
def test_stato_contatti_non_visibile(client, db, spia_sql):
    _, sessione = accedi(client, db)
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")

    inesistente = client.get("/clienti/999999/contatti", headers=sessione)
    spia_sql.clear()
    nascosto = client.get(f"/clienti/{estraneo.cliente_id}/contatti", headers=sessione)

    assert inesistente.status_code == nascosto.status_code == 404
    assert nascosto.json() == inesistente.json() == NON_TROVATA
    assert not any("FOR UPDATE" in s for s in spia_sql)


def test_genera_otp_non_visibile_non_lascia_tracce(client, db, mailer, sms, spia_sql):
    from src.otp.models import Limite, Sfida

    _, sessione = accedi(client, db)
    estraneo = f.crea_attuatore(db, email="estraneo@example.org")
    mailer.svuota()
    spia_sql.clear()

    for tipo, valore in (("email", "estraneo@example.org"), ("cellulare", "")):
        risposta = client.post(f"/clienti/{estraneo.cliente_id}/contatti/{tipo}/genera-otp",
                               json={"valore": valore}, headers=sessione)
        assert risposta.status_code == 404
        assert risposta.json() == NON_TROVATA

    # Nessun lock: il controllo viene prima di blocca_cliente.
    assert not any("FOR UPDATE" in istruzione for istruzione in spia_sql)
    assert db.query(Sfida).count() == 0
    assert db.query(Limite).count() == 0
    assert mailer.inviate == []
    assert sms.inviati == []


def test_verifica_otp_non_visibile_non_consuma_la_sfida(client, db, mailer, spia_sql):
    """Un codice giusto, presentato da chi non vede il cliente, non deve
    consumare la sfida, verificare il contatto ne' attivare l'account."""
    import re

    from src.notifiche.formato_email import come_testo
    from src.otp.models import ContattoVerificato, Sfida
    from tests.conftest import corpo_html
    from tests.integration.test_otp import invia, nuovo

    identita, del_padre = nuovo(client, db)
    sfida = invia(client, identita, del_padre, "email")
    codice = re.search(r"\b\d{6}\b", come_testo(corpo_html(mailer.inviate[-1]))).group()
    riga = db.query(Sfida).one()
    prima = (riga.stato, riga.tentativi)
    inviate = len(mailer.inviate)

    _, estraneo = accedi(client, db)
    spia_sql.clear()
    risposta = client.post(f"/clienti/{identita['cliente_id']}/contatti/email/verifica-otp",
                           json={"sfida": sfida, "codice": codice}, headers=estraneo)

    assert not any("FOR UPDATE" in istruzione for istruzione in spia_sql)
    assert risposta.status_code == 404
    assert risposta.json() == NON_TROVATA
    db.expire_all()
    riga = db.query(Sfida).one()
    assert (riga.stato, riga.tentativi) == prima
    assert db.query(ContattoVerificato).count() == 0
    assert db.get(Utente, identita["utente_id"]).utente_attivoSN == f.DISATTIVO
    assert len(mailer.inviate) == inviate
