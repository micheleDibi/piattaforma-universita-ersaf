export function paginaOpzioni(dati) { return dati; }

export function cambiaSelezione(selezionati, opzione, multipla) {
  if (selezionati.some(({ id }) => id === opzione.id)) {
    return selezionati.filter(({ id }) => id !== opzione.id);
  }
  return multipla ? [...selezionati, opzione] : [opzione];
}
