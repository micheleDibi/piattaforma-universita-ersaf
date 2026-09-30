import { TESTI_CHAT as testi } from "../config/testi/chatPratica.js";

export function unisciMessaggi(attuali, nuovi) {
  return [...new Map([...attuali, ...nuovi].map(m => [m.id, m])).values()]
    .sort((a, b) => BigInt(a.id) < BigInt(b.id) ? -1 : BigInt(a.id) > BigInt(b.id) ? 1 : 0);
}

/** Stato di una sola conversazione. Bozza/cifrato restano esclusivamente in memoria. */
export class ConversazionePratica {
  constructor(id, api) {
    this.id = id; this.api = api; this.listeners = new Set();
    this.stato = { elementi: [], caricamento: true, errore: "", connessione: "connessione", altri: false, precedente: false, invio: null };
    this.consegne = new Map(); this.tentativi = 0; this.serie = 0;
  }
  snapshot = () => this.stato;
  subscribe = fn => { this.listeners.add(fn); return () => this.listeners.delete(fn); };
  cambia(patch) { this.stato = { ...this.stato, ...patch }; this.listeners.forEach(fn => fn()); }
  start() {
    this.controller = new AbortController(); this.attiva = true; this.serie++; this.caricamento = false;
    this.aggiorna().then(ok => { if (ok && this.attiva) this.collega(); });
  }
  stop() {
    this.attiva = false; this.serie++; this.controller?.abort();
    clearTimeout(this.timer); clearTimeout(this.timerInvio); const socket = this.socket; this.socket = null; socket?.close();
  }
  async aggiorna(precedenti = false) {
    const serie = this.serie;
    if (this.caricamento) { this.daAggiornare = true; return false; }
    this.caricamento = true;
    if (precedenti) this.cambia({ precedente: true });
    try {
      let pagina = await this.api.leggi(this.id, precedenti ? this.cursore : null, this.controller.signal);
      if (!this.attiva || serie !== this.serie) return false;
      let nuovi = pagina.elementi;
      const ultimo = this.stato.elementi.at(-1)?.id;
      // Dopo una disconnessione recupera anche il tratto tra l'ultima pagina e
      // l'ultimo messaggio noto: nessun buco silenzioso nello storico.
      while (!precedenti && ultimo && pagina.altri && nuovi.length &&
          BigInt(nuovi.at(-1).id) > BigInt(ultimo) && !nuovi.some(m => BigInt(m.id) <= BigInt(ultimo))) {
        pagina = await this.api.leggi(this.id, pagina.cursore, this.controller.signal);
        nuovi = [...nuovi, ...pagina.elementi];
      }
      if (!this.attiva || serie !== this.serie) return false;
      if (precedenti || !ultimo) { this.cursore = pagina.cursore; this.cambia({ altri: pagina.altri }); }
      const elementi = unisciMessaggi(this.stato.elementi, nuovi);
      this.cambia({ elementi, errore: "", caricamento: false });
      for (const [id, consegna] of this.consegne) {
        if (elementi.some(m => m.id === id) && this.socket?.readyState === 1) {
          this.socket.send(JSON.stringify({ tipo: "conferma", consegna })); this.consegne.delete(id);
        }
      }
      return true;
    } catch (e) {
      if (this.attiva && serie === this.serie) this.cambia({ errore: e.message || testi.errore, caricamento: false });
      return false;
    } finally {
      if (this.attiva && serie === this.serie) {
        this.caricamento = false;
        this.cambia({ precedente: false });
        if (this.daAggiornare) { this.daAggiornare = false; this.aggiorna(); }
      }
    }
  }
  async collega() {
    const serie = this.serie;
    try {
      const socket = await this.api.socket(this.id);
      if (!this.attiva || serie !== this.serie) { socket.close(); return; }
      this.socket = socket;
      socket.onmessage = evento => {
        if (!this.attiva || this.socket !== socket) return;
        let dato; try { dato = JSON.parse(evento.data); } catch { return; }
        if (dato.tipo === "connesso") {
          this.tentativi = 0; this.cambia({ connessione: "connesso" }); this.aggiorna();
          if (this.stato.invio?.cifrato) this.riprovaInvio();
        } else if (dato.tipo === "messaggio") {
          if (dato.consegna) this.consegne.set(dato.id, dato.consegna);
          if (dato.clientMessageId === this.stato.invio?.clientMessageId) {
            clearTimeout(this.timerInvio); this.cambia({ invio: null });
          }
          this.aggiorna();
        } else if (dato.tipo === "errore" && this.stato.invio &&
          (!dato.clientMessageId || dato.clientMessageId === this.stato.invio.clientMessageId)) {
          clearTimeout(this.timerInvio);
          this.cambia({ invio: { ...this.stato.invio, errore: dato.messaggio || testi.invioFallito, ricifra: dato.ricifra === true } });
        }
      };
      socket.onclose = () => {
        if (this.socket !== socket || !this.attiva) return;
        this.consegne.clear(); this.riconnetti();
      };
      socket.onerror = () => socket.close();
    } catch { if (this.attiva && serie === this.serie) this.riconnetti(); }
  }
  riconnetti() {
    this.cambia({ connessione: "disconnesso" });
    clearTimeout(this.timer);
    this.timer = setTimeout(async () => {
      // L'HTTP offre errori leggibili e gestisce il 401 nella sessione comune.
      if (await this.aggiorna()) this.collega(); else if (this.attiva) this.riconnetti();
    }, Math.min(30000, 1000 * 2 ** Math.min(this.tentativi++, 5)));
  }
  async invia(testo) {
    if (this.stato.invio || !testo.trim() || this.stato.connessione !== "connesso") return false;
    if (new TextEncoder().encode(testo).length > 1000) throw new Error(testi.troppoLungo);
    const serie = this.serie;
    const clientMessageId = crypto.randomUUID();
    this.cambia({ invio: { testo, clientMessageId } });
    try {
      const preparato = await this.api.prepara(this.id, testo, clientMessageId, this.controller.signal);
      if (!this.attiva || serie !== this.serie) return false;
      this.cambia({ invio: { testo, ...preparato } }); this.riprovaInvio(); return true;
    } catch (e) {
      if (this.attiva && serie === this.serie) this.cambia({ invio: null });
      throw e;
    }
  }
  async riprovaInvio() {
    let invio = this.stato.invio;
    if (!invio?.cifrato || this.socket?.readyState !== 1) return;
    if (this.preparazione) return;
    if (invio.ricifra) {
      // Java emette key_epoch_stale solo dopo avere escluso un comando gia
      // salvato e annullato la transazione: qui e' sicuro cambiare ciphertext.
      this.preparazione = true;
      const serie = this.serie;
      try {
        const nuovo = await this.api.prepara(this.id, invio.testo, invio.clientMessageId, this.controller.signal);
        if (!this.attiva || serie !== this.serie) return;
        invio = { ...invio, ...nuovo, ricifra: false };
        this.cambia({ invio });
      } catch (e) {
        if (this.attiva && serie === this.serie) this.cambia({ invio: { ...invio, errore: e.message } });
        return;
      } finally { this.preparazione = false; }
      if (this.socket?.readyState !== 1) return;
    }
    // Riusa anche il ciphertext: rigenerarlo con lo stesso ID rompe l'idempotenza Java.
    try { this.socket.send(JSON.stringify({ tipo: "invia", clientMessageId: invio.clientMessageId, cifrato: invio.cifrato })); }
    catch { this.cambia({ invio: { ...invio, errore: testi.invioFallito } }); return; }
    this.cambia({ invio: { ...invio, errore: "" } });
    clearTimeout(this.timerInvio);
    this.timerInvio = setTimeout(() => {
      if (this.stato.invio) this.cambia({ invio: { ...this.stato.invio, errore: testi.invioFallito } });
    }, 15000);
  }
}
