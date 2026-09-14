"""Tema delle email: struttura FindYourGoal, identita Pratiche Universita."""

from pathlib import Path

NOME = "Pratiche Università"
LOGO = Path(__file__).parent / "assets" / "pratiche-universita.png"
LOGO_CID = "pratiche-universita"
COLORI = {
    "primario": "#302878", "testo": "#3E4047", "superficie": "#FFFFFF",
    "sfondo": "#f6f9fc", "bordo": "#eef2f7", "tenue": "#6b7280",
    "riquadro": "#f9fafb",
}
FIRMA = (
    "Ente di Ricerca Scientifica ed Alta Formazione — ERSAF",
    "P.zza del Popolo, 18 · 00187 Roma (RM)",
    "Cod. Fisc. 97905810582 · P. IVA 14061981008",
    "Tel. 06-92949895 · info@ersaf.it · https://www.ersaf.it",
)
STILI_TAG = {
    "p": "margin:0 0 12px;",
    "a": f"color:{COLORI['primario']};overflow-wrap:anywhere;word-break:break-word;",
}
STILI_CLASSI = {
    "email-azione": (
        f"display:inline-block;padding:10px 16px;background:{COLORI['primario']};"
        "color:#ffffff;text-decoration:none;border-radius:6px;font-weight:bold;"
    ),
    "email-riquadro": (
        f"margin:12px 0;padding:12px 14px;background:{COLORI['riquadro']};"
        f"border:1px solid {COLORI['bordo']};border-radius:6px;"
    ),
    "email-codice": (
        f"margin:0;font-size:28px;font-weight:bold;letter-spacing:6px;color:{COLORI['primario']};"
        "font-family:Menlo,Consolas,monospace;"
    ),
    "email-credenziale": "font-family:Menlo,Consolas,monospace;overflow-wrap:anywhere;word-break:break-word;",
    "email-nota": f"font-size:14px;color:{COLORI['tenue']};",
}
