import { etichetta as classiEtichetta } from "../../config/styles/campo";

// Classi statiche perche' Tailwind non vede quelle composte a runtime.
const SPAN = {
  1: "col-span-6 sm:col-span-1",
  2: "col-span-6 sm:col-span-2",
  3: "col-span-6 sm:col-span-3",
  4: "col-span-6 sm:col-span-4",
  5: "col-span-6 sm:col-span-5",
  6: "col-span-6",
};

/**
 * Etichetta e controllo di un campo nella griglia di 6 colonne di
 * SezioneModulo. Il controllo arriva come figlio e resta quello nativo.
 */
export default function CampoModulo({
  etichetta,
  per,
  obbligatorio = false,
  colonne = 3,
  children,
}) {
  return (
    <div className={`flex min-w-0 flex-col ${SPAN[colonne]}`}>
      <label htmlFor={per} className={classiEtichetta()}>
        {etichetta}
        {obbligatorio && <span className="text-negativo"> *</span>}
      </label>
      {children}
    </div>
  );
}
