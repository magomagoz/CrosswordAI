import streamlit as st
import random
import requests
import time
from datetime import datetime
import io
from collections import defaultdict

# ==================== DIZIONARIO CON API E CACHE ====================
class DizionarioAPI:
    def __init__(self):
        self.cache_parole = defaultdict(list)
        self.cache_definizioni = {}
        
        # Parole base di partenza (verificate)
        self.parole_base = {
            3: ["RE", "TRE", "SEI", "ORO", "VIA", "IRA", "ERA", "ORA", "DUE", "QUA", "LA", "CHE", "CHI", "NEL", "DEL", "CON", "PER", "TRA", "FRA", "NON", "MAI", "PIU", "GIA", "SOLE"],
            4: ["CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", "FIORE", "ALBERO", "AUTO", "TRENO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", "ARIA", "AMICO", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ANNO", "MESE", "PORTA", "CARTA"],
            5: ["SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", "INVERNO", "PRIMAVERA", "AUTUNNO", "BIANCO", "NERO", "ROSSO", "VERDE", "GIALLO", "BLU", "GRANDE", "PICCOLO"],
            6: ["GIARDINO", "CUCINA", "BAGNO", "CAMERA", "SALONE", "SCUOLA", "RUMORE", "SILENZIO", "PAROLA", "FRASE", "DISCORSO"],
            7: ["PROFESSORE", "STUDENTE", "UNIVERSITA", "BIBLIOTECA", "OSPEDALE", "DOTTORE"]
        }
        
        # Inizializza cache con parole base
        for lunghezza, parole in self.parole_base.items():
            self.cache_parole[lunghezza].extend(parole)
    
    def verifica_parola(self, parola):
        """Verifica se una parola esiste in italiano usando API"""
        parola = parola.upper()
        lunghezza = len(parola)
        
        # Controlla cache locale
        if parola in self.cache_parole[lunghezza]:
            return True
        
        # Chiamata API
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/it/{parola.lower()}"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Aggiungi alla cache
                    if parola not in self.cache_parole[lunghezza]:
                        self.cache_parole[lunghezza].append(parola)
                    
                    # Salva definizione
                    definizione = self._estrai_definizione(data)
                    self.cache_definizioni[parola] = definizione
                    return True
            return False
        except:
            # Se API non risponde, controlla nelle parole base
            return parola in self.parole_base.get(lunghezza, [])
    
    def get_parole_by_lunghezza(self, lunghezza, lettera_iniziale=None, exclude=None):
        """Restituisce parole di data lunghezza, filtrate"""
        parole = self.cache_parole.get(lunghezza, [])
        
        if lettera_iniziale:
            parole = [p for p in parole if p.startswith(lettera_iniziale.upper())]
        
        if exclude:
            parole = [p for p in parole if p not in exclude]
        
        return parole
    
    def get_definizione(self, parola):
        """Ottiene la definizione di una parola"""
        parola = parola.upper()
        
        if parola in self.cache_definizioni:
            return self.cache_definizioni[parola]
        
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
        
        return f"(Definizione di '{parola}' non disponibile)"
    
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

# ==================== GENERATORE CRUCIVERBA OTTIMIZZATO ====================
class CruciverbaOttimizzato:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['#' for _ in range(colonne)] for _ in range(righe)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()  # Per evitare ripetizioni
        
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

    def _verifica_spazio_orizzontale(self, riga, col, lunghezza):
        """Verifica se c'è spazio per una parola orizzontale"""
        if col + lunghezza > self.colonne:
            return False
        
        # Verifica che ai lati ci siano bordi o caselle nere
        if col > 0 and self.griglia[riga][col-1] != '#':
            return False
        if col + lunghezza < self.colonne and self.griglia[riga][col + lunghezza] != '#':
            return False
        
        # Verifica che tutte le celle siano libere o compatibili
        for k in range(lunghezza):
            if self.griglia[riga][col + k] not in ['#', '.']:
                return False
        return True

    def _verifica_spazio_verticale(self, riga, col, lunghezza):
        """Verifica se c'è spazio per una parola verticale"""
        if riga + lunghezza > self.righe:
            return False
        
        if riga > 0 and self.griglia[riga-1][col] != '#':
            return False
        if riga + lunghezza < self.righe and self.griglia[riga + lunghezza][col] != '#':
            return False
        
        for k in range(lunghezza):
            if self.griglia[riga + k][col] not in ['#', '.']:
                return False
        return True

    def _trova_parola_orizzontale(self, riga, col, lunghezza_max):
        """Trova una parola orizzontale valida per la posizione"""
        # Costruisci il pattern delle lettere già presenti
        lettere_fisse = {}
        for k in range(lunghezza_max):
            if self.griglia[riga][col + k] != '#':
                lettere_fisse[k] = self.griglia[riga][col + k]
        
        # Cerca parole di diverse lunghezze
        for l in range(lunghezza_max, 2, -1):
            # Verifica che la parola non sia già usata
            parole = self.dizionario.get_parole_by_lunghezza(l, exclude=self.parole_usate)
            
            for parola in parole:
                # Verifica compatibilità con lettere fisse
                compatibile = True
                for pos, lett in lettere_fisse.items():
                    if pos < l and parola[pos] != lett:
                        compatibile = False
                        break
                
                if compatibile and self.dizionario.verifica_parola(parola):
                    return parola, l
        
        return None, None

    def _trova_parola_verticale(self, riga, col, lunghezza_max):
        """Trova una parola verticale valida per la posizione"""
        lettere_fisse = {}
        for k in range(lunghezza_max):
            if self.griglia[riga + k][col] != '#':
                lettere_fisse[k] = self.griglia[riga + k][col]
        
        for l in range(lunghezza_max, 2, -1):
            parole = self.dizionario.get_parole_by_lunghezza(l, exclude=self.parole_usate)
            
            for parola in parole:
                compatibile = True
                for pos, lett in lettere_fisse.items():
                    if pos < l and parola[pos] != lett:
                        compatibile = False
                        break
                
                if compatibile and self.dizionario.verifica_parola(parola):
                    return parola, l
        
        return None, None

    def genera(self):
        """Genera un cruciverba ottimizzato"""
        try:
            # Pulisci griglia
            self.griglia = [['#' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_usate.clear()
            
            # === STRATEGIA 1: Inserisci parole orizzontali principali ===
            righe_orizzontali = [0, self.righe//2, self.righe-1]
            for riga in righe_orizzontali:
                if riga >= self.righe:
                    continue
                
                for tentativo in range(5):
                    lunghezza = random.randint(3, min(6, self.colonne))
                    col = random.randint(0, self.colonne - lunghezza)
                    
                    if self._verifica_spazio_orizzontale(riga, col, lunghezza):
                        parola, l = self._trova_parola_orizzontale(riga, col, lunghezza)
                        if parola:
                            # Inserisci parola
                            for k, lettera in enumerate(parola):
                                self.griglia[riga][col + k] = lettera
                            self.parole_orizzontali.append((parola, riga, col))
                            self.parole_usate.add(parola)
                            break
            
            # === STRATEGIA 2: Aggiungi parole verticali agli incroci ===
            for riga in range(self.righe):
                for col in range(self.colonne):
                    if self.griglia[riga][col] not in ['#', '.']:
                        lettera = self.griglia[riga][col]
                        
                        # Trova spazio verticale
                        spazio_su = 0
                        while riga - spazio_su - 1 >= 0 and self.griglia[riga - spazio_su - 1][col] == '#':
                            spazio_su += 1
                        
                        spazio_giu = 0
                        while riga + spazio_giu + 1 < self.righe and self.griglia[riga + spazio_giu + 1][col] == '#':
                            spazio_giu += 1
                        
                        lunghezza_max = spazio_su + 1 + spazio_giu
                        
                        if lunghezza_max >= 3:
                            riga_inizio = riga - spazio_su
                            parola, l = self._trova_parola_verticale(riga_inizio, col, lunghezza_max)
                            
                            if parola and parola not in self.parole_usate:
                                # Verifica che la lettera all'incrocio corrisponda
                                if parola[spazio_su] == lettera:
                                    for k, lettera_v in enumerate(parola):
                                        self.griglia[riga_inizio + k][col] = lettera_v
                                    self.parole_verticali.append((parola, riga_inizio, col))
                                    self.parole_usate.add(parola)
            
            # === STRATEGIA 3: Riempi altri spazi orizzontali ===
            for riga in range(self.righe):
                col = 0
                while col < self.colonne:
                    if self.griglia[riga][col] == '#':
                        col += 1
                        continue
                    
                    inizio = col
                    while col < self.colonne and self.griglia[riga][col] != '#':
                        col += 1
                    lunghezza = col - inizio
                    
                    if lunghezza >= 3:
                        # Verifica se c'è già una parola
                        parola_esistente = ""
                        for k in range(lunghezza):
                            parola_esistente += self.griglia[riga][inizio + k]
                        
                        if not self.dizionario.verifica_parola(parola_esistente):
                            # Cerca una parola compatibile
                            parola, l = self._trova_parola_orizzontale(riga, inizio, lunghezza)
                            if parola and parola not in self.parole_usate:
                                for k, lettera in enumerate(parola):
                                    self.griglia[riga][inizio + k] = lettera
                                self.parole_orizzontali.append((parola, riga, inizio))
                                self.parole_usate.add(parola)
            
            # === STATISTICHE FINALI ===
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
            
            # Calcola percentuale caselle nere
            celle_nere = sum(1 for riga in self.griglia for cella in riga if cella == '#')
            percentuale_nere = (celle_nere / (self.righe * self.colonne)) * 100
            
            # Accetta se percentuale nere < 25%
            return percentuale_nere < 25
            
        except Exception as e:
            st.error(f"Errore: {e}")
            return False

# ==================== FUNZIONI PER ESPORTAZIONE ====================
def genera_txt(generatore, includi_lettere=True):
    """Genera un file TXT formattato"""
    output = io.StringIO()
    
    if includi_lettere:
        output.write("CRUCIVERBA COMPILATO\n")
        output.write("="*50 + "\n\n")
        for riga in generatore.griglia:
            riga_str = "| "
            for cella in riga:
                if cella == '#':
                    riga_str += "█ | "
                else:
                    riga_str += f"{cella} | "
            output.write(riga_str + "\n")
    else:
        output.write("SCHEMA VUOTO\n")
        output.write("="*50 + "\n\n")
        for riga in generatore.griglia:
            riga_str = "| "
            for cella in riga:
                if cella == '#':
                    riga_str += "█ | "
                else:
                    riga_str += "  | "
            output.write(riga_str + "\n")
    
    # Definizioni
    output.write("\n\nDEFINIZIONI\n")
    output.write("="*50 + "\n\n")
    
    if generatore.parole_orizzontali:
        output.write("ORIZZONTALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_orizzontali, 1):
            definizione = generatore.dizionario.get_definizione(parola)
            output.write(f"{i:2d}. {parola} - {definizione}\n")
    
    if generatore.parole_verticali:
        output.write("\nVERTICALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_verticali, len(generatore.parole_orizzontali)+1):
            definizione = generatore.dizionario.get_definizione(parola)
            output.write(f"{i:2d}. {parola} - {definizione}\n")
    
    return output.getvalue()

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
    st.markdown("### Massimi incroci - Minime caselle nere")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        righe = st.number_input("Righe", min_value=5, max_value=12, value=5, step=1)
    with col2:
        colonne = st.number_input("Colonne", min_value=5, max_value=12, value=5, step=1)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
            with st.spinner("Generazione cruciverba..."):
                st.session_state.generatore = CruciverbaOttimizzato(righe, colonne, st.session_state.dizionario)
                if st.session_state.generatore.genera():
                    st.success("✅ Cruciverba generato!")
                else:
                    st.error("❌ Riprova con dimensioni diverse")
    
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
        percentuale_nere = (celle_nere / celle_totali) * 100
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Parole Totali", totale_parole)
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Caselle Nere", f"{celle_nere}/{celle_totali}")
        col5.metric("% Nere", f"{percentuale_nere:.1f}%")

if __name__ == "__main__":
    main()
