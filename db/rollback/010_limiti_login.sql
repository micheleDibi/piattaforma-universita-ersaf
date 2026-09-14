-- Rimuove soltanto i contatori del login; non modifica account o sessioni.
DROP EVENT IF EXISTS ev_auth_login_pulizia;
DROP TABLE IF EXISTS auth_login_limite;
