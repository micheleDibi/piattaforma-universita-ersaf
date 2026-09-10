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
      <div className="flex items-end space-x-2 border-b border-gray-200 px-2 pt-2">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              type="button"
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`relative px-5 py-3 text-sm font-medium transition-all duration-200 rounded-t-xl focus:outline-none cursor-pointer ${
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

      {/* Contenuto del form attivo (senza pulsante di salvataggio interno) */}
      <div className="bg-white border-x border-b border-gray-200 rounded-b-xl p-6 shadow-sm">
        {tabs.find((tab) => tab.id === activeTab)?.component}
      </div>
    </div>
  );
}
