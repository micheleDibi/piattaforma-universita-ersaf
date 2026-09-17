# Istruzioni per gli agenti

Piattaforma Università: applicazione web per la rete ERSAF che gestisce sottoscrittori, attuatori, aziende, pratiche universitarie e prodotti formativi. Backend FastAPI (sincrono) con SQLAlchemy su MariaDB 10.11, frontend React + Vite, pubblicazione su un server di collaudo con Docker.

La documentazione è in `docs/`: parti da [docs/README.md](docs/README.md). Per il funzionamento dell'applicazione vedi `docs/funzionale/`, per il codice `docs/tecnica/`. Tutto il progetto è in italiano: codice, commenti, messaggi, documenti e commit.

## Comandi

Backend, da `backend/`, con l'ambiente virtuale attivo:

```bash
TEST_DATABASE_URL=mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test EMAIL_BACKEND=memoria ERSAF_ENV=test \
  python -m pytest tests/unit                     # senza database
TEST_DATABASE_URL=mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test EMAIL_BACKEND=memoria ERSAF_ENV=test \
  python -m pytest --require-mariadb              # suite completa
docker compose -f db/test/docker-compose.test.yml up -d   # dalla radice: MariaDB di test usa-e-getta
```

Frontend, da `frontend/`: `npm test`, `npm run lint`, `npm run build`.

Documentazione, dalla radice:

```bash
python -X warn_default_encoding -m pytest scripts/documentazione/tests
python scripts/documentazione/genera.py            # rigenera docs/tecnica/riferimenti/
python scripts/documentazione/controlla.py tutto --base origin/main
```

Su Windows `scripts\verify-local.ps1 -Gate Unit|Backend|Frontend|All|Docs` raggruppa gli stessi controlli (funziona solo su Windows). Dettagli: [test](docs/tecnica/test.md), [sviluppo locale](docs/tecnica/sviluppo-locale.md).

## Vincoli

- Il database è **MariaDB 10.11**, non MySQL: le migrazioni usano sintassi che MySQL rifiuta.
- Le migrazioni in `db/migrations/` già pubblicate **non si modificano**. Le nuove sono idempotenti, hanno un rollback in `db/rollback/` e seguono [db/README.md](db/README.md).
- Le rotte del backend sono **sincrone** (`def`), salvo l'eccezione documentata in [architettura](docs/tecnica/architettura.md).
- La configurazione ha due strati: `Impostazioni` non solleva mai, `verifica_configurazione` rifiuta l'avvio. Non aggiungere validator che sollevano all'import.
- Frontend: testi in `src/config/testi/`, stili in `src/config/styles/` e nei token; icone **solo** da `src/config/icone.js`. ESLint vieta glifi e durate scritte a mano.
- Convenzione booleana legacy: vero = -1, falso = 0, con gli helper esistenti.
- Mai aprire, citare o modificare `dump.sql`, i file `.env` reali e `backend/ersaf.db`. Mai collegarsi a database di produzione.
- Mai scrivere segreti, token, password o indirizzi email nei log.
- Il repository è **pubblico**: nei documenti e nei frammenti niente email, IP, nomi di server o domini reali, utenti, percorsi del server, nomi di persone, valori di configurazione reali.
- `CHANGELOG.md` e `docs/tecnica/riferimenti/` non si modificano a mano.
- Un agente non lancia `scripts/deploy.ps1`, non fa push su main e non committa senza che gli venga chiesto.
- Non eseguire script in `scripts_inde/` se presenti: alcuni cancellano tabelle.

## Quando una modifica è finita

1. **Frammento** in `changelog/non-pubblicato/AAAA-MM-GG-slug.md`, con "Novità e correzioni" per chi usa la piattaforma e "Dettagli tecnici" per chi sviluppa, quando pertinenti. Formato ed esempi: [changelog/MODELLO.md](changelog/MODELLO.md). Serve anche se la modifica arriva su main senza pull request.
2. **Documenti collegati** aggiornati: [docs/mappa-documentazione.yml](docs/mappa-documentazione.yml) dice quali documenti rileggere per i file toccati.
3. **Pagine generate** rigenerate con `genera.py` se sono cambiate API, pagine, migrazioni o configurazione.
4. **Test pertinenti** verdi (backend, frontend, strumenti della documentazione).

Se la modifica non ha impatto sulla documentazione, scrivilo nel riepilogo della pull request e chiedi l'etichetta `documentazione-invariata` (o `senza-changelog` se non va raccontata): senza etichetta il controllo CI resta rosso. Dettagli: [documentazione](docs/tecnica/documentazione.md).

## Codice e documentazione in disaccordo

Se il codice contraddice la documentazione, correggi la documentazione nella stessa modifica oppure segnala il disaccordo nel riepilogo. Non ignorarlo. Per i punti in cui l'interfaccia e il server si comportano diversamente vedi i [limiti noti](docs/tecnica/sicurezza.md#limiti-noti).
