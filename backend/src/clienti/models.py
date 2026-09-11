from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Date, text
from datetime import  date
from src.database import Base 
from typing import Optional, List
from src.clienti.schemas import SessoEnum, TipoDocumentoEnum


class Cliente(Base):
    __tablename__= "clienti"

    # Le colonne rispecchiano la DDL reale. Le differenze non erano teoriche:
    # OGNI colonna NOT NULL di questa tabella ha un DEFAULT nel database ('' ,
    # 0, '1999-12-31'), e il modello non ne dichiarava nessuno. SQLAlchemy
    # include nella INSERT le colonne non-nullable senza default, scrivendoci
    # NULL: bastava non compilare il telefono perche' l'intera creazione
    # fallisse con un IntegrityError, cioe' un 500. Con server_default la
    # colonna viene omessa e il DEFAULT della tabella fa il suo lavoro.
    cliente_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Nessun unique: il database non ce l'ha.
    cliente_codice: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("''"))
    # Mappata solo ora: esiste nella tabella e mancava del tutto nel modello.
    cliente_codice_fiscale: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cliente_nome: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_cognome: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_email: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_telefono: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_pec: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cliente_indirizzo: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_civico: Mapped[str] = mapped_column(String(45), nullable=False, server_default=text("''"))
    cliente_citta: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_CAP: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("''"))
    cliente_provincia: Mapped[str] = mapped_column(String(45), nullable=False, server_default=text("''"))
    # DEFAULT NULL nel database, non NOT NULL come dichiarava il modello.
    cliente_cellulare: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    #Relazione
    utente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("utenti.utente_id"), nullable=False, server_default=text("1")
    )
    cliente_luogoNascita: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_provinciaNascita: Mapped[str] = mapped_column(String(45), nullable=False, server_default=text("''"))
    cliente_dataNascita: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("'1999-12-31'"))
    cliente_cittadinanza: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))

    #Enum
    cliente_tipoDocumento: Mapped[TipoDocumentoEnum] = mapped_column(
        String(255), nullable=False, server_default=text("''")
    )

    cliente_documento: Mapped[str] = mapped_column(String(45), nullable=False, server_default=text("''"))
    cliente_comuneRilascio: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    cliente_dataRilascio: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("'1999-12-31'"))
    cliente_dataScadenzaDocumento: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("'1999-12-31'")
    )

    #Enum
    cliente_sesso: Mapped[SessoEnum] = mapped_column(String(45), nullable=False, server_default=text("''"))

    cliente_indirizzoDomicilio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cliente_civicoDomicilio: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    cliente_cittaDomicilio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cliente_CAPDomicilio: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    cliente_provinciaDomicilio: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    #Relazione
    cliente_ruolo: Mapped[int] = mapped_column(
        ForeignKey("ruoli.ruolo_id"), nullable=False, server_default=text("0")
    )
    cliente_gg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attuatore_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    #Relazione
    azienda_id: Mapped[Optional[int]] = mapped_column(ForeignKey("aziende.azienda_id"), nullable=True)
    tessera_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cliente_abilPraticheUniv: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    cliente_pathCertificato: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cliente_abilitazione_ecampus: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    cliente_abilitazione_link_campus: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    # DEFAULT -1 nel database, non 0: il modello diceva il falso. Il codice
    # passa sempre un valore esplicito, quindi il default non entra mai in
    # gioco - ma il modello deve descrivere la tabella, non le intenzioni.
    cliente_abilitazione_corsi_speciali: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("-1"))
    cliente_abilitazione_a4u: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("-1"))

    utente: Mapped["Utente"] = relationship("Utente", foreign_keys=[utente_id], back_populates="clienti")
    ruolo: Mapped["Ruolo"] = relationship(back_populates="clienti")
    azienda: Mapped[Optional["Azienda"]]= relationship(back_populates="clienti")
    universita: Mapped[List["Universita"]] = relationship("Universita", back_populates="cliente")
    pratiche: Mapped[List["Pratica"]] = relationship("Pratica", back_populates="cliente")

    @property
    def curriculum(self) -> Optional["Universita"]:
        """La riga `universita` da mostrare come "il" curriculum formativo.

        La relazione e' correttamente una lista: 4.000 righe su 3.558 clienti
        distinti, con 132 clienti che ne hanno piu' di una. Il resto del
        sistema la tratta come 1:1, quindi qui si sceglie la piu' recente per
        universita_id. Se la regola giusta fosse un'altra, si cambia solo qui.
        """
        return max(self.universita, key=lambda u: u.universita_id, default=None)