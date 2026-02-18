import streamlit as st
import requests
import random
from datetime import datetime
import io
import re
from typing import List, Tuple, Optional

class DizionarioWeb:
    def __init__(self):
        self.base_url = "https://www.listediparole.it/5lettereparolepagina"
        self.cache = {}
    
    def _scarica_pagine(self) -> List[str]:
        """Scarica tutte le 17 pagine di parole 5 lettere"""
        tutte_parole = set()
        session = requests.Session()
        
        for pagina in range(1, 18):  # 17 pagine totali
            try:
                url = f"{self.base_url}{pagina}.htm"
                response = session.get(url, timeout=5)
                if response.status_code == 200:
                    # Estrae parole con regex (es. "ABACA ABACO ABATE")
                    parole = re.findall(r'\b[A-Z]{5}\b', response.text)
                    tutte_parole.update(parole)
                    st.write(f"📖 Pagina {pagina}: {len(parole)} parole")
                else:
                    st.warning(f"Pagina {pagina} non disponibile")
            except:
                continue
        
        self.parole = list(tutte_parole)
        random.shuffle(self.parole)
        st.success(f"✅ Dizionario caricato: {len(self.parole)} parole!")
        return self.parole
    
    def cerca_parola_con_pattern(self, pattern: List[Tuple[int, str]], exclude: set = None) -> Optional[str]:
        """Trova parola che matcha il pattern (es. [(0,'C'), (2,'S')])"""
        pattern_dict = dict(pattern)
        
        for parola in self.parole:
            if exclude and parola in exclude:
                continue
            
            match = True
            for pos, lettera in pattern_dict.items():
                if pos >= 5 or parola[pos] != lettera:
                    match = False
                    break
            
            if match:
                return parola
        
        return None

