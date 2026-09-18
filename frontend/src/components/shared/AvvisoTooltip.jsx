import { TriangleAlert } from "../../config/icone.js";

export default function AvvisoTooltip({ messaggi }) {
  if (!messaggi || messaggi.length === 0) return null;

  return (
    <span
      className="group relative inline-flex items-center"
      style={{ verticalAlign: "middle", transform: "translateY(-1px)" }}
      tabIndex={0}
    >
      <TriangleAlert className="size-icona text-amber-500" aria-hidden="true" />
      <span className="sr-only">{messaggi.join(". ")}</span>

      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-full right-0 z-20 mb-2 hidden w-max max-w-xs rounded-md bg-gray-900 px-3 py-2 text-xs font-medium text-white shadow-lg group-hover:block group-focus:block"
      >
        <ul className="space-y-1">
          {messaggi.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
        <span className="absolute right-3 top-full border-4 border-transparent border-t-gray-900" />
      </span>
    </span>
  );
}
