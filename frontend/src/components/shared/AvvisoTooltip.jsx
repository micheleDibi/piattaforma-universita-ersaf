import { useState } from "react";
import { TriangleAlert, X } from "../../config/icone.js";

export default function AvvisoTooltip({ messaggi }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!messaggi || messaggi.length === 0) return null;

  return (
    <span
      className="inline-flex items-center"
      style={{ verticalAlign: "middle" }}
    >
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="group relative inline-flex items-center focus:outline-none"
      >
        <TriangleAlert
          className="size-icona text-amber-500"
          aria-hidden="true"
        />
        <span className="sr-only">{messaggi.join(". ")}</span>

        {/* TOOLTIP DESKTOP (Mostrato solo da md: in poi) */}
        <span
          role="tooltip"
          className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 z-20 mb-2 hidden w-max max-w-xs rounded-md bg-gray-900 px-3 py-2 text-xs font-medium text-white shadow-lg md:group-hover:block md:group-focus:block"
        >
          <ul className="space-y-1">
            {messaggi.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
          <span className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </span>
      </button>

      {/* POPUP / DIALOG MOBILE (Mostrato al click su schermi piccoli) */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 md:hidden"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="w-full max-w-sm rounded-lg bg-gray-900 p-4 text-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-gray-700">
              <span className="font-semibold text-amber-400 text-sm">
                Avviso
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <ul className="space-y-2 text-xs">
              {messaggi.map((m) => (
                <li key={m}>{m}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </span>
  );
}
