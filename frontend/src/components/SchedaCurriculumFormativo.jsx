import { useState } from "react";
import SezioneTitoli from "./SezioneTitoli";
import ImmatricolazioniIscrizioni from "./ImmatricolazioniIscrizioni";
import AbilitazioniProfessionali from "./AbilitazioniProfessionali";
import Invalidita from "./Invalidita";

export default function SchedaCurriculumFormativo({ formData, handleChange }) {
  const [activeTab, setActiveTab] = useState("titoli");

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
    <div className="w-full">
      {/* Container della barra delle tab interne */}
      <div className="flex items-end space-x-2 border-b border-bordo px-2 pt-2">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              type="button"
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`relative px-5 py-3 text-sm font-medium transition-all duration-200 rounded-t-superficie focus:outline-none cursor-pointer ${
                isActive
                  ? "bg-superficie text-primario shadow-sm border-t border-x border-bordo z-10 -mb-[1px]"
                  : "bg-superficie-tenue text-testo-tenue hover:bg-superficie-alta hover:text-testo-forte border-t border-x border-transparent"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Contenuto del form attivo (senza pulsante di salvataggio interno) */}
      <div className="bg-superficie border-x border-b border-bordo rounded-b-superficie p-6 shadow-sm">
        {tabs.find((tab) => tab.id === activeTab)?.component}
      </div>
    </div>
  );
}
