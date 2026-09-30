"""Risorse del processo, create e chiuse insieme al lifespan FastAPI."""

from src.chat_pratiche.configurazione import configurazione
from src.realtime.esecutore import Esecutore
from src.realtime.uscita import BudgetUscita


class Risorse:
    def __init__(self):
        c = configurazione()
        self.comandi = Esecutore(
            c.realtime_command_workers,
            c.realtime_command_queue,
            c.realtime_commands_per_user,
        )
        self.letture = Esecutore(8, 256, 2)
        self.uscita = BudgetUscita(c.realtime_outbound_global_queue_bytes)

    async def chiudi(self):
        await self.comandi.chiudi()
        await self.letture.chiudi()
