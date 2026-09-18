# Come si scrive un frammento di changelog

Ogni modifica che arriva su main porta con sé un **frammento**: un piccolo file in `changelog/non-pubblicato/` che racconta la modifica. Alla pubblicazione il deploy raccoglie i frammenti, li scrive in [CHANGELOG.md](../CHANGELOG.md) sotto il numero di versione e li cancella. Il meccanismo completo è in [documentazione](../docs/tecnica/documentazione.md).

## Quando serve

- Serve per ogni modifica a `backend/src/`, `frontend/src/`, `db/` o `deploy/` (esclusi i file `.md`): il controllo CI lo pretende.
- Serve anche per le modifiche che arrivano su main senza pull request: il controllo non le vede, ma senza frammento la versione pubblicata non le racconta.
- Se la modifica non va raccontata (per esempio una correzione di battitura in un commento), la pull request riceve l'etichetta `senza-changelog`.

## Il file

- **Nome**: `AAAA-MM-GG-descrizione-breve.md`, con la data del giorno e una descrizione in minuscolo, lettere, cifre e trattini. Esempio: `2026-09-17-pallini-elenco.md`.
- **Uno per pull request**, con entrambe le parti quando servono. Più frammenti nella stessa pull request sono ammessi.
- **Frontmatter**: obbligatorio, anche vuoto. Due chiavi facoltative:
  - `pr`: il numero della pull request, se lo conosci;
  - `incompatibile`: `true` se la modifica rompe qualcosa per chi usa le API o il deploy. Richiede almeno una voce nei dettagli tecnici.
- **Corpo**: al massimo due sezioni, con questi titoli esatti:
  - `## Novità e correzioni`, per chi usa la piattaforma;
  - `## Dettagli tecnici`, per chi sviluppa o pubblica.
- **Voci**: una per riga, nella forma `- tipo: testo`. Il tipo è uno di `aggiunto`, `modificato`, `corretto`, `sicurezza`, `rimosso`. Una voce lunga continua sulla riga dopo, rientrata di due spazi.
- **Link**: solo indirizzi completi (`https://…`). I link relativi si romperebbero quando il testo passa in `CHANGELOG.md`.

Esempio completo:

```markdown
---
pr: 58
---

## Novità e correzioni

- aggiunto: Negli elenchi Sottoscrittori e Attuatori compare lo stato di verifica di email e cellulare.
- corretto: Nella scheda del curriculum l'anno del diploma non sovrascrive più la data del titolo
  universitario.

## Dettagli tecnici

- modificato: `GET /clienti/` restituisce anche `diploma_completo`, calcolato solo per i sottoscrittori.
- aggiunto: Migrazione `016_indici_visibilita_clienti.sql`, con rollback.
```

Il controllo si lancia anche in locale:

```bash
python scripts/documentazione/controlla.py frammenti
```

## Novità e correzioni: scrivere per chi usa la piattaforma

Chi legge è il committente, un operatore, un collaudatore. Deve capire cosa cambia per lui senza conoscere il codice.

- Descrivi quello che la persona vede o può fare, non come è fatto.
- Usa i nomi delle pagine e dei pulsanti come compaiono sullo schermo.
- Niente nomi di tabelle, campi, endpoint, componenti o file; niente codice fra apici inversi (il controllo lo rifiuta).
- Una frase per voce, al presente.

Gli esempi delle tabelle mostrano come scrivere; non tutti descrivono funzioni che esistono oggi.

| Sì | No |
|---|---|
| Negli elenchi Sottoscrittori compare lo stato di verifica di email e cellulare. | Aggiunto campo `email_verificata` a `ClienteResponse`. |
| Il documento PDF della pratica si scarica dalla scheda della pratica. | Nuovo endpoint `GET /pratiche/{id}/documento`. |
| L'accesso resta aperto finché lo si usa, e scade dopo 14 giorni di inattività. | Sessione scorrevole con `SESSION_INATTIVITA_GIORNI`. |
| Corretto: salvare la scheda Utente non annulla più l'attivazione automatica. | Fix PUT utenti. |
| Gli attuatori vedono solo i sottoscrittori della propria rete. | Filtro CTE ricorsiva su `utente_padre`. |

Se una modifica non cambia nulla di visibile, non va nelle novità: basta la parte tecnica.

## Dettagli tecnici: scrivere per chi sviluppa o pubblica

Qui i nomi tecnici servono. Indica sempre, quando c'è:

- migrazioni nuove, con il file e l'eventuale rollback mancante;
- API cambiate: percorsi, campi aggiunti o tolti, codici di risposta;
- variabili di configurazione nuove o cambiate;
- modifiche incompatibili (con `incompatibile: true` nel frontmatter);
- aspetti di sicurezza (tipo `sicurezza`), senza istruzioni per sfruttare un difetto.

| Sì | No |
|---|---|
| `PUT /clienti/{id}` rifiuta con 403 l'assegnazione del ruolo Nazionale da parte di chi non lo è. | Sistemati i permessi. |
| Nuova variabile `TOTP_CHIAVE`, obbligatoria: senza, il backend non parte. | Aggiunta config. |
| Migrazione `015_secondo_fattore.sql` con rollback. | DB aggiornato. |

## Cosa non scrivere mai

Il repository è pubblico: niente indirizzi email, IP, nomi di server o domini reali, utenti, password, chiavi, token, nomi di persone.
