import { leggiUtenteId } from "../lib/sessione";
import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import { apiFetch, messaggioErrore } from "../lib/api";
import AlertMessage from "./AlertMessage";
import ProdottoFormInfo from "./ProdottoFormInfo";
import ProdottoDettagliTabella from "./ProdottoDettagliTabella";
import IntestazionePagina from "./shared/IntestazionePagina";
import { ROTTE } from "../config/routes/rotte";
import { contenutoPagina } from "../config/styles/pagina";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";

// Converte una stringa numerica (con virgola o punto) in Number.
// Restituisce null se non è un numero valido.
const parseNumeroItaliano = (valore) => {
  if (valore === "" || valore === null || valore === undefined) return null;
  const normalizzato = String(valore).replace(",", ".");
  const num = Number(normalizzato);
  return isNaN(num) ? null : num;
};

export default function InserimentoProdotto() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isModifica = Boolean(id);

  const [formData, setFormData] = useState(() => ({
    listTesta_codice: "",
    listTesta_descrizione: "",
    listTesta_livello: "",
    listino_tipo_id: 2,
    listino_modalita_id: "",
    listino_tipoCorso_id: 8,
    listino_durataLaurea_id: "",
    listino_facolta_id: "",
    listino_corsoLaurea_id: "",
    nome_universita_id: "",
    listino_attivoSN: -1,
    listTesta_created_by: leggiUtenteId(),
  }));

  const [dettagli, setDettagli] = useState([
    {
      listDettaglio_dataInizioValidazione: new Date()
        .toISOString()
        .split("T")[0],
      listDettaglio_dataFineValidazionoe: "9999-12-31",
      listDettaglio_prezzo: "",
      listDettaglio_durata: "",
      listDettaglio_CFU: "",
      listDettaglio_tasse: "",
      isNew: true,
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const getIeri = (dataString) => {
    const data = new Date(dataString);
    data.setDate(data.getDate() - 1);
    return data.toISOString().split("T")[0];
  };

  const fetchNextCode = async () => {
    try {
      const response = await apiFetch(`/listini-testa/next-code`);
      if (response.ok) {
        const data = await response.json();
        if (data.codice) {
          setFormData((prev) => ({
            ...prev,
            listTesta_codice: data.codice,
          }));
        }
      }
    } catch (err) {
      console.error("Errore nel recupero del codice automatico:", err);
    }
  };

  useEffect(() => {
    async function caricaDatiProdotto() {
      if (!isModifica) {
        await fetchNextCode();
        return;
      }

      try {
        const res = await apiFetch(`/listini-testa/${id}`);

        if (!res.ok) {
          const testoErrore = await messaggioErrore(
            res,
            "Errore nel recupero del prodotto",
          );
          throw new Error(testoErrore);
        }

        const data = await res.json();

        setFormData({
          listTesta_codice: data.listTesta_codice || "",
          listTesta_descrizione: data.listTesta_descrizione || "",
          listTesta_livello: data.listTesta_livello ?? "",
          listino_tipo_id: data.listino_tipo_id ?? 2,
          listino_modalita_id: data.listino_modalita_id ?? "",
          listino_tipoCorso_id: data.listino_tipoCorso_id ?? 8,
          listino_durataLaurea_id: data.listino_durataLaurea_id ?? "",
          listino_facolta_id: data.listino_facolta_id ?? "",
          listino_corsoLaurea_id: data.listino_corsoLaurea_id ?? "",
          nome_universita_id: data.nome_universita_id ?? "",
          listino_attivoSN: data.listino_attivoSN ?? -1,
          listTesta_created_by: data.listTesta_created_by || 1,
        });

        if (data.dettagli && data.dettagli.length > 0) {
          setDettagli(
            data.dettagli.map((d) => ({
              listDettaglio_dataInizioValidazione:
                d.listDettaglio_dataInizioValidazione || "",
              listDettaglio_dataFineValidazionoe:
                d.listDettaglio_dataFineValidazionoe || "9999-12-31",
              listDettaglio_prezzo: d.listDettaglio_prezzo ?? "",
              listDettaglio_durata: d.listDettaglio_durata ?? "",
              listDettaglio_CFU: d.listDettaglio_CFU ?? "",
              listDettaglio_tasse: d.listDettaglio_tasse ?? "",
              isNew: false, // <-- Distingue le righe già salvate a DB
            })),
          );
        }
      } catch (err) {
        setMessage({ type: "error", text: err.message });
      }
    }

    caricaDatiProdotto();
  }, [id, isModifica]);

  const handleGeneraCodice = async () => {
    await fetchNextCode();
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    let val;
    if (type === "checkbox") {
      val = checked ? -1 : 0;
    } else if (value === "") {
      val = "";
    } else if (name.endsWith("_id") || name === "listTesta_livello") {
      val = Number(value);
    } else {
      val = value;
    }

    setFormData((prev) => {
      const updated = { ...prev, [name]: val };
      if (name === "listino_tipoCorso_id") {
        updated.listino_tipo_id = val === 8 ? 2 : 1;
      }
      return updated;
    });
  };

  const handleDettaglioChange = (index, e) => {
    const { name, value } = e.target;
    const newDettagli = [...dettagli];

    let val = value;

    if (["listDettaglio_durata", "listDettaglio_CFU"].includes(name)) {
      val = value === "" ? null : parseInt(value, 10);
    } else if (["listDettaglio_prezzo", "listDettaglio_tasse"].includes(name)) {
      val = value;
    } else if (value === "") {
      val = null;
    }

    newDettagli[index][name] = val;
    setDettagli(newDettagli);
  };

  const handleDettaglioBlur = (index, e) => {
    const { name, value } = e.target;
    if (!["listDettaglio_prezzo", "listDettaglio_tasse"].includes(name)) return;

    const numero = parseNumeroItaliano(value);
    const newDettagli = [...dettagli];
    newDettagli[index][name] =
      numero === null ? null : Number(numero.toFixed(2));
    setDettagli(newDettagli);
  };

  const handleAggiungiRiga = () => {
    const oggi = new Date().toISOString().split("T")[0];
    const dataIeri = getIeri(oggi);

    setDettagli((prevDettagli) => {
      const dettagliAggiornati = prevDettagli.map((det, index) => {
        if (index === prevDettagli.length - 1) {
          return {
            ...det,
            listDettaglio_dataFineValidazionoe: dataIeri,
          };
        }
        return det;
      });

      return [
        ...dettagliAggiornati,
        {
          listDettaglio_dataInizioValidazione: oggi,
          listDettaglio_dataFineValidazionoe: "9999-12-31",
          listDettaglio_prezzo: "",
          listDettaglio_durata: "",
          listDettaglio_CFU: "",
          listDettaglio_tasse: "",
          isNew: true,
        },
      ];
    });
  };

  const handleRimuoviRiga = (index) => {
    const newDettagli = dettagli.filter((_, i) => i !== index);
    setDettagli(newDettagli);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    if (!formData.listTesta_codice || formData.listTesta_codice.trim() === "") {
      setMessage({
        type: "error",
        text: "Il campo codice non può essere vuoto.",
      });
      setLoading(false);
      return;
    }

    let dettagliDaInviare = dettagli.map((det) => ({ ...det }));

    for (let i = 0; i < dettagliDaInviare.length; i++) {
      const det = dettagliDaInviare[i];
      const prezzo = parseNumeroItaliano(det.listDettaglio_prezzo);
      const tasse = parseNumeroItaliano(det.listDettaglio_tasse);

      // Per QUALSIASI riga (nuova o vecchia): il prezzo non può essere del tutto vuoto/null
      if (prezzo === null) {
        setMessage({
          type: "error",
          text: `Errore nella riga ${i + 1}: Il prezzo è un campo obbligatorio.`,
        });
        setLoading(false);
        return;
      }

      // Solo per le NUOVE righe: blocco su prezzo <= 0
      if (det.isNew && prezzo <= 0) {
        setMessage({
          type: "error",
          text: `Errore nella riga ${i + 1}: Per i nuovi dettagli il prezzo deve essere maggiore di zero.`,
        });
        setLoading(false);
        return;
      }

      // Controllo tasse (valido se compilato)
      if (
        det.listDettaglio_tasse !== "" &&
        det.listDettaglio_tasse !== null &&
        det.listDettaglio_tasse !== undefined &&
        tasse !== null &&
        tasse < 0 // Modificato in < 0 se 0 tasse è consentito, altrimenti mantieni tasse <= 0
      ) {
        setMessage({
          type: "error",
          text: `Errore nella riga ${i + 1}: Le tasse non possono essere negative.`,
        });
        setLoading(false);
        return;
      }
    }

    if (dettagliDaInviare.length > 1) {
      for (let i = 0; i < dettagliDaInviare.length - 1; i++) {
        const dataInizioSuccessiva =
          dettagliDaInviare[i + 1].listDettaglio_dataInizioValidazione;
        if (dataInizioSuccessiva && dataInizioSuccessiva.trim() !== "") {
          dettagliDaInviare[i].listDettaglio_dataFineValidazionoe =
            getIeri(dataInizioSuccessiva);
        } else {
          const oggi = new Date().toISOString().split("T")[0];
          dettagliDaInviare[i].listDettaglio_dataFineValidazionoe =
            getIeri(oggi);
        }
      }
    }

    if (dettagliDaInviare.length > 0) {
      dettagliDaInviare[
        dettagliDaInviare.length - 1
      ].listDettaglio_dataFineValidazionoe = "9999-12-31";
    }

    const payload = {
      ...formData,
      listTesta_livello:
        formData.listTesta_livello !== ""
          ? Number(formData.listTesta_livello)
          : null,
      listino_modalita_id:
        formData.listino_modalita_id !== ""
          ? Number(formData.listino_modalita_id)
          : null,
      listino_tipoCorso_id:
        formData.listino_tipoCorso_id !== ""
          ? Number(formData.listino_tipoCorso_id)
          : null,
      listino_durataLaurea_id:
        formData.listino_durataLaurea_id !== ""
          ? Number(formData.listino_durataLaurea_id)
          : null,
      listino_facolta_id:
        formData.listino_facolta_id !== ""
          ? Number(formData.listino_facolta_id)
          : null,
      listino_corsoLaurea_id:
        formData.listino_corsoLaurea_id !== ""
          ? Number(formData.listino_corsoLaurea_id)
          : null,
      nome_universita_id:
        formData.nome_universita_id !== ""
          ? Number(formData.nome_universita_id)
          : null,
      dettagli: dettagliDaInviare.map((d) => ({
        listDettaglio_dataInizioValidazione:
          d.listDettaglio_dataInizioValidazione || null,
        listDettaglio_dataFineValidazionoe:
          d.listDettaglio_dataFineValidazionoe || "9999-12-31",
        listDettaglio_prezzo: parseNumeroItaliano(d.listDettaglio_prezzo),
        listDettaglio_durata:
          d.listDettaglio_durata !== "" && d.listDettaglio_durata !== null
            ? parseInt(d.listDettaglio_durata, 10)
            : null,
        listDettaglio_CFU:
          d.listDettaglio_CFU !== "" && d.listDettaglio_CFU !== null
            ? parseInt(d.listDettaglio_CFU, 10)
            : null,
        listDettaglio_tasse: parseNumeroItaliano(d.listDettaglio_tasse),
      })),
    };

    try {
      const url = isModifica ? `/listini-testa/${id}` : `/listini-testa`;
      const method = isModifica ? "PUT" : "POST";

      const response = await apiFetch(url, {
        method,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (
          !isModifica &&
          (response.status === 400 || response.status === 409)
        ) {
          await fetchNextCode();
        }
        const testoErrore = await messaggioErrore(
          response,
          `Errore del server (Codice: ${response.status})`,
        );
        throw new Error(testoErrore);
      }

      setMessage({
        type: "success",
        text: isModifica
          ? "Prodotto aggiornato con successo! Reindirizzamento in corso..."
          : "Prodotto salvato con successo! Reindirizzamento in corso...",
      });

      setTimeout(() => {
        navigate(ROTTE.prodotti);
      }, 1000);
    } catch (err) {
      setMessage({ type: "error", text: err.message });
      setLoading(false);
    }
  };

  return (
    <div className={contenutoPagina()}>
      <IntestazionePagina
        titolo={isModifica ? "Modifica prodotto" : "Nuovo prodotto"}
        indietro={{ rotta: ROTTE.prodotti, etichetta: "Prodotti formativi" }}
      />
      <div className={`${scheda()} p-6`}>
        <AlertMessage message={message} />

        <form onSubmit={handleSubmit} className="space-y-6">
          <ProdottoFormInfo
            formData={formData}
            handleChange={handleChange}
            handleGeneraCodice={handleGeneraCodice}
          />

          <ProdottoDettagliTabella
            dettagli={dettagli}
            handleDettaglioChange={handleDettaglioChange}
            handleDettaglioBlur={handleDettaglioBlur}
            handleAggiungiRiga={handleAggiungiRiga}
            handleRimuoviRiga={handleRimuoviRiga}
            isModifica={isModifica}
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-bordo">
            <button
              type="button"
              onClick={() => navigate(ROTTE.prodotti)}
              className={pulsante("secondario", "grande")}
            >
              Annulla
            </button>
            <button
              type="submit"
              disabled={loading}
              className={pulsante("primario", "grande")}
            >
              {loading
                ? "Salvataggio in corso..."
                : isModifica
                  ? "Aggiorna Prodotto"
                  : "Salva Prodotto"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
