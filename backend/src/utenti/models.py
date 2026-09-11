from sqlalchemy import Integer, String, Date, text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from src.database import Base 
from src.clienti.models import Cliente
from typing import Optional
import uuid
from typing import List

class Utente(Base):
    __tablename__ = "utenti"

    utente_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Nessun unique: il database non ha la UNIQUE e contiene cinque gruppi di
    # omonimi. Dichiararla qui non la crea, dice solo il falso a chi legge il
    # modello - ed e' proprio il caso che trova_utente_per_username deve
    # gestire. L'indice arriva con la migrazione 005.
    utente_username: Mapped[str] = mapped_column(String(255), nullable=False)
    # Niente index: era un indice sulla colonna delle password in chiaro.
    utente_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # date DEFAULT NULL nel database, non CURRENT_TIMESTAMP: erano annotazioni
    # non-Optional su colonne che nella pratica sono quasi sempre NULL.
    utente_ultimo_login: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    utente_ultimo_logout: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # utente_padre, utente_created_by e utente_updated_by contengono un
    # utente_id, non un cliente_id. Il database lo dice con
    # FK_utenti_utente_updated_by -> utenti(utente_id), i dati lo confermano
    # (4.767 valori su 4.767 esistono in utenti) e il codice ci scrive
    # current_utente.utente_id. Puntavano a clienti.cliente_id, e siccome i due
    # id coincidono solo in 377 clienti su 3.906 le relazioni caricavano la
    # persona sbagliata in circa il 90% dei casi, senza mai dare errore.
    utente_padre: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("utenti.utente_id"), nullable=True
    )
    utente_attivoSN: Mapped[int] = mapped_column(Integer, default=-1)
    utente_created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("utenti.utente_id"), nullable=True
    )
    utente_created_at: Mapped[date] = mapped_column(Date, default=date.today)
    utente_updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("utenti.utente_id"), nullable=True
    )
    utente_updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=text("CURRENT_TIMESTAMP"), default=datetime.now)
    utente_salt: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))

    # --- Migrazione 001: hashing delle password ------------------------------
    # Finche' utente_password_hash e' NULL, la verifica passa dalla colonna
    # legacy in chiaro. Il login converte la singola riga dell'utente che si
    # autentica (rehash pigro): nessuna operazione massiva, mai.
    #
    # ATTENZIONE: utente_password e' varchar(255) NOT NULL nel database, quindi
    # "svuotare il chiaro" significa scrivere '' e mai NULL.
    utente_password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # server_default e non default: cosi' l'INSERT non manda la colonna e il
    # DEFAULT del database — che le righe esistenti hanno gia' — resta l'unica
    # sorgente di verita'.
    utente_password_algo: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'legacy_plaintext'")
    )
    # Usato dalla query [B] della migrazione 004 come cut-off delle sessioni:
    # ogni sessione nata prima di questo istante e' da considerare revocata.
    # Per questo il rehash pigro NON lo tocca — un rehash non e' un cambio
    # password, e valorizzarlo invaliderebbe la sessione appena creata.
    utente_password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    utente_password_changed_via: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    # Relazione
    clienti: Mapped["Cliente"] = relationship(
        "Cliente", 
        foreign_keys="[Cliente.utente_id]", 
        back_populates="utente", 
        uselist=False, 
        cascade="all, delete-orphan"
    )

    # Auto-riferimenti: remote_side dice a SQLAlchemy quale lato della stessa
    # tabella e' il "uno" della molti-a-uno.
    padre: Mapped[Optional["Utente"]] = relationship(
        "Utente",
        foreign_keys=[utente_padre],
        remote_side=[utente_id],
        uselist=False,
    )

    aggiornato_da: Mapped[Optional["Utente"]] = relationship(
        "Utente",
        foreign_keys=[utente_updated_by],
        remote_side=[utente_id],
        uselist=False,
    )

    pratiche: Mapped[List["Pratica"]] = relationship(
    "Pratica", foreign_keys="Pratica.utente_id", back_populates="utente"
)

    @property
    def cliente(self) -> Optional["Cliente"]:
        """Alias leggibile di `clienti`, che e' uselist=False nonostante il nome.

        Serve agli schemi di risposta: da un utente padre si risale al nome
        della persona senza che il chiamante debba sapere che l'attributo e'
        plurale ma contiene un solo oggetto.
        """
        return self.clienti