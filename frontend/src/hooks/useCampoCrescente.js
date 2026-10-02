import { useLayoutEffect, useRef } from "react";

/** Misura il contenuto, entro min/max del tema, anche se cambia la larghezza. */
export function useCampoCrescente(testo) {
  const campo = useRef(null);
  useLayoutEffect(() => {
    const el = campo.current;
    const ridimensiona = () => {
      el.style.height = "auto";
      const bordi = el.offsetHeight - el.clientHeight;
      el.style.height = `${Math.min(el.scrollHeight + bordi, parseFloat(getComputedStyle(el).maxHeight))}px`;
    };
    ridimensiona();
    let larghezza = el.clientWidth;
    const osservatore = new ResizeObserver(() => {
      if (el.clientWidth === larghezza) return;
      larghezza = el.clientWidth;
      ridimensiona();
    });
    osservatore.observe(el);
    return () => osservatore.disconnect();
  }, [testo]);
  return campo;
}
