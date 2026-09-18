// Domanda di immatricolazione ai corsi di laurea eCampus: le dieci pagine del modello.
#import "/_comune/impaginato.typ": componi
#let dati = json(bytes(sys.inputs.dati))
#set document(title: dati.titolo)
#componi(dati)
