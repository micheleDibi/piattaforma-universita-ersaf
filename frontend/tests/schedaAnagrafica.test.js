import { test } from "node:test";
import assert from "node:assert/strict";
import {
  dataCronologia,
  nomeUtente,
  statoAccount,
  statoRecapito,
} from "../src/lib/schedaAnagrafica.js";
import { TESTI_ANAGRAFICA, TESTI_INFORMAZIONI } from "../src/config/testi/anagrafica.js";

test("stato dell'account: -1 e' attivo, ogni altro valore disattivo, null senza utente", () => {
  assert.deepEqual(statoAccount(-1), { attivo: true, tono: "positivo" });
  assert.deepEqual(statoAccount("-1"), { attivo: true, tono: "positivo" });
  assert.deepEqual(statoAccount(0), { attivo: false, tono: "negativo" });
  // 1 non e' il vero della convenzione legacy su utente_attivoSN.
  assert.deepEqual(statoAccount(1), { attivo: false, tono: "negativo" });
  for (const assente of [null, undefined, ""]) assert.equal(statoAccount(assente), null);
  assert.equal(TESTI_ANAGRAFICA.stato(true), "Attivo");
  assert.equal(TESTI_ANAGRAFICA.stato(false), "Disattivo");
});

test("recapito verificato: pillola al posto del pulsante, solo sul valore salvato", () => {
  const verifica = {
    disponibile: true,
    stato: { valore: "a@b.it", verificato: true, verificato_il: "2024-09-12T17:24:00" },
  };
  assert.deepEqual(statoRecapito(verifica, "a@b.it"), {
    verificato: true,
    verificatoIl: "2024-09-12T17:24:00",
    mostraVerifica: false,
    verificaDisabilitata: false,
    daSalvare: false,
  });
  // Valore cambiato: la verifica non vale piu' e va prima salvato.
  const cambiato = statoRecapito(verifica, "c@d.it");
  assert.equal(cambiato.verificato, false);
  assert.equal(cambiato.verificatoIl, null);
  assert.equal(cambiato.mostraVerifica, true);
  assert.equal(cambiato.verificaDisabilitata, true);
  assert.equal(cambiato.daSalvare, true);
});

test("recapito da verificare: pulsante attivo solo se salvato e non vuoto", () => {
  const verifica = { disponibile: true, stato: { valore: "3331234567", verificato: false } };
  const salvato = statoRecapito(verifica, "3331234567");
  assert.equal(salvato.mostraVerifica, true);
  assert.equal(salvato.verificaDisabilitata, false);
  assert.equal(salvato.daSalvare, false);
  const vuoto = statoRecapito({ disponibile: true, stato: { valore: "" } }, "");
  assert.equal(vuoto.verificaDisabilitata, true);
  assert.equal(vuoto.daSalvare, false);
});

test("recapito vuoto: mai verificato, anche se il server lo segnala", () => {
  const verifica = { disponibile: true, stato: { valore: "", verificato: true } };
  const vuoto = statoRecapito(verifica, "");
  assert.equal(vuoto.verificato, false);
  assert.equal(vuoto.verificatoIl, null);
  assert.equal(vuoto.mostraVerifica, true);
  assert.equal(vuoto.verificaDisabilitata, true);
  assert.equal(vuoto.daSalvare, false);
});

test("recapito in creazione: niente pulsante, niente invito a salvare", () => {
  const nuovo = statoRecapito({ disponibile: false, stato: undefined }, "a@b.it");
  assert.equal(nuovo.verificato, false);
  assert.equal(nuovo.mostraVerifica, false);
  assert.equal(nuovo.daSalvare, false);
  assert.equal(statoRecapito(undefined, "").mostraVerifica, false);
});

test("cronologia: data e ora in formato italiano, vuota se assente", () => {
  assert.match(dataCronologia("2024-09-12T17:24:29"), /^\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}:\d{2}$/);
  assert.equal(dataCronologia(null), "");
  assert.equal(dataCronologia(""), "");
});

test("nome dell'utente collegato: persona, poi username, poi identificativo", () => {
  const cliente = { cliente_nome: "Mario", cliente_cognome: "Rossi" };
  assert.equal(nomeUtente({ utente_id: 7, utente_username: "mrossi", cliente }, 7), "Mario Rossi");
  assert.equal(nomeUtente({ utente_id: 7, utente_username: "mrossi" }, 7), "mrossi");
  assert.equal(nomeUtente({ utente_id: 7 }, 7), "ID: 7");
  assert.equal(nomeUtente(null, 9), "ID: 9");
  assert.equal(nomeUtente(undefined, null), "Nessuno");
});

test("testi della scheda: titolo, pulsante di creazione e descrizione per tipo", () => {
  assert.equal(TESTI_ANAGRAFICA.titolo("sottoscrittore", true), "Modifica sottoscrittore");
  assert.equal(TESTI_ANAGRAFICA.titolo("attuatore", false), "Nuovo attuatore");
  assert.equal(TESTI_ANAGRAFICA.crea("sottoscrittore"), "Crea sottoscrittore");
  assert.equal(TESTI_ANAGRAFICA.crea("attuatore"), "Crea attuatore");
  assert.equal(TESTI_ANAGRAFICA.ritorno("attuatore"), "Attuatori");
  assert.equal(TESTI_INFORMAZIONI.descrizione("sottoscrittore"), "Dati anagrafici del sottoscrittore.");
  assert.equal(TESTI_INFORMAZIONI.descrizione("attuatore"), "Dati anagrafici dell'attuatore.");
});
