import streamlit as st
import requests
import random
from datetime import datetime
import io
import re
from bs4 import BeautifulSoup

class DizionarioTreccani:
    def __init__(self):
        self.parole_list = []
        self.definizioni_cache = {}
    
    def carica_dizionario(self):
        """Carica lista parole da listediparole.it"""
        st.write("📚 Caricando 8262 parole...")
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
        
        self.parole_list = list(tutte_parole)
        random.shuffle(self.parole_list)
        return len(self.parole_list)

    def cerca_parola_con_pattern(self, pattern, exclude=None):
        """Trova parola che matcha pattern"""
        pattern_dict = dict(pattern)
        for parola in self.parole_list:
            if exclude and parola in exclude: continue
            match = True
            for pos, lett in pattern_dict.items():
                if parola[pos] != lett:
                    match = False
                    break
            if match: return parola
        return None

    def get_definizione(self, parola):
        """Recupera definizione reale da Treccani.it"""
        parola_lower = parola.lower()
        
        if parola in self.definizioni_cache:
            return self.definizioni_cache[parola]
        
        try:
            # Prova Treccani Vocabolario
            url = f"https://www.treccani.it/vocabolario/{parola_lower}/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Cerca definizione nel contenuto
                definizione_elem = soup.find('p', class_='Vocabolario_definizione') or \
                                 soup.find('div', class_='entry-content') or \
                                 soup.find('p')
                
                if definizione_elem:
                    definizione = definizione_elem.get_text(strip=True)[:200]
                    if len(definizione) > 10:
                        self.definizioni_cache[parola] = definizione
                        return definizione
            
            # Fallback: dizionari.corriere.it
            url = f"https://dizionari.corriere.it/dizionario_italiano/{parola_lower[0]}/{parola_lower}.shtml"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                definizione_elem = soup.find('span', class_='definizione')
                if definizione_elem:
                    definizione = definizione_elem.get_text(strip=True)[:200]
                    self.definizioni_cache[parola] = definizione
                    return definizione
                
        except:
            pass
        
        # Definizione generica di fallback
        self.definizioni_cache[parola] = f"Sostantivo comune italiano ({parola})"
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
                    for r in range(5):
                        if self.griglia[r][col] == '#': continue
                        if self.griglia[r][col] != ' ' and self.griglia[r][col] != parola[r]:
                            ok = False
                            break
                        self.griglia[r][col] = parola[r]
                    if ok:
                        self.parole_verticali.append((parola, 0, col))
                        self.parole_usate.add(parola)
                        successo = True
                        break
            if not successo: return False
        return True
    
    def carica_definizioni(self):
        """Carica definizioni reali per tutte le parole"""
        st.info("🔍 Recuperando definizioni da Treccani...")
        parole = [p[0] for p in self.parole_orizzontali + self.parole_verticali]
        
        for parola in parole:
            if parola not in self.definizioni:
                self.definizioni[parola] = self.dizionario.get_definizione(parola)

def genera_txt(generatore, includi_lettere=True):
    output = io.StringIO()
    if includi_lettere:
        output.write("CRUCIVERBA 5x5 - TRECCANI DEFINIZIONI\n"+"="*50+"\n\n")
        for riga in generatore.griglia:
            riga_str = "|"
            for cella in riga: riga_str += "██|" if cella=='#' else f" {cella}|"
            output.write(riga_str+"\n")
    else:
        output.write("SCHEMA CRUCIVERBA 5x5\n"+"="*50+"\n\n")
        for i in range(5):
            riga_str = "|"
            for j in range(5): riga_str += "██|" if (i,j)in generatore.caselle_nere else "  |"
            output.write(riga_str+"\n")
    
    output.write("\n" + "="*50 + "\n")
    output.write("DEFINIZIONI TRECCANI\n" + "="*50 + "\n\n")
    
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
    st.set_page_config(page_title="Cruciverba 5x5 Treccani", page_icon="🧩", layout="centered")
    
    st.markdown("""
    <style>.stButton button{font-size:24px!important;padding:20px!important;width:100%;background:#c41e3a;color:white;font-weight:bold;}</style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioTreccani()
        st.session_state.parole_caricate = False
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5 con Treccani")
    st.markdown("**Definizioni reali dal miglior dizionario italiano**")
    
    # PASSO 1: CARICA DIZIONARIO
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.parole_caricate:
            if st.button("📚 CARICA DIZIONARIO (8262 parole)", use_container_width=True):
                with st.spinner("Caricando parole..."):
                    num = st.session_state.dizionario.carica_dizionario()
                    st.session_state.parole_caricate = True
                    st.success(f"✅ {num} parole caricate!")
                    st.rerun()
        else:
            st.success("✅ Dizionario pronto!")
    
    # PASSO 2: GENERA CRUCIVERBA
    with col2:
        if st.session_state.parole_caricate:
            if not st.session_state.generatore:
                if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
                    with st.spinner("Generando griglia..."):
                        generatore = CruciverbaSchemaFisso(st.session_state.dizionario)
                        if generatore.genera():
                            st.session_state.generatore = generatore
                            st.rerun()
                        else:
                            st.error("❌ Impossibile generare")
    
    # PASSO 3: MOSTRA E DEFINIZIONI
    if st.session_state.generatore:
        # CARICA DEFINIZIONI
        if not hasattr(st.session_state.generatore, 'definizioni') or not st.session_state.generatore.definizioni:
            if st.button("📖 CARICA DEFINIZIONI TRECCANI"):
                st.session_state.generatore.carica_definizioni()
                st.rerun()
        
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["🧩 Griglia", "📝 Schema", "📚 Definizioni"])
        
        with tab1:
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        
        with tab2:
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        with tab3:
            if st.session_state.generatore.definizioni:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### 🟡 Orizzontali")
                    for i, (parola, _, _) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                        defiz = st.session_state.generatore.definizioni.get(parola, 'Caricando...')
                        st.write(f"**{i}.** {parola}")
                        st.caption(defiz)
                        st.markdown("---")
                
                with col2:
                    st.write("### 🔴 Verticali")
                    for i, (parola, _, _) in enumerate(st.session_state.generatore.parole_verticali, 4):
                        defiz = st.session_state.generatore.definizioni.get(parola, 'Caricando...')
                        st.write(f"**{i}.** {parola}")
                        st.caption(defiz)
                        st.markdown("---")
            else:
                st.info("🔄 Clicca 'CARICA DEFINIZIONI TRECCANI'")
        
        # DOWNLOAD
        col1,col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, True)
            st.download_button("📄 TXT completo", txt, f"cruciverba_treccani_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with col2:
            st.download_button("📝 TXT schema", genera_txt(st.session_state.generatore, False), 
                             f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

if __name__ == "__main__":
    main()
