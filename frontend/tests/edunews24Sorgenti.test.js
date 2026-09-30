// Sorgenti della sezione EduNews24 letti come testo, senza importarli (i
// test non importano .jsx): vincoli che ESLint non vede.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { RETI_SOCIALI } from "../src/config/edunews24.js";

const RADICE = new URL("../", import.meta.url);
const SRC = new URL("../src/", import.meta.url);
const COMPONENTI = new URL("../src/components/edunews24/", import.meta.url);
const HOOK = new URL("../src/hooks/", import.meta.url);
const ASSET = new URL("../src/assets/edunews24/", import.meta.url);
const STILI = new URL("../src/config/styles/edunews24.css", import.meta.url);
const STILI_DASHBOARD = new URL("../src/config/styles/dashboard.css", import.meta.url);
const RICETTE = new URL("../src/config/styles/edunews24.js", import.meta.url);
const TOKEN = new URL("../src/config/tokens/edunews24.css", import.meta.url);
const SCHEDE = new URL("../src/config/styles/schede.css", import.meta.url);

function leggi(cartella, scelta) {
  return readdirSync(cartella)
    .filter(scelta)
    .sort()
    .map((nome) => ({ nome, testo: readFileSync(new URL(nome, cartella), "utf8") }));
}

// Commenti tolti: la documentazione puo' nominare cio' che il codice evita.
function senzaCommenti(testo) {
  return testo.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/[^\n]*/g, "$1");
}

const componenti = leggi(COMPONENTI, (nome) => nome.endsWith(".jsx"));
const hook = leggi(HOOK, (nome) => /EduNews24|AttesaRiprova|ComparsaRitardata|FasciaScorrevole/.test(nome));
const sorgenti = [...componenti, ...hook];
// Fuori dalla cartella della sezione, i file che disegnano o compongono testi
// visibili: Dashboard, scorciatoie, testi e librerie.
const altri = [
  "components/Dashboard.jsx",
  "components/dashboard/ScorciatoieDashboard.jsx",
  "config/testi/dashboard.js",
  "config/testi/edunews24.js",
  "lib/dashboard.js",
  "lib/edunews24.js",
].map((nome) => ({ nome, testo: readFileSync(new URL(nome, SRC), "utf8") }));

test("i componenti condivisi e gli hook ci sono tutti", () => {
  const nomi = componenti.map(({ nome }) => nome);
  for (const nome of [
    "CopertinaTipografica.jsx", "DistintivoScadenza.jsx", "DistintivoVideo.jsx", "FolioEduNews24.jsx",
    "ImmagineArticolo.jsx", "LinkEsterno.jsx", "MetadatiVoce.jsx", "ScheletroEduNews24.jsx", "Sigillo.jsx",
    "SocialEduNews24.jsx", "Targa.jsx", "Timbro.jsx", "TimbroPlay.jsx", "VideoArticolo.jsx",
  ]) assert.ok(nomi.includes(nome), nome);
  assert.deepEqual(hook.map(({ nome }) => nome), [
    "useAttesaRiprova.js", "useCategorieEduNews24.js", "useComparsaRitardata.js", "useEsitoFunzioneEduNews24.js",
    "useFasciaScorrevole.js", "useModuloEduNews24.js", "usePaginaEduNews24.js",
  ]);
});

test("un solo export per componente, predefinito; un export con nome per hook", () => {
  for (const { nome, testo } of componenti) {
    const codice = senzaCommenti(testo);
    assert.equal((codice.match(/^export /gm) ?? []).length, 1, nome);
    assert.match(codice, /^export default function [A-Z]/m, nome);
  }
  for (const { nome, testo } of hook) {
    const codice = senzaCommenti(testo);
    assert.equal((codice.match(/^export /gm) ?? []).length, 1, nome);
    assert.match(codice, new RegExp(`^export function ${nome.replace(".js", "")}\\(`, "m"), nome);
  }
});

test("un solo link esterno, sempre in una nuova scheda senza riferimenti", () => {
  for (const { nome, testo } of componenti) {
    if (nome === "LinkEsterno.jsx") continue;
    assert.doesNotMatch(senzaCommenti(testo), /<a[\s>]/, nome);
  }
  const link = senzaCommenti(componenti.find(({ nome }) => nome === "LinkEsterno.jsx").testo);
  const aperture = link.match(/<a\s[^>]*>/g) ?? [];
  assert.ok(aperture.length > 0);
  for (const apertura of aperture) {
    assert.match(apertura, /target="_blank"/);
    assert.match(apertura, /rel="noopener noreferrer"/);
  }
  assert.match(link, /<ExternalLink aria-hidden="true"/);
  assert.match(link, /testi\.nuovaScheda/);
});

