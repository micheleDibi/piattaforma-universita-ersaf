// Modello minimo per i test del motore: sfondo, testo, firma, due pagine.
#let dati = json(bytes(sys.inputs.dati))
#set page(width: 105mm, height: 148mm, margin: 0pt, background: image("sfondo.svg", width: 100%, height: 100%))
#set text(size: 9pt)
#place(top + left, dx: 10mm, dy: 10mm)[#dati.nome]
#if "firma" in dati.allegati {
  place(top + left, dx: 10mm, dy: 60mm, image(dati.allegati.firma, width: 40mm))
}
#pagebreak()
#place(top + left, dx: 10mm, dy: 10mm)[Seconda pagina]
