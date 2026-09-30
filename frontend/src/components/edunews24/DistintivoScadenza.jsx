import { AlarmClock, CalendarCheck, CalendarX } from "../../config/icone.js";

const ICONE = { attenzione: AlarmClock, aperto: CalendarCheck, neutro: CalendarX };

/**
 * Distintivo di stato della selezione del personale (statoOpportunita):
 * testo, icona e tono, mai il solo colore. Senza stato (interpelli, stati
 * "altro" o sconosciuti) non compare.
 */
export default function DistintivoScadenza({ stato }) {
  if (!stato) return null;
  const tono = ICONE[stato.tono] ? stato.tono : "neutro";
  const Icona = ICONE[tono];
  return (
    <span className="edunews24-distintivo" data-tono={tono} data-chiave={stato.chiave}>
      <Icona aria-hidden="true" className="edunews24-distintivo__icona" />
      {stato.testo}
    </span>
  );
}
