import { useRef, useState } from "react";
import { TELA_FIRMA, STILI_FIRMA as stili } from "../../config/styles/firma.js";
import { TESTI_FIRMA as testi } from "../../config/testi/firma.js";
import { pulsante } from "../../config/styles/pulsante.js";
import { puntoFirma, disegnaTratto } from "../../lib/trattoFirma.js";

export default function DisegnoFirma({ occupato, onSalva, onAnnulla }) {
  const canvas = useRef(null);
  const tratto = useRef(null);
  const [disegnata, setDisegnata] = useState(false);
  const inizia = evento => {
    if (occupato || evento.button !== 0 || tratto.current) return;
    evento.currentTarget.setPointerCapture(evento.pointerId);
    tratto.current = { id: evento.pointerId, punto: puntoFirma(evento, evento.currentTarget.getBoundingClientRect()) };
  };
  const continua = evento => {
    if (occupato || tratto.current?.id !== evento.pointerId) return;
    const punto = puntoFirma(evento, evento.currentTarget.getBoundingClientRect());
    disegnaTratto(canvas.current, tratto.current.punto, punto);
    tratto.current.punto = punto;
    setDisegnata(true);
  };
  const termina = evento => {
    if (tratto.current?.id === evento.pointerId) tratto.current = null;
  };
  const pulisci = () => {
    canvas.current.getContext("2d").clearRect(0, 0, TELA_FIRMA.larghezza, TELA_FIRMA.altezza);
    tratto.current = null;
    setDisegnata(false);
  };
  return <>
    <p className={stili.nota}>{testi.istruzioni}</p>
    <canvas ref={canvas} width={TELA_FIRMA.larghezza} height={TELA_FIRMA.altezza}
      className={stili.tela} aria-label={testi.area} onPointerDown={inizia} onPointerMove={continua}
      onPointerUp={termina} onPointerCancel={termina} onLostPointerCapture={termina} />
    <div className={stili.azioni}>
      <button type="button" disabled={occupato || !disegnata} className={pulsante("secondario")} onClick={pulisci}>{testi.pulisci}</button>
      <button type="button" disabled={occupato} className={pulsante("secondario")} onClick={onAnnulla}>{testi.annulla}</button>
      <button type="button" disabled={occupato || !disegnata} className={pulsante()} onClick={() => onSalva(canvas.current.toDataURL("image/png"))}>{occupato ? testi.salvataggio : testi.salva}</button>
    </div>
  </>;
}
