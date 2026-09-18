"""Frammenti di changelog: lettura, validazione e composizione.

Un frammento è un file `changelog/non-pubblicato/AAAA-MM-GG-slug.md` con un
piccolo frontmatter (`pr`, `incompatibile`, entrambi facoltativi) e fino a due
sezioni, "Novità e correzioni" e "Dettagli tecnici", fatte di voci
`- tipo: testo`. Il formato completo, con gli esempi, è in changelog/MODELLO.md.

Solo libreria standard: lo usa anche timbra_changelog.py.
"""

from __future__ import annotations

import datetime as dt
import posixpath
import re
from dataclasses import dataclass, field

from comune import normalizza

CARTELLA = "changelog/non-pubblicato"
ESCLUSI = frozenset({"LEGGIMI.md"})

TIPI = ("aggiunto", "modificato", "corretto", "sicurezza", "rimosso")
ETICHETTE_TIPI = {
    "aggiunto": "Aggiunto",
    "modificato": "Modificato",
    "corretto": "Corretto",
    "sicurezza": "Sicurezza",
    "rimosso": "Rimosso",
}
NOVITA = "Novità e correzioni"
TECNICO = "Dettagli tecnici"
PARTI = (NOVITA, TECNICO)

_NOME = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
LUNGHEZZA_MASSIMA_NOME = 80
_VOCE = re.compile(r"^- ([a-z]+): (.*\S)\s*$")
_CONTINUAZIONE = re.compile(r"^ {2,}(\S.*)$")
_TITOLO = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]*)")
_RIFERIMENTO = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
_INTERO = re.compile(r"^[1-9][0-9]*$")


@dataclass(frozen=True)
class Voce:
    parte: str
    tipo: str
    testo: str


@dataclass
class Frammento:
    nome: str
    pr: int | None = None
    incompatibile: bool = False
    voci: list[Voce] = field(default_factory=list)


class FrammentoNonValido(ValueError):
    def __init__(self, nome: str, errori: list[str]):
        self.nome = nome
        self.errori = errori
        super().__init__(f"{nome}: " + "; ".join(errori))


def e_frammento(percorso: str) -> bool:
    """Vero per i file della cartella che vanno validati e raccolti."""
    cartella, nome = posixpath.split(percorso)
    return cartella == CARTELLA and nome.endswith(".md") and nome not in ESCLUSI


def errori_nome(nome: str) -> list[str]:
    if len(nome) > LUNGHEZZA_MASSIMA_NOME:
        return [f"il nome supera {LUNGHEZZA_MASSIMA_NOME} caratteri"]
    trovato = _NOME.match(nome)
    if not trovato:
        return ["il nome deve essere AAAA-MM-GG-slug.md, con lo slug in minuscolo "
                "(lettere, cifre e trattini)"]
    anno, mese, giorno = (int(parte) for parte in trovato.groups()[:3])
    try:
        dt.date(anno, mese, giorno)
    except ValueError:
        return ["la data nel nome non esiste"]
    return []


def _valore_frontmatter(riga: str) -> tuple[str, str] | None:
    # Commento in linea ammesso solo se preceduto da uno spazio, come in YAML.
    senza_commento = re.sub(r"\s+#.*$", "", riga)
    if ":" not in senza_commento:
        return None
    chiave, valore = senza_commento.split(":", 1)
    return chiave.strip(), valore.strip()


def _leggi_frontmatter(righe: list[str], frammento: Frammento, errori: list[str]) -> int:
    """Restituisce l'indice della prima riga del corpo."""
    if not righe or righe[0] != "---":
        errori.append("manca il frontmatter: il file deve iniziare con una riga '---'")
        return 0
    try:
        fine = righe.index("---", 1)
    except ValueError:
        errori.append("il frontmatter non è chiuso da una riga '---'")
        return len(righe)
    viste = set()
    for riga in righe[1:fine]:
        if not riga.strip() or riga.lstrip().startswith("#"):
            continue
        coppia = _valore_frontmatter(riga)
        if coppia is None or riga[:1].isspace():
            errori.append(f"riga del frontmatter non valida: {riga!r}")
            continue
        chiave, valore = coppia
        if chiave in viste:
            errori.append(f"chiave ripetuta nel frontmatter: {chiave}")
            continue
        viste.add(chiave)
        if chiave == "pr":
            if not _INTERO.match(valore):
                errori.append("pr deve essere un numero intero positivo, senza zeri iniziali")
            else:
                frammento.pr = int(valore)
        elif chiave == "incompatibile":
            if valore not in ("true", "false"):
                errori.append("incompatibile deve essere true oppure false")
            else:
                frammento.incompatibile = valore == "true"
        else:
            errori.append(f"chiave non ammessa nel frontmatter: {chiave} (ammesse: pr, incompatibile)")
    return fine + 1


