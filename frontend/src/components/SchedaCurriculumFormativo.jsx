import { useState } from "react";
import SezioneTitoli from "./SezioneTitoli";
import ImmatricolazioniIscrizioni from "./ImmatricolazioniIscrizioni";
import AbilitazioniProfessionali from "./AbilitazioniProfessionali";
import Invalidita from "./Invalidita";
import BarraSchede from "./shared/BarraSchede.jsx";
import { useIngresso } from "../hooks/useIngresso.js";
import { TESTI_CURRICULUM as testi } from "../config/testi/anagrafica.js";

const SOTTOSCHEDE = {
  titoli: SezioneTitoli,
  immatricolazioni: ImmatricolazioniIscrizioni,
  abilitazioni: AbilitazioniProfessionali,
  invalidita: Invalidita,
};

const SCHEDE = Object.keys(SOTTOSCHEDE).map((id) => ({ id, label: testi.schede[id] }));

/**
 * Curriculum: sotto-schede segmentate, poi le sezioni della sotto-scheda
 * direttamente sulla scheda che le contiene (nessun bordo proprio).
 */
export default function SchedaCurriculumFormativo({ formData, handleChange }) {
  const [activeTab, setActiveTab] = useState("titoli");
  const pannello = useIngresso(activeTab);
  const Sottoscheda = SOTTOSCHEDE[activeTab];

  return (
    <div className="schede w-full">
      <BarraSchede id="curriculum" etichetta={testi.etichetta} schede={SCHEDE}
        attiva={activeTab} onChange={setActiveTab} variante="segmentata" />
      <div ref={pannello} role="tabpanel" id={`curriculum-pannello-${activeTab}`}
        aria-labelledby={`curriculum-scheda-${activeTab}`}
        className="movimento-scheda schede__pannello schede__pannello--sezioni">
        <Sottoscheda formData={formData} handleChange={handleChange} />
      </div>
    </div>
  );
}
