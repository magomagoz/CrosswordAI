import streamlit as st
import requests
import random
from datetime import datetime
import re

# --- CONFIGURAZIONE GRIGLIA ---
COLS = 9
ROWS = 13

class DizionarioItalianoCompleto:
    def __init__(self):
        self.parole_per_lunghezza = {}
        self.parole_cache_verificate = {}
    
    def carica_vocabolario(self):
        """Carica un dizionario italiano completo da una sorgente affidabile"""
        progress = st.progress(0)
        st.write("📚 Caricamento vocabolario italiano...")
        
        # Utilizzo di un repository di parole italiane comuni e verificate
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        
        try:
            response = requests.get(url, timeout=10)
            tutte_parole = response.text.splitlines()
            
            for parola in tutte_parole:
                parola = parola.upper().strip()
                if parola.isalpha():
                    lunghezza = len(parola)
                    if lunghezza not in self.parole_per_lunghezza:
                        self.parole_per_lunghezza[lunghezza] = []
                    self.parole_per_lunghezza[lunghezza].append(parola)
            
            progress.progress(100)
            return sum(len(v) for v in self.parole_per_lunghezza.values())
        except Exception as e:
            st.error(f"Errore nel caricamento: {e}")
            return 0

    def cerca_parola(self, pattern_dict, lunghezza, exclude=None):
        """Cerca una parola che corrisponde al pattern (es. {0: 'A', 2: 'B'})"""
        candidati = self.parole_per_lunghezza.get(lunghezza, [])
        random.shuffle(candidati)
        
        for parola in candidati:
            if exclude and parola in exclude:
                continue
            match = True
            for pos, lett in pattern_dict.items():
                if parola[pos] != lett:
                    match = False
                    break
            if match:
                return parola
        return None

class CruciverbaDinamico:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        # Caselle nere distribuite per una griglia 13x9
        self.caselle_nere = [
            (1,1), (1,4), (1,8), (1,11),
            (3,2), (3,6), (3,10),
            (5,2), (5,6), (5,10),
            (7,1), (7,4), (7,8), (7,11)
        ]
        for r, c in self.caselle_nere:
            self.griglia[r][c] = '#'

    def griglia_html(self, mostra_lettere=True):
        html = '<div style="overflow-x:auto;"><table style="border-collapse: collapse; font-family: sans-serif; margin: 0 auto;">'
        for i in range(ROWS):
            html += '<tr>'
            for j in range(COLS):
                base_style = "border: 1px solid #333; width: 40px; height: 40px; text-align: center;"
                if (i,j) in self.caselle_nere:
                    html += f'<td style="{base_style} background: #222;">&nbsp;</td>'
                else:
                    char = self.griglia[i][j] if mostra_lettere else ""
                    html += f'<td style="{base_style} font-weight: bold; background: white; color: black;">{char}</td>'
            html += '</tr>'
        return html + '</table></div>'

    def genera(self):
        """Algoritmo di riempimento semplificato per griglie ampie"""
        # Riempimento Orizzontale (Righe pari)
        for r in range(0, ROWS, 2):
            pattern = {}
            parola = self.dizionario.cerca_parola(pattern, COLS, self.parole_usate)
            if parola:
                for c in range(COLS):
                    if self.griglia[r][c] != '#':
                        self.griglia[r][c] = parola[c]
                self.parole_usate.add(parola)

        # Riempimento Verticale (Colonne pari che incrociano)
        for c in range(0, COLS, 2):
            pattern = {}
            for r in range(ROWS):
                if self.griglia[r][c] != ' ' and self.griglia[r][c] != '#':
                    pattern[r] = self.griglia[r][c]
            
            parola = self.dizionario.cerca_parola(pattern, ROWS, self.parole_usate)
            if parola:
                for r in range(ROWS):
                    if self.griglia[r][c] != '#':
                        self.griglia[r][c] = parola[r]
                self.parole_usate.add(parola)
        return True

def main():
    st.set_page_config(page_title="Cruciverba 9x13", layout="wide")
    st.image("banner.png", use_container_width=True)

    #st.title("🧩 Generatore Cruciverba 9x13")
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioItalianoCompleto()
        st.session_state.caricato = False
        st.session_state.cruciverba = None

    if not st.session_state.caricato:
        if st.button("📥 CARICA VOCABOLARIO ITALIANO"):
            count = st.session_state.dizionario.carica_vocabolario()
            st.session_state.caricato = True
            st.success(f"Dizionario pronto: {count} lemmi caricati.")
            st.rerun()
    else:
        if st.button("🎲 GENERA SCHEMA 9x13"):
            cv = CruciverbaDinamico(st.session_state.dizionario)
            if cv.genera():
                st.session_state.cruciverba = cv

    if st.session_state.cruciverba:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Soluzione")
            st.markdown(st.session_state.cruciverba.griglia_html(True), unsafe_allow_html=True)
        with col2:
            st.markdown("### Schema Vuoto")
            st.markdown(st.session_state.cruciverba.griglia_html(False), unsafe_allow_html=True)
        
        if st.button("🔄 Reset"):
            st.session_state.cruciverba = None
            st.rerun()

if __name__ == "__main__":
main()
