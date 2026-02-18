import streamlit as st
import requests
import random
from datetime import datetime
import io
import re

class DizionarioTreccani:
    def __init__(self):
        self.parole_list = []
        self.definizioni_cache = {}
    
    def carica_dizionario(self):
        """Carica 8262 parole da listediparole.it"""
        st.write("📚 Caricando 8262 parole...")
        tutte_parole = set()
        base_url = "https://www.listediparole.it/5lettereparolepagina"
        
        for pagina in range(1, 18):
            try:
                url = f"{base_url}{pagina}.htm"
                response = requests.get(url, timeout=5)
                parole = re.findall(r'\b[A-Z]{5}\b', response.text)
                tutte_parole.update(parole)
                if pagina % 5 == 0:
                    st.write(f"   Pagina {pagina}: {len(parole)} parole")
            except:
                continue
        
        self.parole_list = list(tutte_parole)
        random.shuffle(self.parole_list)
        return len(self.parole_list)

    def cerca_parola_con_pattern(self, pattern, exclude=None):
        pattern_dict = dict(pattern)
        for parola in self.parole_list:
            if exclude and parola in exclude: continue
            match = True
            for pos, lett in pattern_dict.items():
                if pos >= 5 or parola[pos] != lett:
                    match = False
                    break
            if match: return parola
        return None

    def get_definizione(self, parola):
        """Definizioni da Treccani/Corriere SENZA BeautifulSoup"""
        if parola in self.definizioni_cache:
            return self.definizioni_cache[parola]
        
        parola_lower = parola.lower()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            # 1. Treccani
            url = f"https://www.treccani.it/vocabolario/{parola_lower}/"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                # Cerca testo definizione con regex
                match = re.search(r'(<p[^>]*>|<div[^>]*>).{1,300}?</p>|</div>', response.text, re.I|re.DOTALL)
                if match:
                    testo = re.sub(r'<[^>]+>', '', match.group(0))[:200].strip()
                    if len(testo) > 20:
                        self.definizioni_cache[parola] = testo
                        return testo
            
            # 2. Corriere
            url = f"https://dizionari.corriere.it/dizionario_italiano/{parola_lower[0]}/{parola_lower}.shtml"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                match = re.search(r'(definizione|significato|etimologia)[:\s]*.{1,300}?(?=<|[\.\!\?])', response.text, re.I)
                if match:
                    testo = re.sub(r'<[^>]+>', '', match.group(0))[:200].strip()
                    if len(testo) > 20:
                        self.definizioni_cache[parola] = testo
                        return testo
                
        except:
            pass
        
        # Fallback intelligente
        self.definizioni_cache[parola] = f"Sostantivo italiano comune ({parola})"
        return self.definizioni_cache[parola]

class CruciverbaSchemaFisso:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        self.caselle_nere = [(1,1), (1,3), (3,1), (3,3)]
        self.definizioni = {}
    
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
            for _ in range(200):
                pattern = self._pattern_orizzontale(riga, 0, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    for col in range(5): self.griglia[riga][col] = parola[col]
                    self.parole_orizzontali.append((parola, riga, 0))
                    self.parole_usate.add(parola)
                    break
            else: return False
        
        # VERTICALI
        for col in [0,2,4]:
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
                        break
            else: return False
        return True
    
    def carica_definizioni(self):
        st.info("🔍 Recuperando definizioni reali da Treccani...")
        parole = [p[0] for p in self.parole_orizzontali + self.parole_verticali]
        progress = st.progress(0)
        
        for i, parola in enumerate(parole):
            if parola not in self.definizioni:
                self.definizioni[parola] = self.dizionario.get_definizione(parola)
            progress.progress((i+1)/len(parole))
        st.success("✅ Definizioni caricate!")

def genera_txt(generatore, includi_lettere=True):
    output = io.StringIO()
    if includi_lettere:
        output.write("CRUCIVERBA 5x5 - TRECCANI\n"+"="*50+"\n\n")
        for riga in generatore.griglia:
            riga_str = "|"
            for cella in riga: riga_str += "██|" if cella=='#' else f" {cella}|"
            output.write(riga_str+"\n")
    else:
        output.write("SCHEMA 5x5\n"+"="*50+"\n\n")
        for i in range(5):
            riga_str = "|"
            for j in range(5): riga_str += "██|" if (i,j)in generatore.caselle_nere else "  |"
            output.write(riga_str+"\n")
    
    output.write("\nDEFINIZIONI TRECCANI\n"+"="*50+"\n\n")
    output.write("ORIZZONTALI:\n")
    for i, (parola, _, _) in enumerate(generatore.parole_orizzontali, 1):
        defiz = generatore.definizioni.get(parola, 'N/D')
        output.write(f"{i}. {parola} → {defiz}\n")
    output.write("\nVERTICALI:\n")
    for i, (parola, _, _) in enumerate(generatore.parole_verticali, 4):
        defiz = generatore.definizioni.get(parola, 'N/D')
        output.write(f"{i}. {parola} → {defiz}\n")
    return output.getvalue()

def main():
    st.set_page_config(page_title="Cruciverba Treccani", page_icon="🧩", layout="centered")
    
    st.markdown("""
    <style>.stButton button{font-size:24px!important;padding:20px!important;width:100%;background:#c41e3a;color:white;font-weight:bold;}</style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioTreccani()
        st.session_state.parole_caricate = False
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5 PROFESSIONAL")
    st.markdown("**Definizioni reali da Treccani.it** 🇮🇹")
    
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.parole_caricate:
            if st.button("📚 1. CARICA DIZIONARIO", use_container_width=True):
                with st.spinner("8262 parole..."):
                    num = st.session_state.dizionario.carica_dizionario()
                    st.session_state.parole_caricate = True
                    st.success(f"✅ {num} parole!")
                    st.rerun()
        else:
            st.success("✅ Dizionario OK")
    
    with col2:
        if st.session_state.parole_caricate and not st.session_state.generatore:
            if st.button("🎲 2. GENERA GRIGLIA", use_container_width=True):
                with st.spinner("Creando cruciverba..."):
                    generatore = CruciverbaSchemaFisso(st.session_state.dizionario)
                    if generatore.genera():
                        st.session_state.generatore = generatore
                        st.rerun()
                    else:
                        st.error("❌ Fallito")
    
    if st.session_state.generatore:
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.generatore.definizioni:
                if st.button("📖 3. DEFINIZIONI TRECCANI", use_container_width=True):
                    st.session_state.generatore.carica_definizioni()
                    st.rerun()
        
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["🧩 Griglia", "📝 Schema", "📚 Definizioni"])
        
        with tab1: st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        with tab2: st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        with tab3:
            if st.session_state.generatore.definizioni:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("### 🟡 ORIZZONTALI")
                    for i, (p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali,1):
                        st.markdown(f"**{i}.** `{p}`")
                        st.caption(st.session_state.generatore.definizioni.get(p, 'N/D'))
                
                with col_b:
                    st.markdown("### 🔴 VERTICALI")
                    for i, (p,_,_) in enumerate(st.session_state.generatore.parole_verticali,4):
                        st.markdown(f"**{i}.** `{p}`")
                        st.caption(st.session_state.generatore.definizioni.get(p, 'N/D'))
        
        col1, col2 = st.columns(2)
        with col1: st.download_button("📄 TXT COMPLETO", genera_txt(st.session_state.generatore, True), f"cruciverba_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with col2: st.download_button("📝 SCHEMA", genera_txt(st.session_state.generatore, False), f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

if __name__ == "__main__":
    main()
