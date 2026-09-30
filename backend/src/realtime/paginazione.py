import hashlib
import hmac

from src.chat_pratiche.cifratura import codifica, decodifica
from src.realtime.errori import ErroreRealtime, richiedi
from src.realtime.token import segreto


def firma(raw):
    return hmac.new(segreto(), b"universo:page-cursor:v2\n" + raw, hashlib.sha256).digest()


def cursore(identita, ambito, ultimo):
    raw = f"2\n{ambito}\n{identita.utente_id}:{identita.cliente_id}\n{ultimo}".encode()
    return codifica(raw) + "." + codifica(firma(raw))


def confine(identita, ambito, token):
    if token is None:
        return 9223372036854775807
    try:
        richiedi(0 < len(token) <= 512 and "=" not in token, "invalid_cursor")
        testo, sig = token.split(".")
        raw = decodifica(testo)
        richiedi(codifica(raw) == testo and hmac.compare_digest(codifica(firma(raw)), sig), "invalid_cursor")
        v, a, u, ultimo = raw.decode().split("\n")
        richiedi(
            v == "2"
            and a == ambito
            and u == f"{identita.utente_id}:{identita.cliente_id}"
            and 0 < int(ultimo) <= 9223372036854775807,
            "invalid_cursor",
        )
        return int(ultimo)
    except (ValueError, UnicodeError):
        raise ErroreRealtime("invalid_cursor") from None


def parametri(identita, ambito, richiesta):
    try:
        n = int(richiesta.get("limit", "10"))
    except ValueError:
        raise ErroreRealtime("invalid_limit") from None
    richiedi(1 <= n <= 100, "invalid_limit")
    return dict(
        u=identita.utente_id,
        c=identita.cliente_id,
        n=n + 1,
        prima=confine(identita, ambito, richiesta.get("cursor")),
    )


def pagina(identita, coordinate, elementi, campo):
    ambito, limite = coordinate
    altri = len(elementi) > limite
    elementi = elementi[:limite]
    return dict(
        items=elementi,
        hasMore=altri,
        nextCursor=cursore(identita, ambito, elementi[-1][campo]) if altri else None,
    )
