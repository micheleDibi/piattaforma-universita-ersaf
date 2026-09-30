"""Riduce la vita dei buffer sensibili controllati dall'applicazione.

Le copie interne dell'interprete/provider restano sotto il loro controllo;
non si promette una cancellazione fisica dell'intera memoria del processo.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def cancella(buffer):
    if buffer is not None:
        buffer[:] = b"\0" * len(buffer)


def decifra(chiave, nonce, cifrato, aad):
    buffer = bytearray(len(cifrato) - 16 + 15)
    try:
        decodifica = Cipher(algorithms.AES(chiave), modes.GCM(nonce, cifrato[-16:])).decryptor()
        decodifica.authenticate_additional_data(aad)
        scritti = decodifica.update_into(cifrato[:-16], buffer)
        decodifica.finalize()
        del buffer[scritti:]
        return buffer
    except Exception:
        cancella(buffer)
        raise
