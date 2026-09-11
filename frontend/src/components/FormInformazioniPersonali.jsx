import { campo, etichetta } from "../config/styles/campo";
import { titoloSezione } from "../config/styles/superficie";

export default function FormInformazioniPersonali({ formData, handleChange }) {
  return (
    <div className="space-y-4">
      <h3 className={titoloSezione()}>
        Informazioni Personali
      </h3>

      <div>
        <label className={etichetta()}>
          Codice Fiscale
        </label>
        <input
          type="text"
          name="codiceFiscale"
          value={formData.codiceFiscale}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
        />
      </div>

      <div>
        <label className={etichetta()}>
          Genere
        </label>
        <select
          name="genere"
          value={formData.genere}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
        >
          <option value="">Seleziona il genere</option>
          <option value="uomo">uomo</option>
          <option value="donna">donna</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={etichetta()}>
            Nome
          </label>
          <input
            type="text"
            name="nome"
            value={formData.nome}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
        <div>
          <label className={etichetta()}>
            Cognome
          </label>
          <input
            type="text"
            name="cognome"
            value={formData.cognome}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
      </div>

      <div>
        <label className={etichetta()}>
          Cittadinanza
        </label>
        <input
          type="text"
          name="cittadinanza"
          value={formData.cittadinanza}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
        />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2">
          <label className={etichetta()}>
            Luogo di Nascita
          </label>
          <input
            type="text"
            name="luogoDiNascita"
            value={formData.luogoDiNascita}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
        <div>
          <label className={etichetta()}>
            Prov.
          </label>
          <input
            type="text"
            name="provDiNascita"
            value={formData.provDiNascita}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
          />
        </div>
      </div>

      <div>
        <label className={etichetta()}>
          Data di Nascita
        </label>
        <input
          type="date"
          name="dataDiNascita"
          value={formData.dataDiNascita}
          onChange={handleChange}
          className={`${campo("comodo")} transition`}
        />
      </div>
    </div>
  );
}
