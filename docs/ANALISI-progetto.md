# Analisi del progetto — piattaforma-universita-ersaf

Data: 2026-09-04 · Branch analizzato: `Login` (commit `289af57`)
Fonti: `backend/`, `frontend/`, `dump.sql` (5,3 GB, MariaDB 10.11, 171 tabelle)

---

## 1. La verità scomoda, in tre righe

Le **4.771 password nel database sono in chiaro** e l'autenticazione è l'header
`x-utente-id`: chiunque può impersonare qualsiasi utente scrivendo un numero.
Il recupero password, così com'è nel prompt, **non è implementabile** — i
requisiti 12 e 14 presuppongono un hashing e delle sessioni che non esistono.

E c'è un rischio immediato, indipendente dalla feature: `dump.sql` (5,3 GB) è
**untracked ma non ignorato**. Un `git add -A` distratto committa in modo
permanente password in chiaro, codici fiscali, numeri di documento e date di
nascita di ~3.900 persone. È l'unica cosa da fare oggi, prima di scrivere
codice.

---

## 2. Architettura attuale

**Backend** — FastAPI + SQLAlchemy 2.0 (`Mapped`/`mapped_column`), organizzato
per dominio: `clienti`, `utenti`, `ruolo`, `aziende`, `auth`. Ogni modulo ha
`models.py` / `schemas.py` / `routers.py`. `src/database.py` legge `DATABASE_URL`
da `.env` con fallback hardcoded a `mysql+pymysql://root:1234@localhost`.

**Frontend** — React 19 + Vite + Tailwind 4 + react-router. Quattro componenti:
`Login`, `Sidebar`, `ElencoSottoscrittori`, `NuovoSottoscrittore`.

**Database** — MariaDB 10.11, 171 tabelle ereditate da una piattaforma
**Instant Developer** ancora in produzione (`aderenti.ersaf.it`). Il backend
mappa 4 tabelle su 171. Convenzione legacy pervasiva: **`-1` = TRUE, `0` = FALSE**.

**Cosa non esiste** — e va costruito da zero se la feature lo richiede:

| | |
|---|---|
| Hashing password | assente (confronto `==` in chiaro) |
| Sessioni / token | assenti (header `x-utente-id` non firmato) |
| Invio email | assente (nessun SMTP, nessuna libreria) |
| Rate limiting | assente |
| Migrazioni | assenti (nessun Alembic) |
| Test | assenti |
| `requirements.txt` / `pyproject.toml` | **assenti** — il progetto non è installabile |
| Logging strutturato | assente |

---

## 3. Sicurezza — in ordine di gravità

**S1 · Password in chiaro.** `utente_password` VARCHAR(255), 4.771 righe, zero
hash bcrypt/argon2/md5/sha. Lunghezze da 1 a 20 caratteri.
`utenti.utente_salt` contiene un UUID distinto per utente ma **non viene mai
usato**: è un residuo Instant Developer.

**S2 · Autenticazione falsificabile.** `get_current_utente` in
`backend/src/auth/routers.py` si fida di `x-utente-id`. `curl -H "x-utente-id: 1"`
è già l'exploit completo. Non c'è autorizzazione per ruolo su nessuna rotta.

**S3 · Nessuna verifica dello stato account al login.** `utente_attivoSN` non
viene controllato: i 21 utenti disattivati (di cui 19 attuatori) accedono
regolarmente.

**S4 · 500 come oracolo di enumerazione.** `user.clienti.ruolo.ruolo_codice`
esplode con `AttributeError` per gli **869 utenti senza riga `clienti`**. Chi
prova un login distingue "password sbagliata" (401) da "utente esistente ma
orfano" (500). Va sistemato *insieme* al recupero password, altrimenti il lavoro
sull'indistinguibilità è vano.

**S5 · Credenziali SMTP nel DB.** La tabella `mail` contiene host, porta e
password in chiaro della casella di invio. La nuova app non deve leggerle da lì.

**S6 · Credenziali di default nel codice.** `root:1234` come fallback in
`database.py`: in assenza di `.env` l'app tenta di connettersi con quelle.

**S7 · CORS e configurazione.** `allow_origins=["http://localhost:5173"]`
hardcoded, `allow_credentials=True`. Non deployabile così.

---

## 4. Qualità dei dati — quello che rompe il recupero password

Misurato sul dump, non stimato.

| Rilievo | Numero | Conseguenza |
|---|---:|---|
| Utenti totali | 4.771 | |
| Clienti totali | 3.906 | |
| **Utenti senza riga `clienti`** | **869** | nessuna email → irraggiungibili |
| Utenti con >1 riga `clienti` | 4 | relazione `uselist=False` non deterministica |
| **Username duplicati** | **6 gruppi** | include il valore `/`; il `.first()` del login è arbitrario |
| Email vuote | 43 | |
| Email malformate | 10 | es. `elgacecere@@hotmail.it`, `/` |
| **Valori email condivisi** | **40 su 105 clienti** | max 11 clienti sullo stesso indirizzo |
| Attuatori (ruoli 1,2,3,5) | 168 | perimetro della feature |
| Attuatori senza email valida | 1 | non recupererà mai la password |
| Attuatori con email condivisa | 20 | richiesta **ambigua**: non si invia |
| Attuatori disattivati | 19 | |

