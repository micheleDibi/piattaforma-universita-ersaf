import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { BLOCCHI_PRATICHE } from "../lib/configPratiche";

export default function PannelloPratiche() {
  const navigate = useNavigate();
  const [permessi, setPermessi] = useState(null);
  const [errore, setErrore] = useState(null);

  useEffect(() => {
    let attivo = true;
    apiFetch("/clienti/permessi-pratiche")
      .then(async (risposta) => {
        if (!attivo) return;
        if (!risposta.ok) {
          setErrore(
            await messaggioErrore(
              risposta,
              "Errore nel caricamento dei permessi",
            ),
          );
          return;
        }
        setPermessi(await leggiJson(risposta));
      })
      .catch(
        (err) =>
          attivo &&
          setErrore(err.message ?? "Errore nel caricamento dei permessi"),
      );
    return () => {
      attivo = false;
    };
  }, []);

  // resto del componente invariato

  function bloccoAttivo(blocco) {
    return permessi.abilPraticheUniv && permessi[blocco.flagPermesso];
  }

  function selezionaPulsante(blocco, pulsante) {
    if (pulsante.semprebloccato) return;

    if (pulsante.tipo === "prevalutazione") {
      navigate(`/prevalutazioni?universita=${blocco.nomeUniversitaId}`);
      return;
    }

    const params = new URLSearchParams();
    params.set("universita", blocco.nomeUniversitaId);
    pulsante.listinoTipoCorsoIds.forEach((idTipo) =>
      params.append("tipoCorso", idTipo),
    );
    if (pulsante.haFiltroInterno) params.set("filtroInterno", "1");
    navigate(`/pratiche?${params.toString()}`);
  }

  if (errore) {
    return <div className="p-4 text-red-600">{errore}</div>;
  }

  if (!permessi) {
    return <div className="p-4 text-gray-500">Caricamento permessi...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-10">
      {!permessi.abilPraticheUniv && (
        <div className="rounded-md bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-2 text-sm">
          Non hai l'abilitazione generale alle pratiche universitarie.
        </div>
      )}

      {BLOCCHI_PRATICHE.map((blocco) => {
        const abilitato = bloccoAttivo(blocco);
        return (
          <section
            key={blocco.chiave}
            className="border-t pt-4 first:border-t-0 first:pt-0"
          >
            <h2 className="text-blue-700 font-semibold mb-3">
              {blocco.titolo}
            </h2>
            <div className="flex gap-6 items-center">
              <img
                src={blocco.logo}
                alt={blocco.titolo}
                className="w-24 h-24 object-contain shrink-0"
              />
              <div className="grid grid-cols-3 gap-3 flex-1">
                {blocco.pulsanti.map((pulsante) => {
                  const disabilitato = !abilitato || pulsante.semprebloccato;
                  return (
                    <button
                      key={pulsante.chiave}
                      type="button"
                      disabled={disabilitato}
                      onClick={() => selezionaPulsante(blocco, pulsante)}
                      className={`rounded-md px-4 py-3 text-sm font-medium text-center transition-colors ${
                        disabilitato
                          ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                          : "bg-gray-100 text-gray-800 hover:bg-blue-50 hover:text-blue-700 cursor-pointer"
                      }`}
                    >
                      {pulsante.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>
        );
      })}
    </div>
  );
}
