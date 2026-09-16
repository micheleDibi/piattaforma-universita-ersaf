import { cloneElement } from "react";
import { useParams } from "react-router";
import { idValido } from "../../config/routes/percorsi.js";
import PaginaNonTrovata from "../PaginaNonTrovata.jsx";

/** Un'identita diversa deve avere un form nuovo, anche navigando senza reload. */
export default function PaginaEntita({ risorsa, children }) {
  const id = useParams()[risorsa.parametro];
  if (id !== undefined && !idValido(id)) return <PaginaNonTrovata />;
  return cloneElement(children, { key: `${risorsa.elenco}/${id ?? "nuovo"}` });
}
