/** Invio da desktop; a capo su mobile, con Shift o durante una composizione IME. */
export function invioDaTastiera(evento, { compatto, disabilitato }, invia) {
  if (evento.key !== "Enter" || evento.shiftKey || evento.altKey || evento.ctrlKey || evento.metaKey ||
      evento.isComposing || evento.nativeEvent?.isComposing || evento.keyCode === 229 || compatto) return;
  evento.preventDefault();
  if (!disabilitato && !evento.repeat) invia();
}
