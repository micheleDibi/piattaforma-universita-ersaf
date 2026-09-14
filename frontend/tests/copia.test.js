import test from "node:test";
import assert from "node:assert/strict";
import { copiaTesto } from "../src/lib/copia.js";

test("copia confermata solo dopo il completamento degli appunti", async () => {
  let completa;
  let finita = false;
  let ricevuto;
  const copia = copiaTesto("utente.prova\npassword-di-test", { writeText: (testo) => {
    ricevuto = testo;
    return new Promise((resolve) => { completa = resolve; });
  } }).then(() => { finita = true; });
  await Promise.resolve();
  assert.equal(finita, false);
  completa();
  await copia;
  assert.equal(finita, true);
  assert.equal(ricevuto, "utente.prova\npassword-di-test");
});

test("rifiuto o indisponibilità degli appunti non diventano un falso successo", async () => {
  await assert.rejects(copiaTesto("test", undefined), /not defined|disponibili/);
  await assert.rejects(copiaTesto("test", {}), /disponibili/);
  await assert.rejects(copiaTesto("test", { writeText: () => Promise.reject(new Error("negato")) }), /negato/);
});
