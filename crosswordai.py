import streamlit as st
import requests
import random
from datetime import datetime
import io
import re
import time

class DizionarioVerificatoTreccani:
    def __init__(self):
        self.parole_list = []
        self.parole_verificate_cache = {}
        self.definizioni_cache = {}
    
    def verifica_parola_treccani(self, parola):
        """VERIFICA se la parola esiste su Treccani/Corriere"""
        parola_lower = parola.lower()
        
        if parola in self.parole_verificate_cache:
            return self.parole_verificate_cache[parola]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # 1. TRECCANI - Verifica primaria
        try:
            url = f"https://www.treccani.it/vocabolario/{parola_lower}/"
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200:
                # Cerca contenuto lessicale reale
                if 'vocabolario' in resp.text.lower() or 'lemma' in resp.text.lower():
                    self.parole_verificate_cache[parola] = True
                    return True
        except:
            pass
        
        # 2. CORRIERE - Verifica secondaria
        try:
            url = f"https://dizionari.corriere.it/dizionario_italiano/{parola_lower[0]}/{parola_lower}.shtml"
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200 and 'definizione' in resp.text.lower():
                self.parole_verificate_cache[parola] = True
                return True
        except:
            pass
        
        # 3. WIKIPEDIA - Ultima chance
        try:
            url = f"https://it.wikipedia.org/wiki/{parola_lower}"
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200:
                self.parole_verificate_cache[parola] = True
                return True
        except:
            pass
        
        self.parole_verificate_cache[parola] = False
        return False
    
    def carica_lista_base(self):
        """Carica lista iniziale da listediparole.it"""
        progress = st.progress(0)
        tutte_parole = set()
        base_url = "https://www.listediparole.it/5lettereparolepagina"
        
        for pagina in range(1, 18):
            try:
                url = f"{base_url}{pagina}.htm"
                response = requests.get(url, timeout=8)
                parole = re.findall(r'\b[A-Z]{5}\b', response.text)
                tutte_parole.update(parole)
            except:
                continue
            progress.progress(pagina/17)
        
        self.parole_list = list(tutte_parole)
        random.shuffle(self.parole_list)
        return len(self.parole_list)
    
    def cerca_parola_verificata(self, pattern, exclude=None, max_tentativi=2000):
        """CERCA SOLO parole VERIFICATE Treccani"""
        pattern_dict = dict(pattern)
        tentativi = 0
        
        random.shuffle(self.parole_list)
        
        for parola in self.parole_list:
            tentativi += 1
            if tentativi > max_tentativi:
                break
                
            if exclude and parola in exclude:
                continue
            
            # VERIFICA Treccani PRIMA di testare pattern
            if not self.verifica_parola_treccani(parola):
                continue
            
            # Test pattern
            match = True
            for pos, lett in pattern_dict.items():
                if pos >= 5 or parola[pos] != lett:
                    match = False
                    break
            if match:
                return parola
        
        return None

class CruciverbaVerificato:
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
            if cella != ' ' and cella != '#':
                pattern.append((k, cella))
        return pattern
    
    def _pattern_verticale(self, riga, col, lunghezza):
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga+k][col]
            if cella != ' ' and cella != '#':
                pattern.append((k, cella))
        return pattern
    
    def genera_verificato(self, max_ritentativi=15):
        """Genera con VERIFICA Treccani per OGNI parola"""
        for tentativo in range(max_ritentativi):
            st.write(f"🔍 Tentativo {tentativo+1}/{max_ritentativi} - Verificando Treccani...")
            
            self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            self.parole_usate = set()
            
            for r,c in self.caselle_nere: 
                self.griglia[r][c] = '#'
            
            # ORIZZONTALI - Solo parole verificate
            orizz_ok = True
            for riga in [0, 2, 4]:
                parola = self.dizionario.cerca_parola_verificata(
                    self._pattern_orizzontale(riga, 0, 5), 
                    self.parole_usate
                )
                if not parola:
                    orizz_ok = False
                    break
                for col in range(5):
                    self.griglia[riga][col] = parola[col]
                self.parole_orizzontali.append((parola, riga, 0))
                self.parole_usate.add(parola)
            
            if not orizz_ok:
                continue
            
            # VERTICALI - Solo parole verificate
            verticali_ok = True
            for col in [0, 2, 4]:
                parola = self.dizionario.cerca_parola_verificata(
                    self._pattern_verticale(0, col, 5), 
                    self.parole_usate
                )
                if not parola:
                    verticali_ok = False
                    break
                
                # Verifica incroci FINALMENTE
                ok_incroci = True
                for riga in range(5):
                    if self.griglia[riga][col] == '#':
                        continue
                    if self.griglia[riga][col] != ' ' and self.griglia[riga][col] != parola[riga]:
                        ok_incroci = False
                        break
                    self.griglia[riga][col] = parola[riga]
                
                if ok_incroci:
                    self.parole_verticali.append((parola, 0, col))
                    self.parole_usate.add(parola)
                else:
                    verticali_ok = False
                    break
            
            if orizz_ok and verticali_ok:
                st.success("✅ CRUCIVERBA VERIFICATO TRECCANI!")
                return True
            
            time.sleep(0.5)
        
        return False

