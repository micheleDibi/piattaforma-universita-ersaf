import { useState } from "react";
import SezioneTitoli from "./SezioneTitoli";
import ImmatricolazioniIscrizioni from "./ImmatricolazioniIscrizioni";
import AbilitazioniProfessionali from "./AbilitazioniProfessionali";
import Invalidita from "./Invalidita";
import BarraSchede from "./shared/BarraSchede.jsx";
import { useIngresso } from "../hooks/useIngresso.js";

export default function SchedaCurriculumFormativo({ formData, handleChange }) {
  const [activeTab, setActiveTab] = useState("titoli");
  const pannello = useIngresso(activeTab);

  const tabs = [
    {
      id: "titoli",
      label: "Titoli",
      component: (
        <SezioneTitoli formData={formData} handleChange={handleChange} />
      ),
    },
    {
      id: "immatricolazioni",
      label: "Immatricolazioni ed iscrizioni",
      component: (
        <ImmatricolazioniIscrizioni
          formData={formData}
          handleChange={handleChange}
        />
      ),
    },
    {
      id: "abilitazioni",
      label: "Abilitazioni professionali",
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
    <div className="schede w-full">
      <BarraSchede id="curriculum" etichetta="Curriculum formativo" schede={tabs}
        attiva={activeTab} onChange={setActiveTab} />
      <div ref={pannello} role="tabpanel" id={`curriculum-pannello-${activeTab}`}
        aria-labelledby={`curriculum-scheda-${activeTab}`}
        className="movimento-scheda schede__pannello schede__pannello--sezioni border-x border-b border-bordo rounded-b-superficie">
        {tabs.find((tab) => tab.id === activeTab)?.component}
      </div>
    </div>
  );
}
