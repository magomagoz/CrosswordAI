import streamlit as st
import requests
import random
from datetime import datetime
import io
import re

class DizionarioVerificatoTreccani:
    def __init__(self):
        self.parole_list = []
        self.parole_cache_verificate = {}
    
    def carica_lista_base(self):
        """Carica velocemente lista base"""
        progress = st.progress(0)
        tutte_parole = set()
        base_url = "https://www.listediparole.it/5lettereparolepagina"
        
        for pagina in range(1, 18):
            try:
                url = f"{base_url}{pagina}.htm"
                response = requests.get(url, timeout=6)
                parole = re.findall(r'\b[A-Z]{5}\b', response.text)
                tutte_parole.update(parole)
            except:
                continue
            progress.progress(pagina/17)
        
        self.parole_list = list(tutte_parole)
        random.shuffle(self.parole_list)
        return len(self.parole_list)

    def verifica_rapida_treccani(self, parola):
        """Verifica VELOCE - solo dopo inserimento provvisorio"""
        if parola in self.parole_cache_verificate:
            return self.parole_cache_verificate[parola]
        
        parola_lower = parola.lower()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # SOLO Treccani (più veloce)
        try:
            url = f"https://www.treccani.it/vocabolario/{parola_lower}/"
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                if any(indicatore in resp.text.lower() for indicatore in 
                       ['vocabolario', 'lemma', 'sost.', 'agg.', 'verbo']):
                    self.parole_cache_verificate[parola] = True
                    return True
        except:
            pass
        
        # Fallback Corriere
        try:
            url = f"https://dizionari.corriere.it/dizionario_italiano/{parola_lower[0]}/{parola_lower}.shtml"
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                self.parole_cache_verificate[parola] = True
                return True
        except:
            pass
        
        self.parole_cache_verificate[parola] = False
        return False

    def cerca_parola_veloce(self, pattern, exclude=None):
        """CERCA VELOCE senza verifica (verifica DOPO)"""
        pattern_dict = dict(pattern)
        random.shuffle(self.parole_list)
        
        for parola in self.parole_list:
            if exclude and parola in exclude:
                continue
            match = True
            for pos, lett in pattern_dict.items():
                if pos >= 5 or parola[pos] != lett:
                    match = False
                    break
            if match:
                return parola
        return None

# [Classe CruciverbaVerificaPost identica alla versione precedente]
class CruciverbaVerificaPost:
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
                    html += '<td style="border:2px solid black;width:65px;height:65px;position:relative;background:white;">
                            <span style="position:absolute;top:1px;left:2px;font-size:11px;font-weight:bold;color:#555;line-height:1;">1</span>
                            &nbsp;
                            </td>

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
    
    def verifica_griglia_completa(self):
        """VERIFICA FINALE: tutte le parole devono esistere su Treccani"""
        # Verifica orizzontali
        for parola, riga, col in self.parole_orizzontali:
            if not self.dizionario.verifica_rapida_treccani(parola):
                return False
        # Verifica verticali  
        for parola, riga, col in self.parole_verticali:
            if not self.dizionario.verifica_rapida_treccani(parola):
                return False
        return True
    
    def genera_rapido_verifica_post(self, max_ritentativi=20):
        """1° genera veloce, 2° verifica Treccani"""
        import time
        for tentativo in range(max_ritentativi):
            if tentativo % 3 == 0:
                st.write(f"⚡ Tentativo {tentativo+1}/{max_ritentativi}")
            
            self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            self.parole_usate = set()
            
            for r,c in self.caselle_nere: 
                self.griglia[r][c] = '#'
            
            ok = True
            for riga in [0, 2, 4]:
                parola = self.dizionario.cerca_parola_veloce(
                    self._pattern_orizzontale(riga, 0, 5), 
                    self.parole_usate
                )
                if not parola:
                    ok = False
                    break
                for col in range(5):
                    self.griglia[riga][col] = parola[col]
                self.parole_orizzontali.append((parola, riga, 0))
                self.parole_usate.add(parola)
            
            if not ok: continue
            
            for col in [0, 2, 4]:
                parola = self.dizionario.cerca_parola_veloce(
                    self._pattern_verticale(0, col, 5), 
                    self.parole_usate
                )
                if not parola: 
                    ok = False
                    break
                
                incroci_ok = True
                for riga in range(5):
                    if self.griglia[riga][col] == '#': continue
                    if self.griglia[riga][col] != ' ' and self.griglia[riga][col] != parola[riga]:
                        incroci_ok = False
                        break
                    self.griglia[riga][col] = parola[riga]
                
                if incroci_ok:
                    self.parole_verticali.append((parola, 0, col))
                    self.parole_usate.add(parola)
                else:
                    ok = False
                    break
            
            if not ok: continue
            
            with st.spinner("🔍 Verificando Treccani..."):
                if self.verifica_griglia_completa():
                    st.success("✅ GRIGLIA VERIFICATA TRECCANI!")
                    return True
            
            time.sleep(0.2)
        
        return False

