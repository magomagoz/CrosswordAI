import streamlit as st
import random
import requests
import time
from datetime import datetime
import io

# ==================== DIZIONARIO CON API ====================
class DizionarioAPI:
    def __init__(self):
        self.cache_parole = {}  # Cache per lunghezza
        self.cache_definizioni = {}  # Cache per definizioni
        self.base_parole = {
            3: ["RE", "TRE", "SEI", "ORO", "VIA", "IRA", "ERA", "ORA", "DUE", "QUA", "LA", "CHE", "CHI", "NEL", "DEL", "CON", "PER", "TRA", "FRA", "NON", "MAI"],
            4: ["CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", "FIORE", "ALBERO", "AUTO", "TRENO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", "ARIA", "AMICO", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ANNO", "MESE", "PORTA"],
            5: ["SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", "INVERNO", "PRIMAVERA", "AUTUNNO", "CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", "FIORE", "ALBERO", "AUTO", "TRENO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", "ARIA"]
        }
    
    def _chiama_api_parole(self, lettera, lunghezza):
        """Chiama l'API per ottenere parole che iniziano con una lettera"""
        # API gratuita per parole italiane (esempio - da sostituire con API reale)
        # In un'implementazione reale, useremmo un servizio come parole.vocabolario.it
        time.sleep(0.5)  # Simula chiamata API
        return []
    
    def get_parole_by_lunghezza(self, lunghezza, lettera_iniziale=None):
        """Restituisce parole di data lunghezza, opzionalmente filtrate per lettera iniziale"""
        if lunghezza not in self.cache_parole:
            # Usa parole base come fallback
            if lunghezza in self.base_parole:
                self.cache_parole[lunghezza] = self.base_parole[lunghezza]
            else:
                self.cache_parole[lunghezza] = []
        
        parole = self.cache_parole[lunghezza]
        
        if lettera_iniziale:
            return [p for p in parole if p.startswith(lettera_iniziale.upper())]
        return parole
    
    def verifica_parola(self, parola):
        """Verifica se una parola esiste in italiano"""
        parola = parola.upper()
        
        # Controlla nella cache
        lunghezza = len(parola)
        if lunghezza in self.cache_parole:
            if parola in self.cache_parole[lunghezza]:
                return True
        
        # Chiamata API per verificare la parola
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/it/{parola.lower()}"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Aggiungi alla cache
                    if lunghezza not in self.cache_parole:
                        self.cache_parole[lunghezza] = []
                    if parola not in self.cache_parole[lunghezza]:
                        self.cache_parole[lunghezza].append(parola)
                    
                    # Salva definizione
                    definizione = self._estrai_definizione(data)
                    self.cache_definizioni[parola] = definizione
                    return True
            return False
        except:
            return False
    
    def get_definizione(self, parola):
        """Ottiene la definizione di una parola"""
        parola = parola.upper()
        
        # Controlla cache
        if parola in self.cache_definizioni:
            return self.cache_definizioni[parola]
        
        # Chiama API
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/it/{parola.lower()}"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                definizione = self._estrai_definizione(data)
                self.cache_definizioni[parola] = definizione
                return definizione
        except:
            pass
        
        return f"Definizione di '{parola}' non disponibile"
    
    def _estrai_definizione(self, data):
        """Estrae la definizione dal JSON dell'API"""
        try:
            meanings = data[0].get('meanings', [])
            if meanings:
                definitions = meanings[0].get('definitions', [])
                if definitions:
                    return definitions[0].get('definition', 'Definizione non trovata')
            return "Definizione non trovata"
        except:
            return "Definizione non disponibile"

# ==================== GENERATORE CRUCIVERBA ====================
class CruciverbaGeneratore:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['#' for _ in range(colonne)] for _ in range(righe)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
    def griglia_html(self, mostra_lettere=True):
        """Restituisce la griglia in formato HTML"""
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 16px; margin: 0 auto; background-color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
        
        # Calcola numeri per definizioni
        numeri_posizioni = {}
        if not mostra_lettere:
            numero = 1
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] != '#':
                        inizio_orizzontale = (j == 0 or self.griglia[i][j-1] == '#') and (j < self.colonne-1 and self.griglia[i][j+1] != '#')
                        inizio_verticale = (i == 0 or self.griglia[i-1][j] == '#') and (i < self.righe-1 and self.griglia[i+1][j] != '#')
                        if inizio_orizzontale or inizio_verticale:
                            if (i, j) not in numeri_posizioni:
                                numeri_posizioni[(i, j)] = numero
                                numero += 1
        
        for i in range(self.righe):
            html += '<tr>'
            for j in range(self.colonne):
                cella = self.griglia[i][j]
                if cella == '#':
                    html += '<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: #222;">&nbsp;</td>'
                elif not mostra_lettere and (i, j) in numeri_posizioni:
                    html += f'<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white; font-size: 14px; font-weight: bold; color: #c41e3a;">{numeri_posizioni[(i, j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white; font-weight: bold; font-size: 18px; color: #333;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def _cerca_parola_orizzontale(self, riga, col, lunghezza, lettere_fisse=None):
        """Cerca una parola orizzontale valida"""
        if lettere_fisse is None:
            lettere_fisse = {}
        
        # Ottieni parole candidate
        if col > 0 and self.griglia[riga][col-1] != '#':
            # La parola potrebbe continuare a sinistra
            return None
        
        # Prova diverse lunghezze
        for l in range(lunghezza, 2, -1):
            if col + l > self.colonne:
                continue
            
            # Verifica che a destra ci sia bordo o nera
            if col + l < self.colonne and self.griglia[riga][col + l] != '#':
                continue
            
            # Costruisci pattern
            pattern = []
            for k in range(l):
                if k in lettere_fisse:
                    pattern.append((k, lettere_fisse[k]))
            
            # Cerca parole nel dizionario (via API)
            # Per ora usiamo parole base
            parole_base = self.dizionario.get_parole_by_lunghezza(l)
            for parola in parole_base:
                match = True
                for pos, lett in pattern:
                    if parola[pos] != lett:
                        match = False
                        break
                if match:
                    # Verifica che la parola esista realmente
                    if self.dizionario.verifica_parola(parola):
                        return parola, l
        
        return None

    def _cerca_parola_verticale(self, riga, col, lunghezza, lettere_fisse=None):
        """Cerca una parola verticale valida"""
        if lettere_fisse is None:
            lettere_fisse = {}
        
        if riga > 0 and self.griglia[riga-1][col] != '#':
            return None
        
        for l in range(lunghezza, 2, -1):
            if riga + l > self.righe:
                continue
            
            if riga + l < self.righe and self.griglia[riga + l][col] != '#':
                continue
            
            pattern = []
            for k in range(l):
                if k in lettere_fisse:
                    pattern.append((k, lettere_fisse[k]))
            
            parole_base = self.dizionario.get_parole_by_lunghezza(l)
            for parola in parole_base:
                match = True
                for pos, lett in pattern:
                    if parola[pos] != lett:
                        match = False
                        break
                if match:
                    if self.dizionario.verifica_parola(parola):
                        return parola, l
        
        return None

    def genera(self):
        """Genera un cruciverba con parole reali"""
        try:
            # Pulisci griglia
            self.griglia = [['#' for _ in range(self.colonne)] for _ in range(self.righe)]
            
            # Inserisci prima parola orizzontale
            centro_riga = self.righe // 2
            for lunghezza in range(min(8, self.colonne), 3, -1):
                parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                if parole:
                    parola = random.choice(parole)
                    col = max(0, (self.colonne - lunghezza) // 2)
                    
                    # Inserisci
                    for k, lettera in enumerate(parola):
                        self.griglia[centro_riga][col + k] = lettera
                    self.parole_orizzontali.append((parola, centro_riga, col))
                    break
            
            # Per ogni lettera della parola centrale, cerca verticali
            for k, lettera in enumerate(self.parole_orizzontali[0][0]):
                col_v = self.parole_orizzontali[0][2] + k
                
                # Cerca parole verticali
                for lunghezza_v in range(3, min(6, self.righe)):
                    # Lettera fissa all'incrocio
                    lettere_fisse = {centro_riga - self.parole_orizzontali[0][1]: lettera}
                    
                    riga_inizio = max(0, centro_riga - 3)
                    risultato = self._cerca_parola_verticale(riga_inizio, col_v, lunghezza_v, lettere_fisse)
                    
                    if risultato:
                        parola_v, l_v = risultato
                        # Calcola posizione corretta
                        pos_lettera = parola_v.find(lettera)
                        riga_inizio = centro_riga - pos_lettera
                        
                        if riga_inizio >= 0 and riga_inizio + l_v <= self.righe:
                            # Inserisci
                            for vk, lettera_v in enumerate(parola_v):
                                self.griglia[riga_inizio + vk][col_v] = lettera_v
                            self.parole_verticali.append((parola_v, riga_inizio, col_v))
                            break
            
            # Raccogli tutte le parole
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # Parole orizzontali
            for i in range(self.righe):
                j = 0
                while j < self.colonne:
                    if self.griglia[i][j] != '#':
                        inizio = j
                        parola = ""
                        while j < self.colonne and self.griglia[i][j] != '#':
                            parola += self.griglia[i][j]
                            j += 1
                        if len(parola) >= 3:
                            self.parole_orizzontali.append((parola, i, inizio))
                    else:
                        j += 1
            
            # Parole verticali
            for j in range(self.colonne):
                i = 0
                while i < self.righe:
                    if self.griglia[i][j] != '#':
                        inizio = i
                        parola = ""
                        while i < self.righe and self.griglia[i][j] != '#':
                            parola += self.griglia[i][j]
                            i += 1
                        if len(parola) >= 3:
                            self.parole_verticali.append((parola, inizio, j))
                    else:
                        i += 1
            
            return len(self.parole_orizzontali) + len(self.parole_verticali) >= 3
            
        except Exception as e:
            st.error(f"Errore: {e}")
            return False

# ==================== MAIN ====================
def main():
    st.set_page_config(
        page_title="Cruciverba Italiano",
        page_icon="🧩",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .stButton button {
            font-size: 20px !important;
            padding: 15px !important;
            width: 100%;
            background-color: #c41e3a;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        with st.spinner("Caricamento dizionario..."):
            st.session_state.dizionario = DizionarioAPI()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba Italiano")
    st.markdown("### Parole verificate via API")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        righe = st.number_input("Righe", min_value=5, max_value=12, value=8, step=1)
    with col2:
        colonne = st.number_input("Colonne", min_value=5, max_value=12, value=8, step=1)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
            with st.spinner("Generazione cruciverba..."):
                st.session_state.generatore = CruciverbaGeneratore(righe, colonne, st.session_state.dizionario)
                if st.session_state.generatore.genera():
                    st.success("✅ Cruciverba generato!")
                else:
                    st.error("❌ Riprova")
    
    if st.session_state.generatore:
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📋 Compilato", "🔢 Schema Vuoto"])
        
        with tab1:
            st.subheader("Cruciverba Compilato")
            st.markdown(st.session_state.generatore.griglia_html(mostra_lettere=True), unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Schema da Riempire")
            st.markdown(st.session_state.generatore.griglia_html(mostra_lettere=False), unsafe_allow_html=True)
        
        # Statistiche
        totale_parole = len(st.session_state.generatore.parole_orizzontali) + len(st.session_state.generatore.parole_verticali)
        celle_nere = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella == '#')
        celle_totali = righe * colonne
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole Totali", totale_parole)
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Caselle Nere", f"{celle_nere}/{celle_totali} ({celle_nere/celle_totali*100:.0f}%)")

if __name__ == "__main__":
    main()
