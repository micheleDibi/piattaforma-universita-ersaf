export const LIMITE_PRATICHE = 40;
export function queryPratiche({ ricerca, stato, studenti, percorso }) {
  const query = new URLSearchParams({ limit: LIMITE_PRATICHE });
  if (ricerca.trim()) query.set("search", ricerca.trim());
  if (stato) query.set("pratica_stato_id", stato);
  if (percorso) query.set("percorso_id", percorso.id);
  studenti.forEach(({ id }) => query.append("studenti", id));
  return `/pratiche/?${query}`;
}

export function paginaPratiche(dati) {
  return { elementi: dati, altri: dati.length === LIMITE_PRATICHE };
}
