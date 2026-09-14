START TRANSACTION;
DELETE FROM `messaggi_email` WHERE `messaggio_email_codice` = 'login_otp_nazionale';
COMMIT;