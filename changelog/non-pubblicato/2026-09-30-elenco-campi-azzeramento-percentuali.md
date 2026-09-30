---
---

## Novità e correzioni

- modificato: L'avviso prima di azzerare delle percentuali (nella scheda dell'azienda e nel cambio di padre) ora indica quali atenei verrebbero coinvolti, invece del generico "Alcune percentuali verranno azzerate", con una nota più piccola che ricorda che una percentuale non può superare quella dell'azienda padre.

## Dettagli tecnici

- aggiunto: `messaggioAzzeramento` in `frontend/src/lib/schedaAzienda.js`, che compone il testo dell'avviso a partire dal campo `reset` già restituito dal server con il 409 (prima ignorato); usato sia da `DettaglioConvenzioniUniversitarie.jsx` sia da `GerarchiaAzienda.jsx`. Nessuna modifica al backend.
- aggiunto: `AlertMessage` accetta ora `message.nota`, una riga più piccola sotto il testo principale ma dentro lo stesso riquadro colorato (nuovo `notaFeedback` in `frontend/src/config/styles/feedback.js`).