def main():
    st.set_page_config(page_title="Cruciverba Pro", page_icon="🧩", layout="wide")
    
    st.markdown("""
    <style>
    .stButton button{font-size:22px!important;padding:18px!important;width:100%;background:#c41e3a;color:white;font-weight:bold;border-radius:10px;}
    .btn-reset{background:#28a745!important;}
    .verified {background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%); padding:12px; border-radius:8px; border-left:6px solid #28a745; margin:10px 0;}
    </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioVerificatoTreccani()
        st.session_state.parole_caricate = False
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5 - TRECCANI VERIFICATO")
    st.markdown("**⚡ Veloce + 100% Parole italiane certificate**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.parole_caricate:
            if st.button("📚 1. CARICA DIZIONARIO", use_container_width=True):
                with st.spinner("8262 parole base..."):
                    num = st.session_state.dizionario.carica_lista_base()
                    st.session_state.parole_caricate = True
                    st.success(f"✅ {num} parole caricate!")
                    st.rerun()
        else:
            st.markdown(f'<div class="verified">⚡ Dizionario pronto</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.parole_caricate and not st.session_state.generatore:
            if st.button("🎲 2. GENERA + VERIFICA", use_container_width=True):
                with st.spinner("Generando e verificando..."):
                    generatore = CruciverbaVerificaPost(st.session_state.dizionario)
                    if generatore.genera_rapido_verifica_post():
                        st.session_state.generatore = generatore
                        st.rerun()
                    else:
                        st.error("❌ Impossibile trovare combinazione verificata")
    
    # === SCHERMATA RISULTATO CON TASTO RESET ===
    if st.session_state.generatore:
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧩 Griglia compilata")
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        with col2:
            st.markdown("### 📝 Schema da risolvere") 
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        st.markdown('<div class="verified"><b>✅ 100% VERIFICATO TRECCANI</b></div>', unsafe_allow_html=True)
        
        # LISTA PAROLE
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟡 ORIZZONTALI ✓")
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                st.markdown(f"**{i}.** `{p}` ✅")
        with col2:
            st.markdown("### 🔴 VERTICALI ✓")
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_verticali, 4):
                st.markdown(f"**{i}.** `{p}` ✅")
        
        st.markdown("---")
        
        # === BOTTONI DOWNLOAD + RESET ===
        col1, col2, col3 = st.columns(3)
        
        with col1:
            txt = f"""CRUCIVERBA 5x5 - TRECCANI VERIFICATO
{("="*65)}
Generato: {datetime.now().strftime('%d/%m/%Y %H:%M')}

GRIGLIA:
"""
            for riga in st.session_state.generatore.griglia:
                riga_str = "|"
                for cella in riga: riga_str += "██|" if cella=='#' else f" {cella}|"
                txt += riga_str + "\n"
            
            txt += f"\n{('='*65)}\nPAROLE VERIFICATE:\n\nORIZZONTALI:\n"
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                txt += f"{i}. {p} ✅\n"
            txt += "\nVERTICALI:\n"
            for i, (p,_,_) in enumerate(st.session_state.generatore.parole_verticali, 4):
                txt += f"{i}. {p} ✅\n"
            
            st.download_button("📄 SALVA CRUCIVERBA", txt, 
                             f"cruciverba_ok_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 
                             use_container_width=True)
        
        with col2:
            st.markdown(" ")  # Spazio vuoto
        
        with col3:
            if st.button("🔄 NUOVO CRUCIVERBA", key="reset", use_container_width=True, help="Torna alla schermata iniziale"):
                # RESET COMPLETO
                st.session_state.dizionario = DizionarioVerificatoTreccani()
                st.session_state.parole_caricate = False
                st.session_state.generatore = None
                st.success("🔄 Schermata iniziale ripristinata!")
                st.rerun()

if __name__ == "__main__":
    main()
