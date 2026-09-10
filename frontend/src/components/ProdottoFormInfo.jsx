export default function ProdottoFormInfo({ formData, handleChange }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Codice Prodotto */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Codice Prodotto <span className="text-rose-500">*</span>
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              name="listTesta_codice"
              value={formData.listTesta_codice ?? ""}
              onChange={handleChange}
              placeholder="Inserisci o genera codice"
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Tipo Prodotto */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Tipo Prodotto (Derivato)
          </label>
          <input
            type="text"
            disabled
            value={
              formData.listino_tipo_id === 2
                ? "LAUREE (ID: 2)"
                : "CORSI (ID: 1)"
            }
            className="w-full bg-slate-100 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-500 cursor-not-allowed"
          />
        </div>

        {/* Checkbox Attivo */}
        <div className="flex items-center space-x-3 pt-2">
          <input
            type="checkbox"
            id="listino_attivoSN"
            name="listino_attivoSN"
            checked={formData.listino_attivoSN === -1}
            onChange={handleChange}
            className="w-5 h-5 text-blue-600 border-slate-300 rounded focus:ring-blue-500 cursor-pointer"
          />
          <label
            htmlFor="listino_attivoSN"
            className="text-sm font-medium text-slate-700 cursor-pointer"
          >
            Attivo
          </label>
        </div>

        {/* Università */}
        <div className="md:col-span-2">
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Università
          </label>
          <select
            name="nome_universita_id"
            value={formData.nome_universita_id ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Università --</option>
            <option value={1}>Università Telematica eCampus</option>
            <option value={2}>Link Campus University</option>
            <option value={3}>
              Scuola Superiore Universitaria di Mediazione Linguistica Lamezia
              Terme
            </option>
            <option value={4}>Avatar4University</option>
          </select>
        </div>
      </div>

      {/* Denominazione */}
      <div>
        <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
          Denominazione <span className="text-rose-500">*</span>
        </label>
        <textarea
          name="listTesta_descrizione"
          rows="3"
          value={formData.listTesta_descrizione ?? ""}
          onChange={handleChange}
          required
          className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Livello */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Livello
          </label>
          <select
            name="listTesta_livello"
            value={formData.listTesta_livello ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Livello --</option>
            <option value={1}>1</option>
            <option value={2}>2</option>
          </select>
        </div>

        {/* Modalità di Erogazione */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Modalità di Erogazione
          </label>
          <select
            name="listino_modalita_id"
            value={formData.listino_modalita_id ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Modalità --</option>
            <option value={1}>FULL ONLINE</option>
            <option value={2}>BLENDED</option>
            <option value={3}>PRESENZIALE</option>
          </select>
        </div>

        {/* Facoltà */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Facoltà
          </label>
          <select
            name="listino_facolta_id"
            value={formData.listino_facolta_id ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Facoltà --</option>
            <option value={1}>ECONOMIA</option>
            <option value={2}>GIURISPRUDENZA</option>
            <option value={3}>INGEGNERIA</option>
            <option value={4}>LETTERE</option>
            <option value={5}>PSICOLOGIA</option>
            <option value={6}>MEDIAZIONE LINGUISTICA</option>
          </select>
        </div>

        {/* Tipo di Corso / Laurea */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Tipo di Corso / Laurea
          </label>
          <select
            name="listino_tipoCorso_id"
            value={formData.listino_tipoCorso_id ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Tipo Corso --</option>
            <option value={1}>MASTER</option>
            <option value={2}>MASTER AREA SCUOLA</option>
            <option value={3}>MASTER CLASSI DI CONCORSO</option>
            <option value={4}>CORSI DI PERFEZIONAMENTO</option>
            <option value={5}>PERCORSO DOCENTI</option>
            <option value={6}>CORSI DI FORMAZIONE</option>
            <option value={7}>CORSI DI ALTA FORMAZIONE</option>
            <option value={8}>LAUREE</option>
            <option value={9}>CORSI SINGOLI</option>
            <option value={10}>CORSI SPECIALI</option>
          </select>
        </div>

        {/* Corso di Laurea */}
        <div className="md:col-span-2">
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Corso di Laurea
          </label>
          <select
            name="listino_corsoLaurea_id"
            value={formData.listino_corsoLaurea_id ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Corso di Laurea --</option>
            <option value={1}>L33 - ECONOMIA E COMMERCIO</option>
            <option value={2}>
              L15 - SCIENZE DEL TURISMO PER IL MANAGEMENT
            </option>
            <option value={3}>LM56 - SCIENZE DELL'ECONOMIA</option>
            <option value={4}>LMG01 - GIURISPRUDENZA</option>
            <option value={5}>L36 - SCIENZE POLITICHE</option>
            <option value={6}>L20 - SCIENZE DELLA COMUNICAZIONE</option>
            <option value={7}>L9 - INGEGNERIA INDUSTRIALE</option>
            <option value={8}>
              L8 - INGEGNERIA INFORMATICA E DELL'AUTOMAZIONE
            </option>
            <option value={9}>L7 - INGEGNERIA CIVILE</option>
            <option value={10}>LM33 - INGEGNERIA INDUSTRIALE</option>
            <option value={11}>LM23 - INGEGNERIA CIVILE</option>
            <option value={12}>LM32 - INGEGNERIA INFORMATICA</option>
            <option value={13}>
              L11 - LINGUE E CULTURE EUROPEE E DEL RESTO DEL MONDO
            </option>
            <option value={14}>
              LM37 - LINGUE E LETT. MODERNE E TRADUZIONE
            </option>
            <option value={15}>
              L10 - LETTERATURA, ARTE, MUSICA E SPETTACOLO
            </option>
            <option value={16}>
              LM14 - LETTERATURA, LINGUA E CULTURA ITALIANA
            </option>
            <option value={17}>L3 - DESIGN E DISCIPLINE DELLA MODA</option>
            <option value={18}>L24 - SCIENZE E TECNICHE PSICOLOGICHE</option>
            <option value={19}>LM51 - PSICOLOGIA</option>
            <option value={20}>
              L19 - SCIENZE DELL'EDUCAZIONE E DELLA FORMAZIONE
            </option>
            <option value={21}>LM85 - SCIENZE PEDAGOGICHE</option>
            <option value={22}>
              L22 - SCIENZE DELLE ATTIVITA' MOTORIE E SPORTIVE
            </option>
            <option value={23}>
              LM67 - SCIENZE DELL'ESERCIZIO FISICO PER IL BENESSERE
            </option>
            <option value={24}>L13 - SCIENZE BIOLOGICHE</option>
            <option value={25}>LMCorsiSingoli - MASTER CORSI SINGOLI</option>
            <option value={26}>
              L14 - L-14 - curriculum servizi giuridici per l'impresa
            </option>
            <option value={27}>L12 - L-12 - MEDIAZIONE LINGUISTICA</option>
            <option value={28}>
              LM94 - LM94 Traduzione Specialistica ed Interpretariato
            </option>
          </select>
        </div>

        {/* Durata Laurea */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Durata Laurea
          </label>
          <select
            name="listino_durataLaurea_id"
            value={formData.listino_durataLaurea_id ?? ""}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
          >
            <option value="">-- Seleziona Durata --</option>
            <option value={1}>TRIENNALE</option>
            <option value={2}>MAGISTRALE</option>
            <option value={3}>CICLO UNICO</option>
          </select>
        </div>
      </div>
    </div>
  );
}
