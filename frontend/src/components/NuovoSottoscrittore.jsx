import { useState } from "react";

function NuovoSottoscrittore() {
  const [formData, setFormData] = useState({
    codiceFiscale: "RSSMRA85M01H501Z",
    genere: "",
    nome: "Mario",
    cognome: "Rossi",
    cittadinanza: "Italiana",
    luogoDiNascita: "Roma",
    provDiNascita: "RM",
    dataDiNascita: "1985-01-01",
    tipoDocumento: "",
    nDocumento: "AA1234567",
    comuneDiRilascio: "Milano",
    dataInizioRilascio: "2015-01-01",
    dataScadenza: "2015-01-01",
    residenzaIndirizzo: "Via Roma",
    residenzaCivico: "123",
    residenzaComune: "Milano",
    residenzaCap: "20100",
    residenzaProvincia: "MI",
    domicilioIndirizzo: "Via Milano",
    domicilioCivico: "456",
    domicilioComune: "Roma",
    domicilioCap: "RM",
    domicilioProvincia: "00100",
    email: "mario.rossi@email.com",
    cellulare: "+39 345 678 9100",
    telefono: "+39 02 1234 5678",
    pec: "mario.rossi@pec.it",
  });

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

    try {
      const response = await fetch("http://localhost:8000/clienti", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        throw new Error("Errore durante il salvataggio dei dati");
      }
      const result = await response.json();
      console.log("Dati salvati con successo nel DB:", result);
      alert("Sottoscrittore salvato correttamente!");
    } catch (error) {
      console.error("Errore:", error);
      alert("Si è verificato un errore durante il salvataggio.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
        {/* Header / Tabs simulate */}
        <div className="flex border-b border-slate-100 px-6 pt-6 gap-3 bg-slate-50/50">
          <button className="px-5 py-2.5 text-sm font-semibold text-blue-600 bg-white rounded-2xl shadow-sm border border-slate-100">
            Dati Principali
          </button>
          <button className="px-5 py-2.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition">
            Curriculum Formativo
          </button>
          <button className="px-5 py-2.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition">
            Esami
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-8">
          {/* Sezione: Informazioni Personali & Documento */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Informazioni Personali */}
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
                  <option value="M">uomo</option>
                  <option value="F">donna</option>
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
                  className="w-full py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs uppercase tracking-wider rounded-2xl transition"
                >
                  Ricopia dati residenza in domicilio
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
                    Indirizzo
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

          {/* Sezione: Contatti & Pulsante Salvataggio */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-end">
            <div className="space-y-4">
              <h3 className="text-base font-bold text-slate-800 mb-4">
                Contatti
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                    Username
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
                  />
                </div>
              </div>
            </div>

            {/* Azioni finali modellate sullo stile della seconda foto */}
            <div className="flex justify-end gap-3 pt-6">
              <button
                type="button"
                className="px-6 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm rounded-2xl transition"
              >
                Cambia Riferimenti
              </button>
              <button
                type="submit"
                className="px-8 py-3.5 bg-amber-400 hover:bg-amber-500 text-slate-900 font-bold text-sm rounded-2xl shadow-sm transition flex items-center gap-2"
              >
                Salva
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
export default NuovoSottoscrittore;
