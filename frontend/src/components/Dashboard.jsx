import IntestazionePagina from "./shared/IntestazionePagina";
import { NOME_APPLICAZIONE } from "../config/routes/rotte";
import { contenutoPagina } from "../config/styles/pagina";

export default function Dashboard() {
  return (
    <div className={contenutoPagina()}>
      <IntestazionePagina
        titolo="Dashboard"
        descrizione={`Benvenuto nella ${NOME_APPLICAZIONE}.`}
      />
    </div>
  );
}