class CruciverbaSchemaFisso:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        self.caselle_nere = [(1,1), (1,3), (3,1), (3,3)]
    
    def griglia_html(self, mostra_lettere=True):
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 28px; margin: 0 auto;">'
        numeri = { (0,0):1, (2,0):2, (4,0):3, (0,2):4, (0,4):5 } if not mostra_lettere else {}
        
        for i in range(5):
            html += '<tr>'
            for j in range(5):
                if (i,j) in self.caselle_nere:
                    html += '<td style="border: 2px solid black; width: 65px; height: 65px; background: black;">&nbsp;</td>'
                elif (i,j) in numeri:
                    html += f'<td style="border: 2px solid black; width: 65px; height: 65px; text-align: center; font-weight: bold; color: #c41e3a; background: white;">{numeri[(i,j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid black; width: 65px; height: 65px; background: white;">&nbsp;</td>'
                else:
                    cella = self.griglia[i][j]
                    bg = 'background: #fff3cd;' if cella == ' ' else ''
                    html += f'<td style="border: 2px solid black; width: 65px; height: 65px; text-align: center; font-weight: bold; {bg}">{cella if cella != " " else "&nbsp;"}</td>'
            html += '</tr>'
        return html + '</table>'
    
    def _pattern_orizzontale(self, riga: int, col: int, lunghezza: int) -> List[Tuple[int, str]]:
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga][col + k]
            if cella != ' ' and cella != '#':
                pattern.append((k, cella))
        return pattern
    
    def _pattern_verticale(self, riga: int, col: int, lunghezza: int) -> List[Tuple[int, str]]:
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga + k][col]
            if cella != ' ' and cella != '#':
                pattern.append((k, cella))
        return pattern
    
    def genera(self) -> bool:
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        
        for r, c in self.caselle_nere:
            self.griglia[r][c] = '#'
        
        # ORIZZONTALI (righe 0,2,4)
        for riga in [0, 2, 4]:
            for tentativo in range(200):
                pattern = self._pattern_orizzontale(riga, 0, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    for col in range(5):
                        self.griglia[riga][col] = parola[col]
                    self.parole_orizzontali.append((parola, riga, 0))
                    self.parole_usate.add(parola)
                    break
            else:
                return False
        
        # VERTICALI (colonne 0,2,4)
        for col in [0, 2, 4]:
            for tentativo in range(500):  # Più tentativi per verticali
                pattern = self._pattern_verticale(0, col, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    ok = True
                    for riga in range(5):
                        if self.griglia[riga][col] == '#':
                            continue
                        if self.griglia[riga][col] != ' ' and self.griglia[riga][col] != parola[riga]:
                            ok = False
                            break
                        self.griglia[riga][col] = parola[riga]
                    if ok:
                        self.parole_verticali.append((parola, 0, col))
                        self.parole_usate.add(parola)
                        break
            else:
                return False
        
        return True

def genera_txt(generatore, includi_lettere=True):
    output = io.StringIO()
    if includi_lettere:
        output.write("CRUCIVERBA 5x5 COMPILATO\n"+"="*35+"\n\n")
        for riga in generatore.griglia:
            riga_str = "| "
            for cella in riga:
                riga_str += "██ | " if cella == '#' else f"{cella} | "
            output.write(riga_str.rstrip() + "\n")
    else:
        output.write("SCHEMA 5x5 VUOTO\n"+"="*35+"\n\n")
        for i in range(5):
            riga_str = "| "
            for j in range(5):
                riga_str += "██ | " if (i,j) in generatore.caselle_nere else "   | "
            output.write(riga_str.rstrip() + "\n")
    
    output.write("\nDEFINIZIONI\n"+"="*35+"\n\n")
    output.write("ORIZZONTALI:\n")
    for i, (p,_,_) in enumerate(generatore.parole_orizzontali, 1):
        output.write(f"{i}. {p}\n")
    output.write("\nVERTICALI:\n")
    for i, (p,_,_) in enumerate(generatore.parole_verticali, 4):
        output.write(f"{i}. {p}\n")
    return output.getvalue()

def main():
    st.set_page_config(page_title="Cruciverba 5x5", page_icon="🧩", layout="centered")
    
    st.markdown("""
    <style>
    .stButton button {font-size:24px!important;padding:20px!important;width:100%;background:#c41e3a;color:white;font-weight:bold;}
    </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioWeb()
        st.session_state.parole_caricate = False
    
    st.title("🧩 Cruciverba 5x5")
    st.markdown("**8262 parole italiane reali** da listediparole.it")
    
    if not st.session_state.parole_caricate:
        if st.button("📚 CARICA DIZIONARIO (17 pagine)", use_container_width=True):
            with st.spinner("Scaricando 8262 parole..."):
                st.session_state.dizionario._scarica_pagine()
                st.session_state.parole_caricate = True
    else:
        if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
            with st.spinner("Generando cruciverba perfetto..."):
                generatore = CruciverbaSchemaFisso(st.session_state.dizionario)
                if generatore.genera():
                    st.session_state.generatore = generatore
                    st.success("✅ CRUCIVERBA COMPLETATO!")
                    st.rerun()
                else:
                    st.error("❌ Impossibile trovare combinazione - riprova")
        
        if 'generatore' in st.session_state:
            tab1, tab2 = st.tabs(["🧩 Compilato", "📝 Schema"])
            with tab1:
                st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
            with tab2:
                st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
            
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("Parole", "6")
            col2.metric("Orizzontali", "3")
            col2.metric("Verticali", "3")
            col4.metric("Nere", "4/25")
            
            col1,col2 = st.columns(2)
            with col1:
                st.write("**Orizzontali:**")
                for i,(p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali,1):
                    st.write(f"{i}. **{p}**")
            with col2:
                st.write("**Verticali:**")
                for i,(p,_,_) in enumerate(st.session_state.generatore.parole_verticali,4):
                    st.write(f"{i}. **{p}**")

if __name__ == "__main__":
    main()
