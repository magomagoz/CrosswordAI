import streamlit as st
import random
from datetime import datetime
import io
import requests
import json
import time

# ==================== DIZIONARIO PROFESSIONALE ====================
class DizionarioProfessionale:
    def __init__(self):
        # Dizionario ricco di parole italiane (versione estesa)
        self.parole = {
            3: ["re", "tre", "sei", "oro", "via", "ira", "era", "ora", "due", "qua", "la", "ra", "tre", "uno", "che", "chi", "nel", "del", "con", "per", "tra", "fra", "non", "mai", "piu", "gia", "qui", "qua", "lui", "lei", "noi", "voi"],
            
            4: ["casa", "cane", "gatto", "libro", "sole", "luna", "mare", "monte", "fiore", "albero", "auto", "treno", "pane", "vino", "acqua", "fuoco", "terra", "aria", "amico", "scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "anno", "mese", "porta", "carta", "penna", "banco", "bello", "brutto", "caldo", "freddo", "dolce", "amaro", "sale", "pasta", "pizza", "mamma", "papa", "nonno", "nonna", "gara", "corsa", "volo", "canto", "voce", "suono"],
            
            5: ["scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "estate", "inverno", "primavera", "autunno", "casa", "cane", "gatto", "libro", "sole", "luna", "mare", "monte", "fiore", "albero", "auto", "treno", "pane", "vino", "acqua", "fuoco", "terra", "aria", "amico", "giardino", "cucina", "bagno", "camera", "salone", "letto", "sedia", "tavolo", "porta", "finestra", "muro", "tetto", "piano", "scala"],
            
            6: ["giardino", "cucina", "bagno", "camera", "salone", "scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "estate", "inverno", "primavera", "autunno", "bianco", "nero", "rosso", "verde", "giallo", "blu", "marrone", "grande", "piccolo", "nuovo", "vecchio", "giovane", "anziano", "mattina", "sera", "pomeriggio", "mezzanotte"],
            
            7: ["giardino", "cucina", "bagno", "camera", "salone", "scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "estate", "inverno", "primavera", "autunno", "bianco", "nero", "rosso", "verde", "giallo", "blu", "marrone", "rumore", "silenzio", "parola", "frase", "discorso", "pensiero"],
            
            8: ["giardino", "cucina", "bagno", "camera", "salone", "scuola", "amore", "tempo", "vita", "morte", "notte", "giorno", "estate", "inverno", "primavera", "autunno", "bianco", "nero", "rosso", "verde", "giallo", "blu", "marrone", "professore", "studente", "universita"],
            
            9: ["professore", "studente", "universita", "biblioteca", "laboratorio", "ospedale", "dottore", "infermiere", "farmacia"],
            
            10: ["professore", "studente", "universita", "biblioteca", "laboratorio", "ospedale", "dottore", "infermiere", "farmacia", "ingegnere", "architetto"],
            
            11: ["professore", "universita", "biblioteca", "laboratorio", "ospedale"],
            
            12: ["professore", "universita", "biblioteca"],
        }
        
        # Cache per definizioni
        self.cache_definizioni = {}
        
    def get_parole_by_lunghezza(self, lunghezza):
        """Restituisce parole di una data lunghezza"""
        if lunghezza in self.parole:
            return self.parole[lunghezza]
        # Cerca la lunghezza più vicina
        for l in range(lunghezza-1, lunghezza+2):
            if l in self.parole:
                return self.parole[l]
        return []
    
    def get_definizione(self, parola):
        """Ottiene la definizione di una parola"""
        parola_lower = parola.lower()
        
        if parola_lower in self.cache_definizioni:
            return self.cache_definizioni[parola_lower]
        
        # Definizioni predefinite per parole comuni
        definizioni = {
            "amore": "Sentimento di profondo affetto",
            "vita": "Condizione degli esseri organizzati",
            "tempo": "Durata delle cose soggette a mutamento",
            "morte": "Cessazione della vita",
            "notte": "Periodo di oscurità",
            "giorno": "Periodo di luce",
            "estate": "Stagione più calda",
            "inverno": "Stagione più fredda",
            "casa": "Edificio adibito ad abitazione",
            "cane": "Animale domestico",
            "gatto": "Felino domestico",
            "libro": "Insieme di fogli stampati",
            "sole": "Stella centrale del sistema solare",
            "luna": "Satellite naturale della Terra",
            "mare": "Grande distesa d'acqua salata",
            "acqua": "Liquido essenziale per la vita",
            "terra": "Pianeta su cui viviamo",
            "aria": "Miscuglio di gas",
            "fuoco": "Fiamma che produce calore",
            "bianco": "Colore della neve",
            "nero": "Colore della notte",
            "rosso": "Colore del sangue",
            "verde": "Colore dell'erba",
            "giallo": "Colore del limone",
            "blu": "Colore del cielo",
            "rumore": "Suono confuso e sgradevole",
            "silenzio": "Assenza di rumore",
            "parola": "Unità linguistica dotata di significato",
            "frase": "Insieme di parole con senso compiuto",
        }
        
        if parola_lower in definizioni:
            self.cache_definizioni[parola_lower] = definizioni[parola_lower]
            return definizioni[parola_lower]
        
        return f"(Definizione di '{parola}' non disponibile)"

# ==================== GENERATORE CRUCIVERBA PROFESSIONALE ====================
class CruciverbaProfessionale:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
    def griglia_html(self, mostra_lettere=True):
        """Restituisce la griglia in formato HTML professionale"""
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 16px; margin: 0 auto; width: 100%; background-color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
        
        # Calcola numeri per definizioni
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
                    html += '<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: #222;">&nbsp;</td>'
                elif cella == '.':
                    html += '<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white;">&nbsp;</td>'
                elif not mostra_lettere and (i, j) in numeri_posizioni:
                    html += f'<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white; font-size: 14px; font-weight: bold; color: #c41e3a;">{numeri_posizioni[(i, j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 2px solid #333; width: 40px; height: 40px; text-align: center; background-color: white; font-weight: bold; font-size: 18px; color: #333;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def _cerca_parola_orizzontale(self, riga, col, lunghezza):
        """Cerca una parola orizzontale compatibile con le lettere esistenti"""
        # Costruisci il pattern
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga][col + k]
            if cella != '.' and cella != '#':
                pattern.append((k, cella))
        
        # Cerca parole nel dizionario
        parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
        if not parole:
            return None
        
        # Filtra per pattern
        candidate = []
        for p in parole:
            p_upper = p.upper()
            match = True
            for pos, lettera in pattern:
                if p_upper[pos] != lettera:
                    match = False
                    break
            if match:
                candidate.append(p_upper)
        
        return random.choice(candidate) if candidate else None

    def _cerca_parola_verticale(self, riga, col, lunghezza):
        """Cerca una parola verticale compatibile con le lettere esistenti"""
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga + k][col]
            if cella != '.' and cella != '#':
                pattern.append((k, cella))
        
        parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
        if not parole:
            return None
        
        candidate = []
        for p in parole:
            p_upper = p.upper()
            match = True
            for pos, lettera in pattern:
                if p_upper[pos] != lettera:
                    match = False
                    break
            if match:
                candidate.append(p_upper)
        
        return random.choice(candidate) if candidate else None

    def genera(self):
        """Genera un cruciverba professionale"""
        try:
            # Pulisci griglia
            self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # === STRATEGIA: Costruzione incrementale ===
            
            # 1. Inserisci una parola orizzontale lunga al centro
            centro_riga = self.righe // 2
            lunghezza_max = min(10, self.colonne)
            
            for lunghezza in range(lunghezza_max, 4, -1):
                parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                if parole:
                    parola = random.choice(parole).upper()
                    col_inizio = max(0, (self.colonne - lunghezza) // 2)
                    
                    # Inserisci
                    for k, lettera in enumerate(parola):
                        self.griglia[centro_riga][col_inizio + k] = lettera
                    self.parole_orizzontali.append((parola, centro_riga, col_inizio))
                    break
            
            # 2. Per ogni lettera della parola centrale, prova a inserire verticali
            for j in range(self.colonne):
                if self.griglia[centro_riga][j] != '.':
                    lettera = self.griglia[centro_riga][j]
                    
                    # Cerca parole verticali che contengono questa lettera
                    for lunghezza_v in range(5, min(8, self.righe)):
                        parole_v = self.dizionario.get_parole_by_lunghezza(lunghezza_v)
                        if not parole_v:
                            continue
                        
                        # Filtra parole che hanno la lettera in qualche posizione
                        candidate = []
                        for p in parole_v:
                            p_upper = p.upper()
                            for pos, lett in enumerate(p_upper):
                                if lett == lettera:
                                    candidate.append((p_upper, pos))
                        
                        if candidate:
                            parola_v, pos_lettera = random.choice(candidate)
                            riga_inizio = centro_riga - pos_lettera
                            
                            if riga_inizio >= 0 and riga_inizio + lunghezza_v <= self.righe:
                                # Verifica compatibilità
                                compatibile = True
                                for k in range(lunghezza_v):
                                    cella = self.griglia[riga_inizio + k][j]
                                    if cella not in ['.', '#'] and cella != parola_v[k]:
                                        compatibile = False
                                        break
                                
                                if compatibile:
                                    # Inserisci
                                    for k, lettera_v in enumerate(parola_v):
                                        self.griglia[riga_inizio + k][j] = lettera_v
                                    self.parole_verticali.append((parola_v, riga_inizio, j))
                                    break
            
            # 3. Aggiungi altre parole orizzontali
            for riga in range(self.righe):
                if riga == centro_riga:
                    continue
                
                j = 0
                while j < self.colonne:
                    if self.griglia[riga][j] != '.':
                        # Trova lunghezza della parola esistente
                        inizio = j
                        while j < self.colonne and self.griglia[riga][j] != '.':
                            j += 1
                        lunghezza = j - inizio
                        
                        if lunghezza >= 3:
                            # Cerca di completare con una parola del dizionario
                            parola = self._cerca_parola_orizzontale(riga, inizio, lunghezza)
                            if parola:
                                for k, lettera in enumerate(parola):
                                    self.griglia[riga][inizio + k] = lettera
                                self.parole_orizzontali.append((parola, riga, inizio))
                    else:
                        j += 1
            
            # 4. Aggiungi altre parole verticali
            for col in range(self.colonne):
                i = 0
                while i < self.righe:
                    if self.griglia[i][col] != '.':
                        inizio = i
                        while i < self.righe and self.griglia[i][col] != '.':
                            i += 1
                        lunghezza = i - inizio
                        
                        if lunghezza >= 3:
                            parola = self._cerca_parola_verticale(inizio, col, lunghezza)
                            if parola:
                                for k, lettera in enumerate(parola):
                                    self.griglia[inizio + k][col] = lettera
                                self.parole_verticali.append((parola, inizio, col))
                    else:
                        i += 1
            
            # 5. Aggiungi caselle nere (solo il 5-10%)
            celle_totali = self.righe * self.colonne
            max_nere = int(celle_totali * 0.08)  # 8% massimo
            nere_inserite = 0
            
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] == '.' and nere_inserite < max_nere:
                        # Metti casella nera solo se isolata
                        if random.random() < 0.1:  # 10% probabilità
                            self.griglia[i][j] = '#'
                            nere_inserite += 1
            
            # 6. Raccogli tutte le parole finali
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            for i in range(self.righe):
                j = 0
                while j < self.colonne:
                    if self.griglia[i][j] not in ['#', '.']:
                        inizio = j
                        parola = ""
                        while j < self.colonne and self.griglia[i][j] not in ['#', '.']:
                            parola += self.griglia[i][j]
                            j += 1
                        if len(parola) >= 3:
                            self.parole_orizzontali.append((parola, i, inizio))
                    else:
                        j += 1
            
            for j in range(self.colonne):
                i = 0
                while i < self.righe:
                    if self.griglia[i][j] not in ['#', '.']:
                        inizio = i
                        parola = ""
                        while i < self.righe and self.griglia[i][j] not in ['#', '.']:
                            parola += self.griglia[i][j]
                            i += 1
                        if len(parola) >= 3:
                            self.parole_verticali.append((parola, inizio, j))
                    else:
                        i += 1
            
            return True
            
        except Exception as e:
            st.error(f"Errore: {e}")
            return False

# ==================== FUNZIONI PER ESPORTAZIONE ====================
def genera_txt(generatore, includi_lettere=True):
    """Genera un file TXT formattato"""
    output = io.StringIO()
    
    if includi_lettere:
        output.write("CRUCIVERBA COMPILATO\n")
        output.write("="*40 + "\n\n")
        for riga in generatore.griglia:
            riga_str = "| "
            for cella in riga:
                if cella == '#':
                    riga_str += "█ | "
                elif cella == '.':
                    riga_str += "  | "
                else:
                    riga_str += f"{cella} | "
            output.write(riga_str + "\n")
    else:
        output.write("SCHEMA VUOTO\n")
        output.write("="*40 + "\n\n")
        for riga in generatore.griglia:
            riga_str = "| "
            for cella in riga:
                if cella == '#':
                    riga_str += "█ | "
                else:
                    riga_str += "  | "
            output.write(riga_str + "\n")
    
    return output.getvalue()

# ==================== INTERFACCIA STREAMLIT ====================
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
            st.session_state.dizionario = DizionarioProfessionale()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba Italiano Professionale")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        righe = st.number_input("Righe", min_value=5, max_value=15, value=10, step=1)
    with col2:
        colonne = st.number_input("Colonne", min_value=5, max_value=15, value=12, step=1)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
            with st.spinner("Generazione cruciverba professionale..."):
                st.session_state.generatore = CruciverbaProfessionale(righe, colonne, st.session_state.dizionario)
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
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole Totali", totale_parole)
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Caselle Nere", celle_nere)
        
        # Esportazione
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button("📄 Scarica TXT Compilato", data=txt,
                             file_name=f"cruciverba_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with col2:
            txt2 = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button("📄 Scarica TXT Vuoto", data=txt2,
                             file_name=f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

if __name__ == "__main__":
    main()
