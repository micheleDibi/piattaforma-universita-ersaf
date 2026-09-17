// Moduli a campi: ogni pagina e' un'immagine e i campi arrivano gia' risolti,
// con le posizioni in millimetri dall'angolo in alto a sinistra (vedi
// src/documenti/impaginazione.py). Qui si decide solo come si scrive.

#let corpo = 9pt
#let corpo-minimo = 5.5pt
// Il testo poggia poco sopra la linea di scrittura.
#let rialzo = 0.8mm
#let inchiostro = black
#let tratto-crocetta = 0.9pt + inchiostro
#let altezza-a4 = 297mm
#let allineamenti = (left: left, center: center, right: right)

#let mm(valore) = valore * 1mm

// Il bordo inferiore del contenuto (per il testo, la linea di base) va alla quota y.
#let su-linea(x, y, larghezza, contenuto) = place(
  bottom + left,
  dx: mm(x),
  dy: mm(y) - rialzo - altezza-a4,
  box(width: larghezza, contenuto),
)

// Un testo troppo lungo si rimpicciolisce fino a entrare nella linea.
#let adattato(testo, larghezza) = context {
  let dimensione = corpo
  while dimensione > corpo-minimo and measure(text(size: dimensione, testo)).width > larghezza {
    dimensione -= 0.25pt
  }
  text(size: dimensione, testo)
}

#let testo(campo) = {
  let larghezza = mm(campo.x1 - campo.x0 - 1)
  let allineato = align(allineamenti.at(campo.allinea), adattato(campo.testo, larghezza))
  su-linea(campo.x0 + 0.5, campo.y, larghezza, allineato)
}

#let griglia(campo) = {
  let passo = (campo.x1 - campo.x0) / campo.celle
  let caratteri = campo.testo.clusters()
  for (indice, carattere) in caratteri.slice(0, calc.min(campo.celle, caratteri.len())).enumerate() {
    su-linea(campo.x0 + indice * passo, campo.y, mm(passo), align(center, carattere))
  }
}

#let crocetta(campo) = {
  let (sinistra, destra) = (mm(campo.x + 0.4), mm(campo.x + campo.lato - 0.4))
  let (alto, basso) = (mm(campo.y + 0.4), mm(campo.y + campo.lato - 0.4))
  place(top + left, line(start: (sinistra, alto), end: (destra, basso), stroke: tratto-crocetta))
  place(top + left, line(start: (sinistra, basso), end: (destra, alto), stroke: tratto-crocetta))
}

// La firma, gia' ritagliata sul tratto, poggia sulla linea e la tocca appena.
#let firma(campo, immagine) = place(
  bottom + left,
  dx: mm(campo.x0),
  dy: mm(campo.y + 0.8) - altezza-a4,
  box(
    width: mm(campo.x1 - campo.x0),
    height: mm(campo.altezza),
    image(immagine, width: 100%, height: 100%, fit: "contain"),
  ),
)

#let componi(dati) = {
  set page(paper: "a4", margin: 0pt)
  set text(
    font: "Liberation Sans",
    size: corpo,
    fill: inchiostro,
    lang: "it",
    top-edge: "cap-height",
    bottom-edge: "baseline",
  )
  let immagine-firma = dati.allegati.at("firma", default: none)
  for pagina in dati.pagine {
    page(background: image("/" + pagina.sfondo, width: 100%, height: 100%))[
      #for campo in pagina.campi {
        if campo.tipo == "testo" { testo(campo) }
        else if campo.tipo == "griglia" { griglia(campo) }
        else if campo.tipo == "casella" { crocetta(campo) }
        else if campo.tipo == "firma" and immagine-firma != none { firma(campo, "/" + immagine-firma) }
      }
    ]
  }
}
