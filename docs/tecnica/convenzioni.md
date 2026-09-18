# Convenzioni di sviluppo

Queste sono le regole di lavoro per chi modifica il codice. Le regole della documentazione sono in [Documentazione](documentazione.md).

## Flusso di lavoro

Questa è l'unica descrizione del flusso: gli altri documenti rimandano qui.

1. **Ramo personale.** Si lavora su un ramo proprio, mai direttamente su `main`.

   ```
   git switch -c <ramo>
   ```

2. **Commit frequenti.** I messaggi dicono che cosa cambia (vedi "Stile dei commit").
3. **Push del ramo** su GitHub.

   ```
   git push origin <ramo>
   ```

4. **Pull request verso `main`.**
   - Nella descrizione: che cosa è cambiato e che cosa conviene provare.
   - La PR contiene il frammento di changelog (vedi sotto).
5. **Revisione e unione.** Chi pubblica legge le modifiche e le unisce su `main`.
6. **Pubblicazione.** La stessa persona pubblica sul collaudo, a fine giornata, e pubblica solo `main`. Chi sviluppa non pubblica (procedura in [Deploy](deploy.md)).
   - Dopo la pubblicazione, ognuno ricontrolla il proprio lavoro sul collaudo.
   - Il numero in fondo al menu dice quale versione si sta guardando.
   - All'inizio ogni sviluppatore pubblicava da sé. Poi si è scelto di rivedere il codice prima di pubblicarlo.
7. **Correzioni.** Si fanno sullo stesso ramo: un nuovo push aggiorna la stessa PR.

### Frammento di changelog

- **Quando serve.** Ogni modifica ai file di `backend/src`, `frontend/src`, `db` o `deploy`, esclusi i file `.md`, porta un frammento in `changelog/non-pubblicato/`.
- **Che cosa contiene.** Un frammento per PR, con le voci per chi usa la piattaforma e quelle tecniche. Il formato e i controlli sono in [Documentazione](documentazione.md).
- **Anche senza PR.** La regola vale anche per una modifica che arriva su `main` senza passare da una PR, con un push diretto o un'unione locale.
  - Il controllo che chiede il frammento gira solo sulle pull request, quindi in quel caso il frammento va aggiunto nello stesso push.
  - Altrimenti la modifica non compare nel changelog, e il timbro al deploy lo segnala.
- **`CHANGELOG.md` non si modifica a mano.** Lo scrive il timbro al deploy (vedi [Deploy](deploy.md)).

### Etichette di esenzione

- `senza-changelog`: la PR non richiede un frammento.
- `documentazione-invariata`: la PR non richiede di aggiornare i documenti collegati ai file toccati.

Quando usarle e come far ripartire i controlli: [Documentazione](documentazione.md).

## Stile dei commit

**Titolo.**

- È in italiano e descrive l'effetto della modifica, non l'attività svolta.
- Un prefisso con l'area aiuta a leggere la storia.
- Esempi dalla storia del repository:
  - "Deploy: avviso quando si pubblica un ramo diverso da main"
  - "PDF delle pratiche: niente caratteri di controllo nei testi"
  - "Ogni chiamata autenticata falliva dalla seconda in poi"
- Da evitare i titoli che non dicono nulla, come "Fix" o "Correzioni" senza oggetto.

**Corpo.** Serve per le modifiche non banali.

- Spiega il motivo, che cosa cambia e gli effetti su dati, configurazione o deploy.
- Righe brevi. Un elenco puntato va bene.

**Sezione "Prove:".** È consigliata, in fondo al corpo. Dice che cosa è stato verificato e come: test automatici, prove manuali, ambiente.

**Niente dati sensibili.** Nei messaggi non vanno credenziali, dati personali, indirizzi o nomi di host: il repository è pubblico.

## Lingua

- **Nel codice nuovo, in italiano:** identificatori, commenti, docstring, messaggi all'utente, log, documenti e commit. Esempi di identificatori: `verifica_configurazione`, `a_flag_legacy`, `leggiVersione`.
- **Codice esistente.** Contiene ancora molti nomi inglesi, per esempio `get_db`, `hash_password` e `get_current_utente` nel backend, oppure gli stati `loading` e `saving` nei componenti. Si allineano quando si tocca quel codice.
- **Eccezioni:** restano come sono i nomi imposti da librerie e protocolli e le colonne del database legacy.

## Backend

### Rotte sincrone

- Le rotte si scrivono con `def`, e FastAPI le esegue nel threadpool.
- L'unica eccezione è `POST /auth/password-reset/request`, scritta con `async` (`backend/src/auth/routers.py:73-95`):
  - il pavimento temporale deve attendere senza occupare un thread;
  - il lavoro sul database resta sincrono, dentro `run_in_threadpool`.

### Autenticazione sul router

- **Regola.** La sessione si richiede sul router, con `APIRouter(..., dependencies=[Depends(get_current_utente)])`. Così una rotta nuova nasce già protetta (`backend/src/pratiche/routers.py:12-18`).
- **Sotto-router.** Quelli inclusi in un router protetto ereditano la dipendenza, come `backend/src/pratiche/opzioni.py` e `backend/src/documenti/rotte.py` (`backend/src/pratiche/routers.py:20-22`).
- **Eccezioni.** Chiedono la sessione solo sulle rotte che ne hanno bisogno:
  - i router dell'accesso: `backend/src/auth/`, `backend/src/otp/accesso.py`, `backend/src/mfa/accesso.py`;
  - `backend/src/profilo/routers.py`.
