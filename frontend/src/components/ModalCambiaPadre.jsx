import { useEffect, useState } from "react";

export default function ModalCambiaPadre({ isOpen, onClose, onSelectPadre }) {
  const [attuatori, setAttuatori] = useState([]);
  const [loadingAttuatori, setLoadingAttuatori] = useState(false);
  const [searchTermAttuatore, setSearchTermAttuatore] = useState("");
  const [selectedRuoloAttuatore, setSelectedRuoloAttuatore] = useState("");

  // Funzione per scaricare gli attuatori nel modale
  const fetchAttuatori = async (search = "", ruolo = "") => {
    setLoadingAttuatori(true);
    const token = localStorage.getItem("sessione_token");
    const headers = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    try {
      const ruoloParam = ruolo
        ? `&ruolo_codice=${encodeURIComponent(ruolo)}`
        : "";
      const response = await fetch(
        `http://localhost:8000/clienti/?skip=0&limit=50&solo_attuatori=true${ruoloParam}&search=${encodeURIComponent(search)}`,
        { headers },
      );
      if (!response.ok) throw new Error("Errore nel recupero degli attuatori");
      const data = await response.json();
      setAttuatori(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAttuatori(false);
    }
  };

  // Quando si apre il modale, azzera i filtri e carica i dati iniziali
  useEffect(() => {
    if (isOpen) {
      setSearchTermAttuatore("");
      setSelectedRuoloAttuatore("");
      fetchAttuatori("", "");
    }
  }, [isOpen]);

  // Debounce effect per la ricerca fluida
  useEffect(() => {
    if (!isOpen) return;

    const delayDebounceFn = setTimeout(() => {
      fetchAttuatori(searchTermAttuatore, selectedRuoloAttuatore);
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTermAttuatore, selectedRuoloAttuatore, isOpen]);

  if (!isOpen) return null;

  return (
    <div style={styles.modalOverlay}>
      <div style={styles.modalContent}>
        <div style={styles.modalHeader}>
          <h3>Seleziona Nuovo Utente Padre (Attuatore)</h3>
          <button onClick={onClose} style={styles.closeButton}>
            &times;
          </button>
        </div>

        <div style={styles.modalFilters}>
          <input
            type="text"
            placeholder="Cerca per nome, cognome o azienda..."
            value={searchTermAttuatore}
            onChange={(e) => setSearchTermAttuatore(e.target.value)}
            style={styles.inputModifiable}
            autoFocus
          />
          <select
            value={selectedRuoloAttuatore}
            onChange={(e) => setSelectedRuoloAttuatore(e.target.value)}
            style={styles.select}
          >
            <option value="">Tutti i ruoli</option>
            <option value="Aderente">Aderente</option>
            <option value="Provinciale">Provinciale</option>
            <option value="Regionale">Regionale</option>
            <option value="Nazionale">Nazionale</option>
          </select>
        </div>

        <div style={styles.modalTableContainer}>
          <table style={styles.table}>
            <thead>
              <tr style={styles.trHead}>
                <th style={styles.th}>Nome</th>
                <th style={styles.th}>Cognome</th>
                <th style={styles.th}>Ruolo</th>
                <th style={styles.th}>Azienda</th>
                <th style={styles.th}>Azione</th>
              </tr>
            </thead>
            <tbody>
              {attuatori.map((att) => (
                <tr key={att.cliente_id} style={styles.tr}>
                  <td style={styles.td}>{att.cliente_nome}</td>
                  <td style={styles.td}>{att.cliente_cognome}</td>
                  <td style={styles.td}>{att.ruolo?.ruolo_codice || "-"}</td>
                  <td style={styles.td}>
                    {att.azienda?.azienda_ragione_sociale || "-"}
                  </td>
                  <td style={styles.td}>
                    <button
                      type="button"
                      onClick={() => onSelectPadre(att)}
                      style={styles.selectRowButton}
                    >
                      Seleziona
                    </button>
                  </td>
                </tr>
              ))}
              {attuatori.length === 0 && !loadingAttuatori && (
                <tr>
                  <td
                    colSpan="5"
                    style={{
                      textAlign: "center",
                      padding: "30px",
                      color: "#64748b",
                    }}
                  >
                    Nessun attuatore trovato.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loadingAttuatori && (
          <div
            style={{
              textAlign: "center",
              fontSize: "12px",
              color: "#64748b",
              marginTop: "8px",
            }}
          >
            Aggiornamento in corso...
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: "#ffffff",
    padding: "24px",
    borderRadius: "12px",
    width: "90%",
    maxWidth: "800px",
    maxHeight: "85vh",
    display: "flex",
    flexDirection: "column",
    boxShadow: "0 10px 25px rgba(0,0,0,0.2)",
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
    borderBottom: "1px solid #e2e8f0",
    paddingBottom: "10px",
  },
  closeButton: {
    background: "none",
    border: "none",
    fontSize: "24px",
    cursor: "pointer",
    color: "#64748b",
  },
  modalFilters: {
    display: "flex",
    gap: "12px",
    marginBottom: "16px",
  },
  inputModifiable: {
    padding: "12px 14px",
    backgroundColor: "#ffffff",
    border: "1px solid #cbd5e1",
    borderRadius: "8px",
    fontSize: "14px",
    color: "#0f172a",
    outline: "none",
    width: "100%",
  },
  select: {
    padding: "12px 14px",
    backgroundColor: "#ffffff",
    border: "1px solid #cbd5e1",
    borderRadius: "8px",
    fontSize: "14px",
    color: "#0f172a",
    outline: "none",
  },
  modalTableContainer: {
    overflowY: "auto",
    height: "350px",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    backgroundColor: "#ffffff",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    textAlign: "left",
    fontSize: "14px",
  },
  trHead: {
    backgroundColor: "#f8fafc",
    borderBottom: "1px solid #e2e8f0",
    position: "sticky",
    top: 0,
    zIndex: 1,
  },
  th: {
    padding: "12px",
    fontWeight: "600",
    color: "#475569",
    fontSize: "12px",
    backgroundColor: "#f8fafc",
  },
  tr: {
    borderBottom: "1px solid #e2e8f0",
  },
  td: {
    padding: "12px",
    color: "#1e293b",
  },
  selectRowButton: {
    padding: "6px 12px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    border: "none",
    borderRadius: "6px",
    fontSize: "12px",
    cursor: "pointer",
    fontWeight: "600",
  },
};