def _controlla_link(riga: str, numero: int, errori: list[str]) -> None:
    destinazioni = _LINK.findall(riga)
    riferimento = _RIFERIMENTO.match(riga)
    if riferimento:
        destinazioni.append(riferimento.group(1))
    for destinazione in destinazioni:
        if not re.match(r"^https?://", destinazione):
            errori.append(
                f"riga {numero}: link {destinazione!r} non ammesso; nei frammenti "
                "solo link assoluti http(s), perché il testo finisce in CHANGELOG.md"
            )


def analizza(nome: str, testo: str) -> Frammento:
    """Legge un frammento; solleva FrammentoNonValido con tutti gli errori."""
    errori = errori_nome(nome)
    frammento = Frammento(nome=nome)
    righe = normalizza(testo).split("\n")
    inizio = _leggi_frontmatter(righe, frammento, errori)

    parte = None
    viste: set[str] = set()
    ultima: list[str] | None = None
    raccolte: list[tuple[str, str, list[str]]] = []
    for indice in range(inizio, len(righe)):
        riga = righe[indice]
        numero = indice + 1
        if not riga.strip():
            ultima = None
            continue
        _controlla_link(riga, numero, errori)
        titolo = _TITOLO.match(riga)
        if titolo:
            ultima = None
            if len(titolo.group(1)) != 2 or titolo.group(2) not in PARTI:
                errori.append(f"riga {numero}: titolo non ammesso; usare solo "
                              f"'## {NOVITA}' e '## {TECNICO}'")
                parte = None
                continue
            if titolo.group(2) in viste:
                errori.append(f"riga {numero}: la sezione '{titolo.group(2)}' compare due volte")
            viste.add(titolo.group(2))
            parte = titolo.group(2)
            continue
        voce = _VOCE.match(riga)
        if voce:
            if parte is None:
                errori.append(f"riga {numero}: voce fuori da una sezione")
                ultima = None
                continue
            tipo, testo_voce = voce.groups()
            if tipo not in TIPI:
                errori.append(f"riga {numero}: tipo '{tipo}' non ammesso (ammessi: {', '.join(TIPI)})")
            ultima = [testo_voce]
            raccolte.append((parte, tipo, ultima))
            continue
        continuazione = _CONTINUAZIONE.match(riga)
        if continuazione and ultima is not None:
            ultima.append(continuazione.group(1).strip())
            continue
        errori.append(f"riga {numero}: riga non ammessa; ogni voce è '- tipo: testo' "
                      "e può continuare su righe rientrate di due spazi")

    for parte_voce, tipo, pezzi in raccolte:
        testo_voce = " ".join(pezzi)
        if parte_voce == NOVITA and "`" in testo_voce:
            errori.append(f"voce '{testo_voce[:40]}…': nelle novità niente codice fra "
                          "apici inversi, il testo è per chi usa la piattaforma")
        frammento.voci.append(Voce(parte_voce, tipo, testo_voce))
    for parte_vista in viste:
        if not any(v.parte == parte_vista for v in frammento.voci):
            errori.append(f"la sezione '{parte_vista}' non ha voci")
    if not frammento.voci:
        errori.append("nessuna voce: serve almeno una voce in una delle due sezioni")
    if frammento.incompatibile and not any(v.parte == TECNICO for v in frammento.voci):
        errori.append(f"incompatibile: true richiede almeno una voce in '{TECNICO}'")
    if errori:
        raise FrammentoNonValido(nome, errori)
    return frammento


def componi(frammenti: list[Frammento]) -> str:
    """Corpo di una versione nel CHANGELOG, senza il titolo `## Versione`."""
    ordinati = sorted(frammenti, key=lambda f: f.nome)
    blocchi = []
    for parte in PARTI:
        sezione = []
        for tipo in TIPI:
            voci = []
            for frammento in ordinati:
                for voce in frammento.voci:
                    if voce.parte != parte or voce.tipo != tipo:
                        continue
                    testo = voce.testo
                    if parte == TECNICO and frammento.incompatibile:
                        testo = f"**Incompatibile.** {testo}"
                    if frammento.pr is not None:
                        testo = f"{testo} (PR #{frammento.pr})"
                    voci.append(f"- {testo}")
            if voci:
                sezione.append(f"**{ETICHETTE_TIPI[tipo]}**\n\n" + "\n".join(voci))
        if sezione:
            blocchi.append(f"### {parte}\n\n" + "\n\n".join(sezione))
    if not blocchi:
        return "Nessuna modifica documentata."
    return "\n\n".join(blocchi)
