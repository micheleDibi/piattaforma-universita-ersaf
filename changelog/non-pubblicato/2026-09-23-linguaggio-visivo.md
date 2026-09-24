---
---

## Novità e correzioni

- modificato: Tutta l'applicazione adotta il nuovo linguaggio visivo: cambiano colori, caratteri,
  pulsanti, campi, messaggi, schede e intestazioni delle pagine; menu laterale e barra superiore
  mantengono la loro struttura e la voce attiva dorata.
- modificato: Negli elenchi Sottoscrittori e Attuatori nominativo e azienda vanno a capo al massimo
  su due righe e si leggono per intero passando il mouse; la testata con ricerca, «Filtri» e
  «Nuovo», anche quando resta agganciata in alto, forma una sola scheda con l'elenco.
- modificato: Negli elenchi il segnale giallo accanto al nome apre, subito sotto, un riquadro con il
  numero di errori e l'elenco; si chiude cliccando fuori o con Esc e non apre la scheda.
- modificato: Su schermi stretti, se non c'è spazio, il numero di risultati va a capo sotto il
  titolo dell'elenco invece di spezzare il titolo.
- modificato: Nella scheda di sottoscrittori e attuatori nome, codice fiscale e stato dell'account
  stanno su una riga sotto il titolo e non cambiano più mentre si scrive nei campi; «Annulla» e
  «Salva modifiche» restano visibili in fondo mentre si scorre.
- modificato: Nei dati principali email e cellulare stanno in riquadri in evidenza con lo stato di
  verifica; PEC e telefono sono raccolti in «Altri recapiti».
- modificato: Nel curriculum le sotto-schede si scelgono da un selettore, gli altri titoli sono in
  una tabella e le caselle si attivano anche con un clic sul testo; nella scheda Utente le date
  della cronologia sono sempre in formato italiano.
- modificato: Nella scheda Abilitazioni dell'attuatore ogni abilitazione è un riquadro con
  l'interruttore, che si attiva anche con un clic sul nome.
- modificato: Gli avvisi di un'anagrafica in cima alla scheda del sottoscrittore e dell'azienda hanno
  lo stesso aspetto degli altri messaggi, con un elenco puntato quando sono più di uno.
- aggiunto: Nelle schede di sottoscrittori, attuatori e aziende i campi con un'anomalia hanno il bordo
  giallo e una nota breve sotto, per esempio «Duplicato con 2 anagrafiche» o «Da compilare», che
  sparisce appena si modifica il campo.
- aggiunto: Nella scheda di un'azienda, sotto il titolo, la ragione sociale è seguita da «Figlia di»
  e dal nome dell'azienda padre; la ragione sociale sotto il titolo è quella salvata e non cambia
  mentre si scrive.
- modificato: Nella scheda dell'azienda una partita IVA diversa da 11 cifre è segnalata in giallo,
  come avviso, e non più in rosso; il codice nazionale si può selezionare e copiare, e Codice SDI,
  PEC, IBAN e Codice BIC mostrano un esempio quando sono vuoti.
- modificato: La provincia di un'azienda, ora «Prov.», accetta al massimo 2 caratteri, anche nella
  creazione rapida dalla scheda Azienda di un attuatore.
- modificato: Nella finestra «Nessuna azienda trovata con questa Partita IVA» IBAN e BIC stanno sulla
  stessa riga e i pulsanti «Annulla» e «Crea e associa» sono in basso a destra.
- modificato: Nella pagina Pratiche il pannello degli atenei sta in un riquadro sotto il titolo;
  nell'elenco delle pratiche il corso va a capo al massimo su due righe e lo stato resta su una.
- modificato: I campi numerici, come percentuali, voti, durata e CFU, non mostrano più le frecce per
  aumentare o diminuire il valore.

## Dettagli tecnici

- aggiunto: In `palette.css` un secondo blocco di campioni con i valori esatti del design (`ardesia`,
  `indaco`, `ambra`, `muschio`, `mattone`); i ruoli di `colori.css` li richiamano.
