/** Contratto URL del frontend. Le API hanno un catalogo separato. */
export const ROTTE = Object.freeze({
  accesso: "/", recuperoPassword: "/password-dimenticata",
  reimpostaPassword: "/reimposta-password", dashboard: "/dashboard", profilo: "/profilo",
  sottoscrittori: "/sottoscrittori", attuatori: "/attuatori", aziende: "/aziende",
  pratiche: "/pratiche", prodotti: "/prodotti",
});
export const ROTTA_INIZIALE = ROTTE.sottoscrittori;

export function idValido(id) {
  return /^[1-9]\d*$/.test(String(id)) && Number.isSafeInteger(Number(id));
}

function risorsa(elenco, parametro, nuovo) {
  return Object.freeze({
    elenco, parametro, nuovo: `${elenco}/${nuovo}`, modello: `${elenco}/:${parametro}`,
    dettaglio(id) {
      if (!idValido(id)) throw new TypeError("Identificativo non valido");
      return `${elenco}/${id}`;
    },
  });
}

export const PERCORSI = Object.freeze({
  sottoscrittori: risorsa(ROTTE.sottoscrittori, "clienteId", "nuovo"),
  attuatori: risorsa(ROTTE.attuatori, "clienteId", "nuovo"),
  aziende: risorsa(ROTTE.aziende, "aziendaId", "nuova"),
  prodotti: risorsa(ROTTE.prodotti, "prodottoId", "nuovo"),
  pratiche: risorsa(ROTTE.pratiche, "praticaId", "nuova"),
});
