import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import StatoCaricamentoDettaglio from "./shared/StatoCaricamentoDettaglio.jsx";
import useQueryPagina from "../hooks/useQueryPagina.js";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import { QUERY_ANAGRAFICA } from "../config/routes/query.js";
import { PERCORSI } from "../config/routes/percorsi.js";
import { ANAGRAFICA_INIZIALE } from "../config/anagraficaIniziale.js";
import { useIngresso } from "../hooks/useIngresso.js";
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { leggiUtenteId } from "../lib/sessione";
import SchedaUtente from "./SchedaUtente";
import SchedaCurriculumFormativo from "./SchedaCurriculumFormativo";
import FormInformazioniPersonali from "./FormInformazioniPersonali";
import FormDocumento from "./FormDocumento";
import FormResidenzaDomicilio from "./FormResidenzaDomicilio";
import FormContatti from "./FormContatti";
import IntestazionePagina from "./shared/IntestazionePagina";
import AlertMessage from "./AlertMessage.jsx";
import { ROTTE } from "../config/routes/rotte";
import { contenutoPagina } from "../config/styles/pagina";
import { pulsante } from "../config/styles/pulsante";
import { campo, etichetta } from "../config/styles/campo";
import { scheda, titoloSezione } from "../config/styles/superficie";
import BarraSchede from "./shared/BarraSchede.jsx";
import SchedaAziendaAttuatori from "./SchedaAziendaAttuatori";

const RUOLI_ATTUATORE = ["Aderente", "Provinciale", "Regionale", "Nazionale"];

