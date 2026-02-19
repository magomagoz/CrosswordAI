import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreInterattivo:
    def __init__(self):
        self.dizionario = {i: [] for i in range(2, 11)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []
        self.emergenza = ["CASA", "PANE", "SOLE", "MARE", "VITA", "CUORE"]

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []

    def carica_parole(self):
        for p in self.emergenza:
            self.dizionario[len(p)].append(p.upper())
            self.set_parole.add(p.upper())
        try:
            res = requests.get("https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt", timeout=3)
            if res.status_code == 200:
                for l in res.text.splitlines():
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 10:
                        self.dizionario[len(p)].append(p)
                        self.set_parole.add(p)
        except: pass
        return True

    def salva_stato(self):
        stato = {'griglia': [r[:] for r in self.griglia], 'parole_usate': set(self.parole_usate)}
        self.storico.append(stato)

    def annulla(self):
        if self.storico:
            ultimo = self.storico.pop()
            self.griglia = ultimo['griglia']
            self.parole_usate = ultimo['parole_usate']
            return True
        return False

    def inserisci_manuale(self, r, c, valore):
        self.salva_stato()
        self.griglia[r][c] = valore

    def aggiungi_mossa_auto(self):
        self.salva_stato()
        # (Logica di ricerca incrocio semplificata per brevità, simile alla precedente)
        coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
        random.shuffle(coords)
        for r, c, o in coords:
            for l in [5, 4, 3]:
                # ... logica di verifica e inserimento ...
                # (Assicurati di usare il dizionario caricato)
                pass
        return True, "Mossa eseguita"

def main():
    st.set_page_config(page_title="Editor Cruciverba", layout="centered")
    
    if 'm' not in st.session_state:
        st.session_state.m = MotoreInterattivo()
        st.session_state.m.carica_parole()
        st.session_state.log = "Pronto."

    st.title("🧩 Editor Cruciverba Interattivo")

    # --- BARRA DELLO STRUMENTO ---
    col_str1, col_str2 = st.columns([1, 1])
    with col_str1:
        modalita = st.radio("Strumento Clic:", ["Lettera ✍️", "Casella Nera ⚫"], horizontal=True)
    with col_str2:
        if modalita == "Lettera ✍️":
            lettera_input = st.selectbox("Scegli lettera:", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ "), index=0)

    # --- AZIONI GENERALI ---
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ AUTO-RIEMPIMENTO", use_container_width=True):
            # Qui chiameresti la funzione aggiungi_mossa_auto() definita sopra
            pass
    with c2:
        if st.button("⬅️ UNDO", use_container_width=True):
            st.session_state.m.annulla()
            st.rerun()
    with col_str1: # Aggiungiamo il reset nel menu laterale o sotto
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.m.reset_griglia()
            st.rerun()

    # --- GRIGLIA INTERATTIVA ---
    # Creiamo una griglia di pulsanti
    for r in range(ROWS):
        cols = st.columns(COLS)
        for c in range(COLS):
            valore_cella = st.session_state.m.griglia[r][c]
            
            # Colore e stile in base al contenuto
            label = " " if valore_cella == " " else valore_cella
            tipo = "primary" if valore_cella == "#" else "secondary"
            
            if cols[c].button(label, key=f"btn_{r}_{c}", use_container_width=True, type=tipo):
                if modalita == "Casella Nera ⚫":
                    nuovo_val = "#" if valore_cella != "#" else " "
                    st.session_state.m.inserisci_manuale(r, c, nuovo_val)
                else:
                    st.session_state.m.inserisci_manuale(r, c, lettera_input)
                st.rerun()

    st.info(f"Log: {st.session_state.log}")

if __name__ == "__main__":
    main()
