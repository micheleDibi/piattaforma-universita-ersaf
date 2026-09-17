"""Backfill di ContattoVerificato dai log storici del vecchio sistema OTP
(tabella logs_otp), per i clienti che hanno gia' verificato email o
cellulare prima che esistesse la tabella otp_contatti.

Per ogni cliente e tipo (email/cellulare), prende l'ULTIMA verifica
riuscita (log_otp_check = -1) in ordine di log_otp_datetime_check - coerente
con come funziona ContattoVerificato nel sistema nuovo, dove c'e' una sola
riga per cliente/tipo che rappresenta la verifica piu' recente valida per
il valore corrente - e la scrive SOLO SE il valore verificato all'epoca
(log_otp_riferimento) coincide ancora col valore attuale del cliente: se
l'email o il cellulare sono cambiati da allora, quella vecchia verifica non
e' piu' valida per il dato corrente e va scartata, non riportata.

Non sovrascrive mai una riga ContattoVerificato gia' esistente (es. scritta
dal sistema OTP nuovo): il backfill riguarda solo chi non ha ancora nessuna
riga per quel contatto. Coerente col commento in db/013_verifiche_otp.sql
("Il registro legacy logs_otp resta invariato"): quella migrazione non ha
mai copiato lo storico nelle nuove tabelle, quindi questo script colma un
buco mai colmato, non ripete un lavoro gia' fatto.

Uso (dalla root del backend, con il virtualenv attivo):
    python -m src.comune.backfill_contatti_storici           # dry-run, nessuna scrittura
    python -m src.comune.backfill_contatti_storici --applica  # scrive per davvero
"""
import argparse
import logging
from sqlalchemy import text

from src.database import SessionLocal
from src.clienti.models import Cliente
from src.otp.models import ContattoVerificato
from src.otp.identita import versione
from src.utenti.models import Utente  # noqa: F401
from src.ruolo.models import Ruolo  # noqa: F401
from src.universita.models import Universita  # noqa: F401
from src.aziende.models import Azienda  # noqa: F401
from src.pratiche.models import Pratica  # noqa: F401
from src.aziende.models import Azienda  # noqa: F401
from src.aziende_xcod.models import AziendaXCod  # noqa: F401
from src.ruolo.models import Ruolo  # noqa: F401
from src.utenti.models import Utente  # noqa: F401
from src.universita.models import Universita  # noqa: F401
from src.pratiche_registri_mise.models import PraticaRegistroMise  # noqa: F401
from src.listino_tipoCorso.models import ListinoTipoCorsoDB  # noqa: F401
from src.pratiche_stati.models import PraticaStato  # noqa: F401
from src.listini_testa.models import ListinoTestaDB  # noqa: F401
from src.auth.models import (  # noqa: F401
    AuthSessione,
    PasswordResetRichiesta,
    PasswordResetToken,
)
from src.notifiche.models import MessaggioEmail  # noqa: F401

logger = logging.getLogger("ersaf.backfill_contatti")

CAMPO_CLIENTE = {"email": "cliente_email", "cellulare": "cliente_cellulare"}


def _ultime_verifiche_storiche(db):
    """Per ogni (cliente_id, tipo), l'ULTIMA verifica riuscita nel vecchio
    log, col valore che era stato effettivamente verificato in
    quell'occasione."""
    righe = db.execute(text("""
        SELECT l.cliente_id, l.log_otp_tipo_riferimento AS tipo,
               l.log_otp_riferimento AS valore_verificato,
               l.log_otp_datetime_check AS verificato_il
        FROM admin_entedb.logs_otp l
        INNER JOIN (
            SELECT cliente_id, log_otp_tipo_riferimento AS tipo,
                   MAX(log_otp_datetime_check) AS ultima_verifica
            FROM admin_entedb.logs_otp
            WHERE log_otp_tipo_riferimento IN ('email', 'cellulare')
              AND log_otp_check = -1
              AND log_otp_datetime_check IS NOT NULL
            GROUP BY cliente_id, log_otp_tipo_riferimento
        ) ultime
        ON l.cliente_id = ultime.cliente_id
        AND l.log_otp_tipo_riferimento = ultime.tipo
        AND l.log_otp_datetime_check = ultime.ultima_verifica
        WHERE l.log_otp_check = -1
    """)).all()
    return righe


def esegui_backfill(applica: bool):
    db = SessionLocal()
    try:
        candidate = _ultime_verifiche_storiche(db)
        logger.info("trovate %d verifiche storiche candidate", len(candidate))

        scritte = 0
        saltate_valore_diverso = 0
        saltate_gia_presenti = 0
        saltate_cliente_assente = 0

        for riga in candidate:
            cliente = db.get(Cliente, riga.cliente_id)
            if cliente is None:
                saltate_cliente_assente += 1
                continue

            esistente = db.get(ContattoVerificato, (cliente.cliente_id, riga.tipo))
            if esistente is not None:
                saltate_gia_presenti += 1
                continue

            valore_attuale = getattr(cliente, CAMPO_CLIENTE[riga.tipo]) or ""
            valore_storico = (riga.valore_verificato or "").strip()

            coincide = (
                valore_attuale.strip().lower() == valore_storico.lower()
                if riga.tipo == "email"
                else valore_attuale.strip() == valore_storico
            )
            if not coincide:
                saltate_valore_diverso += 1
                logger.debug(
                    "cliente_id=%s tipo=%s: valore cambiato dopo la verifica storica (storico=%r, attuale=%r)",
                    cliente.cliente_id, riga.tipo, valore_storico, valore_attuale,
                )
                continue

            if applica:
                db.add(ContattoVerificato(
                    cliente_id=cliente.cliente_id,
                    tipo=riga.tipo,
                    versione=versione(cliente, riga.tipo),
                    verificato=riga.verificato_il,
                ))
            scritte += 1

        if applica:
            db.commit()

        logger.info(
            "%s: %d righe %s, %d saltate (valore cambiato), %d saltate (gia' presenti), %d saltate (cliente assente)",
            "APPLICATO" if applica else "DRY-RUN",
            scritte,
            "scritte" if applica else "che verrebbero scritte",
            saltate_valore_diverso,
            saltate_gia_presenti,
            saltate_cliente_assente,
        )
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--applica", action="store_true", help="Scrive davvero nel database (default: dry-run)")
    args = parser.parse_args()
    esegui_backfill(applica=args.applica)