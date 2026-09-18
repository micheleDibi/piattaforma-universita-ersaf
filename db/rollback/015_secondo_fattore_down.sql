-- Annulla la 015: i metodi registrati (authenticator, passkey) vanno persi e
-- gli utenti tornano al solo OTP email. Le verifiche in otp_contatti restano.
DROP EVENT IF EXISTS ev_pulizia_totp_pendenti;
DROP TABLE IF EXISTS auth_passkey, auth_totp, auth_mfa_utente;
