import streamlit as st
import requests
import random
from datetime import datetime
import re
import time

class DizionarioVerificatoTreccani:
    def __init__(self):
        self.parole_per_lunghezza = {} # Dizionario ottimizzato: {lunghezza: [parole]}
        self.parole_cache_verificate = {}
    
    def carica_lista_base(self):
        progress = st.progress(0)
        tutte_parole = set()
        # Nota: Carichiamo parole di diverse lunghezze per la griglia 13x9
        base_url = "https://www.listediparole.it/parole-italiane-pagina"
        
        for pagina in range(1, 15):
            try:
                url = f"{base_url}{pagina}.htm"
                response = requests.get(url, timeout=6)
                # Troviamo parole da 2 a 13 lettere
                parole = re.findall(r'\b[A-Z]{2,13}\b', response.text)
                tutte_parole.update(parole)
            except:
                continue
            progress.progress(pagina/14)
        
        # Organizziamo per lunghezza per velocizzare la ricerca
        for parola in tutte_parole:
            L = len(parola)
            if L not in self.parole_per_lunghezza:
                self.parole_per_lunghezza[L] = []
            self.parole_per_lunghezza[L].append(parola)
        
        progress.empty()
        return len(tutte_parole)

    def verifica_rapida_treccani(self, parola):
        if len(parola) < 2: return True
        if parola in self.parole_cache_verificate:
            return self.parole_cache_verificate[parola]
        
        parola_lower = parola.lower()
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            url = f"https://www.treccani.it/vocabolario/{parola_lower}/"
            resp = requests.get(url, headers=headers, timeout=2)
            if resp.status_code == 200:
                self.parole_cache_verificate[parola] = True
                return True
        except: pass
        
        self.parole_cache_verificate[parola] = False
        return False

    def cerca_parola_veloce(self, pattern_dict, lunghezza, exclude=None):
        if lunghezza not in self.parole_per_lunghezza:
            return None
        
        candidati = self.parole_per_lunghezza[lunghezza]
        random.shuffle(candidati)
        
        for parola in candidati:
            if exclude and parola in exclude:
                continue
            match = True
            for pos, lett in pattern_dict:
                if parola[pos] != lett:
                    match = False
                    break
            if match:
                return parola
        return None

class Cruciverba13x9:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.ROWS = 13
        self.COLS = 9
        self.griglia = [[' ' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.parole_usate = set()
        # Generazione caselle nere simmetriche (circa 15% della griglia)
        self.caselle_nere = self._genera_nere_simmetriche()
        for r, c in self.caselle_nere:
            self.griglia[r][c] = '#'

    def _genera_nere_simmetriche(self):
        nere = set()
        random.seed(time.time())
        # Schema a "macchia di leopardo" simmetrico
        for _ in range(12): 
            r = random.randint(0, self.ROWS // 2)
            c = random.randint(0, self.COLS - 1)
            nere.add((r, c))
            nere.add((self.ROWS - 1 - r, self.COLS - 1 - c)) # Simmetria rotazionale
        return nere

    def griglia_html(self, mostra_lettere=True):
        # Dimensioni ridotte per 13x9
        cell_size = "40px"
        font_size = "20px"
        html = f'<table style="border-collapse: collapse; font-family: sans-serif; font-size: {font_size}; margin: 0 auto; border: 3px solid black;">'
        
        for i in range(self.ROWS):
            html += '<tr>'
            for j in range(self.COLS):
                if (i,j) in self.caselle_nere:
                    html += f'<td style="border: 1px solid black; width: {cell_size}; height: {cell_size}; background: black;">&nbsp;</td>'
                else:
                    cella = self.griglia[i][j] if mostra_lettere else " "
                    html += f'<td style="border: 1px solid black; width: {cell_size}; height: {cell_size}; text-align: center; font-weight: bold; background: white; color: black;">{cella}</td>'
            html += '</tr>'
        return html + '</table>'

    def genera(self):
        # Per una griglia 13x9, usiamo un approccio greedy riga per riga
        # Un algoritmo di backtracking completo sarebbe troppo lento via HTTP
        for r in range(self.ROWS):
            # Trova segmenti bianchi nella riga
            riga_str = "".join(self.griglia[r])
            segmenti = re.finditer(r'[^#]+', riga_str)
            
            for seg in segmenti:
                inizio, fine = seg.start(), seg.end()
                lunghezza = fine - inizio
                if lunghezza < 2: continue
                
                # Crea pattern basato su incroci verticali esistenti
                pattern = []
                for c in range(inizio, fine):
                    if self.griglia[r][c] != ' ':
                        pattern.append((c - inizio, self.griglia[r][c]))
                
                parola = self.dizionario.cerca_parola_veloce(pattern, lunghezza, self.parole_usate)
                if parola:
                    self.parole_usate.add(parola)
                    for k in range(lunghezza):
                        self.griglia[r][inizio + k] = parola[k]
                else:
                    return False # Fallimento semplificato per velocità
        return True

def main():
    st.set_page_config(page_title="Cruciverba 13x9 Pro", layout="wide")
    st.title("🧩 Generatore Cruciverba 13x9")

    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioVerificatoTreccani()
        st.session_state.caricato = False
        st.session_state.grid = None

    if not st.session_state.caricato:
        if st.button("📚 CARICA DIZIONARIO ITALIANO"):
            with st.spinner("Caricamento lemmi..."):
                count = st.session_state.dizionario.carica_lista_base()
                st.session_state.caricato = True
                st.success(f"{count} parole pronte!")
                st.rerun()
    else:
        if st.button("🎲 GENERA SCHEMA 13x9"):
            with st.spinner("Incrociando le parole..."):
                # Tentiamo la generazione finché non ne esce una valida
                for _ in range(5): 
                    g = Cruciverba13x9(st.session_state.dizionario)
                    if g.genera():
                        st.session_state.grid = g
                        break
                if not st.session_state.grid:
                    st.error("Riprova, incrocio troppo complesso!")

    if st.session_state.grid:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Soluzione")
            st.markdown(st.session_state.grid.griglia_html(True), unsafe_allow_html=True)
        with c2:
            st.markdown("### Schema Vuoto")
            st.markdown(st.session_state.grid.griglia_html(False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