- **Test.** `backend/tests/security/test_rotte_protette.py` prova ogni rotta senza sessione. Una nuova rotta pubblica va aggiunta all'elenco `PUBBLICHE`, con il suo motivo (`backend/tests/security/test_rotte_protette.py:21-41`).
- **Permessi.** Autenticazione e permessi si applicano sul server: nascondere un elemento nell'interfaccia non protegge nulla. I casi ancora aperti sono in [Limiti noti](sicurezza.md#limiti-noti).

### Impostazioni nuove

Un'impostazione nuova richiede:

1. un campo con valore predefinito in `Impostazioni` (`backend/src/config.py`);
2. se serve, un controllo in `verifica_configurazione()`;
3. un commento in `backend/.env.example`.

I due strati della configurazione sono descritti in [Architettura](architettura.md). L'elenco completo delle variabili è in [Configurazione](riferimenti/configurazione.md).

### Flag legacy

- **Convenzione.** Nelle tabelle legacy il vero vale -1 e il falso 0. Alcune colonne usano 1 come vero.
- **Conversione.** I valori in ingresso si convertono con `a_flag_legacy` e `a_flag_legacy_uno` di `backend/src/comune/flag_legacy.py`, mai riscrivendo la conversione a mano. Le conversioni sparse nel codice davano risultati diversi fra loro (`backend/src/comune/flag_legacy.py:15-18`).
- **Stato attivo dell'utente.** Si confronta con le costanti `ATTIVO` e `DISATTIVO` di `backend/src/auth/models.py:54-56`.
- **Punti non ancora allineati.** Alcuni confronti usano ancora -1 scritto in chiaro: `backend/src/auth/accesso.py:74`, `backend/src/otp/accesso.py:29`, `backend/src/otp/contatti.py:31`. Vanno allineati quando si tocca quel codice.
- **Frontend.** `frontend/src/lib/flagLegacy.js` considera vero qualunque valore diverso da zero.

### Log

Nei log vanno solo gli identificativi: mai token, impronte, hash, password o indirizzi email (`backend/src/logging_config.py:27-29`). La redazione automatica è una rete di sicurezza, non il modo di rispettare la regola; come funziona e quale test la sorveglia sono in [Sicurezza](sicurezza.md).

### Password

- **Niente riscritture massive.** La conversione all'hash avviene una riga alla volta, quando il singolo utente fa login (`backend/src/utenti/models.py:47-50`). Un aggiornamento in blocco delle password non si scrive, né nel codice né in una migrazione.
- **Scritture sulla colonna in chiaro.** Sono ammesse solo nei punti già elencati nel test di sicurezza che le sorveglia.
- I due test che applicano queste regole sono descritti in [Sicurezza](sicurezza.md).

### Migrazioni

- Le regole sono in [db/README.md](../../db/README.md).
- L'elenco e le anomalie sono in [Migrazioni](riferimenti/migrazioni.md).

## Frontend

### Testi, stili e token

- **Testi dell'interfaccia:** in `frontend/src/config/testi/`, un modulo per area, per esempio `versione.js`.
- **Varianti di stile:** in `frontend/src/config/styles/`.
  - Le funzioni restituiscono le classi, per esempio `pulsante("secondario", "piccolo")` (`frontend/src/config/styles/pulsante.js`).
  - I fogli CSS sono importati da `frontend/src/index.css`.
- **Colori, misure e movimento:** sono token, in `frontend/src/config/tokens/` e `frontend/src/config/theme/`.
  - Le pagine usano i ruoli semantici, non i colori grezzi della palette (`frontend/src/index.css:4-6`).
  - Durate e curve delle animazioni vengono dai token di movimento (`frontend/src/config/tokens/movimento.css`).
- **Codice meno recente.** Diversi componenti contengono ancora testi e colori scritti in linea, per esempio i moduli dell'anagrafica.

### Icone

Si usano solo le icone Lucide, importate esclusivamente da `frontend/src/config/icone.js`. Un'icona nuova si aggiunge lì.

### Regole ESLint del progetto

Sono in `frontend/eslint.config.js` e si lanciano con `npm run lint` dentro `frontend/`.

- **In tutto `src/`:**
  - niente import diretti da librerie di icone fuori da `config/icone.js`;
  - niente simboli testuali usati come icone, come frecce, spunte e croci.
- **In `src/components` e `src/hooks`:** niente durate, ritardi e curve scritti a mano (`duration-N`, `delay-N`, `cubic-bezier(`).
- **Regole di React:** si applica la configurazione raccomandata di `eslint-plugin-react-hooks`.

### React Compiler

- Il compilatore è attivo nella build: `frontend/vite.config.js` applica il suo preset tramite Babel (`babel-plugin-react-compiler`).
- I componenti devono quindi rispettare le regole di React.

### Test

- **Dove mettere la logica.** La logica da provare va in un modulo di `src/lib`, non nel componente: i test girano con il runner di Node, senza trasformazione JSX e senza DOM, e non importano componenti.
- **Come si lanciano e che cosa importano:** [Test](test.md).

### Policy delle password duplicata

- **Due copie.** La politica delle password esiste in due file: `backend/src/security/password.py` e `frontend/src/lib/passwordPolicy.js`. Ogni modifica va replicata nell'altro file.
- Perché la duplicazione è voluta e quale test sorveglia l'allineamento: [Sicurezza](sicurezza.md).

### Pagine e menu

- L'elenco delle pagine è in [Rotte del frontend](riferimenti/rotte-frontend.md).
- Nascondere una voce dal menu non protegge la pagina.

## Documentazione

- In [Documentazione](documentazione.md): chi aggiorna quali documenti, i frammenti, i riferimenti generati e i controlli.
- I file in `docs/tecnica/riferimenti/` sono generati e non si modificano a mano.
