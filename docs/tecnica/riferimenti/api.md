# Riferimento delle API

> Pagina generata da `python scripts/documentazione/genera.py` a partire da `backend/src/main.py` (OpenAPI dell'applicazione).
> Non modificarla a mano: rilancia il comando dopo aver cambiato le fonti.

Elenco delle operazioni esposte dal backend, raggruppate per categoria. Per ognuna:

- **Accesso**: `pubblica`; `sfida di accesso` quando serve la sfida ottenuta con la password, prima che esista una sessione; `sessione` quando serve il cookie di sessione.
- Le richieste che modificano dati passano anche dai controlli del browser e dal token CSRF descritti in [sicurezza](../sicurezza.md).
- I controlli sul ruolo avvengono dentro le operazioni e qui non compaiono: vedi [ruoli e permessi](../../funzionale/ruoli-e-permessi.md) e i [limiti noti](../sicurezza.md#limiti-noti).
- La risposta `422` per i dati non validi vale per tutte le operazioni con parametri o corpo e non viene ripetuta.

## Altre operazioni

### `GET /`

Read Root.

- **Accesso**: pubblica
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

### `POST /auth/rigenera-otp`

Rigenera.

- **Accesso**: sfida di accesso (dopo la password, prima della sessione)
- **Parametri**: —
- **Corpo**: `RichiestaSfida` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/verifica-otp`

Conferma.

- **Accesso**: sfida di accesso (dopo la password, prima della sessione)
- **Parametri**: —
- **Corpo**: `ConfermaSfida` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `GET /clienti/{cliente_id}/contatti`

Stato.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

### `POST /clienti/{cliente_id}/contatti/{tipo}/genera-otp`

Genera.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (path, obbligatorio): `integer`; `tipo` (path, obbligatorio): `"email" | "cellulare"`
- **Corpo**: `InvioContatto` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /clienti/{cliente_id}/contatti/{tipo}/verifica-otp`

Conferma.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (path, obbligatorio): `integer`; `tipo` (path, obbligatorio): `"email" | "cellulare"`
- **Corpo**: `ConfermaSfida` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

## Aziende

### `GET /aziende/`

Lista Aziende.

- **Accesso**: sessione
- **Parametri**: `limit` (query): `integer`; `search` (query): `string | null`; `skip` (query): `integer`
- **Corpo**: —
- **Risposta**: `200` `list[AziendaResponse]`

### `POST /aziende/`

Crea Azienda.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `AziendaCreate` (application/json) obbligatorio
- **Risposta**: `201` `AziendaResponse`

### `GET /aziende/cerca-per-piva`

Cerca Azienda Per Piva.

- **Accesso**: sessione
- **Parametri**: `partita_iva` (query, obbligatorio): `string`
- **Corpo**: —
- **Risposta**: `200` `AziendaResponse`

### `GET /aziende/{azienda_id}`

Dettaglio Azienda.

- **Accesso**: sessione
- **Parametri**: `azienda_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `AziendaResponse`

### `PUT /aziende/{azienda_id}`

Aggiorna Azienda.

- **Accesso**: sessione
- **Parametri**: `azienda_id` (path, obbligatorio): `integer`
- **Corpo**: `AziendaUpdate` (application/json) obbligatorio
- **Risposta**: `200` `AziendaResponse`

### `GET /aziende/{azienda_id}/dettagli`

Dettaglio Azienda Percentuali.

- **Accesso**: sessione
- **Parametri**: `azienda_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `AderenteDettaglioResponse`

### `PUT /aziende/{azienda_id}/dettagli`

Aggiorna Dettaglio Azienda.

- **Accesso**: sessione
- **Parametri**: `azienda_id` (path, obbligatorio): `integer`; `conferma_reset` (query): `boolean`
- **Corpo**: `AderenteDettaglioUpdate` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

## Clienti

### `GET /clienti/`

Leggi Clienti.

- **Accesso**: sessione
- **Parametri**: `limit` (query): `integer`; `ruolo_codice` (query): `string | null`; `search` (query): `string | null`; `skip` (query): `integer`; `solo_attuatori` (query): `boolean`; `solo_sottoscrittori` (query): `boolean`; `solo_utenti` (query): `boolean`
- **Corpo**: —
- **Risposta**: `200` `list[ClienteResponse]`

### `POST /clienti/con-utente`

Crea Cliente E Utente.

- **Accesso**: sessione
- **Parametri**: `tipo_utente` (query): `TipoUtente`
- **Corpo**: `ClienteConUtenteCreate` (application/json) obbligatorio
- **Risposta**: `201` schema non dichiarato

### `GET /clienti/conteggio`

Conta Clienti.

- **Accesso**: sessione
- **Parametri**: `ruolo_codice` (query): `string | null`; `search` (query): `string | null`; `solo_attuatori` (query): `boolean`; `solo_sottoscrittori` (query): `boolean`; `solo_utenti` (query): `boolean`
- **Corpo**: —
- **Risposta**: `200` `ConteggioClientiResponse`

### `GET /clienti/permessi-pratiche`

Permessi Pratiche Correnti.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `PermessiPraticheResponse`

### `GET /clienti/{cliente_id}`

Leggi Cliente.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `ClienteDettaglioResponse`

### `PUT /clienti/{cliente_id}`

Aggiorna Cliente.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (path, obbligatorio): `integer`
- **Corpo**: `ClienteUpdate` (application/json) obbligatorio
- **Risposta**: `200` `ClienteDettaglioResponse`

## Gerarchia aziende

### `GET /aziende-xcod/{azienda_id}/padre`

Leggi Padre.

- **Accesso**: sessione
- **Parametri**: `azienda_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `AziendaXCodResponse | null`

### `PUT /aziende-xcod/{azienda_id}/padre`

Cambia Padre.

- **Accesso**: sessione
- **Parametri**: `azienda_id` (path, obbligatorio): `integer`; `conferma_reset` (query): `boolean`
- **Corpo**: `AziendaXCodCambiaPadre` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

## Listini Testa

### `GET /listini-testa/`

Get All.

- **Accesso**: sessione
- **Parametri**: `attivo` (query): `integer | null`; `limit` (query): `integer`; `search` (query): `string | null`; `skip` (query): `integer`; `tipo_corso` (query): `string | null`; `universita` (query): `string | null`
- **Corpo**: —
- **Risposta**: `200` `list[ListinoTesta]`

### `POST /listini-testa/`

Create Listino Testa.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ListinoTestaCreate` (application/json) obbligatorio
- **Risposta**: `201` `ListinoTesta`

### `GET /listini-testa/next-code`

Get Next Code.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `dict`

### `GET /listini-testa/opzioni/tipi-corso`

Get Opzioni Tipi Corso.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

### `GET /listini-testa/opzioni/universita`

Get Opzioni Universita.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

### `GET /listini-testa/prossimo-codice`

Get Next Code.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `dict`

### `GET /listini-testa/{listTesta_id}`

Get By Id.

- **Accesso**: sessione
- **Parametri**: `listTesta_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `ListinoTesta`

### `PUT /listini-testa/{listTesta_id}`

Update.

- **Accesso**: sessione
- **Parametri**: `listTesta_id` (path, obbligatorio): `integer`
- **Corpo**: `ListinoTestaUpdate` (application/json) obbligatorio
- **Risposta**: `200` `ListinoTesta`

## Listini Tipi Corsi

### `GET /listini-tipi-corsi/`

Get Listino Tipi Corso.

- **Accesso**: sessione
- **Parametri**: `limit` (query): `integer`; `skip` (query): `integer`
- **Corpo**: —
- **Risposta**: `200` `list[ListinoTipoCorso]`

### `POST /listini-tipi-corsi/`

Create Listino Tipo Corso.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ListinoTipoCorsoCreate` (application/json) obbligatorio
- **Risposta**: `201` `ListinoTipoCorso`

### `GET /listini-tipi-corsi/{corso_id}`

Get Listino Tipo Corso By Id.

- **Accesso**: sessione
- **Parametri**: `corso_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `ListinoTipoCorso`

### `PUT /listini-tipi-corsi/{corso_id}`

Update Listino Tipo Corso.

- **Accesso**: sessione
- **Parametri**: `corso_id` (path, obbligatorio): `integer`
- **Corpo**: `ListinoTipoCorsoCreate` (application/json) obbligatorio
- **Risposta**: `200` `ListinoTipoCorso`

## Login

### `POST /auth/login`

Login.

- **Accesso**: pubblica
- **Parametri**: —
- **Corpo**: `LoginRequest` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/login-as/{utente_id}`

Login As.

- **Accesso**: sessione
- **Parametri**: `utente_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

### `POST /auth/logout`

Logout.

- **Accesso**: pubblica
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `204` nessun contenuto

### `POST /auth/password-reset/confirm`

Conferma Reset.

- **Accesso**: pubblica
- **Parametri**: —
- **Corpo**: `ConfermaResetRequest` (application/json) obbligatorio
- **Risposta**: `200` `dict`

### `POST /auth/password-reset/request`

Richiedi Reset.

- **Accesso**: pubblica
- **Parametri**: —
- **Corpo**: `RichiestaResetRequest` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `GET /auth/password-reset/validate`

Valida Token Reset.

- **Accesso**: pubblica
- **Parametri**: `token` (query): `string`
- **Corpo**: —
- **Risposta**: `200` `dict`

### `GET /auth/session`

Sessione.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

## Pratiche

### `GET /pratiche/`

Lista Pratiche.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (query): `integer | null`; `limit` (query): `integer`; `listino_tipo_corso_id` (query): `list[integer]`; `nome_universita_id` (query): `integer | null`; `numero_pratica` (query): `string`; `pratica_stato_id` (query): `integer | null`; `search` (query): `string`; `skip` (query): `integer`; `studenti` (query): `list[integer]`
- **Corpo**: —
- **Risposta**: `200` `list[PraticaResponse]`

### `POST /pratiche/`

Crea Pratica.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `PraticaCreate` (application/json) obbligatorio
- **Risposta**: `201` `PraticaResponse`

### `GET /pratiche/conteggi`

Conteggi Pratiche.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `list[ConteggioPratiche]`

### `GET /pratiche/filtri/stati`

Stati.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `list[Opzione]`

### `GET /pratiche/filtri/{tipo}`

Opzioni.

- **Accesso**: sessione
- **Parametri**: `tipo` (path, obbligatorio): `"studenti" | "percorsi"`; `limit` (query): `integer`; `search` (query): `string`; `skip` (query): `integer`
- **Corpo**: —
- **Risposta**: `200` `PaginaOpzioni`

### `GET /pratiche/{pratica_id}`

Dettaglio Pratica.

- **Accesso**: sessione
- **Parametri**: `pratica_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `PraticaResponse`

### `PUT /pratiche/{pratica_id}`

Aggiorna Pratica.

- **Accesso**: sessione
- **Parametri**: `pratica_id` (path, obbligatorio): `integer`
- **Corpo**: `PraticaUpdate` (application/json) obbligatorio
- **Risposta**: `200` `PraticaResponse`

### `GET /pratiche/{pratica_id}/documento`

Scarica Documento.

- **Accesso**: sessione
- **Parametri**: `pratica_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` application/pdf

### `GET /pratiche/{pratica_id}/documento/disponibile`

Documento Disponibile.

- **Accesso**: sessione
- **Parametri**: `pratica_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `dict`

## Profilo personale

### `GET /profilo/me`

Mio Profilo.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `ProfiloPersonale`

## Ruoli

### `GET /ruoli/`

Leggi Ruoli.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` `list[RuoloResponse]`

### `POST /ruoli/`

Crea Ruolo.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `RuoloCreate` (application/json) obbligatorio
- **Risposta**: `201` `RuoloResponse`

### `GET /ruoli/{ruolo_id}`

Leggi Ruolo.

- **Accesso**: sessione
- **Parametri**: `ruolo_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `RuoloResponse`

### `PUT /ruoli/{ruolo_id}`

Aggiorna Ruolo.

- **Accesso**: sessione
- **Parametri**: `ruolo_id` (path, obbligatorio): `integer`
- **Corpo**: `RuoloUpdate` (application/json) obbligatorio
- **Risposta**: `200` `RuoloResponse`

## Secondo fattore

### `GET /auth/mfa`

Stato.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/metodo`

Metodo.

- **Accesso**: sfida di accesso (dopo la password, prima della sessione)
- **Parametri**: —
- **Corpo**: `CambioMetodo` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/passkey/conferma`

Passkey Conferma.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ConfermaPasskey` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/passkey/opzioni`

Passkey Opzioni.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ConPassword` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/passkey/rimuovi`

Passkey Rimuovi.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `RimozionePasskey` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/totp/attiva`

Totp Attiva.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ConPassword` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/totp/conferma`

Totp Conferma.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ConCodice` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/totp/disattiva`

Totp Disattiva.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `ConPasswordECodice` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/verifica-passkey`

Verifica Passkey.

- **Accesso**: sfida di accesso (dopo la password, prima della sessione)
- **Parametri**: —
- **Corpo**: `RispostaPasskey` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

### `POST /auth/mfa/verifica-totp`

Verifica Totp.

- **Accesso**: sfida di accesso (dopo la password, prima della sessione)
- **Parametri**: —
- **Corpo**: `ConfermaSfida` (application/json) obbligatorio
- **Risposta**: `200` schema non dichiarato

## Servizio

### `GET /salute`

Salute.

- **Accesso**: pubblica
- **Parametri**: —
- **Corpo**: —
- **Risposta**: `200` schema non dichiarato

## Universita

### `GET /universita/`

Get Universita List.

- **Accesso**: sessione
- **Parametri**: `cliente_id` (query): `integer | null`; `limit` (query): `integer`; `skip` (query): `integer`
- **Corpo**: —
- **Risposta**: `200` `list[Universita]`

### `POST /universita/`

Create Universita.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `UniversitaCreate` (application/json) obbligatorio
- **Risposta**: `201` `Universita`

### `GET /universita/{universita_id}`

Get Universita By Id.

- **Accesso**: sessione
- **Parametri**: `universita_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `Universita`

### `PUT /universita/{universita_id}`

Update Universita.

- **Accesso**: sessione
- **Parametri**: `universita_id` (path, obbligatorio): `integer`
- **Corpo**: `UniversitaUpdate` (application/json) obbligatorio
- **Risposta**: `200` `Universita`

## Utenti

### `GET /utenti/`

Leggi Utenti.

- **Accesso**: sessione
- **Parametri**: `limit` (query): `integer`; `skip` (query): `integer`
- **Corpo**: —
- **Risposta**: `200` `list[UtenteResponse]`

### `POST /utenti/`

Crea Utente.

- **Accesso**: sessione
- **Parametri**: —
- **Corpo**: `UtenteCreate` (application/json) obbligatorio
- **Risposta**: `201` `UtenteResponse`

### `GET /utenti/{utente_id}`

Leggi Utente.

- **Accesso**: sessione
- **Parametri**: `utente_id` (path, obbligatorio): `integer`
- **Corpo**: —
- **Risposta**: `200` `UtenteResponse`

### `PUT /utenti/{utente_id}`

Aggiorna Utente.

- **Accesso**: sessione
- **Parametri**: `utente_id` (path, obbligatorio): `integer`
- **Corpo**: `UtenteUpdate` (application/json) obbligatorio
- **Risposta**: `200` `UtenteResponse`

## Modelli

### AderenteDettaglioResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `aderente_dettaglio_id` | `integer \| null` | no |
| `azienda_id` | `integer` | sì |
| `universita_A4U_master` | `integer` | no |
| `universita_A4U_perfezionamenti` | `integer` | no |
| `universita_SSML_lauree` | `integer` | no |
| `universita_SSML_master` | `integer` | no |
| `universita_ecampus_lauree` | `integer` | no |
| `universita_ecampus_master` | `integer` | no |
| `universita_link_lauree` | `integer` | no |
| `universita_link_master` | `integer` | no |

### AderenteDettaglioUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `universita_A4U_master` | `integer` | no |
| `universita_A4U_perfezionamenti` | `integer` | no |
| `universita_SSML_lauree` | `integer` | no |
| `universita_SSML_master` | `integer` | no |
| `universita_ecampus_lauree` | `integer` | no |
| `universita_ecampus_master` | `integer` | no |
| `universita_link_lauree` | `integer` | no |
| `universita_link_master` | `integer` | no |

### AziendaCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda_CAP` | `string` | sì |
| `azienda_citta` | `string` | sì |
| `azienda_civico` | `string \| null` | no |
| `azienda_codiceFiscale` | `string` | sì |
| `azienda_codice_bic` | `string \| null` | no |
| `azienda_codice_nazionale` | `string \| null` | no |
| `azienda_email` | `string \| null` | no |
| `azienda_fatturazioneSDI` | `string \| null` | no |
| `azienda_iban` | `string \| null` | no |
| `azienda_partitaIVA` | `string` | sì |
| `azienda_pec` | `string \| null` | no |
| `azienda_provincia` | `string` | sì |
| `azienda_ragione_sociale` | `string` | sì |
| `azienda_sitoWeb` | `string \| null` | no |
| `azienda_telefono` | `string \| null` | no |
| `azienda_via` | `string` | sì |

### AziendaResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `anomalie` | `list[string]` | no |
| `azienda_CAP` | `string` | sì |
| `azienda_citta` | `string` | sì |
| `azienda_civico` | `string \| null` | no |
| `azienda_codiceFiscale` | `string \| null` | no |
| `azienda_codice_bic` | `string \| null` | no |
| `azienda_codice_nazionale` | `string \| null` | no |
| `azienda_email` | `string \| null` | no |
| `azienda_fatturazioneSDI` | `string \| null` | no |
| `azienda_iban` | `string \| null` | no |
| `azienda_id` | `integer` | sì |
| `azienda_partitaIVA` | `string` | sì |
| `azienda_pec` | `string \| null` | no |
| `azienda_provincia` | `string` | sì |
| `azienda_ragione_sociale` | `string` | sì |
| `azienda_sitoWeb` | `string \| null` | no |
| `azienda_telefono` | `string \| null` | no |
| `azienda_via` | `string` | sì |

### AziendaUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda_CAP` | `string \| null` | no |
| `azienda_citta` | `string \| null` | no |
| `azienda_civico` | `string \| null` | no |
| `azienda_codiceFiscale` | `string \| null` | no |
| `azienda_codice_bic` | `string \| null` | no |
| `azienda_codice_nazionale` | `string \| null` | no |
| `azienda_email` | `string \| null` | no |
| `azienda_fatturazioneSDI` | `string \| null` | no |
| `azienda_iban` | `string \| null` | no |
| `azienda_partitaIVA` | `string \| null` | no |
| `azienda_pec` | `string \| null` | no |
| `azienda_provincia` | `string \| null` | no |
| `azienda_ragione_sociale` | `string \| null` | no |
| `azienda_sitoWeb` | `string \| null` | no |
| `azienda_telefono` | `string \| null` | no |
| `azienda_via` | `string \| null` | no |

### AziendaXCodCambiaPadre

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `nuovo_padre_id` | `integer \| null` | no |

### AziendaXCodResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda_figlia_id` | `integer \| null` | no |
| `azienda_padre_id` | `integer \| null` | no |
| `azienda_xCod_created_at` | `string(date-time) \| null` | no |
| `azienda_xCod_id` | `integer` | sì |
| `azienda_xCod_updated_at` | `string(date-time) \| null` | no |

### CambioMetodo

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `metodo` | `"email" \| "totp" \| "passkey"` | sì |
| `sfida` | `string` | sì |

### ClienteConUtenteCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `attuatore_id` | `integer \| null` | no |
| `azienda_id` | `integer \| null` | no |
| `cliente_CAP` | `string \| null` | no |
| `cliente_CAPDomicilio` | `string \| null` | no |
| `cliente_abilPraticheUniv` | `integer \| null` | no |
| `cliente_abilitazione_a4u` | `integer \| null` | no |
| `cliente_abilitazione_corsi_speciali` | `integer \| null` | no |
| `cliente_abilitazione_ecampus` | `integer \| null` | no |
| `cliente_abilitazione_link_campus` | `integer \| null` | no |
| `cliente_cellulare` | `string \| null` | no |
| `cliente_citta` | `string` | sì |
| `cliente_cittaDomicilio` | `string \| null` | no |
| `cliente_cittadinanza` | `string` | sì |
| `cliente_civico` | `string` | sì |
| `cliente_civicoDomicilio` | `string \| null` | no |
| `cliente_codice` | `string \| null` | no |
| `cliente_codice_fiscale` | `string \| null` | no |
| `cliente_cognome` | `string` | sì |
| `cliente_comuneRilascio` | `string` | sì |
| `cliente_dataNascita` | `string(date)` | sì |
| `cliente_dataRilascio` | `string(date)` | sì |
| `cliente_dataScadenzaDocumento` | `string(date)` | sì |
| `cliente_documento` | `string` | sì |
| `cliente_email` | `string \| null` | no |
| `cliente_gg` | `integer \| null` | no |
| `cliente_id` | `integer \| null` | no |
| `cliente_indirizzo` | `string` | sì |
| `cliente_indirizzoDomicilio` | `string \| null` | no |
| `cliente_luogoNascita` | `string` | sì |
| `cliente_nome` | `string` | sì |
| `cliente_pathCertificato` | `string \| null` | no |
| `cliente_pec` | `string \| null` | no |
| `cliente_provincia` | `string \| null` | no |
| `cliente_provinciaDomicilio` | `string \| null` | no |
| `cliente_provinciaNascita` | `string \| null` | no |
| `cliente_ruolo` | `integer \| null` | no |
| `cliente_sesso` | `SessoEnum \| null` | no |
| `cliente_telefono` | `string \| null` | no |
| `cliente_tipoDocumento` | `TipoDocumentoEnum \| null` | no |
| `tessera_id` | `integer \| null` | no |
| `universita_albo` | `string \| null` | no |
| `universita_altre_attivita_certificate` | `integer \| null` | no |
| `universita_annoSessione_professione` | `integer \| null` | no |
| `universita_anno_scolastico` | `string \| null` | no |
| `universita_anno_scolastico_ai` | `string \| null` | no |
| `universita_ateneoNullaosta` | `string \| null` | no |
| `universita_attIscritto_altro` | `string \| null` | no |
| `universita_attIscritto_annoIscrizione` | `string \| null` | no |
| `universita_attIscritto_citta` | `string \| null` | no |
| `universita_attIscritto_classeLaurea` | `string \| null` | no |
| `universita_attIscritto_denominazione` | `string \| null` | no |
| `universita_attIscritto_modalita` | `string \| null` | no |
| `universita_attIscritto_provincia` | `string \| null` | no |
| `universita_attIscritto_tipo` | `string \| null` | no |
| `universita_attIscritto_universita` | `string \| null` | no |
| `universita_attivita_professionalizzanti` | `integer \| null` | no |
| `universita_cittaUniConclusione` | `string \| null` | no |
| `universita_citta_istituto` | `string \| null` | no |
| `universita_citta_istituto_ai` | `string \| null` | no |
| `universita_conclusione` | `string \| null` | no |
| `universita_corrispondenza` | `string \| null` | no |
| `universita_corsi_di_formazione` | `integer \| null` | no |
| `universita_createBy` | `integer \| null` | no |
| `universita_data_ats1` | `string(date) \| null` | no |
| `universita_data_ats2` | `string(date) \| null` | no |
| `universita_data_conclusione` | `string(date) \| null` | no |
| `universita_data_immatricolazione` | `string(date) \| null` | no |
| `universita_data_pl1` | `string(date) \| null` | no |
| `universita_data_pl2` | `string(date) \| null` | no |
| `universita_data_professione` | `string(date) \| null` | no |
| `universita_data_qualifica` | `string(date) \| null` | no |
| `universita_data_titolo` | `string(date) \| null` | no |
| `universita_diploma` | `string \| null` | no |
| `universita_forzeDellOrdine` | `string \| null` | no |
| `universita_immatricolato` | `integer \| null` | no |
| `universita_iscrizioneAltraUniversita` | `integer \| null` | no |
| `universita_istituto` | `string \| null` | no |
| `universita_istituto_ai` | `string \| null` | no |
| `universita_istituto_ats1` | `string \| null` | no |
| `universita_istituto_ats2` | `string \| null` | no |
| `universita_istituto_pl1` | `string \| null` | no |
| `universita_istituto_pl2` | `string \| null` | no |
| `universita_luogo` | `string \| null` | no |
| `universita_luogo_professione` | `string \| null` | no |
| `universita_materia_ats1` | `string \| null` | no |
| `universita_materia_ats2` | `string \| null` | no |
| `universita_materia_pl1` | `string \| null` | no |
| `universita_materia_pl2` | `string \| null` | no |
| `universita_materia_titolo` | `string \| null` | no |
| `universita_percentualeInvalidita` | `integer \| null` | no |
| `universita_professione` | `string \| null` | no |
| `universita_provinciaConclusione` | `string \| null` | no |
| `universita_provincia_istituto` | `string \| null` | no |
| `universita_provincia_istituto_ai` | `string \| null` | no |
| `universita_qualifica_professionale` | `string \| null` | no |
| `universita_riforma` | `string \| null` | no |
| `universita_sessione_professione` | `string \| null` | no |
| `universita_tipoInvalidita` | `string \| null` | no |
| `universita_titolo_universitario` | `string \| null` | no |
| `universita_universitaConclusione` | `string \| null` | no |
| `universita_universita_titolo` | `string \| null` | no |
| `universita_updateBy` | `integer \| null` | no |
| `universita_via_istituto` | `string \| null` | no |
| `universita_via_istituto_ai` | `string \| null` | no |
| `universita_votoMassimo_ai` | `integer \| null` | no |
| `universita_votoMassimo_diploma` | `integer \| null` | no |
| `universita_votoMassimo_titolo` | `integer \| null` | no |
| `universita_votoRicevuto_ai` | `integer \| null` | no |
| `universita_votoRicevuto_diploma` | `integer \| null` | no |
| `universita_votoRicevuto_titolo` | `integer \| null` | no |
| `universita_voto_professione` | `integer \| null` | no |
| `utente_id` | `integer \| null` | no |
| `utente_password` | `string \| null` | no |
| `utente_username` | `string \| null` | no |

### ClienteDettaglioResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `anomalie` | `list[string]` | no |
| `attuatore_id` | `integer \| null` | no |
| `azienda` | `AziendaResponse \| null` | no |
| `azienda_id` | `integer \| null` | no |
| `cellulare_verificato` | `boolean` | no |
| `cliente_CAP` | `string \| null` | no |
| `cliente_CAPDomicilio` | `string \| null` | no |
| `cliente_abilPraticheUniv` | `integer \| null` | no |
| `cliente_abilitazione_a4u` | `integer \| null` | no |
| `cliente_abilitazione_corsi_speciali` | `integer \| null` | no |
| `cliente_abilitazione_ecampus` | `integer \| null` | no |
| `cliente_abilitazione_link_campus` | `integer \| null` | no |
| `cliente_cellulare` | `string \| null` | no |
| `cliente_citta` | `string` | sì |
| `cliente_cittaDomicilio` | `string \| null` | no |
| `cliente_cittadinanza` | `string` | sì |
| `cliente_civico` | `string` | sì |
| `cliente_civicoDomicilio` | `string \| null` | no |
| `cliente_codice` | `string \| null` | no |
| `cliente_codice_fiscale` | `string \| null` | no |
| `cliente_cognome` | `string` | sì |
| `cliente_comuneRilascio` | `string` | sì |
| `cliente_dataNascita` | `string(date)` | sì |
| `cliente_dataRilascio` | `string(date)` | sì |
| `cliente_dataScadenzaDocumento` | `string(date)` | sì |
| `cliente_documento` | `string` | sì |
| `cliente_email` | `string \| null` | no |
| `cliente_gg` | `integer \| null` | no |
| `cliente_id` | `integer` | sì |
| `cliente_indirizzo` | `string` | sì |
| `cliente_indirizzoDomicilio` | `string \| null` | no |
| `cliente_luogoNascita` | `string` | sì |
| `cliente_nome` | `string` | sì |
| `cliente_pathCertificato` | `string \| null` | no |
| `cliente_pec` | `string \| null` | no |
| `cliente_provincia` | `string \| null` | no |
| `cliente_provinciaDomicilio` | `string \| null` | no |
| `cliente_provinciaNascita` | `string \| null` | no |
| `cliente_ruolo` | `integer \| null` | no |
| `cliente_sesso` | `SessoEnum \| null` | no |
| `cliente_telefono` | `string \| null` | no |
| `cliente_tipoDocumento` | `TipoDocumentoEnum \| null` | no |
| `curriculum` | `Universita \| null` | no |
| `diploma_completo` | `boolean \| null` | no |
| `email_verificata` | `boolean` | no |
| `ruolo` | `RuoloResponse \| null` | no |
| `tessera_id` | `integer \| null` | no |
| `utente` | `UtenteResponse \| null` | no |
| `utente_id` | `integer \| null` | no |

### ClientePadreSchema

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cliente_cognome` | `string \| null` | no |
| `cliente_id` | `integer` | sì |
| `cliente_nome` | `string \| null` | no |

### ClienteResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `anomalie` | `list[string]` | no |
| `attuatore_id` | `integer \| null` | no |
| `azienda` | `AziendaResponse \| null` | no |
| `azienda_id` | `integer \| null` | no |
| `cellulare_verificato` | `boolean` | no |
| `cliente_CAP` | `string \| null` | no |
| `cliente_CAPDomicilio` | `string \| null` | no |
| `cliente_abilPraticheUniv` | `integer \| null` | no |
| `cliente_abilitazione_a4u` | `integer \| null` | no |
| `cliente_abilitazione_corsi_speciali` | `integer \| null` | no |
| `cliente_abilitazione_ecampus` | `integer \| null` | no |
| `cliente_abilitazione_link_campus` | `integer \| null` | no |
| `cliente_cellulare` | `string \| null` | no |
| `cliente_citta` | `string` | sì |
| `cliente_cittaDomicilio` | `string \| null` | no |
| `cliente_cittadinanza` | `string` | sì |
| `cliente_civico` | `string` | sì |
| `cliente_civicoDomicilio` | `string \| null` | no |
| `cliente_codice` | `string \| null` | no |
| `cliente_codice_fiscale` | `string \| null` | no |
| `cliente_cognome` | `string` | sì |
| `cliente_comuneRilascio` | `string` | sì |
| `cliente_dataNascita` | `string(date)` | sì |
| `cliente_dataRilascio` | `string(date)` | sì |
| `cliente_dataScadenzaDocumento` | `string(date)` | sì |
| `cliente_documento` | `string` | sì |
| `cliente_email` | `string \| null` | no |
| `cliente_gg` | `integer \| null` | no |
| `cliente_id` | `integer` | sì |
| `cliente_indirizzo` | `string` | sì |
| `cliente_indirizzoDomicilio` | `string \| null` | no |
| `cliente_luogoNascita` | `string` | sì |
| `cliente_nome` | `string` | sì |
| `cliente_pathCertificato` | `string \| null` | no |
| `cliente_pec` | `string \| null` | no |
| `cliente_provincia` | `string \| null` | no |
| `cliente_provinciaDomicilio` | `string \| null` | no |
| `cliente_provinciaNascita` | `string \| null` | no |
| `cliente_ruolo` | `integer \| null` | no |
| `cliente_sesso` | `SessoEnum \| null` | no |
| `cliente_telefono` | `string \| null` | no |
| `cliente_tipoDocumento` | `TipoDocumentoEnum \| null` | no |
| `diploma_completo` | `boolean \| null` | no |
| `email_verificata` | `boolean` | no |
| `ruolo` | `RuoloResponse \| null` | no |
| `tessera_id` | `integer \| null` | no |
| `utente` | `UtenteResponse \| null` | no |
| `utente_id` | `integer \| null` | no |

### ClienteUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `attuatore_id` | `integer \| null` | no |
| `azienda_id` | `integer \| null` | no |
| `cliente_CAP` | `string \| null` | no |
| `cliente_CAPDomicilio` | `string \| null` | no |
| `cliente_abilPraticheUniv` | `integer \| null` | no |
| `cliente_abilitazione_a4u` | `integer \| null` | no |
| `cliente_abilitazione_corsi_speciali` | `integer \| null` | no |
| `cliente_abilitazione_ecampus` | `integer \| null` | no |
| `cliente_abilitazione_link_campus` | `integer \| null` | no |
| `cliente_cellulare` | `string \| null` | no |
| `cliente_citta` | `string \| null` | no |
| `cliente_cittaDomicilio` | `string \| null` | no |
| `cliente_cittadinanza` | `string \| null` | no |
| `cliente_civico` | `string \| null` | no |
| `cliente_civicoDomicilio` | `string \| null` | no |
| `cliente_codice` | `string \| null` | no |
| `cliente_codice_fiscale` | `string \| null` | no |
| `cliente_cognome` | `string \| null` | no |
| `cliente_comuneRilascio` | `string \| null` | no |
| `cliente_dataNascita` | `string(date) \| null` | no |
| `cliente_dataRilascio` | `string(date) \| null` | no |
| `cliente_dataScadenzaDocumento` | `string(date) \| null` | no |
| `cliente_documento` | `string \| null` | no |
| `cliente_email` | `string \| null` | no |
| `cliente_gg` | `integer \| null` | no |
| `cliente_id` | `integer \| null` | no |
| `cliente_indirizzo` | `string \| null` | no |
| `cliente_indirizzoDomicilio` | `string \| null` | no |
| `cliente_luogoNascita` | `string \| null` | no |
| `cliente_nome` | `string \| null` | no |
| `cliente_pathCertificato` | `string \| null` | no |
| `cliente_pec` | `string \| null` | no |
| `cliente_provincia` | `string \| null` | no |
| `cliente_provinciaDomicilio` | `string \| null` | no |
| `cliente_provinciaNascita` | `string \| null` | no |
| `cliente_ruolo` | `integer \| null` | no |
| `cliente_sesso` | `SessoEnum \| null` | no |
| `cliente_telefono` | `string \| null` | no |
| `cliente_tipoDocumento` | `TipoDocumentoEnum \| null` | no |
| `tessera_id` | `integer \| null` | no |
| `universita_albo` | `string \| null` | no |
| `universita_altre_attivita_certificate` | `integer \| null` | no |
| `universita_annoSessione_professione` | `integer \| null` | no |
| `universita_anno_scolastico` | `string \| null` | no |
| `universita_anno_scolastico_ai` | `string \| null` | no |
| `universita_ateneoNullaosta` | `string \| null` | no |
| `universita_attIscritto_altro` | `string \| null` | no |
| `universita_attIscritto_annoIscrizione` | `string \| null` | no |
| `universita_attIscritto_citta` | `string \| null` | no |
| `universita_attIscritto_classeLaurea` | `string \| null` | no |
| `universita_attIscritto_denominazione` | `string \| null` | no |
| `universita_attIscritto_modalita` | `string \| null` | no |
| `universita_attIscritto_provincia` | `string \| null` | no |
| `universita_attIscritto_tipo` | `string \| null` | no |
| `universita_attIscritto_universita` | `string \| null` | no |
| `universita_attivita_professionalizzanti` | `integer \| null` | no |
| `universita_cittaUniConclusione` | `string \| null` | no |
| `universita_citta_istituto` | `string \| null` | no |
| `universita_citta_istituto_ai` | `string \| null` | no |
| `universita_conclusione` | `string \| null` | no |
| `universita_corrispondenza` | `string \| null` | no |
| `universita_corsi_di_formazione` | `integer \| null` | no |
| `universita_createBy` | `integer \| null` | no |
| `universita_data_ats1` | `string(date) \| null` | no |
| `universita_data_ats2` | `string(date) \| null` | no |
| `universita_data_conclusione` | `string(date) \| null` | no |
| `universita_data_immatricolazione` | `string(date) \| null` | no |
| `universita_data_pl1` | `string(date) \| null` | no |
| `universita_data_pl2` | `string(date) \| null` | no |
| `universita_data_professione` | `string(date) \| null` | no |
| `universita_data_qualifica` | `string(date) \| null` | no |
| `universita_data_titolo` | `string(date) \| null` | no |
| `universita_diploma` | `string \| null` | no |
| `universita_forzeDellOrdine` | `string \| null` | no |
| `universita_immatricolato` | `integer \| null` | no |
| `universita_iscrizioneAltraUniversita` | `integer \| null` | no |
| `universita_istituto` | `string \| null` | no |
| `universita_istituto_ai` | `string \| null` | no |
| `universita_istituto_ats1` | `string \| null` | no |
| `universita_istituto_ats2` | `string \| null` | no |
| `universita_istituto_pl1` | `string \| null` | no |
| `universita_istituto_pl2` | `string \| null` | no |
| `universita_luogo` | `string \| null` | no |
| `universita_luogo_professione` | `string \| null` | no |
| `universita_materia_ats1` | `string \| null` | no |
| `universita_materia_ats2` | `string \| null` | no |
| `universita_materia_pl1` | `string \| null` | no |
| `universita_materia_pl2` | `string \| null` | no |
| `universita_materia_titolo` | `string \| null` | no |
| `universita_percentualeInvalidita` | `integer \| null` | no |
| `universita_professione` | `string \| null` | no |
| `universita_provinciaConclusione` | `string \| null` | no |
| `universita_provincia_istituto` | `string \| null` | no |
| `universita_provincia_istituto_ai` | `string \| null` | no |
| `universita_qualifica_professionale` | `string \| null` | no |
| `universita_riforma` | `string \| null` | no |
| `universita_sessione_professione` | `string \| null` | no |
| `universita_tipoInvalidita` | `string \| null` | no |
| `universita_titolo_universitario` | `string \| null` | no |
| `universita_universitaConclusione` | `string \| null` | no |
| `universita_universita_titolo` | `string \| null` | no |
| `universita_updateBy` | `integer \| null` | no |
| `universita_via_istituto` | `string \| null` | no |
| `universita_via_istituto_ai` | `string \| null` | no |
| `universita_votoMassimo_ai` | `integer \| null` | no |
| `universita_votoMassimo_diploma` | `integer \| null` | no |
| `universita_votoMassimo_titolo` | `integer \| null` | no |
| `universita_votoRicevuto_ai` | `integer \| null` | no |
| `universita_votoRicevuto_diploma` | `integer \| null` | no |
| `universita_votoRicevuto_titolo` | `integer \| null` | no |
| `universita_voto_professione` | `integer \| null` | no |
| `utente_id` | `integer \| null` | no |

### ConCodice

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `codice` | `string` | sì |

### ConPassword

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `password` | `string` | sì |

### ConPasswordECodice

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `codice` | `string` | sì |
| `password` | `string` | sì |

### ConfermaPasskey

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `credenziale` | `dict` | sì |
| `nome` | `string` | sì |
| `sfida` | `string` | sì |

### ConfermaResetRequest

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `password` | `string` | sì |
| `password_conferma` | `string` | sì |
| `token` | `string` | sì |

### ConfermaSfida

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `codice` | `string` | sì |
| `sfida` | `string` | sì |

### ConteggioClientiResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `totale` | `integer` | sì |

### ConteggioPratiche

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `listino_tipo_corso_id` | `integer \| null` | no |
| `nome_universita_id` | `integer` | sì |
| `pratica_stato_id` | `integer` | sì |
| `totale` | `integer` | sì |

### EmittenteBreve

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cliente_codice` | `string \| null` | no |
| `cliente_cognome` | `string \| null` | no |
| `cliente_id` | `integer` | sì |
| `cliente_nome` | `string \| null` | no |

### IndirizzoProfilo

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cap` | `string \| null` | sì |
| `citta` | `string \| null` | sì |
| `civico` | `string \| null` | sì |
| `indirizzo` | `string \| null` | sì |
| `provincia` | `string \| null` | sì |

### InvioContatto

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `valore` | `string` | sì |

### ListinoDettaglioCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `listDettaglio_CFU` | `integer \| null` | no |
| `listDettaglio_dataFineValidazionoe` | `string \| null` | no |
| `listDettaglio_dataInizioValidazione` | `string(date) \| null` | no |
| `listDettaglio_durata` | `integer \| null` | no |
| `listDettaglio_prezzo` | `number \| null` | no |
| `listDettaglio_tasse` | `number \| null` | no |

### ListinoDettaglioResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `listDettaglio_CFU` | `integer \| null` | no |
| `listDettaglio_dataFineValidazionoe` | `string(date)` | no |
| `listDettaglio_dataInizioValidazione` | `string(date) \| null` | no |
| `listDettaglio_durata` | `integer \| null` | no |
| `listDettaglio_id` | `integer` | sì |
| `listDettaglio_prezzo` | `number \| string` | sì |
| `listDettaglio_tasse` | `number \| string \| null` | no |
| `listTesta_id` | `integer` | sì |

### ListinoTesta

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `dettagli` | `list[ListinoDettaglioResponse]` | no |
| `listTesta_codice` | `string` | sì |
| `listTesta_created_at` | `string(date-time) \| null` | no |
| `listTesta_created_by` | `integer \| null` | no |
| `listTesta_descrizione` | `string` | sì |
| `listTesta_id` | `integer` | sì |
| `listTesta_livello` | `integer \| null` | no |
| `listTesta_updated_at` | `string(date-time) \| null` | no |
| `listTesta_updated_by` | `integer \| null` | no |
| `listino_attivoSN` | `integer` | no |
| `listino_corsoLaurea_id` | `integer \| null` | no |
| `listino_durataLaurea_id` | `integer \| null` | no |
| `listino_facolta_id` | `integer \| null` | no |
| `listino_modalita_id` | `integer \| null` | no |
| `listino_tipoCorso_descrizione` | `string \| null` | no |
| `listino_tipoCorso_id` | `integer \| null` | no |
| `listino_tipo_id` | `integer` | sì |
| `nome_universita` | `string \| null` | no |
| `nome_universita_id` | `integer` | no |

### ListinoTestaCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `dettagli` | `list[ListinoDettaglioCreate] \| null` | no |
| `listTesta_codice` | `string` | sì |
| `listTesta_created_by` | `integer \| null` | no |
| `listTesta_descrizione` | `string` | sì |
| `listTesta_livello` | `integer \| null` | no |
| `listino_attivoSN` | `integer` | no |
| `listino_corsoLaurea_id` | `integer \| null` | no |
| `listino_durataLaurea_id` | `integer \| null` | no |
| `listino_facolta_id` | `integer \| null` | no |
| `listino_modalita_id` | `integer \| null` | no |
| `listino_tipoCorso_id` | `integer \| null` | no |
| `listino_tipo_id` | `integer` | sì |
| `nome_universita_id` | `integer` | no |

### ListinoTestaUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `dettagli` | `list[ListinoDettaglioCreate] \| null` | no |
| `listTesta_codice` | `string \| null` | no |
| `listTesta_descrizione` | `string \| null` | no |
| `listTesta_livello` | `integer \| null` | no |
| `listTesta_updated_by` | `integer \| null` | no |
| `listino_attivoSN` | `integer \| null` | no |
| `listino_corsoLaurea_id` | `integer \| null` | no |
| `listino_durataLaurea_id` | `integer \| null` | no |
| `listino_facolta_id` | `integer \| null` | no |
| `listino_modalita_id` | `integer \| null` | no |
| `listino_tipoCorso_id` | `integer \| null` | no |
| `listino_tipo_id` | `integer \| null` | no |
| `nome_universita_id` | `integer \| null` | no |

### ListinoTipoCorso

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `listino_tipoCorso_descrizione` | `string` | sì |
| `listino_tipoCorso_id` | `integer` | sì |

### ListinoTipoCorsoCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `listino_tipoCorso_descrizione` | `string` | sì |

### LoginRequest

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `utente_password` | `string` | sì |
| `utente_username` | `string` | sì |

### Opzione

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `dettaglio` | `string \| null` | no |
| `id` | `integer` | sì |
| `label` | `string` | sì |

### PaginaOpzioni

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `altri` | `boolean` | sì |
| `elementi` | `list[Opzione]` | sì |

### PermessiPraticheResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `a4u` | `boolean` | sì |
| `abilPraticheUniv` | `boolean` | sì |
| `corsi_speciali` | `boolean` | sì |
| `ecampus` | `boolean` | sì |
| `link_campus` | `boolean` | sì |

### PraticaCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda_id` | `integer \| null` | no |
| `cliente_consulente_id` | `integer \| null` | no |
| `cliente_emittente_aderente_id` | `integer \| null` | no |
| `cliente_id` | `integer \| null` | no |
| `listTesta_corso2_id` | `integer \| null` | no |
| `listTesta_corso3_id` | `integer \| null` | no |
| `listTesta_id` | `integer \| null` | no |
| `listino_tipo_corso_id` | `integer \| null` | no |
| `nome_universita_id` | `integer \| null` | no |
| `pratica_annoAccademico` | `string \| null` | no |
| `pratica_codiceASG` | `string \| null` | no |
| `pratica_corso1_24CFU` | `integer \| null` | no |
| `pratica_corso2_24CFU` | `integer \| null` | no |
| `pratica_corso3_24CFU` | `integer \| null` | no |
| `pratica_corso4_24CFU` | `integer \| null` | no |
| `pratica_dataCreazione` | `string(date) \| null` | no |
| `pratica_forzeDellOrdine` | `integer \| null` | no |
| `pratica_missFlag_dilazioni` | `integer \| null` | no |
| `pratica_missFlag_firma` | `integer \| null` | no |
| `pratica_missFlag_firma_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload1_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload2_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload3_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload4_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload5_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload_1` | `integer \| null` | no |
| `pratica_missFlag_upload_2` | `integer \| null` | no |
| `pratica_missFlag_upload_3` | `integer \| null` | no |
| `pratica_missFlag_upload_4` | `integer \| null` | no |
| `pratica_missFlag_upload_5` | `integer \| null` | no |
| `pratica_note` | `string \| null` | no |
| `pratica_numero` | `string \| null` | no |
| `pratica_pathFile` | `string \| null` | no |
| `pratica_pathFile_rateizzazione` | `string \| null` | no |
| `pratica_prezzo` | `number \| string \| null` | no |
| `pratica_rinnPrimoAnno` | `integer \| null` | no |
| `pratica_rinnSecondoAnno` | `integer \| null` | no |
| `pratica_rinnTerzoAnno` | `integer \| null` | no |
| `pratica_sedeErogazione` | `string \| null` | no |
| `pratica_stato_id` | `integer \| null` | no |
| `utente_consulente_id` | `integer \| null` | no |
| `utente_id` | `integer \| null` | no |

### PraticaResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda_id` | `integer \| null` | no |
| `cliente_consulente_id` | `integer \| null` | no |
| `cliente_emittente_aderente_id` | `integer \| null` | no |
| `cliente_id` | `integer \| null` | no |
| `cliente_nome_completo` | `string \| null` | no |
| `emittente` | `EmittenteBreve \| null` | no |
| `listTesta_corso2_id` | `integer \| null` | no |
| `listTesta_corso3_id` | `integer \| null` | no |
| `listTesta_descrizione` | `string \| null` | no |
| `listTesta_id` | `integer \| null` | no |
| `listino_tipoCorso_descrizione` | `string \| null` | no |
| `listino_tipo_corso_id` | `integer \| null` | no |
| `nome_universita_descrizione` | `string \| null` | no |
| `nome_universita_id` | `integer \| null` | no |
| `pratica_annoAccademico` | `string \| null` | no |
| `pratica_codiceASG` | `string \| null` | no |
| `pratica_corso1_24CFU` | `integer \| null` | no |
| `pratica_corso2_24CFU` | `integer \| null` | no |
| `pratica_corso3_24CFU` | `integer \| null` | no |
| `pratica_corso4_24CFU` | `integer \| null` | no |
| `pratica_created_at` | `string(date-time) \| null` | no |
| `pratica_dataCreazione` | `string(date) \| null` | no |
| `pratica_forzeDellOrdine` | `integer \| null` | no |
| `pratica_id` | `integer` | sì |
| `pratica_missFlag_dilazioni` | `integer \| null` | no |
| `pratica_missFlag_firma` | `integer \| null` | no |
| `pratica_missFlag_firma_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload1_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload2_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload3_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload4_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload5_cliente` | `integer \| null` | no |
| `pratica_missFlag_upload_1` | `integer \| null` | no |
| `pratica_missFlag_upload_2` | `integer \| null` | no |
| `pratica_missFlag_upload_3` | `integer \| null` | no |
| `pratica_missFlag_upload_4` | `integer \| null` | no |
| `pratica_missFlag_upload_5` | `integer \| null` | no |
| `pratica_note` | `string \| null` | no |
| `pratica_numero` | `string \| null` | no |
| `pratica_pathFile` | `string \| null` | no |
| `pratica_pathFile_rateizzazione` | `string \| null` | no |
| `pratica_prezzo` | `number \| string \| null` | no |
| `pratica_rinnPrimoAnno` | `integer \| null` | no |
| `pratica_rinnSecondoAnno` | `integer \| null` | no |
| `pratica_rinnTerzoAnno` | `integer \| null` | no |
| `pratica_sedeErogazione` | `string \| null` | no |
| `pratica_stato_descrizione` | `string \| null` | no |
| `pratica_stato_id` | `integer \| null` | no |
| `pratica_updated_at` | `string(date-time) \| null` | no |
| `utente_consulente_id` | `integer \| null` | no |
| `utente_id` | `integer \| null` | no |

### PraticaUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda_id` | `integer \| null` | no |
| `cliente_consulente_id` | `integer \| null` | no |
| `listTesta_corso2_id` | `integer \| null` | no |
| `listTesta_corso3_id` | `integer \| null` | no |
| `listino_tipo_corso_id` | `integer \| null` | no |
| `pratica_annoAccademico` | `string \| null` | no |
| `pratica_corso1_24CFU` | `integer \| null` | no |
| `pratica_corso2_24CFU` | `integer \| null` | no |
| `pratica_corso3_24CFU` | `integer \| null` | no |
| `pratica_corso4_24CFU` | `integer \| null` | no |
| `pratica_note` | `string \| null` | no |
| `pratica_numero` | `string \| null` | no |
| `pratica_pathFile` | `string \| null` | no |
| `pratica_pathFile_rateizzazione` | `string \| null` | no |
| `pratica_prezzo` | `number \| string \| null` | no |
| `pratica_sedeErogazione` | `string \| null` | no |
| `pratica_stato_id` | `integer \| null` | no |
| `utente_consulente_id` | `integer \| null` | no |
| `utente_id` | `integer \| null` | no |

### ProfiloPersonale

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `azienda` | `string \| null` | sì |
| `cellulare` | `string \| null` | sì |
| `cittadinanza` | `string \| null` | sì |
| `codice_fiscale` | `string \| null` | sì |
| `cognome` | `string \| null` | sì |
| `domicilio` | `IndirizzoProfilo` | sì |
| `email` | `string \| null` | sì |
| `nome` | `string \| null` | sì |
| `pec` | `string \| null` | sì |
| `residenza` | `IndirizzoProfilo` | sì |
| `ruolo` | `string \| null` | sì |
| `telefono` | `string \| null` | sì |
| `username` | `string` | sì |

### RichiestaResetRequest

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `email` | `string` | sì |

### RichiestaSfida

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `sfida` | `string` | sì |

### RimozionePasskey

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `id` | `integer` | sì |
| `password` | `string` | sì |

### RispostaPasskey

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `credenziale` | `dict` | sì |
| `sfida` | `string` | sì |

### RuoloCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `ruolo_codice` | `string` | sì |
| `ruolo_descrizione` | `string` | sì |

### RuoloResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `ruolo_codice` | `string` | sì |
| `ruolo_descrizione` | `string` | sì |
| `ruolo_id` | `integer` | sì |

### RuoloUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `ruolo_codice` | `string \| null` | no |
| `ruolo_descrizione` | `string \| null` | no |

### SessoEnum

Valori: "uomo" | "donna".

### TipoDocumentoEnum

Valori: "Carta d'identità" | "Carta d'Identità" | "Passaporto" | "Patente" | "Altro".

### TipoUtente

Valori: "sottoscrittore" | "attuatore".

### Universita

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cliente_id` | `integer \| null` | no |
| `universita_albo` | `string \| null` | no |
| `universita_altre_attivita_certificate` | `integer \| null` | no |
| `universita_annoSessione_professione` | `integer \| null` | no |
| `universita_anno_scolastico` | `string \| null` | no |
| `universita_anno_scolastico_ai` | `string \| null` | no |
| `universita_ateneoNullaosta` | `string \| null` | no |
| `universita_attIscritto_altro` | `string \| null` | no |
| `universita_attIscritto_annoIscrizione` | `string \| null` | no |
| `universita_attIscritto_citta` | `string \| null` | no |
| `universita_attIscritto_classeLaurea` | `string \| null` | no |
| `universita_attIscritto_denominazione` | `string \| null` | no |
| `universita_attIscritto_modalita` | `string \| null` | no |
| `universita_attIscritto_provincia` | `string \| null` | no |
| `universita_attIscritto_tipo` | `string \| null` | no |
| `universita_attIscritto_universita` | `string \| null` | no |
| `universita_attivita_professionalizzanti` | `integer \| null` | no |
| `universita_cittaUniConclusione` | `string \| null` | no |
| `universita_citta_istituto` | `string \| null` | no |
| `universita_citta_istituto_ai` | `string \| null` | no |
| `universita_conclusione` | `string \| null` | no |
| `universita_corrispondenza` | `string \| null` | no |
| `universita_corsi_di_formazione` | `integer \| null` | no |
| `universita_createBy` | `integer \| null` | no |
| `universita_createDate` | `string(date) \| null` | no |
| `universita_data_ats1` | `string(date) \| null` | no |
| `universita_data_ats2` | `string(date) \| null` | no |
| `universita_data_conclusione` | `string(date) \| null` | no |
| `universita_data_immatricolazione` | `string(date) \| null` | no |
| `universita_data_pl1` | `string(date) \| null` | no |
| `universita_data_pl2` | `string(date) \| null` | no |
| `universita_data_professione` | `string(date) \| null` | no |
| `universita_data_qualifica` | `string(date) \| null` | no |
| `universita_data_titolo` | `string(date) \| null` | no |
| `universita_diploma` | `string \| null` | no |
| `universita_forzeDellOrdine` | `string \| null` | no |
| `universita_id` | `integer` | sì |
| `universita_immatricolato` | `integer \| null` | no |
| `universita_iscrizioneAltraUniversita` | `integer \| null` | no |
| `universita_istituto` | `string \| null` | no |
| `universita_istituto_ai` | `string \| null` | no |
| `universita_istituto_ats1` | `string \| null` | no |
| `universita_istituto_ats2` | `string \| null` | no |
| `universita_istituto_pl1` | `string \| null` | no |
| `universita_istituto_pl2` | `string \| null` | no |
| `universita_luogo` | `string \| null` | no |
| `universita_luogo_professione` | `string \| null` | no |
| `universita_materia_ats1` | `string \| null` | no |
| `universita_materia_ats2` | `string \| null` | no |
| `universita_materia_pl1` | `string \| null` | no |
| `universita_materia_pl2` | `string \| null` | no |
| `universita_materia_titolo` | `string \| null` | no |
| `universita_percentualeInvalidita` | `integer \| null` | no |
| `universita_professione` | `string \| null` | no |
| `universita_provinciaConclusione` | `string \| null` | no |
| `universita_provincia_istituto` | `string \| null` | no |
| `universita_provincia_istituto_ai` | `string \| null` | no |
| `universita_qualifica_professionale` | `string \| null` | no |
| `universita_riforma` | `string \| null` | no |
| `universita_sessione_professione` | `string \| null` | no |
| `universita_tipoInvalidita` | `string \| null` | no |
| `universita_titolo_universitario` | `string \| null` | no |
| `universita_universitaConclusione` | `string \| null` | no |
| `universita_universita_titolo` | `string \| null` | no |
| `universita_updateBy` | `integer \| null` | no |
| `universita_updateDate` | `string(date) \| null` | no |
| `universita_via_istituto` | `string \| null` | no |
| `universita_via_istituto_ai` | `string \| null` | no |
| `universita_votoMassimo_ai` | `integer \| null` | no |
| `universita_votoMassimo_diploma` | `integer \| null` | no |
| `universita_votoMassimo_titolo` | `integer \| null` | no |
| `universita_votoRicevuto_ai` | `integer \| null` | no |
| `universita_votoRicevuto_diploma` | `integer \| null` | no |
| `universita_votoRicevuto_titolo` | `integer \| null` | no |
| `universita_voto_professione` | `integer \| null` | no |

### UniversitaCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cliente_id` | `integer \| null` | no |
| `universita_albo` | `string \| null` | no |
| `universita_altre_attivita_certificate` | `integer \| null` | no |
| `universita_annoSessione_professione` | `integer \| null` | no |
| `universita_anno_scolastico` | `string \| null` | no |
| `universita_anno_scolastico_ai` | `string \| null` | no |
| `universita_ateneoNullaosta` | `string \| null` | no |
| `universita_attIscritto_altro` | `string \| null` | no |
| `universita_attIscritto_annoIscrizione` | `string \| null` | no |
| `universita_attIscritto_citta` | `string \| null` | no |
| `universita_attIscritto_classeLaurea` | `string \| null` | no |
| `universita_attIscritto_denominazione` | `string \| null` | no |
| `universita_attIscritto_modalita` | `string \| null` | no |
| `universita_attIscritto_provincia` | `string \| null` | no |
| `universita_attIscritto_tipo` | `string \| null` | no |
| `universita_attIscritto_universita` | `string \| null` | no |
| `universita_attivita_professionalizzanti` | `integer \| null` | no |
| `universita_cittaUniConclusione` | `string \| null` | no |
| `universita_citta_istituto` | `string \| null` | no |
| `universita_citta_istituto_ai` | `string \| null` | no |
| `universita_conclusione` | `string \| null` | no |
| `universita_corrispondenza` | `string \| null` | no |
| `universita_corsi_di_formazione` | `integer \| null` | no |
| `universita_createBy` | `integer \| null` | no |
| `universita_data_ats1` | `string(date) \| null` | no |
| `universita_data_ats2` | `string(date) \| null` | no |
| `universita_data_conclusione` | `string(date) \| null` | no |
| `universita_data_immatricolazione` | `string(date) \| null` | no |
| `universita_data_pl1` | `string(date) \| null` | no |
| `universita_data_pl2` | `string(date) \| null` | no |
| `universita_data_professione` | `string(date) \| null` | no |
| `universita_data_qualifica` | `string(date) \| null` | no |
| `universita_data_titolo` | `string(date) \| null` | no |
| `universita_diploma` | `string \| null` | no |
| `universita_forzeDellOrdine` | `string \| null` | no |
| `universita_immatricolato` | `integer \| null` | no |
| `universita_iscrizioneAltraUniversita` | `integer \| null` | no |
| `universita_istituto` | `string \| null` | no |
| `universita_istituto_ai` | `string \| null` | no |
| `universita_istituto_ats1` | `string \| null` | no |
| `universita_istituto_ats2` | `string \| null` | no |
| `universita_istituto_pl1` | `string \| null` | no |
| `universita_istituto_pl2` | `string \| null` | no |
| `universita_luogo` | `string \| null` | no |
| `universita_luogo_professione` | `string \| null` | no |
| `universita_materia_ats1` | `string \| null` | no |
| `universita_materia_ats2` | `string \| null` | no |
| `universita_materia_pl1` | `string \| null` | no |
| `universita_materia_pl2` | `string \| null` | no |
| `universita_materia_titolo` | `string \| null` | no |
| `universita_percentualeInvalidita` | `integer \| null` | no |
| `universita_professione` | `string \| null` | no |
| `universita_provinciaConclusione` | `string \| null` | no |
| `universita_provincia_istituto` | `string \| null` | no |
| `universita_provincia_istituto_ai` | `string \| null` | no |
| `universita_qualifica_professionale` | `string \| null` | no |
| `universita_riforma` | `string \| null` | no |
| `universita_sessione_professione` | `string \| null` | no |
| `universita_tipoInvalidita` | `string \| null` | no |
| `universita_titolo_universitario` | `string \| null` | no |
| `universita_universitaConclusione` | `string \| null` | no |
| `universita_universita_titolo` | `string \| null` | no |
| `universita_updateBy` | `integer \| null` | no |
| `universita_via_istituto` | `string \| null` | no |
| `universita_via_istituto_ai` | `string \| null` | no |
| `universita_votoMassimo_ai` | `integer \| null` | no |
| `universita_votoMassimo_diploma` | `integer \| null` | no |
| `universita_votoMassimo_titolo` | `integer \| null` | no |
| `universita_votoRicevuto_ai` | `integer \| null` | no |
| `universita_votoRicevuto_diploma` | `integer \| null` | no |
| `universita_votoRicevuto_titolo` | `integer \| null` | no |
| `universita_voto_professione` | `integer \| null` | no |

### UniversitaUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cliente_id` | `integer \| null` | no |
| `universita_albo` | `string \| null` | no |
| `universita_altre_attivita_certificate` | `integer \| null` | no |
| `universita_annoSessione_professione` | `integer \| null` | no |
| `universita_anno_scolastico` | `string \| null` | no |
| `universita_anno_scolastico_ai` | `string \| null` | no |
| `universita_ateneoNullaosta` | `string \| null` | no |
| `universita_attIscritto_altro` | `string \| null` | no |
| `universita_attIscritto_annoIscrizione` | `string \| null` | no |
| `universita_attIscritto_citta` | `string \| null` | no |
| `universita_attIscritto_classeLaurea` | `string \| null` | no |
| `universita_attIscritto_denominazione` | `string \| null` | no |
| `universita_attIscritto_modalita` | `string \| null` | no |
| `universita_attIscritto_provincia` | `string \| null` | no |
| `universita_attIscritto_tipo` | `string \| null` | no |
| `universita_attIscritto_universita` | `string \| null` | no |
| `universita_attivita_professionalizzanti` | `integer \| null` | no |
| `universita_cittaUniConclusione` | `string \| null` | no |
| `universita_citta_istituto` | `string \| null` | no |
| `universita_citta_istituto_ai` | `string \| null` | no |
| `universita_conclusione` | `string \| null` | no |
| `universita_corrispondenza` | `string \| null` | no |
| `universita_corsi_di_formazione` | `integer \| null` | no |
| `universita_createBy` | `integer \| null` | no |
| `universita_data_ats1` | `string(date) \| null` | no |
| `universita_data_ats2` | `string(date) \| null` | no |
| `universita_data_conclusione` | `string(date) \| null` | no |
| `universita_data_immatricolazione` | `string(date) \| null` | no |
| `universita_data_pl1` | `string(date) \| null` | no |
| `universita_data_pl2` | `string(date) \| null` | no |
| `universita_data_professione` | `string(date) \| null` | no |
| `universita_data_qualifica` | `string(date) \| null` | no |
| `universita_data_titolo` | `string(date) \| null` | no |
| `universita_diploma` | `string \| null` | no |
| `universita_forzeDellOrdine` | `string \| null` | no |
| `universita_immatricolato` | `integer \| null` | no |
| `universita_iscrizioneAltraUniversita` | `integer \| null` | no |
| `universita_istituto` | `string \| null` | no |
| `universita_istituto_ai` | `string \| null` | no |
| `universita_istituto_ats1` | `string \| null` | no |
| `universita_istituto_ats2` | `string \| null` | no |
| `universita_istituto_pl1` | `string \| null` | no |
| `universita_istituto_pl2` | `string \| null` | no |
| `universita_luogo` | `string \| null` | no |
| `universita_luogo_professione` | `string \| null` | no |
| `universita_materia_ats1` | `string \| null` | no |
| `universita_materia_ats2` | `string \| null` | no |
| `universita_materia_pl1` | `string \| null` | no |
| `universita_materia_pl2` | `string \| null` | no |
| `universita_materia_titolo` | `string \| null` | no |
| `universita_percentualeInvalidita` | `integer \| null` | no |
| `universita_professione` | `string \| null` | no |
| `universita_provinciaConclusione` | `string \| null` | no |
| `universita_provincia_istituto` | `string \| null` | no |
| `universita_provincia_istituto_ai` | `string \| null` | no |
| `universita_qualifica_professionale` | `string \| null` | no |
| `universita_riforma` | `string \| null` | no |
| `universita_sessione_professione` | `string \| null` | no |
| `universita_tipoInvalidita` | `string \| null` | no |
| `universita_titolo_universitario` | `string \| null` | no |
| `universita_universitaConclusione` | `string \| null` | no |
| `universita_universita_titolo` | `string \| null` | no |
| `universita_updateBy` | `integer \| null` | no |
| `universita_via_istituto` | `string \| null` | no |
| `universita_via_istituto_ai` | `string \| null` | no |
| `universita_votoMassimo_ai` | `integer \| null` | no |
| `universita_votoMassimo_diploma` | `integer \| null` | no |
| `universita_votoMassimo_titolo` | `integer \| null` | no |
| `universita_votoRicevuto_ai` | `integer \| null` | no |
| `universita_votoRicevuto_diploma` | `integer \| null` | no |
| `universita_votoRicevuto_titolo` | `integer \| null` | no |
| `universita_voto_professione` | `integer \| null` | no |

### UtenteCreate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `utente_attivoSN` | `integer \| null` | no |
| `utente_created_by` | `integer \| null` | no |
| `utente_padre` | `integer \| null` | no |
| `utente_password` | `string` | sì |
| `utente_updated_by` | `integer \| null` | no |
| `utente_username` | `string` | sì |

### UtentePadreSchema

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `cliente` | `ClientePadreSchema \| null` | no |
| `utente_id` | `integer` | sì |
| `utente_username` | `string` | sì |

### UtenteResponse

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `aggiornato_da` | `UtentePadreSchema \| null` | no |
| `padre` | `UtentePadreSchema \| null` | no |
| `utente_attivoSN` | `integer` | sì |
| `utente_created_at` | `string(date) \| null` | no |
| `utente_id` | `integer` | sì |
| `utente_padre` | `integer \| null` | no |
| `utente_updated_at` | `string(date-time) \| null` | no |
| `utente_updated_by` | `integer \| null` | no |
| `utente_username` | `string` | sì |

### UtenteUpdate

| Campo | Tipo | Obbligatorio |
|---|---|---|
| `utente_attivoSN` | `integer \| null` | no |
| `utente_padre` | `integer \| null` | no |
| `utente_username` | `string \| null` | no |
