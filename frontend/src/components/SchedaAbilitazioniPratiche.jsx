const CAMPI_ABILITAZIONE = [
  {
    chiave: "cliente_abilPraticheUniv",
    etichetta: "Abilitazione generale pratiche universitarie",
  },
  {
    chiave: "cliente_abilitazione_ecampus",
    etichetta: "Università Telematica eCampus",
  },
  {
    chiave: "cliente_abilitazione_link_campus",
    etichetta: "Link Campus University",
  },
  {
    chiave: "cliente_abilitazione_corsi_speciali",
    etichetta: "SSML Lamezia Terme",
  },
  { chiave: "cliente_abilitazione_a4u", etichetta: "Avatar4University" },
];

export default function SchedaAbilitazioniPratiche({ formData, onCambia }) {
  return (
    <div className="space-y-4">
      {CAMPI_ABILITAZIONE.map(({ chiave, etichetta }) => {
        const attivo = formData[chiave] === -1;
        return (
          <div
            key={chiave}
            className="flex items-center justify-between rounded-md border border-bordo px-4 py-3"
          >
            <span className="text-sm font-medium">{etichetta}</span>
            <button
              type="button"
              role="switch"
              aria-checked={attivo}
              onClick={() => onCambia(chiave, attivo ? 0 : -1)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                attivo ? "bg-primario" : "bg-gray-300"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  attivo ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        );
      })}
    </div>
  );
}
