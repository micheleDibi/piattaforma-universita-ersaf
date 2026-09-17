# Come lavorare sul progetto e mandare le proprie modifiche

Aggiornata all'11 settembre 2026, dopo la decisione sul flusso di pubblicazione.

L'ambiente di collaudo **https://unistaging.ersaf.it** pubblica soltanto quello
che si trova sul ramo `main`, e la pubblicazione la fa una persona sola, a fine
giornata, dopo aver rivisto il codice. Chi sviluppa non pubblica.

Questo non e' un limite di fiducia: serve a tenere il collaudo in uno stato
prevedibile, visto che l'ambiente e' uno solo e lo guarda anche chi non
sviluppa.

---

## Il giro di tutti i giorni

### 1. Lavora sul tuo ramo

```powershell
git switch Login
```

Committa spesso, con messaggi che dicano cosa cambia.

### 2. A fine lavoro manda il ramo su GitHub

```powershell
git push origin Login
```

### 3. Apri una pull request verso `main`

Dalla pagina del repository su GitHub, il pulsante compare da solo dopo il push.
Nella descrizione basta poco: cosa hai fatto e cosa conviene provare.

### 4. Da li' in poi tocca a chi revisiona

Le modifiche vengono lette, unite su `main` e pubblicate sul collaudo. Se serve
una correzione te lo si dice sulla pull request, tu committi ancora sul tuo ramo
e il push aggiorna la stessa richiesta.

Quando la pubblicazione e' fatta, ricontrolla il tuo lavoro su
https://unistaging.ersaf.it, ricaricando con Ctrl+F5 per non restare sulla
versione vecchia del browser.

---

## Due cose da sapere sul collaudo

**Il database e' una copia.** I dati veri stanno su un altro server e non
vengono mai modificati da qui. Quello che provi in collaudo non arriva in
produzione.

**Le email non partono davvero.** In collaudo i messaggi, per esempio quelli di
recupero password, vengono scritti su file sul server invece di essere spediti.
Se ti serve leggerne uno, chiedi.

---

## Se il collaudo non risponde

Non provare a intervenire sul server: segnalalo e basta, indicando cosa stavi
facendo e cosa hai visto. Chi pubblica ha gli strumenti per guardare lo stato e
i log, e se una pubblicazione va storta l'ambiente torna da solo alla versione
precedente.

---

## Nota storica

La prima configurazione prevedeva che ogni sviluppatore pubblicasse da se' con
`scripts\deploy.ps1`. La scelta e' stata poi cambiata a favore della revisione
prima della pubblicazione. Lo script resta nel repository ed e' usato da chi
pubblica.
