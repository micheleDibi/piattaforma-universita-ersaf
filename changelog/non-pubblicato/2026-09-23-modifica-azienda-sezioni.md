---
---

## Novità e correzioni

- modificato: La pagina Modifica azienda è divisa in sezioni (Dati anagrafici, Sede legale, Contatti,
  Coordinate bancarie, Gerarchia, Convenzioni universitarie) e mostra subito se la partita IVA non
  ha 11 cifre.
- modificato: Le percentuali delle convenzioni universitarie sono in una tabella per ateneo e
  tipologia di corso, sia nella scheda dell'azienda sia nella scheda Azienda dell'attuatore.

## Dettagli tecnici

- aggiunto: Componente `shared/SezioneModulo` e `SEZIONI_AZIENDA` in `config/campiAzienda.js`.
- modificato: `DettaglioConvenzioniUniversitarie` accetta `inSezione` per stare dentro una sezione di
  modulo senza scheda e titolo propri.
