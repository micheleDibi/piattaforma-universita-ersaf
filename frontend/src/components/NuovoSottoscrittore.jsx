import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router";
import { apiFetch } from "../lib/api";
import { leggiUtenteId } from "../lib/sessione";
import SchedaUtente from "./SchedaUtente"; // Assicurati che il percorso di import sia corretto

function NuovoSottoscrittore() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const isEditMode = Boolean(id);

  // Stato per gestire la scheda attiva superiore
  const [activeTab, setActiveTab] = useState("dati-principali");

  // Rileva se siamo su un attuatore (es. tramite URL o query param)
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

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Dettagli errore backend:", errorData);
        throw new Error("Errore durante il salvataggio dei dati");
      }

      const result = await response.json();
      console.log("Dati salvati con successo nel DB:", result);
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

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
        {/* SEZIONE SUPERIORE: Schede / Tabs di navigazione */}
        <div className="flex flex-wrap border-b border-slate-200 px-6 pt-4 gap-2 bg-slate-50/50 justify-between items-center">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setActiveTab("dati-principali")}
              className={`px-5 py-2.5 text-sm font-semibold rounded-t-2xl border-t border-x transition cursor-pointer ${
                activeTab === "dati-principali"
                  ? "bg-white text-blue-600 border-slate-200 shadow-sm -mb-px z-10"
                  : "bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200"
              }`}
            >
              Dati Principali
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("curriculum")}
              className={`px-5 py-2.5 text-sm font-semibold rounded-t-2xl border-t border-x transition cursor-pointer ${
                activeTab === "curriculum"
                  ? "bg-white text-blue-600 border-slate-200 shadow-sm -mb-px z-10"
                  : "bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200"
              }`}
            >
              Curriculum Formativo
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("utente")}
              className={`px-5 py-2.5 text-sm font-semibold rounded-t-2xl border-t border-x transition cursor-pointer ${
                activeTab === "utente"
                  ? "bg-white text-blue-600 border-slate-200 shadow-sm -mb-px z-10"
                  : "bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200"
              }`}
            >
              Utente
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("esami")}
              className={`px-5 py-2.5 text-sm font-semibold rounded-t-2xl border-t border-x transition cursor-pointer ${
                activeTab === "esami"
                  ? "bg-white text-blue-600 border-slate-200 shadow-sm -mb-px z-10"
                  : "bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200"
              }`}
            >
              Esami
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("prevalutazioni")}
              className={`px-5 py-2.5 text-sm font-semibold rounded-t-2xl border-t border-x transition cursor-pointer ${
                activeTab === "prevalutazioni"
                  ? "bg-white text-blue-600 border-slate-200 shadow-sm -mb-px z-10"
                  : "bg-slate-100 text-slate-600 border-transparent hover:bg-slate-200"
              }`}
            >
              Prevalutazioni e-campus
            </button>
          </div>

          <button
            type="button"
            onClick={() => navigate("/home")}
            className="text-sm font-medium text-slate-500 hover:text-slate-800 mb-2 px-3 py-1"
          >
            ← Torna all'elenco
          </button>
        </div>

        {/* CONTENUTO SCHEDA ATTIVA */}
        {activeTab === "dati-principali" ? (
          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 mb-4">
                  Informazioni Personali
                </h3>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Codice Fiscale
                  </label>
                  <input
                    type="text"
                    name="codiceFiscale"
                    value={formData.codiceFiscale}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Genere
                  </label>
                  <select
                    name="genere"
                    value={formData.genere}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  >
                    <option value="">Seleziona il genere</option>
                    <option value="uomo">uomo</option>
                    <option value="donna">donna</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Nome
                    </label>
                    <input
                      type="text"
                      name="nome"
                      value={formData.nome}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Cognome
                    </label>
                    <input
                      type="text"
                      name="cognome"
                      value={formData.cognome}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Cittadinanza
                  </label>
                  <input
                    type="text"
                    name="cittadinanza"
                    value={formData.cittadinanza}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Luogo di Nascita
                    </label>
                    <input
                      type="text"
                      name="luogoDiNascita"
                      value={formData.luogoDiNascita}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Prov.
                    </label>
                    <input
                      type="text"
                      name="provDiNascita"
                      value={formData.provDiNascita}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Data di Nascita
                  </label>
                  <input
                    type="date"
                    name="dataDiNascita"
                    value={formData.dataDiNascita}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
              </div>

              {/* Documento */}
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 mb-4">
                  Documento
                </h3>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Tipo Documento
                  </label>
                  <select
                    name="tipoDocumento"
                    value={formData.tipoDocumento}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  >
                    <option value="">Seleziona il tipo di documento</option>
                    <option value="Carta d'identità">Carta d'identità</option>
                    <option value="Passaporto">Passaporto</option>
                    <option value="Patente">Patente</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    N° Documento
                  </label>
                  <input
                    type="text"
                    name="nDocumento"
                    value={formData.nDocumento}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Comune di Rilascio
                  </label>
                  <input
                    type="text"
                    name="comuneDiRilascio"
                    value={formData.comuneDiRilascio}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Data Rilascio
                    </label>
                    <input
                      type="date"
                      name="dataInizioRilascio"
                      value={formData.dataInizioRilascio}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Data Scadenza
                    </label>
                    <input
                      type="date"
                      name="dataScadenza"
                      value={formData.dataScadenza}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>
              </div>
            </div>

            <hr className="border-slate-100 my-6" />

            {/* Sezione: Residenza & Domicilio */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Residenza */}
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 mb-4">
                  Residenza
                </h3>

                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Indirizzo
                    </label>
                    <input
                      type="text"
                      name="residenzaIndirizzo"
                      value={formData.residenzaIndirizzo}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Civico
                    </label>
                    <input
                      type="text"
                      name="residenzaCivico"
                      value={formData.residenzaCivico}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Comune
                  </label>
                  <input
                    type="text"
                    name="residenzaComune"
                    value={formData.residenzaComune}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      CAP
                    </label>
                    <input
                      type="text"
                      name="residenzaCap"
                      value={formData.residenzaCap}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Provincia
                    </label>
                    <input
                      type="text"
                      name="residenzaProvincia"
                      value={formData.residenzaProvincia}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    type="button"
                    onClick={handleCopyResidenza}
                    className="w-full py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs uppercase tracking-wider rounded-2xl transition cursor-pointer"
                  >
                    Copia Residenza in Domicilio
                  </button>
                </div>
              </div>

              {/* Domicilio */}
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 mb-4">
                  Domicilio
                </h3>

                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Indirizzo Domicilio
                    </label>
                    <input
                      type="text"
                      name="domicilioIndirizzo"
                      value={formData.domicilioIndirizzo}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Civico
                    </label>
                    <input
                      type="text"
                      name="domicilioCivico"
                      value={formData.domicilioCivico}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Comune
                  </label>
                  <input
                    type="text"
                    name="domicilioComune"
                    value={formData.domicilioComune}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      CAP
                    </label>
                    <input
                      type="text"
                      name="domicilioCap"
                      value={formData.domicilioCap}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                      Provincia
                    </label>
                    <input
                      type="text"
                      name="domicilioProvincia"
                      value={formData.domicilioProvincia}
                      onChange={handleChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                    />
                  </div>
                </div>
              </div>
            </div>

            <hr className="border-slate-100 my-6" />

            {/* Contatti */}
            <div className="space-y-4">
              <h3 className="text-base font-bold text-slate-800 mb-4">
                Contatti
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    PEC
                  </label>
                  <input
                    type="email"
                    name="pec"
                    value={formData.pec}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Cellulare
                  </label>
                  <input
                    type="text"
                    name="cellulare"
                    value={formData.cellulare}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Telefono
                  </label>
                  <input
                    type="text"
                    name="telefono"
                    value={formData.telefono}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
              </div>
            </div>

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
          /* Sostituisce il form con il componente SchedaUtente */
          <div className="p-8">
            <SchedaUtente />
          </div>
        ) : (
          /* Segnaposto per le altre sezioni non ancora implementate */
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
