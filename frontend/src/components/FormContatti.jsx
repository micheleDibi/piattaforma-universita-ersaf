import { useState } from "react";
import VerificaContattoModal from "./VerificaContattoModal";

export default function FormContatti({
  formData,
  handleChange,
  clienteId,
  emailVerificata,
  onEmailVerificata,
}) {
  const [modaleAperto, setModaleAperto] = useState(false);

  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-slate-800 mb-4">Contatti</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Email
            </label>
            {clienteId &&
              (emailVerificata ? (
                <span className="text-xs font-semibold text-emerald-600">
                  ✓ Verificata
                </span>
              ) : (
                <button
                  type="button"
                  onClick={() => setModaleAperto(true)}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-800"
                >
                  Verifica
                </button>
              ))}
          </div>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
          />
          {clienteId && !emailVerificata && (
            <p className="mt-1 text-xs text-amber-600">
              Email non ancora verificata.
            </p>
          )}
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
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Cellulare
            </label>
            {clienteId && (
              <span className="text-xs font-semibold text-slate-400">
                Verifica presto disponibile
              </span>
            )}
          </div>
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

      {modaleAperto && (
        <VerificaContattoModal
          clienteId={clienteId}
          tipo="email"
          etichetta={formData.email}
          onVerificato={() => {
            setModaleAperto(false);
            onEmailVerificata?.();
          }}
          onChiudi={() => setModaleAperto(false)}
        />
      )}
    </div>
  );
}
