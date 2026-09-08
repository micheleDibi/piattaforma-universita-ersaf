from datetime import date
from typing import Optional
from src.database import Base 
from sqlalchemy import Date, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import text

class Universita(Base):
    __tablename__ = "universita"

    universita_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    universita_immatricolato: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    universita_data_immatricolazione: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_riforma: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_conclusione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_conclusione: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_iscrizioneAltraUniversita: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    universita_diploma: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_istituto: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_via_istituto: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_citta_istituto: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_provincia_istituto: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_anno_scolastico: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_votoRicevuto_diploma: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_votoMassimo_diploma: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_istituto_ai: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_citta_istituto_ai: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_provincia_istituto_ai: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_via_istituto_ai: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_anno_scolastico_ai: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_votoRicevuto_ai: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_votoMassimo_ai: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_titolo_universitario: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_materia_titolo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_universita_titolo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_titolo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_votoRicevuto_titolo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_votoMassimo_titolo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_materia_pl1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_istituto_pl1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_pl1: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_materia_pl2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_istituto_pl2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_pl2: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_materia_ats1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_istituto_ats1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_ats1: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_materia_ats2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_istituto_ats2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_ats2: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_attivita_professionalizzanti: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    universita_corsi_di_formazione: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    universita_altre_attivita_certificate: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    
    # cliente_id e' NOT NULL, ma NON esiste alcuna FOREIGN KEY nel database -
    # e nemmeno un indice, pur essendo l'unica colonna con cui si cerca. La
    # ForeignKey resta perche' e' quella che definisce il join della relazione
    # lato ORM; non crea alcun vincolo e non verifica nulla, quindi
    # l'esistenza del cliente va controllata in codice.
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("clienti.cliente_id"), nullable=False)
    
    universita_ateneoNullaosta: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_percentualeInvalidita: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_tipoInvalidita: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_professione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_professione: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_luogo_professione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_sessione_professione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # CORRETTO: Nel DB è un intero (int), non stringa
    universita_annoSessione_professione: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    universita_voto_professione: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_qualifica_professionale: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_data_qualifica: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_luogo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_corrispondenza: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_albo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # CORRETTO: Nel DB è una stringa (varchar) e non un booleano
    universita_forzeDellOrdine: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # date DEFAULT NULL nel database, non CURRENT_DATE: dopo un db.refresh()
    # il valore letto era NULL e non la data di oggi, contro quanto diceva
    # il modello. Le due date le valorizza payload_universita.
    universita_createBy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_createDate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_updateBy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    universita_updateDate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    universita_universitaConclusione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_cittaUniConclusione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_provinciaConclusione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_tipo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_altro: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_classeLaurea: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_denominazione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_universita: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_citta: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_provincia: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_annoIscrizione: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    universita_attIscritto_modalita: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="universita")