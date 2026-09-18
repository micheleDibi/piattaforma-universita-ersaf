# Pagine del frontend

> Pagina generata da `python scripts/documentazione/genera.py` a partire da `frontend/src/App.jsx` e `frontend/src/config/routes/`.
> Non modificarla a mano: rilancia il comando dopo aver cambiato le fonti.

Pagine registrate nell'applicazione web, nell'ordine in cui sono dichiarate.

- **Accesso**: `pubblica` per tutti; `solo ospiti` rimanda all'applicazione chi ha già una sessione; `sessione` richiede di aver effettuato l'accesso.
- **Menu**: la voce del menu laterale, se esiste. Una voce "solo Nazionale" è nascosta agli altri ruoli, ma la pagina resta raggiungibile digitando l'indirizzo: vedi i [limiti noti](../sicurezza.md#limiti-noti).

| Percorso | Pagina | Accesso | Menu |
|---|---|---|---|
| `/` | `Login` | solo ospiti | — |
| `/password-dimenticata` | `PasswordDimenticata` | pubblica | — |
| `/reimposta-password` | `ReimpostaPassword` | pubblica | — |
| `/dashboard` | `Dashboard` | sessione | Dashboard |
| `/profilo` | `MioProfilo` | sessione | — |
| `/sottoscrittori` | `ElencoClienti` (soloAttuatori=false, soloUtenti=true) | sessione | Sottoscrittori |
| `/attuatori` | `ElencoClienti` (soloAttuatori=true) | sessione | Attuatori (solo Nazionale) |
| `/aziende` | `ElencoAziende` (soloAttuatori=true) | sessione | Aziende |
| `/pratiche` | `ElencoPratiche` | sessione | Pratiche (solo Nazionale) |
| `/prodotti` | `ElencoProdottiFormativi` (soloAttuatori=true) | sessione | Prodotti formativi (solo Nazionale) |
| `/sottoscrittori/nuovo` | `NuovoSottoscrittore` (tipoUtente=sottoscrittore) | sessione | — |
| `/sottoscrittori/:clienteId` | `NuovoSottoscrittore` (tipoUtente=sottoscrittore) | sessione | — |
| `/attuatori/nuovo` | `NuovoSottoscrittore` (tipoUtente=attuatore) | sessione | — |
| `/attuatori/:clienteId` | `NuovoSottoscrittore` (tipoUtente=attuatore) | sessione | — |
| `/aziende/nuova` | `SchedaAzienda` | sessione | — |
| `/aziende/:aziendaId` | `SchedaAzienda` | sessione | — |
| `/prodotti/nuovo` | `InserimentoProdotto` | sessione | — |
| `/prodotti/:prodottoId` | `InserimentoProdotto` | sessione | — |
| `/pratiche/nuova` | `SchedaPratica` | sessione | — |
| `/pratiche/:praticaId` | `SchedaPratica` | sessione | — |
| `*` | `PaginaNonTrovata` | pubblica | — |
