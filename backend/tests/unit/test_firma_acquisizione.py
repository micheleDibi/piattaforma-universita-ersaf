import base64
import io

import pytest
from fastapi import HTTPException
from PIL import Image, ImageDraw

from src.pratiche.firma import normalizza_firma, stato_firma


def disegno(colore="black", formato="PNG", dimensioni=(180, 70)):
    immagine = Image.new("RGBA", dimensioni, (255, 255, 255, 0))
    ImageDraw.Draw(immagine).line([(10, 45), (55, 15), (80, 55), (160, 25)], fill=colore, width=3)
    output = io.BytesIO()
    immagine.save(output, formato)
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()


def test_png_normalizzato_e_compatibile_con_pdf_legacy():
    png = normalizza_firma(disegno())
    with Image.open(io.BytesIO(png)) as img:
        assert img.mode == "L"
        assert img.getpixel((0, 0)) == 255
    stato = stato_firma(b"BLOBpng" + bytes(9) + png)
    assert stato["presente"]
    assert base64.b64decode(stato["immagine"].split(",")[1]).startswith(b"\x89PNG")


@pytest.mark.parametrize("valore", [disegno("white"), disegno((0, 0, 0, 0)),
    disegno(formato="GIF"), disegno(dimensioni=(2049, 70)), "data:image/png;base64,nonvalido", "<svg></svg>"])
def test_rifiuta_firme_vuote_formati_alternativi_e_dimensioni_eccessive(valore):
    with pytest.raises(HTTPException) as errore:
        normalizza_firma(valore)
    assert errore.value.status_code == 422