- modificato: `tipografia.css` ha nuove dimensioni (`titolo-elenco`, `titolo-evidenziato`,
  `descrizione`, `dettaglio`, `evidenziato`, `avviso`), con interlinea `normal` dove il design non la
  fissa; `controlli.css` aggiunge i raggi `evidenza`, `riquadro`, `segmento` e `comando`, le altezze
  `h-controllo` (42px) e `h-controllo-compatto` (40px) e porta `max-w-pagina` a 1120px e
  `max-w-modulo` a 1080px.
- modificato: `pulsante()` ha le varianti `contorno` (bordo grigio), `contornoPrimario` e `testuale`,
  le dimensioni `medio` e `minimo` e i sinonimi `barra` e `testata`; il passaggio del puntatore vale
  anche per i link stilati come pulsante.
- modificato: `campo()` ha nuove dimensioni e le opzioni `avviso` e `fuocoAvviso`; `CampoModulo`
  accetta note sotto il campo; `SezioneModulo` accetta rilievo, etichetta, azioni e contenuto
  evidenziato; `BarraSchede` ha la variante `segmentata`; `IntestazionePagina` accetta una
  descrizione composta; `AlertMessage` mostra come elenco puntato un testo fatto di più voci.
- aggiunto: `barraAzioniModulo()` in `superficie.js`, agganciata in fondo alla scheda (`"scheda"`) o
  semplice in fondo alla pagina (`"pagina"`); `barraAzioni.css` riserva in fondo l'altezza della
  barra (`scroll-padding-bottom`), così il campo che riceve il fuoco non finisce sotto di essa.
- aggiunto: `tabellaCampi()`, `intestazioneCampi()` e `rigaCampi()` in `tabella.js` per le tabelle di
  campi a griglia; `pillola.js` per le pillole di stato ed etichetta; `schedaEvidenziata()` e
  `separatoreTratteggiato()` in `superficie.js`.
- aggiunto: Composizioni per schermata in `config/styles/anagrafica.js`, `config/styles/azienda.js`
  e `STILI_PANNELLO_PRATICHE` in `pratica.js`; testi in `config/testi/anagrafica.js`, `azienda.js` e
  `pratiche.js`, più quelli degli elenchi dei clienti in `config/testi/elenco.js`.
- modificato: `AvvisoTooltip` usa un popover nativo ancorato al segnale, reso in un portale su
  `document.body`, al posto della finestra di dialogo, con gli stili in `avvisi.css`;
  `posizionePopover()` accetta `allinea` e `rientro`.
- aggiunto: `lib/anomalieCampi.js` ricava dalle anomalie restituite da `GET /clienti/{id}` e
  `GET /aziende/{id}` le note per campo, con i testi in `config/testi/anomalie.js`, senza modifiche
  all'API.
- aggiunto: `lib/schedaAnagrafica.js` (stato dell'account, verifica dei recapiti, date) e
  `lib/schedaAzienda.js` (sottotitolo, controllo della partita IVA, note per campo, lettura del
  padre), con i test; l'hook `usePadreAzienda` legge il padre una volta per il sottotitolo e per
  `GerarchiaAzienda`, che lo riceve con `onRicarica`.
- modificato: `config/campiAzienda.js` contiene solo la struttura (nomi dei campi, `PROPRIETA_CAMPI`,
  sezioni per chiave); `CampiAzienda` usa `soloLettura` (readOnly) al posto di `disabilita`.
- modificato: Negli elenchi i valori `principale` e `secondario` si fermano a due righe
  (`line-clamp-2` in `righeElenco.css`); una colonna con `righe: 2` in `config/elenchi.js` ha in più
  il `title` con il valore intero; la tabella usa i bordi separati, con il bordo inferiore sulle
  celle.
- rimosso: `erroreCampo()`, sostituito da `notaCampo("errore")`, `STILI_AVVISI` di `feedback.js` e il
  ruolo `accento-tenue-hover`, rimasto senza uso.
