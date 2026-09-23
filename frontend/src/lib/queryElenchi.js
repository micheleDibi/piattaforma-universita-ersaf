const LIMITE = 40;
export const paginaElenco = dati => ({ elementi: dati, altri: dati.length === LIMITE });
export function queryClienti({ ricerca, ruolo }, { soloAttuatori, soloSottoscrittori }) {
  const params = new URLSearchParams({ limit: LIMITE, search: ricerca });
  if (soloAttuatori) params.set("solo_attuatori", "true");
  if (soloSottoscrittori) params.set("solo_sottoscrittori", "true");
  if (soloAttuatori && ruolo) params.set("ruolo_codice", ruolo);
  return `/clienti/?${params}`;
}
/** Stessi filtri di queryClienti, senza paginazione: per il totale dei risultati. */
export function conteggioClienti({ ricerca, ruolo }, { soloAttuatori, soloSottoscrittori }) {
  const params = new URLSearchParams({ search: ricerca });
  if (soloAttuatori) params.set("solo_attuatori", "true");
  if (soloSottoscrittori) params.set("solo_sottoscrittori", "true");
  if (soloAttuatori && ruolo) params.set("ruolo_codice", ruolo);
  return `/clienti/conteggio?${params}`;
}
export function queryAziende({ ricerca }) {
  return `/aziende/?${new URLSearchParams({ limit: LIMITE, search: ricerca })}`;
}
export function queryProdotti({ ricerca, universita, tipo, attivo }) {
  const params = new URLSearchParams({ limit: LIMITE });
  if (ricerca.trim()) params.set("search", ricerca.trim());
  if (universita !== "Tutte le università") params.set("universita", universita);
  if (tipo !== "Tutti i tipi") params.set("tipo_corso", tipo);
  if (attivo !== "Tutti") params.set("attivo", attivo === "Sì" ? -1 : 0);
  return `/listini-testa/?${params}`;
}