**Indici.** `clienti` (3.906 righe) ha **solo la PRIMARY KEY**: nessun indice su
`cliente_email`, `utente_id`, `cliente_ruolo`. La lookup centrale del recupero
password sarebbe un full scan — e un full scan è anche un canale laterale sui
tempi di risposta.

**Vincoli dichiarati ma inesistenti.** `models.py` dichiara `unique=True` su
`utente_username` e `ForeignKey` su `clienti.utente_id`, `cliente_ruolo`,
`azienda_id`. Nel DB reale **non c'è nessuno di questi vincoli**. Il codice non
può assumerli.

---

## 5. I ruoli: "attuatore" non esiste in tabella

```
0 Utente   1 Aderente   2 Regionale   3 Provinciale
4 Consulente   5 Nazionale   6 Operatore
```

Il prompt parla di *attuatori* e *sottoscrittori* come se fossero due valori.
Non lo sono. L'unico posto dove la piattaforma definisce "attuatore" è il filtro
`solo_attuatori` in `backend/src/clienti/routers.py`, che seleziona
`{Aderente, Regionale, Provinciale, Nazionale}` → **168 clienti**.

Restano scoperti **Consulente (9)** e **Operatore (0 clienti)**: non sono
attuatori e non sono sottoscrittori. Decisione presa: trattati come i
sottoscrittori — nessuna mail, stesso messaggio a video.

---

## 6. Bug funzionali (indipendenti dalla feature)

1. `auth/routers.py` → 500 sugli 869 utenti orfani (vedi S4).
2. `utenti/routers.py::aggiorna_utente` → `setattr` ciclico su tutti i campi
   dello schema: sovrascrive `utente_password` con quella in arrivo, senza
   hashing e senza validazione, e azzera i campi non passati.
3. `utenti/routers.py::crea_utente` → forza `utente_padre = current_utente.id`
   ignorando il valore dello schema. Se è voluto, il campo va tolto da
   `UtenteCreate`.
4. `Login.jsx` → naviga a `/nazionale`, rotta **non registrata** in `App.jsx`:
   gli utenti Nazionale finiscono su una pagina bianca.
5. `Login.jsx` → il ramo `requires_2fa` del backend non è gestito: il frontend
   legge `data.utente_id` che in quel caso è `undefined` e scrive
   `"undefined"` in `localStorage`.
6. `models.py::Utente` → `utente_ultimo_login`/`_logout` sono `Date` nel modello
   e `date` nel DB, ma lo schema `UtenteResponse` li tipizza `datetime`.
7. `Cliente.utente` → `relationship` con `cascade="all, delete-orphan"` sul lato
   `Utente.clienti`: cancellare un utente cancella il cliente. Con 4 utenti che
   hanno 2 clienti, il comportamento è imprevedibile.
8. Nessuna rotta `DELETE` da nessuna parte (rimosse in `6a82858`): coerente, ma
   va detto che la disattivazione logica via `utente_attivoSN` non è esposta.

---

## 7. Cosa è stato prodotto

- `db/diagnostica/000_*.sql` — 15 controlli in sola lettura, con i valori attesi
- `db/diagnostica/010_*.sql` — avanzamento del rehash pigro, sola lettura
- `db/migrations/001..006` — hashing, token, rate limiting, sessioni, indici,
  template email. **Nessuna modifica ai dati esistenti**: solo DDL più due
  template email inseriti.
- `db/rollback/` — annullamento di ognuna
- `docs/PROMPT-recupero-password.md` — il prompt riscritto

Le migrazioni sono state applicate, rieseguite (idempotenza), annullate e
ri-applicate su MariaDB 10.11.14 reale. Il flusso token (consumo atomico,
replay, revoca sessioni, conteggio rate limit) è stato eseguito end-to-end.

---

## 8. Ordine consigliato

**Oggi, prima di tutto**
1. `echo "dump.sql" >> .gitignore` e verificare con `git status`.
2. Creare `backend/requirements.txt` — il progetto oggi non si installa.

**Prima della feature**
3. Applicare `000` diagnostica e leggerne l'output.
4. Applicare `001`–`006` su una copia.

**Con la feature**
5. Hashing bcrypt + rehash pigro, sessioni, e il fix di S4 (il 500).

**Dopo**
6. Bonifica username duplicati → `UNIQUE`.
7. Chiavi esterne su `clienti`.

**Mai**
- Nessuna riscrittura massiva delle password. La conversione a bcrypt avviene
  una riga alla volta, al login del singolo utente. Chi non accede resta
  intatto e continua a entrare come prima. L'avanzamento si legge con
  `db/diagnostica/010_stato_migrazione_password.sql`; cosa fare degli utenti
  rimasti indietro è una decisione da prendere quando i numeri saranno noti.
