import streamlit as st
import requests
import random
from datetime import datetime

# --- CONFIGURAZIONE GRIGLIA INVERTITA ---
COLS = 9
ROWS = 13

class DizionarioItalianoCompleto:
    def __init__(self):
        self.parole_per_lunghezza = {}
    
    def carica_vocabolario(self):
        """Carica un dizionario italiano esteso da repository open source"""
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            response = requests.get(url, timeout=10)
            tutte_parole = response.text.splitlines()
            for parola in tutte_parole:
                p = parola.upper().strip()
                if p.isalpha():
                    lung = len(p)
                    if lung not in self.parole_per_lunghezza:
                        self.parole_per_lunghezza[lung] = []
                    self.parole_per_lunghezza[lung].append(p)
            return sum(len(v) for v in self.parole_per_lunghezza.values())
        except:
            return 0

    def cerca_parola(self, pattern_dict, lunghezza, exclude=None):
        candidati = self.parole_per_lunghezza.get(lunghezza, [])
        if not candidati: return None
        
        # Copia e mescola per non alterare il dizionario originale
        campionario = random.sample(candidati, min(len(candidati), 1000))
        for parola in campionario:
            if exclude and parola in exclude: continue
            if all(parola[pos] == lett for pos, lett in pattern_dict.items()):
                return parola
        return None

class Cruciverba9x13:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        # Caselle nere per schema 9 (col) x 13 (righe)
        self.nere = [
            (2,2), (2,6), 
            (4,1), (4,4), (4,7),
            (6,0), (6,2), (6,6), (6,8),
            (8,1), (8,4), (8,7),
            (10,2), (10,6)
        ]
        for r, c in self.nere:
            self.griglia[r][c] = '#'

    def genera(self):
        # 1. Riempiamo le righe orizzontali (lunghezza 9)
        for r in [0, 2, 5, 7, 9, 12]:
            pattern = {c: self.griglia[r][c] for c in range(COLS) if self.griglia[r][c] not in [' ', '#']}
            parola = self.dizionario.cerca_parola(pattern, COLS, self.parole_usate)
            if parola:
                for c in range(COLS):
                    if self.griglia[r][c] != '#':
                        self.griglia[r][c] = parola[c]
                self.parole_usate.add(parola)
        
        # 2. Riempiamo le colonne verticali (lunghezza 13)
        for c in [0, 3, 5, 8]:
            pattern = {r: self.griglia[r][c] for r in range(ROWS) if self.griglia[r][c] not in [' ', '#']}
            parola = self.dizionario.cerca_parola(pattern, ROWS, self.parole_usate)
            if parola:
                for r in range(ROWS):
                    if self.griglia[r][c] != '#':
                        self.griglia[r][c] = parola[r]
                self.parole_usate.add(parola)
        return True

    def render_html(self, mostra=True):
        html = '<table style="border-collapse: collapse; margin: auto; border: 3px solid #000;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                is_nera = self.griglia[r][c] == '#'
                bg = "#000" if is_nera else "#fff"
                txt = self.griglia[r][c] if (mostra and not is_nera) else ""
                html += f'''<td style="width:40px; height:40px; border:1px solid #000; 
                           background:{bg}; text-align:center; font-family:Arial; 
                           font-weight:bold; font-size:18px; color:black;">{txt}</td>'''
            html += '</tr>'
        return html + "</table>"

def main():
    st.set_page_config(page_title="Cruciverba 9x13", layout="centered")
    st.title("🧩 Cruciverba Verticale $9 \times 13$")

    if 'diz' not in st.session_state:
        st.session_state.diz = DizionarioItalianoCompleto()
        st.session_state.caricato = False
        st.session_state.cv = None

    if not st.session_state.caricato:
        if st.button("📥 1. CARICA DIZIONARIO ITALIANO", use_container_width=True):
            with st.spinner("Estrazione lemmi in corso..."):
                n = st.session_state.diz.carica_vocabolario()
                st.session_state.caricato = True
                st.success(f"Caricate {n} parole dal vocabolario!")
                st.rerun()
    else:
        if st.button("🎲 2. GENERA SCHEMA VERTICALE", use_container_width=True):
            cv = Cruciverba9x13(st.session_state.diz)
            cv.genera()
            st.session_state.cv = cv

    if st.session_state.cv:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Soluzione")
            st.markdown(st.session_state.cv.render_html(True), unsafe_allow_html=True)
        with col2:
            st.subheader("Schema Vuoto")
            st.markdown(st.session_state.cv.render_html(False), unsafe_allow_html=True)
            
        if st.button("🔄 Ricomincia"):
            st.session_state.cv = None
            st.rerun()

if __name__ == "__main__":
    main()
