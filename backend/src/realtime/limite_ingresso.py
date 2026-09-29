"""Bucket per connessione: i controlli ACK non consumano il budget chat."""

import time
from dataclasses import dataclass


@dataclass
class Bucket:
    capacita: int
    ricarica: int
    ultimo: float
    gettoni: float = 0

    def consuma(self, adesso):
        self.gettoni = min(self.capacita, self.gettoni + max(0, adesso - self.ultimo) * self.ricarica)
        self.ultimo = adesso
        if self.gettoni < 1:
            return False
        self.gettoni -= 1
        return True


class LimiteIngresso:
    SOGLIE = dict(
        ALL=(100, 50),
        CHAT=(20, 10),
        TYPING=(30, 15),
        LIST_USERS=(5, 1),
        ACK=(60, 30),
        OTHER=(10, 2),
    )

    def __init__(self, orologio=time.monotonic):
        self.orologio, self.violazioni = orologio, 0
        self.buckets = {k: Bucket(cap, rate, orologio(), cap) for k, (cap, rate) in self.SOGLIE.items()}

    def consenti(self, envelope):
        canale, tipo = envelope.get("channel"), envelope.get("payload", {}).get("type")
        categoria = (
            "ACK"
            if canale == "system"
            else tipo
            if canale == "chat" and tipo in ("CHAT", "TYPING", "LIST_USERS")
            else "OTHER"
        )
        adesso = self.orologio()
        ok = self.buckets["ALL"].consuma(adesso) and self.buckets[categoria].consuma(adesso)
        self.violazioni = 0 if ok else self.violazioni + 1
        return ok, self.violazioni >= 3