test("niente HTML esterno, iframe, crossorigin, autoplay, muted, archivi del browser o stili in linea", () => {
  for (const { nome, testo } of sorgenti) {
    const codice = senzaCommenti(testo);
    assert.doesNotMatch(codice, /dangerouslySetInnerHTML/, nome);
    assert.doesNotMatch(codice, /<iframe/i, nome);
    assert.doesNotMatch(codice, /crossorigin/i, nome);
    assert.doesNotMatch(codice, /autoplay/i, nome);
    assert.doesNotMatch(codice, /\bmuted\b/i, nome);
    assert.doesNotMatch(codice, /\bloop\b/, nome);
    assert.doesNotMatch(codice, /localStorage|sessionStorage|indexedDB/, nome);
    assert.doesNotMatch(codice, /style=\{/, nome);
    assert.doesNotMatch(codice, /AbortError/, nome);
  }
});

test("icone solo dal catalogo e nessun glifo al posto delle icone", () => {
  for (const { nome, testo } of [...sorgenti, ...altri]) {
    assert.doesNotMatch(testo, /from "lucide-react"/, nome);
    assert.doesNotMatch(testo, /\.svg"/, nome);
    assert.doesNotMatch(testo, /[→←↑↓›‹•·×▶◀✓✕]/, nome);
  }
});

test("Dashboard, testi e librerie: niente stili in linea", () => {
  for (const { nome, testo } of altri) assert.doesNotMatch(senzaCommenti(testo), /style=\{/, nome);
});

test("social: gli indirizzi dei profili stanno solo in config/edunews24.js", () => {
  // Espressione composta a pezzi: questo file non contiene nessun indirizzo.
  const dominio = new RegExp(`(${RETI_SOCIALI.join("|")})\\.com`, "i");
  const file = ["src", "tests"].flatMap((cartella) =>
    readdirSync(new URL(`${cartella}/`, RADICE), { recursive: true })
      .map((nome) => `${cartella}/${nome.replaceAll("\\", "/")}`)
      .filter((nome) => /\.(css|html|js|jsx|json|md|svg)$/.test(nome)));
  file.push("index.html");
  assert.ok(file.includes("src/config/edunews24.js"));
  const fuoriPosto = file.filter((nome) =>
    nome !== "src/config/edunews24.js" && dominio.test(readFileSync(new URL(nome, RADICE), "utf8")));
  assert.deepEqual(fuoriPosto, []);
});

test("Riprova nel modulo porta il fuoco sul corpo prima di ricaricare", () => {
  const modulo = senzaCommenti(componenti.find(({ nome }) => nome === "ModuloEduNews24.jsx").testo);
  assert.match(modulo, /id="edunews24-modulo-corpo"[^>]*tabIndex=\{-1\}/);
  assert.match(modulo, /rifCorpo\.current\?\.focus\(\);\s*modulo\.riprova\(\);/);
  assert.match(modulo, /onRiprova=\{riprova\}/);
  // Niente aria-busy sul corpo: coprirebbe il role="status" dello scheletro.
  // L'esito del nuovo tentativo va nella regione aria-live del modulo.
  assert.doesNotMatch(modulo, /aria-busy/);
  assert.match(modulo, /function riprova\(\) \{[^}]*setAnnunciaEsito\(true\);/);
  assert.match(modulo, /aria-live="polite">\s*\{annunciaEsito \? annuncioEsitoModulo\(modulo\.stato, sezione\) : annuncio\}/);
});

test("errore del primo caricamento della pagina: i secondi in una nota che sparisce allo sblocco", () => {
  const pannello = senzaCommenti(componenti.find(({ nome }) => nome === "PannelloSezioneEduNews24.jsx").testo);
  assert.match(pannello, /aria-describedby=\{errore\.nota \? idNota : undefined\}/);
  assert.match(pannello, /\{errore\.nota && <p id=\{idNota\}/);
  const hook = readFileSync(new URL("usePaginaEduNews24.js", HOOK), "utf8");
  assert.match(hook, /messaggioErrorePagina\(sezione, corrente\.statoErrore, corrente\.attesaSecondi, bloccato\)/);
});

test("fila delle categorie senza scroll-snap: la linguetta a fuoco entra con l'anello", () => {
  const barra = senzaCommenti(componenti.find(({ nome }) => nome === "BarraFiltriEduNews24.jsx").testo);
  assert.match(barra, /onFocus=\{fuocoNellaFila\}/);
  assert.match(barra, /matches\(":focus-visible"\)/);
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  assert.match(css, /\.edunews24-filtri__categorie \{/);
  assert.doesNotMatch(css, /\.edunews24-filtri__categorie[^{]*\{[^}]*scroll-snap/);
});

// Corpo della prima regola che comincia la riga con questo selettore esatto
// (commenti tolti).
function regola(css, selettore) {
  const inizio = css.split("\n").findIndex((riga) => riga.startsWith(`${selettore} {`));
  assert.ok(inizio >= 0, selettore);
  const resto = css.split("\n").slice(inizio).join("\n");
  return resto.slice(0, resto.indexOf("}"));
}

test("fascia e miniatura posizionate: il titolo sr-only non allarga la pagina", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  assert.match(regola(css, ".edunews24-fascia"), /position: relative;/);
  assert.match(regola(css, ".edunews24-miniatura"), /position: relative;/);
  assert.match(regola(css, ".edunews24-modulo"), /position: relative;/);
  const fascia = senzaCommenti(componenti.find(({ nome }) => nome === "FasciaMiniature.jsx").testo);
  // Lo sr-only sta dentro il pulsante della miniatura.
  assert.match(fascia, /<button[^>]*className="edunews24-miniatura[\s\S]*?className="sr-only"[\s\S]*?<\/button>/);
  // Nell'apertura il titolo completo sr-only sta nella colonna del testo, posizionata.
  assert.match(regola(css, ".edunews24-apertura__testo"), /position: relative;/);
  const apertura = senzaCommenti(componenti.find(({ nome }) => nome === "AperturaNotizia.jsx").testo);
  assert.match(apertura, /className="edunews24-apertura__testo"[\s\S]*?className="sr-only"/);
});

// Corpo del primo blocco @container che comincia la riga con questa
// intestazione esatta (commenti tolti), fino alla graffa di chiusura in
// colonna 0.
function blocco(css, intestazione) {
  const righe = css.split("\n");
  const inizio = righe.findIndex((riga) => riga.startsWith(`${intestazione} {`));
  assert.ok(inizio >= 0, intestazione);
  const fine = righe.findIndex((riga, indice) => indice > inizio && riga === "}");
  return righe.slice(inizio + 1, fine).join("\n");
}

test("filtri attivi sotto i 40rem: una riga che scorre, posizionata, con \"Filtri attivi\" solo per i lettori di schermo", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  const stretto = blocco(css, "@container edunews24-foglio (width < theme(--breakpoint-edunews24-griglia))");
  const riga = stretto.slice(stretto.indexOf(".edunews24-filtri__attivi {"));
  const corpo = riga.slice(0, riga.indexOf("}"));
  for (const dichiarazione of ["position: relative;", "flex-wrap: nowrap;", "overflow-x: auto;", "margin-inline: -0.3125rem;", "padding-inline: 0.3125rem;"]) {
    assert.ok(corpo.includes(dichiarazione), dichiarazione);
  }
  assert.match(stretto, /\.edunews24-filtri__attivi > \* \{ flex-shrink: 0; \}/);
  assert.match(stretto, /\.edunews24-filtri__titolo-attivi \{ @apply sr-only; \}/);
  // Le etichette restano a 44px sotto i 40rem: la misura ridotta vale solo dai 40rem.
  assert.match(regola(css, ".edunews24-etichetta-filtro"), /min-height: 2\.75rem;/);
  const attivi = senzaCommenti(componenti.find(({ nome }) => nome === "FiltriAttiviEduNews24.jsx").testo);
  assert.match(attivi, /aria-labelledby=\{idTitolo\} onFocus=\{onFocus\}/);
  assert.match(attivi, /id=\{idTitolo\} className=\{\["edunews24-filtri__titolo-attivi"/);
  const barra = senzaCommenti(componenti.find(({ nome }) => nome === "BarraFiltriEduNews24.jsx").testo);
  assert.match(barra, /<FiltriAttiviEduNews24[^>]*onFocus=\{fuocoNellaFila\}/);
});

test("errore e vuoto del modulo centrati in verticale nella lastra, testo a sinistra", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  const stato = regola(css, ".edunews24-stato");
  assert.match(stato, /justify-content: center;/);
  assert.match(stato, /align-items: flex-start;/);
  assert.match(css, /\.edunews24-modulo__corpo > :is\(\.edunews24-stato, \.edunews24-scheletro\) \{ grid-row: 1 \/ -1; \}/);
});

test("modulo, Interpelli e Selezione: tabellone subito sotto la voce principale, lo spazio libero sotto", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  for (const contenitore of [".edunews24-modulo__corpo", ".edunews24-scheletro__forme"]) {
    // Le Notizie non cambiano: la fascia resta in fondo, dopo la riga 1fr.
    assert.ok(css.includes(`${contenitore} > .edunews24-fascia { grid-row: 3; }`), contenitore);
    const tabellone = regola(css, `${contenitore} > .edunews24-tabellone`);
    assert.match(tabellone, /grid-row: 2;/);
    assert.match(tabellone, /align-self: start;/);
  }
  assert.match(regola(css, ".edunews24-modulo__corpo"), /grid-template-rows: auto 1fr auto;/);
});

test("coppia e specchio con la colonna B doppia: un solo figlio della banda, due voci di testo con il divisore", () => {
  const banda = senzaCommenti(componenti.find(({ nome }) => nome === "BandaNotizie.jsx").testo);
  assert.match(banda, /<div className="edunews24-banda__colonna">/);
  assert.match(banda, /colonnaB\.map\(\(voce\) => <VoceNotiziaPagina [^\n]*\{\.\.\.TESTO\} \/>\)/);
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  // Il divisore sta nello spazio fra le voci, fuori dall'anello di fuoco
  // della voce: la voce non ha ne' padding ne' bordo.
  const divisore = regola(css, ".edunews24-banda__colonna > * + *::before");
  assert.match(divisore, /position: absolute;/);
  assert.match(divisore, /top: calc\(-1\.25rem - 1px\);/);
  assert.match(divisore, /border-top: 1px solid var\(--color-divisore\);/);
  assert.match(regola(css, ".edunews24-banda__colonna"), /row-gap: calc\(2\.5rem \+ 1px\);/);
  assert.doesNotMatch(css, /(__secondari|__colonna|\[data-schema="trio"\]) > \* \+ \* \{[^}]*(padding-top: 1\.25rem|border-top)/);
});

test("voci della pagina: la forma la decide formaVocePagina, anche per il riquadro e il distintivo", () => {
  const voce = senzaCommenti(componenti.find(({ nome }) => nome === "VoceNotiziaPagina.jsx").testo);
  assert.match(voce, /const formaVoce = formaVocePagina\(forma, voce\);/);
  assert.match(voce, /data-forma=\{formaVoce\}/);
  assert.match(voce, /\{formaVoce !== "testo" && \(/);
  assert.match(voce, /\{formaVoce === "testo" && video && <DistintivoVideo/);
  assert.doesNotMatch(voce, /\bforma (!|=)== "testo"/);
});

test("controlli in attesa spenti nel colore, non con l'opacita' che sbiadisce l'anello", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  const attesa = regola(css, '.edunews24 [aria-disabled="true"]');
  assert.doesNotMatch(attesa, /opacity/);
  assert.match(attesa, /color: var\(--color-testo-spento\);/);
  assert.match(css, /\.edunews24 \[aria-disabled="true"\]:hover \{ background-color: var\(--color-superficie\); \}/);
});

test("\"Tutte le aree\" in testo-tenue dentro la barra dei filtri", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  assert.match(css, /\.edunews24-filtri select:has\(> option\[data-senza-filtro\]:checked\):not\(:disabled\),\s*\.edunews24-filtri select option\[data-senza-filtro\] \{ color: var\(--color-testo-tenue\); \}/);
});

test("barra dei filtri da bordo a bordo: margini negativi pari al padding del pannello delle schede", () => {
  const schede = senzaCommenti(readFileSync(SCHEDE, "utf8"));
  const [, verticale, orizzontale] = schede.match(/\.schede__pannello \{ padding: (clamp\([^)]*\)) (clamp\([^)]*\)); \}/) ?? [];
  assert.ok(verticale && orizzontale);
  const filtri = regola(senzaCommenti(readFileSync(STILI, "utf8")), ".edunews24-filtri");
  assert.ok(filtri.includes(`margin-top: calc(-1 * ${verticale});`));
  assert.ok(filtri.includes(`margin-inline: calc(-1 * ${orizzontale});`));
  assert.ok(filtri.includes(`padding-inline: ${orizzontale};`));
});

test("classi mai composte a runtime", () => {
  for (const { nome, testo } of componenti) {
    assert.doesNotMatch(senzaCommenti(testo), /className=\{`[^`]*\$\{/, nome);
  }
  const ricette = senzaCommenti(readFileSync(RICETTE, "utf8"));
  assert.doesNotMatch(ricette, /(text-edunews24|line-clamp|text-testo)-\$\{/);
  assert.doesNotMatch(ricette, /["'`](text-edunews24|line-clamp)-["'`]\s*\+/);
});

test("il player e' nativo e parte solo al clic", () => {
  const video = senzaCommenti(componenti.find(({ nome }) => nome === "VideoArticolo.jsx").testo);
  const apertura = video.match(/<video\s[^>]*>/)?.[0] ?? "";
  assert.match(apertura, /\bcontrols\b/);
  assert.match(apertura, /\bplaysInline\b/);
  assert.match(apertura, /preload="none"/);
  assert.match(video, /<source src=\{[^}]+\} type=\{/);
  // Il video si monta solo dopo il clic sulla copertina.
  assert.match(video, /\{attivo && !errore && \(\s*<video/);
  assert.match(video, /flushSync\(\(\) => setAttivo\(true\)\)/);
  assert.match(video, /avviaEsclusivo\(/);
  assert.match(video, /rilasciaVideo\(/);
  // Smontato, il player smette anche di scaricare il file.
  assert.match(video, /return \(\) => \{\s*if \(!video\) return;\s*rilasciaVideo\(video\);\s*svuotaVideo\(video\);\s*\};/);
});

test("immagini con misure dichiarate, alt vuoto e senza crossorigin", () => {
  const immagine = senzaCommenti(componenti.find(({ nome }) => nome === "ImmagineArticolo.jsx").testo);
  const img = immagine.match(/<img\s[\s\S]*?\/>/)?.[0] ?? "";
  for (const attributo of ["width=", "height=", 'alt=""', "loading=", 'decoding="async"', "onError="]) {
    assert.ok(img.includes(attributo), attributo);
  }
});

test("SVG monocromatici e senza indirizzi, adatti a mask-image", () => {
  const svg = leggi(ASSET, (nome) => nome.endsWith(".svg"));
  assert.deepEqual(svg.map(({ nome }) => nome), ["facebook.svg", "instagram.svg", "logo.svg", "tiktok.svg"]);
  for (const { nome, testo } of svg) {
    // Unico indirizzo ammesso: lo spazio dei nomi SVG, senza il quale il
    // browser non disegna il file caricato come immagine.
    const resto = testo.replace('xmlns="http://www.w3.org/2000/svg"', "");
    assert.doesNotMatch(resto, /https?:|www\.|\/\/|@/, nome);
    assert.doesNotMatch(resto, /<script|<foreignObject|href=/i, nome);
  }
  for (const { nome, testo } of svg.filter(({ nome }) => nome !== "logo.svg")) {
    assert.equal((testo.match(/<path/g) ?? []).length, 1, nome);
    assert.doesNotMatch(testo, /fill=|stroke=|class=/, nome);
    assert.match(testo, /viewBox="0 0 24 24"/, nome);
  }
  const logo = svg.find(({ nome }) => nome === "logo.svg").testo;
  assert.match(logo, /viewBox="0 0 209 41"/);
  assert.doesNotMatch(logo, /animate-logo-entrance|class=/);
});

// Colori solo dai token; durate e curve solo da var(--durata-*) e
// var(--curva-*). Restituisce le dichiarazioni di movimento trovate.
function coloriEMovimentoDaiToken(css, nome) {
  assert.doesNotMatch(css, /#[0-9a-fA-F]{3,8}\b/, nome);
  assert.doesNotMatch(css, /\b(rgb|rgba|hsl|hsla|oklch)\(/, nome);
  assert.doesNotMatch(css, /cubic-bezier\(|\b\d+m?s\b/, nome);
  const movimenti = css.match(/^\s*(transition|animation)\s*:[^;]+;/gm) ?? [];
  for (const dichiarazione of movimenti) {
    if (/:\s*none\s*;/.test(dichiarazione)) continue;
    assert.match(dichiarazione, /var\(--durata-/, `${nome}: ${dichiarazione}`);
    assert.match(dichiarazione, /var\(--curva-/, `${nome}: ${dichiarazione}`);
  }
  return movimenti;
}

test("CSS della Dashboard: colori dai token, durate e curve dai token di movimento", () => {
  coloriEMovimentoDaiToken(senzaCommenti(readFileSync(STILI_DASHBOARD, "utf8")), "dashboard.css");
});

test("CSS della sezione: colori dai token, durate e curve dai token di movimento", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  assert.ok(coloriEMovimentoDaiToken(css, "edunews24.css").length > 0);
  // Le keyframe nuove si fermano con il movimento ridotto.
  const ridotto = css.slice(css.lastIndexOf("@media (prefers-reduced-motion: reduce)"));
  assert.match(ridotto, /animation: none/);
  assert.match(css, /@media \(forced-colors: active\)/);
});

test("token: i colori grezzi stanno solo nel file dei token", () => {
  const token = readFileSync(TOKEN, "utf8");
  const colori = token.match(/--color-edunews24-[a-z-]+:\s*#[0-9A-Fa-f]{6};/g) ?? [];
  assert.equal(colori.length, 10);
  for (const { nome, testo } of componenti) assert.doesNotMatch(senzaCommenti(testo), /#[0-9a-fA-F]{6}\b/, nome);
  assert.doesNotMatch(readFileSync(RICETTE, "utf8"), /#[0-9a-fA-F]{6}\b/);
});

test("container query sempre con il nome del contenitore e soglie dai token", () => {
  const forma = /^@container [a-z][a-z0-9-]* \(width [<>]=? theme\(--breakpoint-[a-z0-9-]+\)\)( and \(width [<>]=? theme\(--breakpoint-[a-z0-9-]+\)\))? \{$/;
  for (const [nome, file] of [["edunews24.css", STILI], ["dashboard.css", STILI_DASHBOARD]]) {
    const righe = senzaCommenti(readFileSync(file, "utf8")).split("\n").map((riga) => riga.trim())
      .filter((riga) => riga.startsWith("@container"));
    assert.ok(righe.length > 0, nome);
    for (const riga of righe) assert.match(riga, forma, `${nome}: ${riga}`);
  }
  // Il ripiego e' un contenitore con nome e soglia propria.
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  assert.match(regola(css, ".edunews24-ripiego"), /container: edunews24-ripiego \/ inline-size;/);
  assert.match(readFileSync(TOKEN, "utf8"), /--breakpoint-edunews24-ripiego: 20rem;/);
});

test("anelli di fuoco completi: player, tabpanel sotto la barra, celle delle scorciatoie", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  // Il player sta nel quadro, che taglia: l'anello doppio va sul media.
  assert.match(css, /\.edunews24 \.edunews24-media__player:focus-visible \{ outline: none; \}/);
  const player = regola(css, ".edunews24-media:has(> .edunews24-media__quadro > .edunews24-media__player:focus-visible)");
  assert.match(player, /outline: 2px solid var\(--color-fuoco\);/);
  assert.match(player, /box-shadow: 0 0 0 2px var\(--color-edunews24-su-blu\);/);
  // Il lato che la barra dei filtri copre si ridisegna su uno pseudo-elemento
  // della barra, che scende sul suo bordo inferiore; in basso l'anello segue
  // gli angoli del foglio.
  const barra = regola(css, '.edunews24 [role="tabpanel"]:focus-visible > .edunews24-filtri::after');
  assert.match(barra, /inset: 0 0 -1px;/);
  assert.match(barra, /border: 2px solid var\(--color-fuoco\);\s*border-bottom: 0;/);
  assert.match(barra, /pointer-events: none;/);
  assert.match(regola(css, ".edunews24-filtri"), /position: sticky;/);
  assert.match(css, /\.edunews24 \[role="tabpanel"\]:focus-visible \{\s*border-bottom-left-radius: calc\(var\(--radius-superficie\) - 1px\);/);
  // Scorciatoie: anello con gli angoli della scheda su uno pseudo-elemento,
  // la cella resta rettangolare.
  const dashboard = senzaCommenti(readFileSync(STILI_DASHBOARD, "utf8"));
  const cella = regola(dashboard, ".dashboard__scorciatoia:has(.dashboard__collegamento:focus-visible)::before");
  assert.match(cella, /border: 2px solid var\(--color-fuoco\);/);
  assert.match(cella, /border-radius: calc\(var\(--radius-superficie\) - 1px\);/);
  assert.match(cella, /pointer-events: none;/);
  assert.doesNotMatch(dashboard, /\.dashboard__scorciatoia:has\([^)]*\) \{/);
});

test("colori forzati: la scelta della miniatura lascia libero l'outline del fuoco", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  const forzati = blocco(css, "@media (forced-colors: active)");
  assert.doesNotMatch(forzati, /\.edunews24-miniatura\[aria-pressed="true"\] \{/);
  assert.match(forzati, /\.edunews24-miniatura\[aria-pressed="true"\] \.edunews24-cornice\[data-misura="piccola"\] > \.edunews24-media \{\s*outline: 2px solid Highlight;/);
  assert.match(forzati, /\.edunews24 \[aria-disabled="true"\] \{\s*border-color: GrayText;\s*color: GrayText;/);
  assert.match(forzati, /\.edunews24-ripiego__motivo \{ display: none; \}/);
  // Il filo sta sugli elementi assoluti che coprono il quadro, non sul quadro.
  assert.match(forzati, /\.edunews24-ripiego,\s*\.edunews24-media__errore \{\s*outline: 1px solid CanvasText;\s*outline-offset: -1px;/);
  assert.doesNotMatch(forzati, /\.edunews24-media__quadro \{/);
});

test("Dashboard: il fuoco non finisce sotto la barra superiore della shell", () => {
  const dashboard = senzaCommenti(readFileSync(STILI_DASHBOARD, "utf8"));
  assert.match(dashboard, /html:has\(\.dashboard\) \{ scroll-padding-top: calc\(var\(--spacing-barra-superiore\) \+ 0\.5rem\); \}/);
  assert.match(dashboard, /@media \(width >= theme\(--breakpoint-lg\)\) \{\s*html:has\(\.dashboard\) \{ scroll-padding-top: 0; \}/);
});

test("social: elenco con role=\"list\", come gli altri elenchi senza puntini", () => {
  const social = senzaCommenti(componenti.find(({ nome }) => nome === "SocialEduNews24.jsx").testo);
  assert.match(social, /<ul role="list" className=\{\["edunews24-social"/);
});

test("cifre tabulari solo sulla data dei metadati, non sui nomi composti", () => {
  const ricette = senzaCommenti(readFileSync(RICETTE, "utf8"));
  const meta = ricette.match(/export function metaVoce\(\) \{\s*return "([^"]*)";/)?.[1];
  assert.ok(meta);
  assert.doesNotMatch(meta, /tabular-nums/);
  assert.match(ricette, /cifre: "tabular-nums",/);
  const metadati = senzaCommenti(componenti.find(({ nome }) => nome === "MetadatiVoce.jsx").testo);
  assert.match(metadati, /<time dateTime=\{data\.iso\} className=\{STILI_EDUNEWS24\.cifre\}>/);
});

test("pagina: apertura compatta, voci di solo testo con la sintesi, pagine vuote con un seguito spiegate", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  assert.match(css, /\n {2}\.edunews24-prima-pagina__apertura \{\s*grid-column: span 8;\s*align-self: start;/);
  const voce = senzaCommenti(componenti.find(({ nome }) => nome === "VoceNotiziaPagina.jsx").testo);
  assert.match(voce, /const righe = formaVoce === "testo" \? Math\.max\(righeSintesi, 3\) : righeSintesi;/);
  assert.match(voce, /\{righe > 0 && voce\.sintesi && <p className=\{sintesi\(righe\)\}>/);
  const pannello = senzaCommenti(componenti.find(({ nome }) => nome === "PannelloSezioneEduNews24.jsx").testo);
  assert.match(pannello, /const senzaVoci = pagina\.primaCaricata && pagina\.elementi\.length === 0 && pagina\.altri;/);
  assert.match(pannello, /\} else if \(senzaVoci\) \{\s*contenuto = <p className=\{STILI_EDUNEWS24\.rigaStato\}>\{testi\.vociSuccessive\}<\/p>;/);
  assert.match(pannello, /senzaVoci \? testi\.vociSuccessive : testi\.annunci\.aggiornato/);
});

test("modulo: fascia con lo spazio fra le miniature sotto i 56rem, timbro a cavallo staccato dall'occhiello", () => {
  const css = senzaCommenti(readFileSync(STILI, "utf8"));
  const stretto = blocco(css, "@container edunews24-modulo (width < theme(--breakpoint-edunews24-ampio))");
  assert.match(stretto, /\.edunews24-fascia \{ column-gap: 1rem; \}/);
  assert.match(css, /\.edunews24-modulo \.edunews24-apertura:has\(\.edunews24-media\[data-video="player"\]\) \{ row-gap: 1\.75rem; \}/);
  // Il minimo del corpo impilato accoglie i .5rem in piu'.
  assert.match(regola(css, ".edunews24-modulo__corpo"), /min-height: max\(calc\(49cqi \+ 21\.5rem\), var\(--spacing-edunews24-corpo-stretto\)\);/);
  // Nel regime ampio il minimo lascia spazio al timbro fra media e fascia.
  assert.match(readFileSync(TOKEN, "utf8"), /--spacing-edunews24-corpo-ampio: 26\.5rem;/);
});

test("video che non si carica: il messaggio descrive il link che riceve il fuoco", () => {
  const video = senzaCommenti(componenti.find(({ nome }) => nome === "VideoArticolo.jsx").testo);
  assert.match(video, /const idErrore = useId\(\);/);
  assert.match(video, /<p id=\{idErrore\} className="edunews24-media__errore-testo">/);
  assert.match(video, /<LinkEsterno href=\{voce\.url\} rif=\{rifLink\} descrizione=\{idErrore\}/);
  const link = senzaCommenti(componenti.find(({ nome }) => nome === "LinkEsterno.jsx").testo);
  assert.match(link, /aria-describedby=\{descrizione\}/);
});

test("testata con la funzione spenta: niente folio e niente frase sui titoli", () => {
  const testata = senzaCommenti(componenti.find(({ nome }) => nome === "TestataEduNews24.jsx").testo);
  assert.match(testata, /\{spenta \? testi\.presentazione : `\$\{testi\.presentazione\} \$\{testi\.presentazioneTitoli\}`\}/);
  assert.match(testata, /\{!spenta && <FolioEduNews24 [^>]*errore=\{errore\}/);
  const pagina = senzaCommenti(componenti.find(({ nome }) => nome === "PaginaEduNews24.jsx").testo);
  assert.match(pagina, /errore=\{pagina\.errorePrimaPagina\?\.azione === "riprova"\}/);
  assert.match(pagina, /spenta=\{spenta\}/);
});

test("categorie: dopo un errore un solo nuovo tentativo a ogni occasione, mai in ciclo", () => {
  const categorie = senzaCommenti(hook.find(({ nome }) => nome === "useCategorieEduNews24.js").testo);
  // L'errore torna "attesa" solo quando cambia l'occasione; la richiesta
  // dipende solo da daCaricare, quindi un'occasione nuova durante un volo non
  // lo interrompe.
  assert.match(categorie,
    /if \(occasione !== occasioneVista\) \{\s*setOccasioneVista\(occasione\);\s*if \(esito\.stato === "errore"\) setEsito\(ATTESA\);\s*\}/);
  assert.match(categorie, /const daCaricare = attivo && esito\.stato === "attesa";/);
  assert.match(categorie, /\}, \[daCaricare\]\);/);
  const pagina = senzaCommenti(componenti.find(({ nome }) => nome === "PaginaEduNews24.jsx").testo);
  assert.match(pagina, /useCategorieEduNews24\(sezione === "notizie" && accesa, pagina\.primaCaricata \? chiave : null\)/);
});

test("folio del modulo: dopo un caricamento fallito lo stesso resoconto della pagina", () => {
  const modulo = senzaCommenti(componenti.find(({ nome }) => nome === "ModuloEduNews24.jsx").testo);
  assert.match(modulo, /<FolioEduNews24 [^>]*errore=\{modulo\.stato === "errore"\}/);
});
