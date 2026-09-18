import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { TESTI_TITOLI } from "../src/config/testi/titoli.js";

// node --test non legge JSX: si controlla il sorgente del componente.
const sorgente = readFileSync(new URL("../src/components/SezioneTitoli.jsx", import.meta.url), "utf8");
const tagInput = (nome) => sorgente.match(new RegExp(`<input\\b[^>]*\\bname="${nome}"[^>]*/>`, "g")) ?? [];

test("scheda titoli: gli anni di diploma e anno integrativo sono testo sui propri campi", () => {
  for (const nome of ["universita_anno_scolastico", "universita_anno_scolastico_ai"]) {
    const tag = tagInput(nome);
    assert.equal(tag.length, 1, `${nome}: un solo input`);
    assert.match(tag[0], /\btype="text"/);
    assert.match(tag[0], new RegExp(`\\bvalue=\\{formData\\.${nome}\\}`));
    assert.match(tag[0], /\bmaxLength=\{45\}/);
    assert.match(tag[0], /\bplaceholder=\{TESTI_TITOLI\.segnapostoAnno\}/);
    // L'etichetta punta all'input.
    const suffisso = tag[0].match(/\bid=\{`\$\{id\}-([a-z-]+)`\}/)?.[1];
    assert.ok(suffisso, `${nome}: id assente`);
    assert.ok(sorgente.includes(`htmlFor={\`\${id}-${suffisso}\`}`), `${nome}: etichetta non associata`);
  }
  assert.equal(TESTI_TITOLI.segnapostoAnno, "es. 2015 oppure 2014/2015");
});

test("scheda titoli: la data del titolo universitario resta una data, e compare una volta sola", () => {
  const tag = tagInput("universita_data_titolo");
  assert.equal(tag.length, 1);
  assert.match(tag[0], /\btype="date"/);
  assert.equal(sorgente.match(/universita_data_titolo/g).length, 2, "name e value dello stesso input");
});
