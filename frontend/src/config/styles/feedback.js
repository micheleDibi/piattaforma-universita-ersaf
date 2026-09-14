const VARIANTI = {
  error: "bg-negativo-tenue border-negativo-bordo text-negativo-forte",
  success: "bg-positivo-tenue border-positivo-bordo text-positivo-forte",
  warning: "bg-attenzione-tenue border-attenzione-bordo text-attenzione-forte",
  info: "bg-informazione-tenue border-informazione-bordo text-informazione-forte",
};

export function feedback(tipo, { separato = true } = {}) {
  return ["movimento-feedback flex items-start gap-3 rounded-controllo border p-4 text-sm leading-relaxed whitespace-pre-wrap", VARIANTI[tipo] ?? VARIANTI.error, separato ? "mb-6" : ""].filter(Boolean).join(" ");
}

export const STILI_FEEDBACK = {
  icona: "mt-0.5 size-icona-piccola shrink-0",
  testo: "min-w-0 break-words",
};
