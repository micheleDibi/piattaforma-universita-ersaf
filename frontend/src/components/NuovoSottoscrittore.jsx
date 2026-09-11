import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { leggiUtenteId } from "../lib/sessione";
import SchedaUtente from "./SchedaUtente";
import SchedaCurriculumFormativo from "./SchedaCurriculumFormativo";
import FormInformazioniPersonali from "./FormInformazioniPersonali";
import FormDocumento from "./FormDocumento";
import FormResidenzaDomicilio from "./FormResidenzaDomicilio";
import FormContatti from "./FormContatti";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";

function NuovoSottoscrittore() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const isEditMode = Boolean(id);

  const [activeTab, setActiveTab] = useState("dati-principali");
  // Credenziali generate dal server, da mostrare una volta sola.
  const [credenziali, setCredenziali] = useState(null);

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
    universita_immatricolato: false,
    universita_data_immatricolazione: "",
    universita_riforma: "",
    universita_conclusione: "",
    universita_data_conclusione: "",
    universita_iscrizioneAltraUniversita: false,
    universita_diploma: "",
    universita_istituto: "",
    universita_via_istituto: "",
    universita_citta_istituto: "",
    universita_provincia_istituto: "",
    universita_anno_scolastico: "",
    universita_votoRicevuto_diploma: "",
    universita_votoMassimo_diploma: "",
    universita_istituto_ai: "",
    universita_citta_istituto_ai: "",
    universita_provincia_istituto_ai: "",
    universita_via_istituto_ai: "",
    universita_anno_scolastico_ai: "",
    universita_votoRicevuto_ai: "",
    universita_votoMassimo_ai: "",
    universita_titolo_universitario: "",
    universita_materia_titolo: "",
    universita_universita_titolo: "",
    universita_data_titolo: "",
    universita_votoRicevuto_titolo: "",
    universita_votoMassimo_titolo: "",
    universita_materia_pl1: "",
    universita_istituto_pl1: "",
    universita_data_pl1: "",
    universita_materia_pl2: "",
    universita_istituto_pl2: "",
    universita_data_pl2: "",
    universita_materia_ats1: "",
    universita_istituto_ats1: "",
    universita_data_ats1: "",
    universita_materia_ats2: "",
    universita_istituto_ats2: "",
    universita_data_ats2: "",
    universita_attivita_professionalizzanti: false,
    universita_corsi_di_formazione: false,
    universita_altre_attivita_certificate: false,
    universita_ateneoNullaosta: "",
    universita_percentualeInvalidita: "",
    universita_tipoInvalidita: "",
    universita_professione: "",
    universita_data_professione: "",
    universita_luogo_professione: "",
    universita_sessione_professione: "",
    universita_annoSessione_professione: "",
    universita_voto_professione: "",
    universita_qualifica_professionale: "",
    universita_data_qualifica: "",
    universita_luogo: "",
    universita_corrispondenza: "",
    universita_albo: "",
    universita_forzeDellOrdine: "",
    universita_universitaConclusione: "",
    universita_cittaUniConclusione: "",
    universita_provinciaConclusione: "",
    universita_attIscritto_tipo: "",
    universita_attIscritto_altro: "",
    universita_attIscritto_classeLaurea: "",
    universita_attIscritto_denominazione: "",
    universita_attIscritto_universita: "",
    universita_attIscritto_citta: "",
    universita_attIscritto_provincia: "",
    universita_attIscritto_annoIscrizione: "",
    universita_attIscritto_modalita: "",
  });

  useEffect(() => {
    if (isEditMode) {
      apiFetch(`/clienti/${id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Errore nel recupero del cliente");
          return res.json();
        })
        .then((data) => {
          // Il curriculum arriva in `curriculum`. Prima era
          // `data.universita || data`: ClienteResponse non esponeva la
          // relazione, quindi si leggeva l'oggetto cliente e la scheda restava
          // sempre vuota.
          const uniData = data.curriculum || {};

          setFormData((prev) => ({
            ...prev,
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

            ...Object.keys(prev)
              .filter((k) => k.startsWith("universita_"))
              .reduce((acc, k) => {
                acc[k] =
                  uniData[k] !== undefined && uniData[k] !== null
                    ? uniData[k]
                    : prev[k];
                return acc;
              }, {}),
          }));
        })
        .catch((err) => {
          console.error("Errore:", err);
          alert("Impossibile caricare i dati.");
        });
    }
  }, [id, isEditMode]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let finalValue = value;

    // Campi che richiedono un valore numerico (0 o 1) da select o input numerici
    const numericFields = [
      "universita_immatricolato",
      "universita_iscrizioneAltraUniversita",
    ];

    // Campi checkbox che devono inviare 1 o 0
    const numericCheckboxFields = [
      "universita_attivita_professionalizzanti",
      "universita_corsi_di_formazione",
      "universita_altre_attivita_certificate",
    ];

    if (numericFields.includes(name)) {
      finalValue = value === "" ? "" : Number(value);
    } else if (numericCheckboxFields.includes(name)) {
      finalValue = checked ? 1 : 0;
    } else if (type === "checkbox") {
      finalValue = checked;
    }

    setFormData((prev) => ({ ...prev, [name]: finalValue }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const utenteId = leggiUtenteId();
    if (utenteId === null) {
      alert("Sessione scaduta. Rifai il login prima di salvare.");
      navigate("/");
      return;
    }

    const payloadAnagrafica = {
      cliente_codice: formData.codiceFiscale || null,
      cliente_nome: formData.nome || null,
      cliente_cognome: formData.cognome || null,
      cliente_email: formData.email || null,
      cliente_telefono: formData.telefono || null,
      cliente_pec: formData.pec || null,
      cliente_indirizzo: formData.residenzaIndirizzo || null,
      cliente_civico: formData.residenzaCivico || null,
      cliente_citta: formData.residenzaComune || null,
      cliente_CAP: formData.residenzaCap || null,
      cliente_provincia: formData.residenzaProvincia || null,
      cliente_cellulare: formData.cellulare || null,
      utente_id: utenteId,
      // Solo in creazione, e solo 0: il ruolo lo assegna poi un
      // amministratore dalla scheda utente. Mandarlo anche in modifica
      // declassava a "Utente" chiunque si salvasse, attuatori compresi.
      ...(isEditMode ? {} : { cliente_ruolo: 0 }),
      cliente_luogoNascita: formData.luogoDiNascita || null,
      cliente_provinciaNascita: formData.provDiNascita || null,
      cliente_dataNascita: formData.dataDiNascita || null,
      cliente_cittadinanza: formData.cittadinanza || null,
      cliente_tipoDocumento: formData.tipoDocumento || null,
      cliente_documento: formData.nDocumento || null,
      cliente_comuneRilascio: formData.comuneDiRilascio || null,
      cliente_dataRilascio: formData.dataInizioRilascio || null,
      cliente_dataScadenzaDocumento: formData.dataScadenza || null,
      cliente_sesso: formData.genere || null,
      cliente_indirizzoDomicilio: formData.domicilioIndirizzo || null,
      cliente_civicoDomicilio: formData.domicilioCivico || null,
      cliente_cittaDomicilio: formData.domicilioComune || null,
      cliente_CAPDomicilio: formData.domicilioCap || null,
      cliente_provinciaDomicilio: formData.domicilioProvincia || null,
    };

    const curriculumKeys = Object.keys(formData).filter((key) =>
      key.startsWith("universita_"),
    );
    const curriculumPayload = {};

    // I cinque flag si mandano cosi' come sono. Il Boolean() che stava qui
    // distruggeva il -1 costruito da ImmatricolazioniIscrizioni: diventava
    // true, il backend lo salvava 1, e la casella si rileggeva vuota. La
    // conversione nella convenzione legacy (-1 per quattro colonne, 1 per
    // universita_immatricolato) la fa ora il validatore di UniversitaBase, che
    // vale per tutti i percorsi di scrittura e non solo per questo.
    curriculumKeys.forEach((key) => {
      const val = formData[key];
      curriculumPayload[key] = val === "" || val === undefined ? null : val;
    });

    const payload = {
      ...payloadAnagrafica,
      ...curriculumPayload,
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
        // Un 422 porta l'elenco dei campi mancanti: ridurlo a "si è
        // verificato un errore" lasciava l'operatore senza modo di capire
        // quale campo compilare.
        throw new Error(await messaggioErrore(response));
      }

      if (isEditMode) {
        alert("Modifiche salvate con successo!");
        navigate("/home");
        return;
      }

      // Le credenziali generate esistono in chiaro solo in questa risposta:
      // nel database c'e' soltanto l'hash. Prima si controllava response.ok e
      // si navigava via senza leggere il corpo, e l'utente appena creato
      // restava senza modo di accedere.
      const creato = await leggiJson(response);
      setCredenziali(
        creato?.username_generato
          ? {
              username: creato.username_generato,
              password: creato.password_generata,
            }
          : null,
      );
      if (!creato?.username_generato) {
        alert(`${labelTitolo} salvato correttamente!`);
        navigate("/home");
      }
    } catch (error) {
      console.error("Errore:", error);
      alert(error.message);
    }
  };

  const tabs = [
    { id: "dati-principali", label: "Dati Principali" },
    { id: "curriculum", label: "Curriculum Formativo" },
    { id: "utente", label: "Utente" },
    { id: "esami", label: "Esami" },
    { id: "prevalutazioni", label: "Prevalutazioni e-campus" },
  ];

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

  // Le credenziali generate dal server esistono in chiaro solo nella risposta
  // di creazione: nel database c'e' l'hash. Si mostrano qui, e finche' non le
  // si conferma non si naviga via.
  if (credenziali) {
    return (
      <div className="min-h-screen bg-superficie-tenue py-10 px-4 flex items-start justify-center">
        <div className={`${scheda()} max-w-lg w-full p-8`}>
          <h2 className="text-xl font-bold text-testo mb-2">
            {labelTitolo} creato
          </h2>
          <p className="text-sm text-testo-tenue mb-6">
            Annota queste credenziali e consegnale alla persona: la password non
            sarà più recuperabile, nel database resta solo la sua impronta.
          </p>

          <dl className="rounded-superficie border border-attenzione-bordo bg-attenzione-tenue p-5 mb-6">
            <dt className="text-nota font-bold tracking-wide text-attenzione-forte">
              USERNAME
            </dt>
            <dd className="font-mono text-base text-testo-forte mb-4 select-all break-all">
              {credenziali.username}
            </dd>
            <dt className="text-nota font-bold tracking-wide text-attenzione-forte">
              PASSWORD
            </dt>
            <dd className="font-mono text-base text-testo-forte select-all break-all">
              {credenziali.password}
            </dd>
          </dl>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() =>
                navigator.clipboard
                  ?.writeText(
                    `${credenziali.username}\n${credenziali.password}`,
                  )
                  .catch(() => {})
              }
              className={pulsante("secondario", "grande")}
            >
              Copia
            </button>
            <button
              type="button"
              onClick={() => navigate("/home")}
              className={pulsante("primario", "grande")}
            >
              Le ho annotate, continua
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-superficie-tenue py-10 px-4 sm:px-6 lg:px-8">
      <div className={`${scheda()} max-w-5xl mx-auto overflow-hidden`}>
        <form onSubmit={handleSubmit}>
          <div className="flex flex-wrap border-b border-bordo px-6 pt-4 gap-2 bg-superficie-tenue/50 justify-between items-center">
            <div className="flex flex-wrap gap-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-5 py-2.5 text-sm font-semibold rounded-t-controllo border-t border-x transition cursor-pointer ${
                    activeTab === tab.id
                      ? "bg-superficie text-primario border-bordo shadow-sm -mb-px z-10"
                      : "bg-superficie-tenue text-testo-tenue border-transparent hover:bg-superficie-alta"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => navigate("/home")}
              className={`${pulsante("discreto")} mb-2`}
            >
              ← Torna all'elenco
            </button>
          </div>

          <div className="p-8">
            {activeTab === "dati-principali" ? (
              <div className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <FormInformazioniPersonali
                    formData={formData}
                    handleChange={handleChange}
                  />
                  <FormDocumento
                    formData={formData}
                    handleChange={handleChange}
                  />
                </div>
                <hr className="border-bordo my-6" />
                <FormResidenzaDomicilio
                  formData={formData}
                  handleChange={handleChange}
                  handleCopyResidenza={handleCopyResidenza}
                />
                <hr className="border-bordo my-6" />
                <FormContatti formData={formData} handleChange={handleChange} />
              </div>
            ) : activeTab === "utente" ? (
              <SchedaUtente />
            ) : activeTab === "curriculum" ? (
              <SchedaCurriculumFormativo
                formData={formData}
                handleChange={handleChange}
              />
            ) : (
              <div className="py-12 text-center text-testo-tenue">
                <h3 className="text-lg font-semibold mb-2">
                  Sezione in fase di sviluppo
                </h3>
                <p className="text-sm">
                  Stai visualizzando la scheda:{" "}
                  <span className="font-medium text-primario capitalize">
                    {activeTab.replace("-", " ")}
                  </span>
                </p>
              </div>
            )}

            <div className="flex justify-end gap-4 pt-8 mt-10 border-t border-bordo">
              <button
                type="button"
                onClick={() => navigate("/home")}
                className={pulsante("secondario", "grande")}
              >
                Annulla
              </button>
              <button
                type="submit"
                className={pulsante("primario", "grande")}
              >
                {isEditMode ? "Salva Modifiche" : `Crea ${labelTitolo}`}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default NuovoSottoscrittore;
