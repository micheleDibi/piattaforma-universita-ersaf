// Stampa in JSON le rotte registrate in frontend/src/App.jsx e le voci di menu.
//
// Uso: node rotte_frontend.mjs <cartella frontend>
//
// I percorsi si leggono importando i moduli di configurazione; App.jsx contiene
// JSX e si legge come albero sintattico con @babel/core, gia' dipendenza del
// frontend. Una forma che lo script non riconosce e' un errore: meglio fermarsi
// che produrre un elenco sbagliato.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const argomento = process.argv[2];
if (!argomento) {
  console.error("uso: node rotte_frontend.mjs <cartella frontend>");
  process.exit(2);
}
const frontend = resolve(argomento);

const richiedi = createRequire(join(frontend, "package.json"));
const babel = richiedi("@babel/core");
const importa = (relativo) => import(pathToFileURL(join(frontend, relativo)).href);
const { ROTTE, PERCORSI } = await importa("src/config/routes/percorsi.js");
const { VOCI_MENU } = await importa("src/config/routes/rotte.js");
const valori = { ROTTE, PERCORSI };

const WRAPPER = { SoloOspiti: "solo ospiti", RichiediSessione: "sessione" };
const CONTENITORI = new Set(["GuscioApplicazione", "PaginaEntita"]);

class FormaNonRiconosciuta extends Error {}

function errore(nodo, messaggio) {
  const riga = nodo?.loc?.start?.line ?? "?";
  return new FormaNonRiconosciuta(`App.jsx:${riga}: ${messaggio}`);
}

function nomeElemento(elemento) {
  const nome = elemento.openingElement.name;
  if (nome.type !== "JSXIdentifier") throw errore(elemento, "nome di elemento non previsto");
  return nome.name;
}

function attributi(elemento) {
  const risultato = {};
  for (const attributo of elemento.openingElement.attributes) {
    if (attributo.type !== "JSXAttribute") throw errore(elemento, "attributo non previsto");
    risultato[attributo.name.name] = attributo.value;
  }
  return risultato;
}

function figliSignificativi(elemento) {
  return elemento.children.filter((figlio) => {
    if (figlio.type === "JSXText") return figlio.value.trim() !== "";
    if (figlio.type === "JSXExpressionContainer") return figlio.expression.type !== "JSXEmptyExpression";
    return true;
  });
}

// Valuta ROTTE.x, PERCORSI.x.nuovo e simili sui moduli importati.
function valuta(espressione, ambito = {}) {
  if (espressione.type === "StringLiteral") return espressione.value;
  if (espressione.type === "Identifier") {
    if (espressione.name in ambito) return ambito[espressione.name];
    if (espressione.name in valori) return valori[espressione.name];
    throw errore(espressione, `identificatore sconosciuto: ${espressione.name}`);
  }
  if (espressione.type === "MemberExpression" && !espressione.computed) {
    const oggetto = valuta(espressione.object, ambito);
    const valore = oggetto?.[espressione.property.name];
    if (valore === undefined) throw errore(espressione, `proprieta' inesistente: ${espressione.property.name}`);
    return valore;
  }
  throw errore(espressione, `espressione non prevista: ${espressione.type}`);
}

function proprieta(elemento) {
  const risultato = {};
  for (const [nome, valore] of Object.entries(attributi(elemento))) {
    if (nome === "key") continue;
    if (valore?.type === "StringLiteral") risultato[nome] = valore.value;
    else if (valore?.type === "JSXExpressionContainer"
      && ["BooleanLiteral", "NumericLiteral", "StringLiteral"].includes(valore.expression.type)) {
      risultato[nome] = valore.expression.value;
    } else if (valore === null) risultato[nome] = true;
  }
  return risultato;
}

// Scende fra wrapper e contenitori fino alla pagina; restituisce anche l'accesso.
function pagina(elemento, accesso) {
  const nome = nomeElemento(elemento);
  if (nome in WRAPPER || CONTENITORI.has(nome)) {
    const figli = figliSignificativi(elemento);
    const nuovoAccesso = WRAPPER[nome] ?? accesso;
    if (figli.length === 0) return { pagina: null, accesso: nuovoAccesso };
    if (figli.length !== 1) throw errore(elemento, `${nome} con piu' figli`);
    const [figlio] = figli;
    if (figlio.type === "JSXElement") return pagina(figlio, nuovoAccesso);
    if (figlio.type === "JSXExpressionContainer" && figlio.expression.type === "Identifier") {
      return { pagina: { segnaposto: figlio.expression.name }, accesso: nuovoAccesso };
    }
    throw errore(figlio, `contenuto di ${nome} non previsto`);
  }
  return { pagina: { nome, proprieta: proprieta(elemento) }, accesso };
}

function elementoDi(valore, nodo) {
  if (valore?.type !== "JSXExpressionContainer" || valore.expression.type !== "JSXElement") {
    throw errore(nodo, "element deve essere un elemento JSX");
  }
  return valore.expression;
}

const rotte = [];

function registra(percorso, risultato, nodo) {
  if (typeof percorso !== "string") throw errore(nodo, "percorso non testuale");
  if (!risultato.pagina || risultato.pagina.segnaposto) throw errore(nodo, "pagina non risolta");
  rotte.push({ percorso, pagina: risultato.pagina.nome, proprieta: risultato.pagina.proprieta,
    accesso: risultato.accesso });
}

