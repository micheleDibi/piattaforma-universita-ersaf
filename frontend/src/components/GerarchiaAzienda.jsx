import { useEffect, useState } from "react";
import { apiFetch, messaggioErrore } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";
import { pulsante } from "../config/styles/pulsante";
import { etichetta as classiEtichetta } from "../config/styles/campo";
import ModalCambiaPadreAzienda from "./ModalCambiaPadreAzienda.jsx";

export default function GerarchiaAzienda({ aziendaId }) {
  // undefined = in caricamento, null = nessun padre (azienda radice)
  const [padre, setPadre] = useState(undefined);
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  const [messaggioSalvataggio, setMessaggioSalvataggio] = useState("");
  const [modaleAperta, setModaleAperta] = useState(false);

  const eNazionale = leggiRuolo() === "nazionale";

  const caricaPadre = () => {
    setErrore("");
    apiFetch(`/aziende-xcod/${aziendaId}/padre`)
      .then(async (risposta) => {
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
        return risposta.json();
      })
      .then(async (arco) => {
        if (!arco || arco.azienda_padre_id == null) {
          setPadre(null);
          return;
        }
        const rispostaAzienda = await apiFetch(
          `/aziende/${arco.azienda_padre_id}`,
        );
        setPadre(
          rispostaAzienda.ok
            ? await rispostaAzienda.json()
            : {
                azienda_id: arco.azienda_padre_id,
                azienda_ragione_sociale: null,
              },
        );
      })
      .catch((err) => setErrore(err.message));
  };

  useEffect(caricaPadre, [aziendaId]);

  // Niente <form>/onSubmit: questo componente vive dentro il <form> di
  // SchedaAzienda.jsx, e React non gestisce form annidati.
  const cambiaPadre = async (aziendaSelezionata) => {
    setModaleAperta(false);
    setSalvataggio(true);
    setMessaggioSalvataggio("");
    try {
      const risposta = await apiFetch(`/aziende-xcod/${aziendaId}/padre`, {
        method: "PUT",
        body: JSON.stringify({
          nuovo_padre_id: aziendaSelezionata
            ? aziendaSelezionata.azienda_id
            : null,
        }),
      });
      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      caricaPadre();
    } catch (err) {
      setMessaggioSalvataggio(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  if (errore) return <p className="text-sm text-negativo">Errore: {errore}</p>;

  return (
    <div className="mb-8 rounded-controllo border border-bordo p-4">
      <p className={classiEtichetta()}>AZIENDA PADRE</p>
      <div className="mt-1 flex items-center gap-3">
        <p>
          {padre === undefined && "Caricamento..."}
          {padre === null && "Nessuna (azienda radice)"}
          {padre &&
            (padre.azienda_ragione_sociale ?? `Azienda #${padre.azienda_id}`)}
        </p>

        {eNazionale && (
          <button
            type="button"
            onClick={() => setModaleAperta(true)}
            disabled={salvataggio}
            className={pulsante("ausiliario")}
          >
            {salvataggio ? "Salvataggio..." : "Cambia padre"}
          </button>
        )}
      </div>

      {messaggioSalvataggio && (
        <p className="mt-2 text-sm text-negativo">{messaggioSalvataggio}</p>
      )}

      <ModalCambiaPadreAzienda
        isOpen={modaleAperta}
        onClose={() => setModaleAperta(false)}
        onSelectPadre={cambiaPadre}
        aziendaIdEsclusa={Number(aziendaId)}
      />
    </div>
  );
}
