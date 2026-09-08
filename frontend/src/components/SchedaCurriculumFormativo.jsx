import { useState } from "react";
import SezioneTitoli from "./SezioneTitoli";
import ImmatricolazioniIscrizioni from "./ImmatricolazioniIscrizioni";
import AbilitazioniProfessionali from "./AbilitazioniProfessionali";
import Invalidita from "./Invalidita";

export default function FormContainer() {
  const [activeTab, setActiveTab] = useState("titoli");

  // Stato globale che rispecchia esattamente lo schema Pydantic di FastAPI
  const [formData, setFormData] = useState({
    universita_immatricolato: "",
    universita_data_immatricolazione: "",
    universita_riforma: "",
    universita_conclusione: "",
    universita_data_conclusione: "",
    universita_iscrizioneAltraUniversita: "",
    universita_diploma: "",
    universita_istituto: "",
    universita_via_istituto: "",
    universita_citta_istituto: "",
    universita_provincia_istituto: "",
    universita_anno_scolastico: "",
    universita_votoRicevuto_diploma: "",
    universita_votoMassimo_diploma: "",
    universita_istituto_ai: "",
    universita_citta_istituto_ai: "",
    universita_provincia_istituto_ai: "",
    universita_via_istituto_ai: "",
    universita_anno_scolastico_ai: "",
    universita_votoRicevuto_ai: "",
    universita_votoMassimo_ai: "",
    universita_titolo_universitario: "",
    universita_materia_titolo: "",
    universita_universita_titolo: "",
    universita_data_titolo: "",
    universita_votoRicevuto_titolo: "",
    universita_votoMassimo_titolo: "",
    universita_materia_pl1: "",
    universita_istituto_pl1: "",
    universita_data_pl1: "",
    universita_materia_pl2: "",
    universita_istituto_pl2: "",
    universita_data_pl2: "",
    universita_materia_ats1: "",
    universita_istituto_ats1: "",
    universita_data_ats1: "",
    universita_materia_ats2: "",
    universita_istituto_ats2: "",
    universita_data_ats2: "",
    universita_attivita_professionalizzanti: false,
    universita_corsi_di_formazione: false,
    universita_altre_attivita_certificate: false,
    cliente_id: "1",
    universita_ateneoNullaosta: "",
    universita_percentualeInvalidita: "",
    universita_tipoInvalidita: "",
    universita_professione: "",
    universita_data_professione: "",
    universita_luogo_professione: "",
    universita_sessione_professione: "",
    universita_annoSessione_professione: "",
    universita_voto_professione: "",
    universita_qualifica_professionale: "",
    universita_data_qualifica: "",
    universita_luogo: "",
    universita_corrispondenza: "",
    universita_albo: "",
    universita_forzeDellOrdine: "",
    universita_universitaConclusione: "",
    universita_cittaUniConclusione: "",
    universita_provinciaConclusione: "",
    universita_attIscritto_tipo: "",
    universita_attIscritto_altro: "",
    universita_attIscritto_classeLaurea: "",
    universita_attIscritto_denominazione: "",
    universita_attIscritto_universita: "",
    universita_attIscritto_citta: "",
    universita_attIscritto_provincia: "",
    universita_attIscritto_annoIscrizione: "",
    universita_attIscritto_modalita: "",
  });

  // Funzione generica per gestire i cambiamenti in qualsiasi input
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    let finalValue = type === "checkbox" ? checked : value;

    // Lista di tutti i campi che nel backend sono booleani
    const booleanFields = [
      "universita_immatricolato",
      "universita_attivita_professionalizzanti",
      "universita_corsi_di_formazione",
      "universita_altre_attivita_certificate",
    ];

    if (booleanFields.includes(name)) {
      if (value === "true" || value === true || value === "1" || value === -1) {
        finalValue = true;
      } else if (
        value === "false" ||
        value === false ||
        value === "0" ||
        value === 0
      ) {
        finalValue = false;
      } else {
        finalValue = Boolean(finalValue);
      }
    }

    setFormData((prev) => ({
      ...prev,
      [name]: finalValue,
    }));
  };

  // Funzione di Invio POST verso FastAPI
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Pulisce i campi vuoti e forza i booleani a true/false effettivi
    const cleanedData = Object.fromEntries(
      Object.entries(formData)
        .filter(([key]) => {
          // Escludi esplicitamente i campi gestiti dal database
          const autoFields = [
            "universita_createDate",
            "universita_updateDate",
            "utente_ultimo_login",
          ];
          return !autoFields.includes(key);
        })
        .map(([key, value]) => {
          const booleanFields = [
            "universita_immatricolato",
            "universita_attivita_professionalizzanti",
            "universita_corsi_di_formazione",
            "universita_altre_attivita_certificate",
            "universita_iscrizioneAltraUniversita",
          ];

          if (booleanFields.includes(key)) {
            return [key, Boolean(value && value !== "-1" && value !== -1)];
          }

          return [key, value === "" ? null : value];
        }),
    );

    try {
      const response = await fetch("http://localhost:8000/universita/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(cleanedData),
      });

      if (response.ok) {
        const result = await response.json();
        alert("Dati salvati con successo!");
        console.log("Risposta:", result);
      } else {
        const errorData = await response.json();
        alert(
          "Errore durante il salvataggio: " +
            JSON.stringify(errorData.detail || errorData),
        );
      }
    } catch (error) {
      console.error("Errore di rete:", error);
      alert("Impossibile connettersi al server.");
    }
  };

  // Mappatura delle tab passando formData e handleChange come props
  const tabs = [
    {
      id: "titoli",
      label: "Sezione Titoli",
      component: (
        <SezioneTitoli formData={formData} handleChange={handleChange} />
      ),
    },
    {
      id: "immatricolazioni",
      label: "Immatricolazioni ed Iscrizioni",
      component: (
        <ImmatricolazioniIscrizioni
          formData={formData}
          handleChange={handleChange}
        />
      ),
    },
    {
      id: "abilitazioni",
      label: "Abilitazioni Professionali",
      component: (
        <AbilitazioniProfessionali
          formData={formData}
          handleChange={handleChange}
        />
      ),
    },
    {
      id: "invalidita",
      label: "Invalidità",
      component: <Invalidita formData={formData} handleChange={handleChange} />,
    },
  ];

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-6xl mx-auto p-4">
      {/* Container della barra delle tab */}
      <div className="flex items-end space-x-2 border-b border-gray-200 px-2 pt-2">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              type="button"
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`relative px-5 py-3 text-sm font-medium transition-all duration-200 rounded-t-xl focus:outline-none ${
                isActive
                  ? "bg-white text-blue-600 shadow-sm border-t border-x border-gray-200 z-10 -mb-[1px]"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900 border-t border-x border-transparent"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Contenuto del form attivo */}
      <div className="bg-white border-x border-b border-gray-200 rounded-b-xl p-6 shadow-sm">
        {tabs.find((tab) => tab.id === activeTab)?.component}

        {/* Pulsante di invio globale */}
        <div className="mt-8 pt-4 border-t border-gray-100 flex justify-end">
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2.5 rounded-lg shadow transition-colors"
          >
            Salva
          </button>
        </div>
      </div>
    </form>
  );
}
