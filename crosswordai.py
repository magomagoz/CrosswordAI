import streamlit as st
import requests
import random
import re

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreArchitetto:
    def __init__(self):
        self.dizionario = {i: [] for i in range(2, 14)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []
        
    def carica_dizionario(self):
        # Utilizzo del repository ufficiale per parole italiane
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                linee = res.text.splitlines()
                count = 0
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 12:
                        self.set_parole.add(p)
                        self.dizionario[len(p)].append(p)
                        count += 1
                return count
        except: pass
        return 0

    def salva_stato(self):
        self.storico.append({
            'griglia': [r[:] for r in self.griglia],
            'parole_usate': set(self.parole_usate)
        })

    def annulla(self):
        if self.storico:
            stato = self.storico.pop()
            self.griglia = stato['griglia']
            self.parole_usate = stato['parole_usate']
            return True
        return False

    def inserisci_parola(self, parola, r, c, orient):
        self.salva_stato()
        parola = parola.upper()
        for i in range(len(parola)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        self.parole_usate.add(parola)

    def toggle_nera(self, r, c):
        self.salva_stato()
        if self.griglia[r][c] == '#':
            self.griglia[r][c] = ' '
        else:
            self.griglia[r][c] = '#'

    def verifica_legalita(self, r, c, parola, orient):
        L = len(parola)
        if orient == 'O' and c + L > COLS: return False
        if orient == 'V' and r + L > ROWS: return False
        
        ha_incrocio = False
        for i in range(L):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            cella = self.griglia[rr][cc]
            if cella == '#': return False # Non può sovrascrivere una nera
            if cella.isalpha():
                if cella != parola[i]: return False
                ha_incrocio = True
        
        return True if (len(self.parole_usate) == 0 or ha_incrocio) else False

    def trova_incastri(self, parola):
        validi = []
        if not parola: return validi
        for r in range(ROWS):
            for c in range(COLS):
                for o in ['O', 'V']:
                    if self.verifica_legalita(r, c, parola, o):
                        validi.append({'r': r, 'c': c, 'o': o})
        return validi

def main():
    st.set_page_config(page_title="Editor Cruciverba 13x9", layout="wide")
    
    if 'm' not in st.session_state:
        st.session_state.m = MotoreArchitetto()
        st.session_state.caricato = False

    st.title("🧩 Editor Cruciverba Professionale 13x9")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Pannello Controllo")
        
        if not st.session_state.caricato:
            if st.button("📚 CARICA DIZIONARIO"):
                n = st.session_state.m.carica_dizionario()
                if n > 0:
                    st.session_state.caricato = True
                    st.success(f"Dizionario caricato: {n} parole!")
                else:
                    st.error("Errore nel download.")
        else:
            st.success("✅ Dizionario Pronto")

        st.divider()
        
        # Modalità di interazione
        modo = st.radio("Cosa vuoi fare?", ["Inserisci Parole ✍️", "Piazza Caselle Nere ⚫"])
        
        st.divider()
        
        if modo == "Inserisci Parole ✍️":
            parola_input = st.text_input("Parola da incastrare:").upper()
            if parola_input:
                opzioni = st.session_state.m.trova_incastri(parola_input)
                if opzioni:
                    st.info(f"Trovate {len(opzioni)} posizioni.")
                    scelta = st.selectbox("Scegli dove metterla:", range(len(opzioni)), 
                                        format_func=lambda x: f"{opzioni[x]['o']} - Riga {opzioni[x]['r']+1}, Col {opzioni[x]['c']+1}")
                    if st.button("🚀 INSERISCI"):
                        p = opzioni[scelta]
                        st.session_state.m.inserisci_parola(parola_input, p['r'], p['c'], p['o'])
                        st.rerun()
                else:
                    st.warning("Nessun incastro possibile per questa parola.")
        
        st.divider()
        if st.button("⬅️ ANNULLA ULTIMA AZIONE"):
            if st.session_state.m.annulla():
                st.rerun()

    # --- AREA GRIGLIA ---
    st.markdown("### Clicca sulle caselle per modificarle" if modo == "Piazza Caselle Nere ⚫" else "### Visualizzazione Schema")
    
    for r in range(ROWS):
        cols = st.columns([1]*COLS)
        for c in range(COLS):
            valore = st.session_state.m.griglia[r][c]
            
            # Colore e stile del bottone basato sul contenuto
            if valore == '#':
                btn_type = "primary" # Bottone scuro
                label = " "
            elif valore.isalpha():
                btn_type = "secondary"
                label = valore
            else:
                btn_type = "secondary"
                label = " "

            # Il click funziona solo in modalità "Caselle Nere"
            if cols[c].button(label, key=f"cell_{r}_{c}", use_container_width=True, type=btn_type):
                if modo == "Piazza Caselle Nere ⚫":
                    st.session_state.m.toggle_nera(r, c)
                    st.rerun()
                else:
                    st.toast("Passa alla modalità 'Caselle Nere' per modificare i neri!", icon="⚠️")

    st.divider()
    st.write(f"**Parole in griglia ({len(st.session_state.m.parole_usate)}):** " + ", ".join(st.session_state.m.parole_usate))

if __name__ == "__main__":
    main()
