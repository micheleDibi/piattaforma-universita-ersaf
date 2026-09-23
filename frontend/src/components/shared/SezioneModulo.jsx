import {
  campiSezioneModulo,
  introSezioneModulo,
  sezioneModulo,
} from "../../config/styles/superficie";

/**
 * Sezione di un modulo lungo: titolo e descrizione a sinistra, contenuto a
 * destra. Con `griglia` il contenuto sta su una griglia di 6 colonne.
 */
export default function SezioneModulo({
  titolo,
  descrizione,
  griglia = true,
  children,
}) {
  return (
    <section className={sezioneModulo()}>
      <div className={introSezioneModulo()}>
        <h2 className="text-sm font-semibold text-testo-forte">{titolo}</h2>
        {descrizione && (
          <p className="text-sm text-testo-tenue text-pretty">{descrizione}</p>
        )}
      </div>
      <div
        className={
          griglia ? campiSezioneModulo() : "min-w-0 flex-[3_1_520px]"
        }
      >
        {children}
      </div>
    </section>
  );
}
