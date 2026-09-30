---
---

## Dettagli tecnici

- corretto: La cache dei modelli PDF sotto la cartella temporanea si confronta con il modello a ogni
  composizione, file per file con la dimensione, e si rifà se ne manca qualcuno: prima una cartella
  rimasta senza `modulo.typ` o senza immagini, per esempio dopo la pulizia automatica dei
  temporanei di Windows, restava in uso e ogni PDF di quel modello falliva.
- aggiunto: Il compilatore PDF scrive su stderr solo una categoria dell'errore, che
  `documenti/esecuzione.py` registra nel log con il codice d'uscita; anche l'interruzione per tempo
  scaduto finisce nel log.
