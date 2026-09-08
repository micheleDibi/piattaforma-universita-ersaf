from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

from src.comune.flag_legacy import a_flag_legacy, a_flag_legacy_uno

# Le cinque colonne booleane del curriculum, con la convenzione di ciascuna.
# Vedi src/comune/flag_legacy.py per i conteggi sui dati reali.
CAMPI_FLAG_MENO_UNO = (
    "universita_iscrizioneAltraUniversita",
    "universita_attivita_professionalizzanti",
    "universita_corsi_di_formazione",
    "universita_altre_attivita_certificate",
)
CAMPO_FLAG_UNO = "universita_immatricolato"


class UniversitaBase(BaseModel):
    universita_immatricolato: Optional[int] = 0
    universita_data_immatricolazione: Optional[date] = None
    universita_riforma: Optional[str] = None
    universita_conclusione: Optional[str] = None
    universita_data_conclusione: Optional[date] = None
    universita_iscrizioneAltraUniversita: Optional[int] = 0
    universita_diploma: Optional[str] = None
    universita_istituto: Optional[str] = None
    universita_via_istituto: Optional[str] = None
    universita_citta_istituto: Optional[str] = None
    universita_provincia_istituto: Optional[str] = None
    universita_anno_scolastico: Optional[str] = None
    universita_votoRicevuto_diploma: Optional[int] = None
    universita_votoMassimo_diploma: Optional[int] = None
    universita_istituto_ai: Optional[str] = None
    universita_citta_istituto_ai: Optional[str] = None
    universita_provincia_istituto_ai: Optional[str] = None
    universita_via_istituto_ai: Optional[str] = None
    universita_anno_scolastico_ai: Optional[str] = None
    universita_votoRicevuto_ai: Optional[int] = None
    universita_votoMassimo_ai: Optional[int] = None
    universita_titolo_universitario: Optional[str] = None
    universita_materia_titolo: Optional[str] = None
    universita_universita_titolo: Optional[str] = None
    universita_data_titolo: Optional[date] = None
    universita_votoRicevuto_titolo: Optional[int] = None
    universita_votoMassimo_titolo: Optional[int] = None
    universita_materia_pl1: Optional[str] = None
    universita_istituto_pl1: Optional[str] = None
    universita_data_pl1: Optional[date] = None
    universita_materia_pl2: Optional[str] = None
    universita_istituto_pl2: Optional[str] = None
    universita_data_pl2: Optional[date] = None
    universita_materia_ats1: Optional[str] = None
    universita_istituto_ats1: Optional[str] = None
    universita_data_ats1: Optional[date] = None
    universita_materia_ats2: Optional[str] = None
    universita_istituto_ats2: Optional[str] = None
    universita_data_ats2: Optional[date] = None
    universita_attivita_professionalizzanti: Optional[int] = 0
    universita_corsi_di_formazione: Optional[int] = 0
    universita_altre_attivita_certificate: Optional[int] = 0
    cliente_id: Optional[int] = None
    universita_ateneoNullaosta: Optional[str] = None
    universita_percentualeInvalidita: Optional[int] = None
    universita_tipoInvalidita: Optional[str] = None
    universita_professione: Optional[str] = None
    universita_data_professione: Optional[date] = None
    universita_luogo_professione: Optional[str] = None
    universita_sessione_professione: Optional[str] = None
    universita_annoSessione_professione: Optional[int] = None  # Corretto a int come nel DB
    universita_voto_professione: Optional[int] = None
    universita_qualifica_professionale: Optional[str] = None
    universita_data_qualifica: Optional[date] = None
    universita_luogo: Optional[str] = None
    universita_corrispondenza: Optional[str] = None
    universita_albo: Optional[str] = None
    universita_forzeDellOrdine: Optional[str] = None
    universita_createBy: Optional[int] = None
    universita_updateBy: Optional[int] = None
    universita_universitaConclusione: Optional[str] = None
    universita_cittaUniConclusione: Optional[str] = None
    universita_provinciaConclusione: Optional[str] = None
    universita_attIscritto_tipo: Optional[str] = None
    universita_attIscritto_altro: Optional[str] = None
    universita_attIscritto_classeLaurea: Optional[str] = None
    universita_attIscritto_denominazione: Optional[str] = None
    universita_attIscritto_universita: Optional[str] = None
    universita_attIscritto_citta: Optional[str] = None
    universita_attIscritto_provincia: Optional[str] = None
    universita_attIscritto_annoIscrizione: Optional[str] = None
    universita_attIscritto_modalita: Optional[str] = None


    # I validatori stanno qui e non nei router: UniversitaBase e' ereditata da
    # UniversitaCreate, UniversitaUpdate, Universita e da
    # ClienteConUtenteCreate, quindi ogni percorso di scrittura e di lettura
    # passa di qui senza doversene ricordare. Prima la conversione viveva in
    # clienti/routers.py, cioe' in uno solo dei tre percorsi, e sbagliava.
    @field_validator(*CAMPI_FLAG_MENO_UNO, mode="before")
    @classmethod
    def _normalizza_flag(cls, v):
        return a_flag_legacy(v)

    @field_validator(CAMPO_FLAG_UNO, mode="before")
    @classmethod
    def _normalizza_flag_immatricolato(cls, v):
        return a_flag_legacy_uno(v)


class UniversitaCreate(UniversitaBase):
    pass


class UniversitaUpdate(UniversitaBase):
    pass


class Universita(UniversitaBase):
    universita_id: int
    universita_createDate: Optional[date] = None
    universita_updateDate: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


# Lo schema di risposta si chiama `Universita` come il modello SQLAlchemy, e
# per questo universita/routers.py deve importare il modello con l'alias
# UniversitaModel. Il nome giusto e' questo; l'altro resta per non rompere gli
# import esistenti.
UniversitaResponse = Universita