function visitaRoute(elemento, accesso) {
  if (nomeElemento(elemento) !== "Route") throw errore(elemento, "atteso <Route>");
  const attr = attributi(elemento);
  const risultato = pagina(elementoDi(attr.element, elemento), accesso);
  if (attr.path === undefined) {
    if (risultato.pagina) throw errore(elemento, "rotta di layout con una pagina");
    for (const figlio of figliSignificativi(elemento)) visitaFiglio(figlio, risultato.accesso);
    return;
  }
  if (attr.path.type !== "StringLiteral" && attr.path.type !== "JSXExpressionContainer") {
    throw errore(elemento, "path non previsto");
  }
  const percorso = valuta(attr.path.type === "StringLiteral" ? attr.path : attr.path.expression);
  registra(percorso, risultato, elemento);
}

// [[PERCORSI.x, <Pagina/>], ...].flatMap(([risorsa, pagina]) => [risorsa.a, risorsa.b].map(path => <Route .../>))
function visitaGenerate(espressione, accesso) {
  const chiamata = espressione;
  if (chiamata.type !== "CallExpression" || chiamata.callee.type !== "MemberExpression"
    || chiamata.callee.property.name !== "flatMap" || chiamata.callee.object.type !== "ArrayExpression") {
    throw errore(espressione, "espressione fra le rotte non prevista");
  }
  const [funzione] = chiamata.arguments;
  const [coppia] = funzione.params;
  if (coppia?.type !== "ArrayPattern" || coppia.elements.length !== 2) {
    throw errore(funzione, "la funzione di flatMap deve ricevere [risorsa, pagina]");
  }
  const [nomeRisorsa, nomePagina] = coppia.elements.map((e) => e.name);
  const corpo = funzione.body;
  if (corpo.type !== "CallExpression" || corpo.callee.property?.name !== "map"
    || corpo.callee.object.type !== "ArrayExpression") {
    throw errore(corpo, "atteso [..].map(...) dentro flatMap");
  }
  const chiavi = corpo.callee.object.elements.map((e) => {
    if (e.type !== "MemberExpression" || e.object.name !== nomeRisorsa) throw errore(e, "atteso risorsa.chiave");
    return e.property.name;
  });
  const interna = corpo.arguments[0];
  const [parametroPercorso] = interna.params;
  const route = interna.body;
  if (route.type !== "JSXElement" || nomeElemento(route) !== "Route") throw errore(route, "atteso <Route> nel map");
  const attr = attributi(route);
  if (attr.path?.expression?.name !== parametroPercorso.name) throw errore(route, "path non previsto nel map");
  for (const voce of chiamata.callee.object.elements) {
    if (voce.type !== "ArrayExpression" || voce.elements.length !== 2 || voce.elements[1].type !== "JSXElement") {
      throw errore(voce, "attesa la coppia [PERCORSI.x, <Pagina/>]");
    }
    const risorsa = valuta(voce.elements[0]);
    const risultato = pagina(elementoDi(attr.element, route), accesso);
    if (risultato.pagina?.segnaposto !== nomePagina) throw errore(route, "pagina non presa dalla coppia");
    const effettiva = pagina(voce.elements[1], risultato.accesso);
    for (const chiave of chiavi) registra(risorsa[chiave], effettiva, voce);
  }
}

function visitaFiglio(figlio, accesso) {
  if (figlio.type === "JSXElement") visitaRoute(figlio, accesso);
  else if (figlio.type === "JSXExpressionContainer") visitaGenerate(figlio.expression, accesso);
  else throw errore(figlio, `figlio non previsto: ${figlio.type}`);
}

function trovaRoutes(nodo) {
  if (!nodo || typeof nodo !== "object") return null;
  if (nodo.type === "JSXElement" && nodo.openingElement.name.name === "Routes") return nodo;
  for (const [chiave, valore] of Object.entries(nodo)) {
    if (chiave === "loc" || chiave === "start" || chiave === "end") continue;
    const trovato = Array.isArray(valore) ? valore.map(trovaRoutes).find(Boolean) : trovaRoutes(valore);
    if (trovato) return trovato;
  }
  return null;
}

try {
  const sorgente = readFileSync(join(frontend, "src/App.jsx"), "utf8");
  const albero = babel.parseSync(sorgente, {
    configFile: false, babelrc: false, sourceType: "module", filename: "App.jsx",
    parserOpts: { plugins: ["jsx"] },
  });
  const routes = trovaRoutes(albero.program);
  if (!routes) throw new FormaNonRiconosciuta("App.jsx: <Routes> non trovato");
  for (const figlio of figliSignificativi(routes)) visitaFiglio(figlio, "pubblica");
  const menu = VOCI_MENU.map((voce) => ({
    rotta: voce.rotta, etichetta: voce.etichetta, soloNazionale: Boolean(voce.soloNazionale),
  }));
  process.stdout.write(JSON.stringify({ rotte, menu }));
} catch (eccezione) {
  console.error(eccezione instanceof FormaNonRiconosciuta ? eccezione.message : eccezione.stack);
  process.exit(2);
}