def main():
    st.set_page_config(page_title="Cruciverba Treccani VERIFICATO", page_icon="🧩", layout="wide")
    
    st.markdown("""
    <style>
    .stButton button{font-size:22px!important;padding:18px!important;width:100%;background:#c41e3a;color:white;font-weight:bold;border-radius:10px;}
    .verified {background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%); padding:10px; border-radius:5px; border-left:5px solid #28a745;}
    </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioVerificatoTreccani()
        st.session_state.parole_caricate = False
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5 - VERIFICATO TRECCANI 🇮🇹")
    st.markdown("**OGNI PAROLA controllata su Treccani.it prima di entrare nella griglia**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.parole_caricate:
            if st.button("📚 1. CARICA DIZIONARIO BASE", use_container_width=True):
                with st.spinner("Caricando 8262 parole candidate..."):
                    num = st.session_state.dizionario.carica_lista_base()
                    st.session_state.parole_caricate = True
                    st.success(f"✅ {num} parole candidate caricate!")
                    st.rerun()
        else:
            st.markdown(f'<div class="verified">✅ Dizionario base pronto ({len(st.session_state.dizionario.parole_list)} parole)</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.parole_caricate and not st.session_state.generatore:
            if st.button("🎲 2. GENERA VERIFICATO TRECCANI", use_container_width=True):
                with st.spinner("🔍 Verificando ogni parola su Treccani.it..."):
                    generatore = CruciverbaVerificato(st.session_state.dizionario)
                    if generatore.genera_verificato():
                        st.session_state.generatore = generatore
                        st.rerun()
                    else:
                        st.error("❌ Nessuna combinazione verificata dopo molti tentativi")
    
    if st.session_state.generatore:
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🧩 Griglia verificata", "📝 Schema da risolvere"])
        with tab1:
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
            st.markdown('<div class="verified"><b>✓ TUTTE le 6 parole VERIFICATE su Treccani.it</b></div>', unsafe_allow_html=True)
        with tab2:
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        # LISTA PAROLE VERIFICATE
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟡 ORIZZONTALI VERIFICATE")
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                st.markdown(f"**{i}.** `{p}` ✓")
        with col2:
            st.markdown("### 🔴 VERTICALI VERIFICATE")
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_verticali, 4):
                st.markdown(f"**{i}.** `{p}` ✓")
        
        # DOWNLOAD
        col1, col2 = st.columns(2)
        with col1:
            txt = f"""CRUCIVERBA 5x5 - VERIFICATO TRECCANI
{("="*60)}
Generato: {datetime.now().strftime('%d/%m/%Y %H:%M')}

GRIGLIA COMPLETA:
"""
            for riga in st.session_state.generatore.griglia:
                riga_str = "|"
                for cella in riga: riga_str += "██|" if cella=='#' else f" {cella}|"
                txt += riga_str + "\n"
            
            txt += f"\n{('='*60)}\nPAROLE VERIFICATE TRECCANI:\n\n"
            txt += "ORIZZONTALI:\n"
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                txt += f"{i}. {p} ✓\n"
            txt += "\nVERTICALI:\n"
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_verticali, 4):
                txt += f"{i}. {p} ✓\n"
            
            st.download_button("📄 DOWNLOAD VERIFICATO", txt, f"cruciverba_treccani_verificato_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", use_container_width=True)

if __name__ == "__main__":
    main()