function NuovoSottoscrittore({ tipoUtente }) {
  const { clienteId: id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [{ scheda: activeTab }, aggiornaQuery] =
    useQueryPagina(QUERY_ANAGRAFICA);
  const setActiveTab = (scheda) =>
    aggiornaQuery({ scheda }, { replace: false });
  const pannello = useIngresso(activeTab);

  const labelTitolo =
    tipoUtente === "attuatore" ? "Attuatore" : "Sottoscrittore";
  const risorsa =
    tipoUtente === "attuatore" ? PERCORSI.attuatori : PERCORSI.sottoscrittori;
  const { ritorno: rottaElenco } = useNavigazioneElenco(risorsa.elenco);

  const [lettura, setLettura] = useState({ loading: isEditMode, errore: null });
  const [formData, setFormData] = useState(ANAGRAFICA_INIZIALE);
  const [avviso, setAvviso] = useState(null);

  // Ruoli disponibili per la select dell'attuatore. Non serve per i
  // sottoscrittori, che restano sempre ruolo "Utente" (0).
  const [ruoli, setRuoli] = useState([]);
  const [ruoloSelezionato, setRuoloSelezionato] = useState("");

  useEffect(() => {
    if (tipoUtente !== "attuatore") return;
    apiFetch("/ruoli/")
      .then((res) => {
        if (!res.ok) throw new Error("Errore nel recupero dei ruoli");
        return res.json();
      })
      .then((data) => setRuoli(data))
      .catch((err) => console.error("Errore nel recupero dei ruoli:", err));
  }, [tipoUtente]);

  useEffect(() => {
    if (isEditMode) {
      apiFetch(`/clienti/${id}`)
        .then((res) => {
          if (!res.ok)
            throw Object.assign(
              new Error("Impossibile caricare l’anagrafica."),
              { status: res.status },
            );
          return res.json();
        })
        .then((data) => {
          // Il curriculum arriva in `curriculum`. Prima era
          // `data.universita || data`: ClienteResponse non esponeva la
          // relazione, quindi si leggeva l'oggetto cliente e la scheda restava
          // sempre vuota.
          const uniData = data.curriculum || {};

          if (data.cliente_ruolo != null) {
            setRuoloSelezionato(String(data.cliente_ruolo));
          }

          setFormData((prev) => ({
            ...prev,
            // Letto dalla colonna dedicata: prima si leggeva da
            // cliente_codice, che non e' il codice fiscale.
            codiceFiscale: data.cliente_codice_fiscale || "",
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
            // FK verso aziende: non ha prefisso "cliente_" nella risposta,
            // e' la colonna grezza della tabella clienti. Serve alla scheda
            // Azienda per sapere quale azienda caricare.
            azienda_id: data.azienda_id ?? null,

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
        .then(() => setLettura({ loading: false, errore: null }))
        .catch((errore) => setLettura({ loading: false, errore }));
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
    setAvviso(null);
    const utenteId = leggiUtenteId();
    if (utenteId === null) {
      setAvviso({
        type: "error",
        text: "Sessione scaduta. Rifai il login prima di salvare.",
      });
      navigate(ROTTE.accesso);
      return;
    }

    const payloadAnagrafica = {
      // cliente_codice non si manda piu': lo genera il backend da
      // cliente_id subito dopo la creazione.
      cliente_codice_fiscale: formData.codiceFiscale || null,
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
      // Sottoscrittori: sempre ruolo 0 ("Utente") in creazione, mai in
      // modifica (lo assegna un amministratore dalla scheda utente).
      // Attuatori: se in creazione l'operatore ha scelto un ruolo dalla
      // select lo si manda; altrimenti si omette e il backend assegna
      // "Aderente" di default. In modifica il ruolo si manda solo se
      // l'operatore lo ha effettivamente cambiato dalla select.
      ...(isEditMode
        ? tipoUtente === "attuatore" && ruoloSelezionato
          ? { cliente_ruolo: Number(ruoloSelezionato) }
          : {}
        : tipoUtente === "attuatore"
          ? ruoloSelezionato
            ? { cliente_ruolo: Number(ruoloSelezionato) }
            : {}
          : { cliente_ruolo: 0 }),
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
      azienda_id: formData.azienda_id ?? null,
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
        navigate(rottaElenco, {
          state: {
            avviso: {
              type: "success",
              text: "Modifiche salvate con successo!",
            },
          },
        });
        return;
      }

      const creato = await leggiJson(response);
      navigate(risorsa.dettaglio(creato.cliente_id), {
        replace: true,
        state: { elenco: rottaElenco },
      });
    } catch (error) {
      console.error("Errore:", error);
      setAvviso({ type: "error", text: error.message });
    }
  };

  const tabs = [
    { id: "dati-principali", label: "Dati Principali" },
    { id: "curriculum", label: "Curriculum Formativo" },
    { id: "utente", label: "Utente" },
    ...(tipoUtente === "attuatore"
      ? [{ id: "azienda", label: "Azienda" }]
      : [{ id: "esami", label: "Esami" }]),
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

  if (lettura.errore?.status === 404) return <PaginaNonTrovata />;
  if (lettura.loading || lettura.errore)
    return <StatoCaricamentoDettaglio {...lettura} ritorno={rottaElenco} />;

  return (
    <div className={contenutoPagina("modulo")}>
      <IntestazionePagina
        titolo={`${isEditMode ? "Modifica" : "Nuovo"} ${labelTitolo.toLowerCase()}`}
        indietro={{
          rotta: rottaElenco,
          etichetta:
            tipoUtente === "attuatore" ? "Attuatori" : "Sottoscrittori",
        }}
      />
      <AlertMessage message={avviso} />
      <div className={`${scheda()} schede overflow-hidden`}>
        <form onSubmit={handleSubmit}>
          <BarraSchede
            id="anagrafica"
            etichetta="Schede anagrafica"
            schede={tabs}
            attiva={activeTab}
            onChange={setActiveTab}
          />

          <div
            ref={pannello}
            role="tabpanel"
            id={`anagrafica-pannello-${activeTab}`}
            aria-labelledby={`anagrafica-scheda-${activeTab}`}
            className="movimento-scheda schede__pannello"
          >
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

                {tipoUtente === "attuatore" && (
                  <>
                    <hr className="border-bordo my-6" />
                    <div className="space-y-4">
                      <h3 className={titoloSezione()}>Ruolo</h3>
                      <div className="max-w-xs">
                        <label className={etichetta()}>Ruolo attuatore</label>
                        <select
                          name="ruolo"
                          value={ruoloSelezionato}
                          onChange={(e) => setRuoloSelezionato(e.target.value)}
                          className={`${campo("comodo")} transition`}
                        >
                          <option value="">Aderente (default)</option>
                          {ruoli
                            .filter((r) =>
                              RUOLI_ATTUATORE.includes(r.ruolo_codice),
                            )
                            .map((r) => (
                              <option key={r.ruolo_id} value={r.ruolo_id}>
                                {r.ruolo_codice}
                              </option>
                            ))}
                        </select>
                      </div>
                    </div>
                  </>
                )}

                <hr className="border-bordo my-6" />
                <FormResidenzaDomicilio
                  formData={formData}
                  handleChange={handleChange}
                  handleCopyResidenza={handleCopyResidenza}
                />
                <hr className="border-bordo my-6" />
                <FormContatti
                  key={id || "nuovo"}
                  clienteId={id}
                  formData={formData}
                  handleChange={handleChange}
                />
              </div>
            ) : activeTab === "utente" ? (
              <SchedaUtente />
            ) : activeTab === "curriculum" ? (
              <SchedaCurriculumFormativo
                formData={formData}
                handleChange={handleChange}
              />
            ) : activeTab === "azienda" ? (
              <SchedaAziendaAttuatori
                aziendaId={formData.azienda_id}
                isEditMode={isEditMode}
                clienteId={id}
                onCambiaAziendaId={(nuovoId) =>
                  setFormData((prev) => ({ ...prev, azienda_id: nuovoId }))
                }
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
                onClick={() => navigate(rottaElenco)}
                className={pulsante("secondario", "grande")}
              >
                Annulla
              </button>
              <button type="submit" className={pulsante("primario", "grande")}>
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
