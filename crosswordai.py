import streamlit as st
import random
from datetime import datetime
import io
import requests
import json
import time

# ==================== DIZIONARIO ITALIANO CON API E CACHE ====================
class DizionarioItalianoAPI:
    def __init__(self):
        # Liste base di parole italiane comuni (fallback se API non risponde)
        self.parole_base = {
            3: ["re", "tre", "sei", "oro", "via", "ira", "era", "ora", "due", "qua", "la", "ra", "tre", "uno", "che", "chi", "nel", "del", "con", "per", "tra", "fra"],
            4: ["casa", "cane", "gatto", "libro", "sole", "luna", "mare", "monte", "fiore", "albero", "auto", "treno", "pane", "vino", "acqua", "fuoco", "terra", "aria", "amico", "scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "anno", "mese", "porta", "carta", "penna", "banco"],
            5: ["scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "estate", "inverno", "primavera", "autunno", "casa", "cane", "gatto", "libro", "sole", "luna", "mare", "monte", "fiore", "albero", "auto", "treno", "pane", "vino", "acqua", "fuoco", "terra", "aria"],
        }
        
        # Cache per le definizioni
        self.cache_definizioni = {}
        
    def get_parole_by_lunghezza(self, lunghezza):
        """Restituisce parole di una data lunghezza"""
        if lunghezza in self.parole_base:
            return self.parole_base[lunghezza]
        # Se la lunghezza non è disponibile, usa la più vicina
        if lunghezza < 3:
            return self.parole_base.get(3, [])
        if lunghezza > 5:
            return self.parole_base.get(5, [])
        return []
    
    def get_definizione(self, parola):
        """Ottiene la definizione di una parola via API con cache"""
        parola_lower = parola.lower()
        
        # Controlla cache
        if parola_lower in self.cache_definizioni:
            return self.cache_definizioni[parola_lower]
        
        # Prova API
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/it/{parola_lower}"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    definizione = self._estrai_definizione(data)
                    self.cache_definizioni[parola_lower] = definizione
                    return definizione
        except:
            pass
        
        # Fallback: definizione generica
        definizioni_fallback = {
            "casa": "Edificio adibito ad abitazione",
            "cane": "Animale domestico a quattro zampe",
            "gatto": "Felino domestico",
            "libro": "Insieme di fogli stampati rilegati",
            "sole": "Stella centrale del sistema solare",
            "luna": "Satellite naturale della Terra",
            "mare": "Grande distesa d'acqua salata",
            "acqua": "Liquido essenziale per la vita",
            "terra": "Pianeta su cui viviamo",
            "amore": "Sentimento di profondo affetto",
            "vita": "Condizione degli esseri organizzati",
            "tempo": "Durata delle cose soggette a mutamento"
        }
        
        if parola_lower in definizioni_fallback:
            return definizioni_fallback[parola_lower]
        
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

# ==================== GENERATORE CRUCIVERBA ROBUSTO ====================
class CruciverbaGeneratoreRobusto:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
    def griglia_html(self, mostra_lettere=True):
        """Restituisce la griglia in formato HTML"""
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 18px; margin: 0 auto; width: 100%; background-color: white;">'
        
        # Calcola numeri se necessario
        numeri_posizioni = {}
        if not mostra_lettere:
            numero = 1
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] not in ['#', '.']:
                        inizio_orizzontale = (j == 0 or self.griglia[i][j-1] in ['#', '.']) and (j < self.colonne-1 and self.griglia[i][j+1] not in ['#', '.'])
                        inizio_verticale = (i == 0 or self.griglia[i-1][j] in ['#', '.']) and (i < self.righe-1 and self.griglia[i+1][j] not in ['#', '.'])
                        if inizio_orizzontale or inizio_verticale:
                            if (i, j) not in numeri_posizioni:
                                numeri_posizioni[(i, j)] = numero
                                numero += 1
        
        for i in range(self.righe):
            html += '<tr>'
            for j in range(self.colonne):
                cella = self.griglia[i][j]
                if cella == '#':
                    html += '<td style="border: 2px solid black; width: 40px; height: 40px; text-align: center; background-color: black;">&nbsp;</td>'
                elif cella == '.':
                    html += '<td style="border: 2px solid black; width: 40px; height: 40px; text-align: center; background-color: white;">&nbsp;</td>'
                elif not mostra_lettere and (i, j) in numeri_posizioni:
                    html += f'<td style="border: 2px solid black; width: 40px; height: 40px; text-align: center; background-color: white; font-size: 16px; font-weight: bold;">{numeri_posizioni[(i, j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid black; width: 40px; height: 40px; text-align: center; background-color: white;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 2px solid black; width: 40px; height: 40px; text-align: center; background-color: white; font-weight: bold; font-size: 18px;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def _verifica_spazio_orizzontale(self, riga, col, lunghezza):
        """Verifica se c'è spazio per una parola orizzontale"""
        if col + lunghezza > self.colonne:
            return False
        try:
            for k in range(lunghezza):
                if self.griglia[riga][col + k] != '.':
                    return False
            return True
        except IndexError:
            return False

    def _verifica_spazio_verticale(self, riga, col, lunghezza):
        """Verifica se c'è spazio per una parola verticale"""
        if riga + lunghezza > self.righe:
            return False
        try:
            for k in range(lunghezza):
                if self.griglia[riga + k][col] != '.':
                    return False
            return True
        except IndexError:
            return False

    def _inserisci_parola_orizzontale(self, parola, riga, col):
        """Inserisce una parola orizzontale"""
        try:
            for k, lettera in enumerate(parola):
                self.griglia[riga][col + k] = lettera
            self.parole_orizzontali.append((parola, riga, col))
            return True
        except IndexError:
            return False

    def _inserisci_parola_verticale(self, parola, riga, col):
        """Inserisce una parola verticale"""
        try:
            for k, lettera in enumerate(parola):
                self.griglia[riga + k][col] = lettera
            self.parole_verticali.append((parola, riga, col))
            return True
        except IndexError:
            return False

    def genera(self):
        """Genera un cruciverba semplice ma funzionale"""
        try:
            # Pulisci griglia
            self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # Determina quante parole inserire in base alla dimensione
            num_parole_oriz = min(2, self.righe)
            num_parole_vert = min(2, self.colonne)
            
            # PAROLE ORIZZONTALI
            righe_disponibili = list(range(self.righe))
            random.shuffle(righe_disponibili)
            
            for _ in range(num_parole_oriz):
                if not righe_disponibili:
                    break
                riga = righe_disponibili.pop()
                
                # Scegli lunghezza appropriata
                lunghezza_max = min(4, self.colonne)
                if lunghezza_max < 3:
                    continue
                    
                for lunghezza in range(lunghezza_max, 2, -1):
                    parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                    if not parole:
                        continue
                    
                    # Prova diverse posizioni
                    for _ in range(5):  # 5 tentativi
                        col = random.randint(0, max(0, self.colonne - lunghezza))
                        if self._verifica_spazio_orizzontale(riga, col, lunghezza):
                            parola = random.choice(parole).upper()
                            if self._inserisci_parola_orizzontale(parola, riga, col):
                                break
                    break
            
            # PAROLE VERTICALI
            colonne_disponibili = list(range(self.colonne))
            random.shuffle(colonne_disponibili)
            
            for _ in range(num_parole_vert):
                if not colonne_disponibili:
                    break
                col = colonne_disponibili.pop()
                
                lunghezza_max = min(4, self.righe)
                if lunghezza_max < 3:
                    continue
                    
                for lunghezza in range(lunghezza_max, 2, -1):
                    parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                    if not parole:
                        continue
                    
                    for _ in range(5):
                        riga = random.randint(0, max(0, self.righe - lunghezza))
                        if self._verifica_spazio_verticale(riga, col, lunghezza):
                            parola = random.choice(parole).upper()
                            if self._inserisci_parola_verticale(parola, riga, col):
                                break
                    break
            
            # CASELLE NERE (circa 10%)
            celle_totali = self.righe * self.colonne
            max_nere = int(celle_totali * 0.10)
            nere_inserite = 0
            
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] == '.' and nere_inserite < max_nere:
                        if random.random() < 0.2:  # 20% di probabilità
                            self.griglia[i][j] = '#'
                            nere_inserite += 1
            
            # Raccogli parole finali
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # Parole orizzontali
            for i in range(self.righe):
                j = 0
                while j < self.colonne:
                    if j < self.colonne and self.griglia[i][j] not in ['#', '.']:
                        inizio = j
                        parola = ""
                        while j < self.colonne and self.griglia[i][j] not in ['#', '.']:
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
                    if i < self.righe and self.griglia[i][j] not in ['#', '.']:
                        inizio = i
                        parola = ""
                        while i < self.righe and self.griglia[i][j] not in ['#', '.']:
                            parola += self.griglia[i][j]
                            i += 1
                        if len(parola) >= 3:
                            self.parole_verticali.append((parola, inizio, j))
                    else:
                        i += 1
            
            # Controlla se abbiamo abbastanza parole
            totale_parole = len(self.parole_orizzontali) + len(self.parole_verticali)
            return totale_parole >= 2  # Almeno 2 parole totali
            
        except Exception as e:
            st.error(f"Errore dettagliato: {e}")
            return False

