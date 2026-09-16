import IntestazionePagina from "./shared/IntestazionePagina";
import { contenutoPagina } from "../config/styles/pagina";
import PannelloPratiche from "./PannelloPratiche";

export default function Dashboard() {
  return (
    <div className={contenutoPagina()}>
      <IntestazionePagina
        titolo="Dashboard"
        descrizione="Benvenuto nell’area riservata."
      />
      <PannelloPratiche />
    </div>
  );
}
