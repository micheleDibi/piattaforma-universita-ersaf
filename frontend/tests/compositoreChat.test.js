import test from "node:test";
import assert from "node:assert/strict";
import { invioDaTastiera } from "../src/lib/compositoreChat.js";

function premi(modifiche = {}, opzioni = {}) {
  let invii = 0, prevenuto = false;
  invioDaTastiera({ key: "Enter", preventDefault: () => { prevenuto = true; }, ...modifiche },
    { compatto: false, disabilitato: false, ...opzioni }, () => { invii++; });
  return { invii, prevenuto };
}

test("Invio spedisce una volta; tenere il tasto premuto non duplica il messaggio", () => {
  assert.deepEqual(premi(), { invii: 1, prevenuto: true });
  assert.deepEqual(premi({ repeat: true }), { invii: 0, prevenuto: true });
});
test("Shift e mobile conservano il comportamento nativo a capo", () => {
  assert.deepEqual(premi({ shiftKey: true }), { invii: 0, prevenuto: false });
  assert.deepEqual(premi({}, { compatto: true }), { invii: 0, prevenuto: false });
});
test("una composizione IME non spedisce prima di confermare il testo", () => {
  for (const evento of [{ isComposing: true }, { nativeEvent: { isComposing: true } }, { keyCode: 229 }]) {
    assert.deepEqual(premi(evento), { invii: 0, prevenuto: false });
  }
});
test("campo vuoto, conferma pendente o disconnessione non inviano", () => {
  assert.deepEqual(premi({}, { disabilitato: true }), { invii: 0, prevenuto: true });
});
