import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router";
import { apiFetch } from "../lib/api";
import { leggiUtenteId } from "../lib/sessione";
import SchedaUtente from "./SchedaUtente";
import SchedaCurriculumFormativo from "./SchedaCurriculumFormativo";
import FormInformazioniPersonali from "./FormInformazioniPersonali";
import FormDocumento from "./FormDocumento";
import FormResidenzaDomicilio from "./FormResidenzaDomicilio";
import FormContatti from "./FormContatti";

function NuovoSottoscrittore() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const isEditMode = Boolean(id);

  const [activeTab, setActiveTab] = useState("dati-principali");

  const queryParams = new URLSearchParams(location.search);
  const tipoUtente =
    queryParams.get("tipo") ||
    (location.pathname.includes("attuatore") ? "attuatore" : "sottoscrittore");

  const labelTitolo =
    tipoUtente === "attuatore" ? "Attuatore" : "Sottoscrittore";

  const [formData, setFormData] = useState({
    codiceFiscale: "",
    genere: "",
    nome: "",
    cognome: "",
    cittadinanza: "",
    luogoDiNascita: "",
    provDiNascita: "",
    dataDiNascita: "",
    tipoDocumento: "",
    nDocumento: "",
    comuneDiRilascio: "",
    dataInizioRilascio: "",
    dataScadenza: "",
    residenzaIndirizzo: "",
    residenzaCivico: "",
    residenzaComune: "",
    residenzaCap: "",
    residenzaProvincia: "",
    domicilioIndirizzo: "",
    domicilioCivico: "",
    domicilioComune: "",
    domicilioCap: "",
    domicilioProvincia: "",
    email: "",
    cellulare: "",
    telefono: "",
    pec: "",
  });

  useEffect(() => {
    if (isEditMode) {
      apiFetch(`/clienti/${id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Errore nel recupero del cliente");
          return res.json();
        })
        .then((data) => {
          setFormData({
            codiceFiscale: data.cliente_codice || "",
            genere: data.cliente_sesso || "",
            nome: data.cliente_nome || "",
            cognome: data.cliente_cognome || "",
            cittadinanza: data.cliente_cittadinanza || "",
            luogoDiNascita: data.cliente_luogoNascita || "",
            provDiNascita: data.cliente_provinciaNascita || "",
            dataDiNascita: data.cliente_dataNascita
              ? data.cliente_dataNascita.split("T")[0]
              : "",
            tipoDocumento: data.cliente_tipoDocumento || "",
            nDocumento: data.cliente_documento || "",
            comuneDiRilascio: data.cliente_comuneRilascio || "",
            dataInizioRilascio: data.cliente_dataRilascio
              ? data.cliente_dataRilascio.split("T")[0]
              : "",
            dataScadenza: data.cliente_dataScadenzaDocumento
              ? data.cliente_dataScadenzaDocumento.split("T")[0]
              : "",
            residenzaIndirizzo: data.cliente_indirizzo || "",
            residenzaCivico: data.cliente_civico || "",
            residenzaComune: data.cliente_citta || "",
            residenzaCap: data.cliente_CAP || "",
            residenzaProvincia: data.cliente_provincia || "",
            domicilioIndirizzo: data.cliente_indirizzoDomicilio || "",
            domicilioCivico: data.cliente_civicoDomicilio || "",
            domicilioComune: data.cliente_cittaDomicilio || "",
            domicilioCap: data.cliente_CAPDomicilio || "",
            domicilioProvincia: data.cliente_provinciaDomicilio || "",
            email: data.cliente_email || "",
            cellulare: data.cliente_cellulare || "",
            telefono: data.cliente_telefono || "",
            pec: data.cliente_pec || "",
          });
        })
        .catch((err) => {
          console.error("Errore:", err);
          alert("Impossibile caricare i dati.");
        });
    }
  }, [id, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCopyResidenza = () => {
    setFormData((prev) => ({
      ...prev,
      domicilioIndirizzo: prev.residenzaIndirizzo,
      domicilioCivico: prev.residenzaCivico,
      domicilioComune: prev.residenzaComune,
      domicilioCap: prev.residenzaCap,
      domicilioProvincia: prev.residenzaProvincia,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const utenteId = leggiUtenteId();
    if (utenteId === null) {
      alert("Sessione scaduta. Rifai il login prima di salvare.");
      navigate("/");
      return;
    }

    const payload = {
      cliente_codice: formData.codiceFiscale,
      cliente_nome: formData.nome,
      cliente_cognome: formData.cognome,
      cliente_email: formData.email || null,
      cliente_telefono: formData.telefono || null,
      cliente_pec: formData.pec || null,
      cliente_indirizzo: formData.residenzaIndirizzo,
      cliente_civico: formData.residenzaCivico,
      cliente_citta: formData.residenzaComune,
      cliente_CAP: formData.residenzaCap || null,
      cliente_provincia: formData.residenzaProvincia,
      cliente_cellulare: formData.cellulare || null,
      utente_id: utenteId,
      cliente_ruolo: 0,
      cliente_luogoNascita: formData.luogoDiNascita,
      cliente_provinciaNascita: formData.provDiNascita,
      cliente_dataNascita: formData.dataDiNascita,
      cliente_cittadinanza: formData.cittadinanza,
      cliente_tipoDocumento: formData.tipoDocumento,
      cliente_documento: formData.nDocumento,
      cliente_comuneRilascio: formData.comuneDiRilascio,
      cliente_dataRilascio: formData.dataInizioRilascio,
      cliente_dataScadenzaDocumento: formData.dataScadenza,
      cliente_sesso: formData.genere,
      cliente_indirizzoDomicilio: formData.domicilioIndirizzo || null,
      cliente_civicoDomicilio: formData.domicilioCivico || null,
      cliente_cittaDomicilio: formData.domicilioComune || null,
      cliente_CAPDomicilio: formData.domicilioCap || null,
      cliente_provinciaDomicilio: formData.domicilioProvincia || null,
    };

    const url = isEditMode
      ? `/clienti/${id}`
      : `/clienti/con-utente?tipo_utente=${tipoUtente}`;
    const method = isEditMode ? "PUT" : "POST";

    try {
      const response = await apiFetch(url, {
        method: method,
        body: JSON.stringify(payload),
      });

      if (!response.ok)
        throw new Error("Errore durante il salvataggio dei dati");

      alert(
        isEditMode
          ? "Modifiche salvate con successo!"
          : `${labelTitolo} salvato correttamente!`,
      );
      navigate("/home");
    } catch (error) {
      console.error("Errore:", error);
      alert("Si è verificato un errore durante il salvataggio.");
    }
  };

  const tabs = [
    { id: "dati-principali", label: "Dati Principali" },
    { id: "curriculum", label: "Curriculum Formativo" },
    { id: "utente", label: "Utente" },
    { id: "esami", label: "Esami" },
    { id: "prevalutazioni", label: "Prevalutazioni e-campus" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap border-b border-slate-200 px-6 pt-4 gap-2 bg-slate-50/50 justify-between items-center">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`px-5 py-2.5 text-sm font-semibold rounded-t-2xl border-t border-x transition cursor-pointer ${
                  activeTab === tab.id
                    ? "bg-white text-blue-600 border-slate-200 shadow-sm -mb-px z-10"
                    : "bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => navigate("/home")}
            className="text-sm font-medium text-slate-500 hover:text-slate-800 mb-2 px-3 py-1"
          >
            ← Torna all'elenco
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "dati-principali" ? (
          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <FormInformazioniPersonali
                formData={formData}
                handleChange={handleChange}
              />
              <FormDocumento formData={formData} handleChange={handleChange} />
            </div>

            <hr className="border-slate-100 my-6" />

            <FormResidenzaDomicilio
              formData={formData}
              handleChange={handleChange}
              handleCopyResidenza={handleCopyResidenza}
            />

            <hr className="border-slate-100 my-6" />

            <FormContatti formData={formData} handleChange={handleChange} />

            <div className="flex justify-end gap-4 pt-4">
              <button
                type="button"
                onClick={() => navigate("/home")}
                className="px-6 py-3 border border-slate-200 text-slate-600 font-semibold text-sm rounded-2xl hover:bg-slate-50 transition cursor-pointer"
              >
                Annulla
              </button>
              <button
                type="submit"
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-2xl shadow-sm transition cursor-pointer"
              >
                {isEditMode ? "Salva Modifiche" : `Crea ${labelTitolo}`}
              </button>
            </div>
          </form>
        ) : activeTab === "utente" ? (
          <div className="p-8">
            <SchedaUtente />
          </div>
        ) : activeTab === "curriculum" ? (
          <div className="p-8">
            <SchedaCurriculumFormativo />
          </div>
        ) : (
          <div className="p-12 text-center text-slate-500">
            <h3 className="text-lg font-semibold mb-2">
              Sezione in fase di sviluppo
            </h3>
            <p className="text-sm">
              Stai visualizzando la scheda:{" "}
              <span className="font-medium text-blue-600 capitalize">
                {activeTab.replace("-", " ")}
              </span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default NuovoSottoscrittore;
