import { TELA_FIRMA as tela } from "../config/styles/firma.js";

export function puntoFirma(evento, area) {
  return {
    x: Math.min(tela.larghezza, Math.max(0, (evento.clientX - area.left) / area.width * tela.larghezza)),
    y: Math.min(tela.altezza, Math.max(0, (evento.clientY - area.top) / area.height * tela.altezza)),
  };
}
export function disegnaTratto(canvas, precedente, prossimo) {
  const ctx = canvas.getContext("2d");
  ctx.strokeStyle = getComputedStyle(canvas).getPropertyValue("--color-testo-forte").trim() || "CanvasText";
  ctx.lineWidth = tela.tratto;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  ctx.moveTo(precedente.x, precedente.y);
  ctx.lineTo(prossimo.x, prossimo.y);
  ctx.stroke();
}
