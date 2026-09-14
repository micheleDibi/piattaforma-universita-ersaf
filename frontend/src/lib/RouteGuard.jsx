import { Navigate, Outlet } from "react-router";
import { leggiToken } from "./sessione";

/**
 * Senza token di sessione, nessuna pagina applicativa deve essere
 * raggiungibile a URL diretto. Con "nazionale" il caso e' concreto: prima
 * della verifica OTP non esiste alcun token, quindi qualunque rotta protetta
 * deve rimandare al login.
 */
function RouteGuard() {
  if (!leggiToken()) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}

export default RouteGuard;
