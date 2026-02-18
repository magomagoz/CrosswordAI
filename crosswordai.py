import streamlit as st
import requests
import random
from datetime import datetime
import io
import re

class DizionarioWeb:
    def __init__(self):
        self.parole = []
    
    def carica_dizionario(self):
        st.write("📚 Scaricando 8262 parole da listediparole.it...")
        tutte_parole = set()
        base_url = "https://www.listediparole.it/5lettereparolepagina"
        
        for pagina in range(1, 18):
            try:
                url = f"{base_url}{pagina}.htm"
                response = requests.get(url, timeout=5)
                parole = re.findall(r'\b[A-Z]{5}\b', response.text)
                tutte_parole.update(parole)
            except:
                continue
        
        self.parole = list(tutte_parole)
        random.shuffle(self.parole)
        return len(self.parole)

    def cerca_parola_con_pattern(self, pattern, exclude=None):
        pattern_dict = dict(pattern)
        for parola in self.parole:
            if exclude and parola in exclude: continue
            match = True
            for pos, lett in pattern_dict.items():
                if parola[pos] != lett:
                    match = False
                    break
            if match: return parola
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
        numeri = {(0,0):1, (2,0):2, (4,0):3, (0,2):4, (0,4):5} if not mostra_lettere else {}
        
        for i in range(5):
            html += '<tr>'
            for j in range(5):
                if (i,j) in self.caselle_nere:
                    html += '<td style="border: 2px solid black; width: 65px; height: 65px; background: black;">&nbsp;</td>'
                elif not mostra_lettere and (i,j) in numeri:
                    html += f'<td style="border: 2px solid black; width: 65px; height: 65px; text-align:center;font-weight:bold;color:#c41e3a;">{numeri[(i,j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid black; width: 65px; height: 65px;">&nbsp;</td>'
                else:
                    cella = self.griglia[i][j]
                    html += f'<td style="border: 2px solid black; width: 65px; height: 65px; text-align: center; font-weight: bold;">{cella if cella != " " else "&nbsp;"}</td>'
            html += '</tr>'
        return html + '</table>'
    
    def _pattern_orizzontale(self, riga, col, lunghezza):
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga][col+k]
            if cella != ' ' and cella != '#': pattern.append((k, cella))
        return pattern
    
    def _pattern_verticale(self, riga, col, lunghezza):
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga+k][col]
            if cella != ' ' and cella != '#': pattern.append((k, cella))
        return pattern
    
    def genera(self):
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        
        for r,c in self.caselle_nere: self.griglia[r][c] = '#'
        
        # ORIZZONTALI
        for riga in [0,2,4]:
            successo = False
            for _ in range(200):
                pattern = self._pattern_orizzontale(riga, 0, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    for col in range(5): self.griglia[riga][col] = parola[col]
                    self.parole_orizzontali.append((parola, riga, 0))
                    self.parole_usate.add(parola)
                    successo = True
                    break
            if not successo: return False
        
        # VERTICALI
        for col in [0,2,4]:
            successo = False
            for _ in range(500):
                pattern = self._pattern_verticale(0, col, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    ok = True
                    for riga in range(5):
                        if self.griglia[riga][col] == '#': continue
                        if self.griglia[riga][col] != ' ' and self.griglia[riga][col] != parola[riga]:
                            ok = False
                            break
                        self.griglia[riga][col] = parola[riga]
                    if ok:
                        self.parole_verticali.append((parola, 0, col))
                        self.parole_usate.add(parola)
                        successo = True
                        break
            if not successo: return False
        return True

def genera_txt(generatore, includi_lettere=True):
    output = io.StringIO()
    if includi_lettere:
        output.write("CRUCIVERBA 5x5\n"+"="*30+"\n\n")
        for riga in generatore.griglia:
            riga_str = "|"
            for cella in riga: riga_str += "██|" if cella=='#' else f" {cella}|"
            output.write(riga_str+"\n")
    else:
        output.write("SCHEMA VUOTO\n"+"="*30+"\n\n")
        for i in range(5):
            riga_str = "|"
            for j in range(5): riga_str += "██|" if (i,j)in generatore.caselle_nere else "  |"
            output.write(riga_str+"\n")
    
    output.write("\nORIZZONTALI:\n")
    for i,(p,_,_) in enumerate(generatore.parole_orizzontali,1): output.write(f"{i}. {p}\n")
    output.write("\nVERTICALI:\n")
    for i,(p,_,_) in enumerate(generatore.parole_verticali,4): output.write(f"{i}. {p}\n")
    return output.getvalue()

def main():
    st.set_page_config(page_title="Cruciverba 5x5", page_icon="🧩", layout="centered")
    
    st.markdown("""
    <style>.stButton button{font-size:24px!important;padding:20px!important;width:100%;background:#c41e3a;color:white;font-weight:bold;}</style>
    """, unsafe_allow_html=True)
    
    # Inizializza session state
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioWeb()
        st.session_state.parole_caricate = False
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5")
    st.markdown("**Caselle nere: B2, B4, D2, D4**")
    
    # === PASSO 1: CARICA DIZIONARIO ===
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.parole_caricate:
            if st.button("📚 CARICA DIZIONARIO", use_container_width=True):
                with st.spinner("Caricamento 8262 parole..."):
                    num = st.session_state.dizionario.carica_dizionario()
                    st.session_state.parole_caricate = True
                    st.success(f"✅ {num} parole caricate!")
                    st.rerun()
        else:
            st.success("✅ Dizionario caricato!")
    
    # === PASSO 2: GENERA CRUCIVERBA ===
    with col2:
        if st.session_state.parole_caricate and not st.session_state.generatore:
            if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
                with st.spinner("Generando cruciverba..."):
                    generatore = CruciverbaSchemaFisso(st.session_state.dizionario)
                    if generatore.genera():
                        st.session_state.generatore = generatore
                        st.success("✅ Cruciverba generato!")
                        st.rerun()
                    else:
                        st.error("❌ Impossibile generare")
    
    # === PASSO 3: MOSTRA RISULTATO ===
    if st.session_state.generatore:
        st.markdown("---")
        
        # TABS
        tab1, tab2 = st.tabs(["🧩 Compilato", "📝 Schema"])
        with tab1:
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        with tab2:
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        # METRICHE
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Parole", "6")
        col2.metric("Orizzontali", "3")
        col3.metric("Verticali", "3")
        col4.metric("Nere", "4")
        
        # PAROLE
        col1,col2 = st.columns(2)
        with col1:
            st.write("**Orizzontali:**")
            for i,(p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali,1):
                st.write(f"{i}. **{p}**")
        with col2:
            st.write("**Verticali:**")
            for i,(p,_,_) in enumerate(st.session_state.generatore.parole_verticali,4):
                st.write(f"{i}. **{p}**")
        
        # DOWNLOAD
        col1,col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, True)
            st.download_button("📄 TXT compilato", txt, f"cruciverba_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with col2:
            txt = genera_txt(st.session_state.generatore, False)
            st.download_button("📄 TXT schema", txt, f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

if __name__ == "__main__":
    main()