# ==================== FUNZIONI PER ESPORTAZIONE ====================
def genera_txt(generatore, includi_lettere=True):
    """Genera un file TXT semplice"""
    output = io.StringIO()
    
    if includi_lettere:
        output.write("CRUCIVERBA COMPILATO\n")
        output.write("="*20 + "\n\n")
        for riga in generatore.griglia:
            riga_str = ""
            for cella in riga:
                if cella == '#':
                    riga_str += "█ "
                elif cella == '.':
                    riga_str += "· "
                else:
                    riga_str += f"{cella} "
            output.write(riga_str + "\n")
    else:
        output.write("SCHEMA VUOTO\n")
        output.write("="*20 + "\n\n")
        for riga in generatore.griglia:
            riga_str = ""
            for cella in riga:
                if cella == '#':
                    riga_str += "█ "
                else:
                    riga_str += "□ "
            output.write(riga_str + "\n")
    
    # Definizioni
    output.write("\n\nDEFINIZIONI\n")
    output.write("="*20 + "\n\n")
    
    if generatore.parole_orizzontali:
        output.write("ORIZZONTALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_orizzontali, 1):
            output.write(f"  {i}. {parola}\n")
    
    if generatore.parole_verticali:
        output.write("\nVERTICALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_verticali, len(generatore.parole_orizzontali)+1):
            output.write(f"  {i}. {parola}\n")
    
    return output.getvalue()

# ==================== INTERFACCIA STREAMLIT PER IPAD ====================
def main():
    st.set_page_config(
        page_title="Cruciverba Italiano",
        page_icon="🧩",
        layout="centered"
    )
    
    # Stile touch-friendly
    st.markdown("""
        <style>
        .stButton button {
            font-size: 20px !important;
            padding: 15px !important;
            width: 100%;
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .stNumberInput input {
            font-size: 18px !important;
            padding: 10px !important;
        }
        .st-emotion-cache-1kyxreq {
            font-size: 18px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Inizializza dizionario
    if 'dizionario' not in st.session_state:
        with st.spinner("Caricamento dizionario..."):
            st.session_state.dizionario = DizionarioItalianoAPI()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    # Header
    st.title("🧩 Cruciverba Italiani")
    st.caption("Parole dalla Treccani")
    
    # Input in colonne
    col1, col2 = st.columns(2)
    with col1:
        righe = st.number_input("Righe", min_value=4, max_value=7, value=5, step=1)
    with col2:
        colonne = st.number_input("Colonne", min_value=4, max_value=7, value=5, step=1)
    
    # Pulsante grande
    if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
        with st.spinner("Creazione in corso..."):
            st.session_state.generatore = CruciverbaGeneratoreRobusto(righe, colonne, st.session_state.dizionario)
            if st.session_state.generatore.genera():
                st.success("✅ Cruciverba pronto!")
            else:
                st.error("❌ Riprova con dimensioni diverse")
    
    # Mostra risultato
    if st.session_state.generatore:
        st.markdown("---")
        
        # Due tab
        tab1, tab2 = st.tabs(["📋 Compilato", "🔢 Vuoto"])
        
        with tab1:
            st.subheader("Cruciverba Compilato")
            st.markdown(st.session_state.generatore.griglia_html(mostra_lettere=True), unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Schema da Riempire")
            st.markdown(st.session_state.generatore.griglia_html(mostra_lettere=False), unsafe_allow_html=True)
        
        # Statistiche
        totale_parole = len(st.session_state.generatore.parole_orizzontali) + len(st.session_state.generatore.parole_verticali)
        celle_nere = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella == '#')
        celle_piene = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella not in ['#', '.'])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole", totale_parole)
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Caselle nere", celle_nere)
        
        # Definizioni
        st.markdown("---")
        st.subheader("📚 Definizioni")
        
        if st.button("📖 CARICA DEFINIZIONI", use_container_width=True):
            with st.spinner("Caricamento definizioni..."):
                if st.session_state.generatore.parole_orizzontali:
                    st.write("**Orizzontali:**")
                    for i, (parola, r, c) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                        definizione = st.session_state.dizionario.get_definizione(parola)
                        st.write(f"**{i}.** {parola}: {definizione}")
                        time.sleep(0.3)
                
                if st.session_state.generatore.parole_verticali:
                    st.write("**Verticali:**")
                    for i, (parola, r, c) in enumerate(st.session_state.generatore.parole_verticali, len(st.session_state.generatore.parole_orizzontali)+1):
                        definizione = st.session_state.dizionario.get_definizione(parola)
                        st.write(f"**{i}.** {parola}: {definizione}")
                        time.sleep(0.3)
        
        # Esportazione
        st.markdown("---")
        st.subheader("📥 Esporta")
        
        col1, col2 = st.columns(2)
        with col1:
            txt_compilato = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button("📄 TXT Compilato", data=txt_compilato, 
                             file_name=f"cruciverba_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             use_container_width=True)
        with col2:
            txt_vuoto = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button("📄 TXT Vuoto", data=txt_vuoto,
                             file_name=f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             use_container_width=True)

if __name__ == "__main__":
    main()
