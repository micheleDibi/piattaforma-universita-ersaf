export const LIMITE_PRATICHE = 40;
export function queryPratiche({
  ricerca,
  numeroPratica,
  stato,
  studenti,
  universita,
  tipoCorso,
  tipoSelezionato,
}) {
  const query = new URLSearchParams({ limit: LIMITE_PRATICHE });
  if (ricerca.trim()) query.set("search", ricerca.trim());
  if (numeroPratica.trim()) query.set("numero_pratica", numeroPratica.trim());
  if (stato) query.set("pratica_stato_id", stato);
  studenti.forEach(({ id }) => query.append("studenti", id));
  if (universita) query.set("nome_universita_id", universita);
  const tipiDaUsare = tipoSelezionato ? [tipoSelezionato] : tipoCorso;
  tipiDaUsare.forEach((idTipo) =>
    query.append("listino_tipo_corso_id", idTipo),
  );
  return `/pratiche/?${query}`;
}

export function paginaPratiche(dati) {
  return { elementi: dati, altri: dati.length === LIMITE_PRATICHE };
}
