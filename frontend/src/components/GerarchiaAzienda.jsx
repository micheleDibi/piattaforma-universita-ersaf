import { useEffect, useState } from "react";
import { apiFetch, messaggioErrore } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";
import { pulsante } from "../config/styles/pulsante";
import { etichetta as classiEtichetta } from "../config/styles/campo";
import ModalCambiaPadreAzienda from "./ModalCambiaPadreAzienda.jsx";
import AlertMessage from "./AlertMessage.jsx";

export default function GerarchiaAzienda({ aziendaId }) {
  // undefined = in caricamento, null = nessun padre (azienda radice)
  const [padre, setPadre] = useState(undefined);
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  const [messaggioSalvataggio, setMessaggioSalvataggio] = useState("");
  const [modaleAperta, setModaleAperta] = useState(false);
  // undefined = nessuna conferma in sospeso. Puo' contenere null (valore
  // valido: "rendi radice") o un oggetto azienda selezionata dal modale.
  const [azionePendente, setAzionePendente] = useState(undefined);

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
  const cambiaPadre = async (aziendaSelezionata, conferma = false) => {
    setModaleAperta(false);
    setSalvataggio(true);
    setMessaggioSalvataggio("");
    try {
      const query = conferma ? "?conferma_reset=true" : "";
      const risposta = await apiFetch(
        `/aziende-xcod/${aziendaId}/padre${query}`,
        {
          method: "PUT",
          body: JSON.stringify({
            nuovo_padre_id: aziendaSelezionata
              ? aziendaSelezionata.azienda_id
              : null,
          }),
        },
      );

      if (risposta.status === 409) {
        setAzionePendente(aziendaSelezionata ?? null);
        return;
      }

      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      setAzionePendente(undefined);
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

      {azionePendente !== undefined && (
        <div className="mt-3 flex items-center justify-between gap-4 rounded-controllo border border-bordo p-3">
          <AlertMessage
            message={{
              type: "warning",
              text: "Alcune percentuali verranno azzerate. Continuare?",
            }}
            separato={false}
          />
          <div className="flex shrink-0 gap-3">
            <button
              type="button"
              onClick={() => cambiaPadre(azionePendente, true)}
              disabled={salvataggio}
              className={pulsante("primario", "piccolo")}
            >
              Conferma
            </button>
            <button
              type="button"
              onClick={() => setAzionePendente(undefined)}
              className={pulsante("discreto", "piccolo")}
            >
              Annulla
            </button>
          </div>
        </div>
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
