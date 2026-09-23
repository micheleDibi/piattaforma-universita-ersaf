import { useState } from "react";
import { campo } from "../config/styles/campo";
import { pulsante, pulsanteIcona } from "../config/styles/pulsante";
import { Plus, Trash2 } from "../config/icone.js";
import {
  cellaAzioni,
  cellaIntestazione,
  contenitoreTabella,
  intestazioneTabella,
  rigaTabella,
} from "../config/styles/tabella";

export default function ProdottoDettagliTabella({
  dettagli,
  handleDettaglioChange,
  handleDettaglioBlur,
  handleAggiungiRiga,
  handleRimuoviRiga,
  isModifica,
}) {
  const haRigaNuova = dettagli.some((det) => det.isNew);

  // Tiene traccia del testo "grezzo" che l'utente sta digitando per i campi decimali,
  // finché il campo ha il focus. Chiave: "index-nomeCampo".
  const [editingField, setEditingField] = useState({});

  const getKey = (index, field) => `${index}-${field}`;

  // Filtra l'input: solo cifre + UN separatore decimale (virgola o punto), max 2 decimali.
  const filtraNumeroDecimale = (valore) => {
    valore = valore.replace(/[^0-9.,]/g, "");
    const primoSeparatore = valore.search(/[.,]/);
    if (primoSeparatore !== -1) {
      const parteIniziale = valore.slice(0, primoSeparatore + 1); // include il separatore
      const parteDecimale = valore
        .slice(primoSeparatore + 1)
        .replace(/[.,]/g, "") // scarta eventuali separatori ripetuti
        .slice(0, 2); // massimo 2 cifre decimali durante la digitazione
      valore = parteIniziale + parteDecimale;
    }
    return valore;
  };

  const handleValoreDecimaleFocus = (index, field, valoreCorrente) => {
    // All'ingresso nel campo, parto dal valore mostrato (formattato a 2 decimali)
    // così l'utente può cancellare/modificare liberamente da lì.
    let valoreIniziale = "";
    if (
      valoreCorrente !== "" &&
      valoreCorrente !== null &&
      valoreCorrente !== undefined
    ) {
      const numero = Number(String(valoreCorrente).replace(",", "."));
      valoreIniziale = !isNaN(numero)
        ? numero.toFixed(2).replace(".", ",")
        : String(valoreCorrente);
    }
    setEditingField((prev) => ({
      ...prev,
      [getKey(index, field)]: valoreIniziale,
    }));
  };

  const handleValoreDecimaleChange = (index, field, e) => {
    const valoreFiltrato = filtraNumeroDecimale(e.target.value);
    setEditingField((prev) => ({
      ...prev,
      [getKey(index, field)]: valoreFiltrato,
    }));
    handleDettaglioChange(index, {
      target: { name: field, value: valoreFiltrato },
    });
  };

  const handleValoreDecimaleBlur = (index, field, e) => {
    setEditingField((prev) => {
      const copia = { ...prev };
      delete copia[getKey(index, field)];
      return copia;
    });
    handleDettaglioBlur(index, e);
  };

  // Cosa mostrare nell'input: se sto editando quel campo, il testo grezzo;
  // altrimenti il valore salvato, formattato a 2 decimali con la virgola.
  // Gestisce sia number che string (es. "30.30000000" arrivato da Decimal via Pydantic).
  const formattaValoreVisualizzato = (index, field, valore) => {
    const key = getKey(index, field);
    if (editingField[key] !== undefined) return editingField[key];

    if (valore === "" || valore === null || valore === undefined) return "";

    const numero = Number(String(valore).replace(",", "."));
    if (!isNaN(numero)) return numero.toFixed(2).replace(".", ",");

    return String(valore);
  };

  return (
    <div className="pt-6 border-t border-divisore">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-titolo-sezione text-testo">Dettaglio prodotto</h3>
        {isModifica && (
          <button
            type="button"
            onClick={handleAggiungiRiga}
            disabled={haRigaNuova}
            className={`${pulsante("ausiliario", "piccolo")} disabled:cursor-not-allowed`}
          >
            <Plus aria-hidden="true" className="size-icona-piccola" />
            Aggiungi nuova riga
          </button>
        )}
      </div>

      <div className={contenitoreTabella()}>
        <table className="w-full text-left text-sm text-testo">
          <thead className={intestazioneTabella()}>
            <tr>
              <th className={cellaIntestazione()}>Inizio Validità</th>
              <th className={cellaIntestazione()}>Fine Validità</th>
              <th className={cellaIntestazione()}>Prezzo (€)</th>
              <th className={cellaIntestazione()}>Durata (mesi)</th>
              <th className={cellaIntestazione()}>CFU</th>
              <th className={cellaIntestazione()}>Tasse (€)</th>
              <th className={cellaIntestazione("destra")}>Azioni</th>
            </tr>
          </thead>
          <tbody>
            {dettagli.map((det, index) => (
              <tr
                key={index}
                className={rigaTabella()}
              >
                <td className="p-2">
                  <input
                    type="date"
                    name="listDettaglio_dataInizioValidazione"
                    value={det.listDettaglio_dataInizioValidazione ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className={campo("minimo")}
                  />
                </td>
                <td className="p-2">
                  <input
                    type="date"
                    name="listDettaglio_dataFineValidazionoe"
                    value={det.listDettaglio_dataFineValidazionoe ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className={campo("minimo")}
                  />
                </td>
                <td className="p-2">
                  <input
                    type="text"
                    inputMode="decimal"
                    name="listDettaglio_prezzo"
                    placeholder="0,00"
                    value={formattaValoreVisualizzato(
                      index,
                      "listDettaglio_prezzo",
                      det.listDettaglio_prezzo,
                    )}
                    onFocus={() =>
                      handleValoreDecimaleFocus(
                        index,
                        "listDettaglio_prezzo",
                        det.listDettaglio_prezzo,
                      )
                    }
                    onChange={(e) =>
                      handleValoreDecimaleChange(
                        index,
                        "listDettaglio_prezzo",
                        e,
                      )
                    }
                    onBlur={(e) =>
                      handleValoreDecimaleBlur(index, "listDettaglio_prezzo", e)
                    }
                    className={campo("minimo")}
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    name="listDettaglio_durata"
                    placeholder="Mesi"
                    value={det.listDettaglio_durata ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className={campo("minimo")}
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    name="listDettaglio_CFU"
                    placeholder="CFU"
                    value={det.listDettaglio_CFU ?? ""}
                    onChange={(e) => handleDettaglioChange(index, e)}
                    className={campo("minimo")}
                  />
                </td>
                <td className="p-2">
                  <input
                    type="text"
                    inputMode="decimal"
                    name="listDettaglio_tasse"
                    placeholder="0,00"
                    value={formattaValoreVisualizzato(
                      index,
                      "listDettaglio_tasse",
                      det.listDettaglio_tasse,
                    )}
                    onFocus={() =>
                      handleValoreDecimaleFocus(
                        index,
                        "listDettaglio_tasse",
                        det.listDettaglio_tasse,
                      )
                    }
                    onChange={(e) =>
                      handleValoreDecimaleChange(
                        index,
                        "listDettaglio_tasse",
                        e,
                      )
                    }
                    onBlur={(e) =>
                      handleValoreDecimaleBlur(index, "listDettaglio_tasse", e)
                    }
                    className={campo("minimo")}
                  />
                </td>
                <td className={cellaAzioni()}>
                  {det.isNew && (
                    <button
                      type="button"
                      onClick={() => handleRimuoviRiga(index)}
                      className={pulsanteIcona("pericolo")}
                      aria-label="Rimuovi riga"
                      title="Rimuovi riga"
                    >
                      <Trash2 aria-hidden="true" className="size-icona-piccola" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
