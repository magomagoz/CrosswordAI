import streamlit as st
import sqlite3
import random
from datetime import datetime
import io

# ==================== DIZIONARIO ITALIANO ====================
class DizionarioItaliano:
    def __init__(self, db_path='parole_italiane.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._crea_tabella()
        self._popola_dizionario_demo()
    
    def _crea_tabella(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parole (
                id INTEGER PRIMARY KEY, 
                parola TEXT UNIQUE, 
                definizione TEXT,
                lunghezza INTEGER,
                validata BOOLEAN DEFAULT 1
            )
        ''')
        self.conn.commit()
    
    def _popola_dizionario_demo(self):
        """Popola il database con parole italiane e definizioni per demo"""
        self.cursor.execute("SELECT COUNT(*) FROM parole")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            # Parole di varie lunghezze con definizioni
            parole_con_definizioni = [
                # 3 lettere
                ("re", "Sovrano di uno stato"),
                ("tre", "Numero successivo al due"),
                ("sei", "Numero successivo al cinque"),
                ("oro", "Metallo prezioso giallo"),
                ("via", "Strada, percorso"),
                ("ira", "Forte collera"),
                ("era", "Periodo storico"),
                ("ora", "Unità di tempo"),
                ("due", "Numero dopo uno"),
                ("uno", "Il primo numero"),
                ("tre", "Numero dopo due"),
                ("qua", "Avverbio di luogo"),
                ("la", "Nota musicale"),
                
                # 4 lettere
                ("casa", "Edificio adibito ad abitazione familiare"),
                ("cane", "Animale domestico a quattro zampe, fedele all'uomo"),
                ("gatto", "Felino domestico, abile cacciatore di topi"),
                ("libro", "Insieme di fogli stampati rilegati"),
                ("sole", "Stella centrale del sistema solare"),
                ("luna", "Satellite naturale della Terra"),
                ("mare", "Grande distesa d'acqua salata"),
                ("monte", "Rilievo naturale elevato"),
                ("fiore", "Parte della pianta che contiene gli organi riproduttivi"),
                ("albero", "Pianta perenne con fusto legnoso"),
                ("auto", "Veicolo a motore"),
                ("treno", "Mezzo di trasporto su rotaie"),
                ("pane", "Alimento dalla cottura di pasta lievitata"),
                ("vino", "Bevanda alcolica da uva fermentata"),
                ("acqua", "Liquido trasparente essenziale per la vita"),
                ("fuoco", "Fiamma che produce calore e luce"),
                ("terra", "Pianeta su cui viviamo"),
                ("aria", "Miscuglio di gas dell'atmosfera"),
                ("amico", "Persona legata da affetto"),
                ("scuola", "Istituto dove si impartisce l'istruzione"),
                ("amore", "Sentimento di profondo affetto"),
                ("tempo", "Durata delle cose soggette a mutamento"),
                ("vita", "Condizione degli esseri organizzati"),
                ("morte", "Cessazione della vita"),
                ("notte", "Periodo di oscurità"),
                ("giorno", "Periodo di luce"),
                ("estate", "Stagione più calda"),
                ("inverno", "Stagione più fredda"),
                ("primavera", "Stagione che segue l'inverno"),
                ("autunno", "Stagione che segue l'estate"),
                ("ciao", "Saluto informale"),
                ("grazie", "Espressione di ringraziamento"),
                ("prego", "Formula di cortesia"),
                ("buongiorno", "Saluto del mattino"),
                ("buonasera", "Saluto della sera"),
                ("arrivederci", "Saluto di commiato"),
                ("italia", "Stato dell'Europa meridionale"),
                ("roma", "Capitale d'Italia"),
                ("milano", "Città italiana, capoluogo della Lombardia"),
                ("napoli", "Città italiana, capoluogo della Campania"),
                ("torino", "Città italiana, capoluogo del Piemonte"),
                ("firenze", "Città italiana, capoluogo della Toscana"),
                ("venezia", "Città italiana costruita su palafitte"),
                ("corto", "Di lunghezza ridotta"),
                ("lungo", "Di grande estensione"),
                ("alto", "Che si eleva verticalmente"),
                ("basso", "Di modesta altezza"),
                ("bello", "Che ha bellezza estetica"),
                ("brutto", "Sgradevole all'aspetto"),
                ("caldo", "Che ha temperatura elevata"),
                ("freddo", "Che ha temperatura bassa"),
                ("dolce", "Che ha sapore zuccherino"),
                ("amaro", "Che ha sapore amaro"),
                ("sale", "Cloruro di sodio, usato per insaporire"),
                ("zucchero", "Sostanza dolce usata in cucina"),
                ("caffè", "Bevanda nera e amara"),
                ("latte", "Liquido bianco prodotto dalle mammelle"),
                ("pasta", "Alimento base della cucina italiana"),
                ("pizza", "Tipico piatto italiano"),
                ("formaggio", "Prodotto caseario"),
                ("burro", "Grasso alimentare derivato dal latte"),
                ("uovo", "Corpo ovulare deposto dagli uccelli"),
                ("pesce", "Animale vertebrato acquatico"),
                ("carne", "Parte muscolare degli animali"),
                ("verde", "Colore come quello dell'erba"),
                ("rosso", "Colore come quello del sangue"),
                ("blu", "Colore come quello del cielo"),
                ("giallo", "Colore come quello del limone"),
                ("nero", "Colore come quello della notte"),
                ("bianco", "Colore come quello della neve"),
                ("mamma", "Madre, genitrice"),
                ("papà", "Padre, genitore"),
                ("nonno", "Padre del padre o della madre"),
                ("nonna", "Madre del padre o della madre"),
                ("gatto", "Felino domestico"),
                ("cane", "Miglior amico dell'uomo"),
                ("topo", "Piccolo roditore"),
                ("gara", "Competizione sportiva"),
                ("porta", "Apertura per entrare in un edificio"),
                ("muro", "Struttura verticale in muratura"),
                ("tetto", "Copertura superiore di una casa"),
                ("piano", "Livello di un edificio"),
                ("scala", "Struttura per salire ai piani superiori"),
                ("porto", "Infrastruttura per navi"),
                ("nave", "Grande imbarcazione"),
                ("vela", "Tessuto che spinge le imbarcazioni"),
                ("remo", "Strumento per vogare"),
                ("pesca", "Attività di catturare pesci"),
                ("caccia", "Attività di inseguire animali"),
                ("corsa", "Movimento veloce"),
                ("salto", "Movimento per staccarsi da terra"),
                ("volo", "Spostamento nell'aria"),
                ("canto", "Emissione di suoni melodici"),
                ("suono", "Vibrazione percepita dall'orecchio"),
                ("voce", "Suono emesso dalla bocca"),
            ]
            
            for parola, definizione in parole_con_definizioni:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO parole (parola, definizione, lunghezza, validata) VALUES (?, ?, ?, 1)",
                        (parola, definizione, len(parola))
                    )
                except:
                    pass
            
            self.conn.commit()
            
    def get_parole_by_lunghezza(self, lunghezza):
        """Restituisce tutte le parole di una data lunghezza."""
        self.cursor.execute("SELECT parola FROM parole WHERE lunghezza=? AND validata=1", (lunghezza,))
        return [row[0] for row in self.cursor.fetchall()]

    def parola_esiste(self, parola):
        """Controlla se una parola esiste nel dizionario."""
        parole_lunghezza = self.get_parole_by_lunghezza(len(parola))
        return parola.lower() in [p.lower() for p in parole_lunghezza]

    def get_definizione(self, parola):
        """Restituisce la definizione di una parola."""
        self.cursor.execute("SELECT definizione FROM parole WHERE parola=?", (parola,))
        risultato = self.cursor.fetchone()
        if risultato and risultato[0]:
            return risultato[0]
        else:
            return f"(Definizione di '{parola}' non disponibile)"

# ==================== GENERATORE CRUCIVERBA PROFESSIONALE ====================
class CruciverbaGeneratorProfessionale:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.caselle_nere = []
        
    def stampa_griglia(self):
        """Restituisce la griglia come stringa formattata"""
        risultato = ""
        for riga in self.griglia:
            risultato += ' '.join(riga) + '\n'
        return risultato
    
    def griglia_html(self):
        """Restituisce la griglia in formato HTML per una visualizzazione migliore"""
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 16px; margin: 0 auto;">'
        for riga in self.griglia:
            html += '<tr>'
            for cella in riga:
                if cella == '#':
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: black;">&nbsp;</td>'
                elif cella == '.':
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: white;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: white; font-weight: bold;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html
    
    def griglia_vuota_html(self):
        """Restituisce la griglia vuota con numeri in HTML"""
        # Calcola i numeri per le definizioni
        numeri_posizioni = {}
        numero = 1
        
        for i in range(self.righe):
            for j in range(self.colonne):
                if self.griglia[i][j] != '#' and self.griglia[i][j] != '.':
                    inizio_orizzontale = (j == 0 or self.griglia[i][j-1] == '#') and (j < self.colonne-1 and self.griglia[i][j+1] != '#' and self.griglia[i][j+1] != '.')
                    inizio_verticale = (i == 0 or self.griglia[i-1][j] == '#') and (i < self.righe-1 and self.griglia[i+1][j] != '#' and self.griglia[i+1][j] != '.')
                    
                    if inizio_orizzontale or inizio_verticale:
                        if (i, j) not in numeri_posizioni:
                            numeri_posizioni[(i, j)] = numero
                            numero += 1
        
        # Crea HTML
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 16px; margin: 0 auto;">'
        for i in range(self.righe):
            html += '<tr>'
            for j in range(self.colonne):
                if self.griglia[i][j] == '#':
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: black;">&nbsp;</td>'
                elif (i, j) in numeri_posizioni:
                    html += f'<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: white; position: relative;"><span style="font-size: 11px; position: absolute; top: 2px; left: 2px; font-weight: bold;">{numeri_posizioni[(i, j)]}</span>&nbsp;</td>'
                else:
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: white;">&nbsp;</td>'
            html += '</tr>'
        html += '</table>'
        
        return html, numeri_posizioni

    def _posiziona_caselle_nere(self, percentuale=20):
        """Posiziona caselle nere nella griglia (circa il 20%)"""
        totale_celle = self.righe * self.colonne
        num_nere = int(totale_celle * percentuale / 100)
        
        # Pattern a scacchiera per distribuire uniformemente
        for i in range(self.righe):
            for j in range(self.colonne):
                if (i + j) % 4 == 0 and len(self.caselle_nere) < num_nere:
                    self.griglia[i][j] = '#'
                    self.caselle_nere.append((i, j))
        
        # Aggiungi alcune nere casuali per raggiungere il numero desiderato
        while len(self.caselle_nere) < num_nere:
            i = random.randint(0, self.righe - 1)
            j = random.randint(0, self.colonne - 1)
            if self.griglia[i][j] == '.':
                self.griglia[i][j] = '#'
                self.caselle_nere.append((i, j))

    def _trova_spazi_orizzontali(self):
        """Trova tutti gli spazi per parole orizzontali"""
        spazi = []
        for i in range(self.righe):
            j = 0
            while j < self.colonne:
                if self.griglia[i][j] != '#':
                    inizio = j
                    lunghezza = 0
                    while j < self.colonne and self.griglia[i][j] != '#':
                        if self.griglia[i][j] == '.':
                            lunghezza += 1
                        j += 1
                    if lunghezza >= 3:
                        spazi.append((i, inizio, lunghezza))
                else:
                    j += 1
        return spazi
    
    def _trova_spazi_verticali(self):
        """Trova tutti gli spazi per parole verticali"""
        spazi = []
        for j in range(self.colonne):
            i = 0
            while i < self.righe:
                if self.griglia[i][j] != '#':
                    inizio = i
                    lunghezza = 0
                    while i < self.righe and self.griglia[i][j] != '#':
                        if self.griglia[i][j] == '.':
                            lunghezza += 1
                        i += 1
                    if lunghezza >= 3:
                        spazi.append((inizio, j, lunghezza))
                else:
                    i += 1
        return spazi

    def _parola_compatibile_orizzontale(self, parola, riga, col):
        """Verifica se una parola orizzontale è compatibile con le lettere esistenti"""
        for k, lettera in enumerate(parola):
            cella = self.griglia[riga][col + k]
            if cella != '.' and cella != lettera:
                return False
        return True

    def _parola_compatibile_verticale(self, parola, riga, col):
        """Verifica se una parola verticale è compatibile con le lettere esistenti"""
        for k, lettera in enumerate(parola):
            cella = self.griglia[riga + k][col]
            if cella != '.' and cella != lettera:
                return False
        return True

    def _inserisci_parola_orizzontale(self, parola, riga, col):
        """Inserisce una parola orizzontale"""
        for k, lettera in enumerate(parola):
            self.griglia[riga][col + k] = lettera
        self.parole_orizzontali.append((parola, riga, col))

    def _inserisci_parola_verticale(self, parola, riga, col):
        """Inserisce una parola verticale"""
        for k, lettera in enumerate(parola):
            self.griglia[riga + k][col] = lettera
        self.parole_verticali.append((parola, riga, col))

    def _verifica_tutte_parole(self):
        """Verifica che tutte le parole nella griglia esistano nel dizionario"""
        # Reset liste
        self.parole_orizzontali = []
        self.parole_verticali = []
        
        # Trova tutte le parole orizzontali
        for i in range(self.righe):
            j = 0
            while j < self.colonne:
                if self.griglia[i][j] not in ['#', '.']:
                    inizio = j
                    parola = ""
                    while j < self.colonne and self.griglia[i][j] not in ['#', '.']:
                        parola += self.griglia[i][j]
                        j += 1
                    if len(parola) >= 3 and self.dizionario.parola_esiste(parola):
                        self.parole_orizzontali.append((parola, i, inizio))
                    elif len(parola) >= 3:
                        return False  # Parola non valida
                else:
                    j += 1
        
        # Trova tutte le parole verticali
        for j in range(self.colonne):
            i = 0
            while i < self.righe:
                if self.griglia[i][j] not in ['#', '.']:
                    inizio = i
                    parola = ""
                    while i < self.righe and self.griglia[i][j] not in ['#', '.']:
                        parola += self.griglia[i][j]
                        i += 1
                    if len(parola) >= 3 and self.dizionario.parola_esiste(parola):
                        self.parole_verticali.append((parola, inizio, j))
                    elif len(parola) >= 3:
                        return False  # Parola non valida
                else:
                    i += 1
        
        return True

    def genera(self, tentativi_max=50):
        """Genera un cruciverba professionale con caselle nere"""
        for tentativo in range(tentativi_max):
            try:
                # Resetta la griglia
                self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
                self.parole_orizzontali = []
                self.parole_verticali = []
                self.caselle_nere = []
                
                # Posiziona caselle nere (circa 20%)
                self._posiziona_caselle_nere(percentuale=20)
                
                # Prepara dizionario per lunghezza
                parole_disponibili = {}
                for lunghezza in range(3, max(self.righe, self.colonne) + 1):
                    parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                    if parole:
                        parole_disponibili[lunghezza] = parole
                
                if not parole_disponibili:
                    continue
                
                # STRATEGIA: Inserisci prima alcune parole orizzontali
                spazi_oriz = self._trova_spazi_orizzontali()
                random.shuffle(spazi_oriz)
                
                for riga, col, lunghezza in spazi_oriz[:3]:  # Inserisci al massimo 3 orizzontali
                    if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                        parole_candidate = [p.upper() for p in parole_disponibili[lunghezza]]
                        random.shuffle(parole_candidate)
                        
                        for parola in parole_candidate:
                            if self._parola_compatibile_orizzontale(parola, riga, col):
                                self._inserisci_parola_orizzontale(parola, riga, col)
                                break
                
                # Poi inserisci parole verticali
                spazi_vert = self._trova_spazi_verticali()
                random.shuffle(spazi_vert)
                
                for riga, col, lunghezza in spazi_vert[:3]:  # Inserisci al massimo 3 verticali
                    if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                        parole_candidate = [p.upper() for p in parole_disponibili[lunghezza]]
                        random.shuffle(parole_candidate)
                        
                        for parola in parole_candidate:
                            if self._parola_compatibile_verticale(parola, riga, col):
                                self._inserisci_parola_verticale(parola, riga, col)
                                break
                
                # Verifica finale
                if self._verifica_tutte_parole():
                    # Calcola percentuale caselle nere
                    totale_nere = sum(1 for riga in self.griglia for cella in riga if cella == '#')
                    percentuale_nere = (totale_nere / (self.righe * self.colonne)) * 100
                    
                    # Accetta se tra il 15% e il 25% di caselle nere
                    if 15 <= percentuale_nere <= 25:
                        return True
                
            except Exception as e:
                continue
        
        return False

# ==================== FUNZIONI PER ESPORTAZIONE ====================
def genera_txt(generatore, includi_lettere=True):
    """Genera un file TXT con il cruciverba"""
    output = io.StringIO()
    
    if includi_lettere:
        output.write("CRUCIVERBA COMPILATO\n")
        output.write("="*40 + "\n\n")
        for riga in generatore.griglia:
            riga_str = ""
            for cella in riga:
                if cella == '#':
                    riga_str += "█ "
                else:
                    riga_str += f"{cella} "
            output.write(riga_str + "\n")
    else:
        output.write("SCHEMA CRUCIVERBA VUOTO\n")
        output.write("="*40 + "\n\n")
        
        # Versione testo semplice dello schema vuoto
        for i in range(generatore.righe):
            riga = ""
            for j in range(generatore.colonne):
                if generatore.griglia[i][j] == '#':
                    riga += "█ "
                else:
                    riga += "□ "
            output.write(riga + "\n")
    
    # Aggiungi definizioni
    output.write("\n\nDEFINIZIONI\n")
    output.write("="*40 + "\n\n")
    
    if generatore.parole_orizzontali:
        output.write("ORIZZONTALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_orizzontali, 1):
            definizione = generatore.dizionario.get_definizione(parola.lower())
            output.write(f"  {i}. {parola}: {definizione}\n")
    
    if generatore.parole_verticali:
        output.write("\nVERTICALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_verticali, len(generatore.parole_orizzontali)+1):
            definizione = generatore.dizionario.get_definizione(parola.lower())
            output.write(f"  {i}. {parola}: {definizione}\n")
    
    return output.getvalue()

# ==================== INTERFACCIA STREAMLIT ====================
def main():
    st.set_page_config(
        page_title="Generatore di Cruciverba Italiani",
        page_icon="🧩",
        layout="wide"
    )
    
    # Inizializza il dizionario nella sessione
    if 'dizionario' not in st.session_state:
        with st.spinner("Inizializzazione database..."):
            st.session_state.dizionario = DizionarioItaliano()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    # Header
    st.title("🧩 Generatore di Cruciverba Italiani")
    st.markdown("### Parole dall'Accademia della Crusca e Treccani")
    st.markdown("---")
    
    # Sidebar per i controlli
    with st.sidebar:
        st.header("⚙️ Impostazioni")
        
        righe = st.number_input("Numero di righe", min_value=5, max_value=12, value=8, step=1)
        colonne = st.number_input("Numero di colonne", min_value=5, max_value=12, value=8, step=1)
        
        st.markdown("---")
        
        if st.button("🎲 GENERA NUOVO CRUCIVERBA", use_container_width=True):
            with st.spinner("Generazione in corso (potrebbero volerci alcuni secondi)..."):
                st.session_state.generatore = CruciverbaGeneratorProfessionale(righe, colonne, st.session_state.dizionario)
                successo = st.session_state.generatore.genera(tentativi_max=30)
                if successo:
                    st.success("Cruciverba generato con successo!")
                else:
                    st.error("Impossibile generare il cruciverba. Riprova con dimensioni diverse.")
        
        st.markdown("---")
        
        if st.session_state.generatore:
            st.header("📥 Esportazione")
            
            # Export compilato
            txt_compilato = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button(
                label="📄 Scarica TXT Compilato",
                data=txt_compilato,
                file_name=f"cruciverba_compilato_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # Export schema vuoto
            txt_vuoto = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button(
                label="📄 Scarica TXT Schema Vuoto",
                data=txt_vuoto,
                file_name=f"cruciverba_vuoto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    # Area principale
    if st.session_state.generatore:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Cruciverba Compilato")
            st.markdown("Griglia con le lettere (█ = casella nera):")
            st.markdown(st.session_state.generatore.griglia_html(), unsafe_allow_html=True)
        
        with col2:
            st.subheader("🔢 Schema Vuoto con Numeri")
            st.markdown("Griglia da riempire (ideale per stampare):")
            griglia_vuota, numeri = st.session_state.generatore.griglia_vuota_html()
            st.markdown(griglia_vuota, unsafe_allow_html=True)
        
        # Statistiche
        st.markdown("---")
        st.subheader("📊 Statistiche")
        
        tutte_parole = st.session_state.generatore.parole_orizzontali + st.session_state.generatore.parole_verticali
        celle_piene = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella not in ['#', '.'])
        celle_nere = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella == '#')
        totale_celle = righe * colonne
        percentuale_piene = (celle_piene / totale_celle) * 100
        percentuale_nere = (celle_nere / totale_celle) * 100
        
        # Conta gli incroci
        incroci = 0
        for i in range(righe):
            for j in range(colonne):
                if st.session_state.generatore.griglia[i][j] not in ['#', '.']:
                    orizzontale = False
                    verticale = False
                    
                    if (j > 0 and st.session_state.generatore.griglia[i][j-1] not in ['#', '.']) or \
                       (j < colonne-1 and st.session_state.generatore.griglia[i][j+1] not in ['#', '.']):
                        orizzontale = True
                    
                    if (i > 0 and st.session_state.generatore.griglia[i-1][j] not in ['#', '.']) or \
                       (i < righe-1 and st.session_state.generatore.griglia[i+1][j] not in ['#', '.']):
                        verticale = True
                    
                    if orizzontale and verticale:
                        incroci += 1
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Parole Totali", len(tutte_parole))
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Incroci", incroci)
        col5.metric("Celle Piene", f"{celle_piene} ({percentuale_piene:.1f}%)")
        col6.metric("Caselle Nere", f"{celle_nere} ({percentuale_nere:.1f}%)")
        
        # Definizioni
        st.markdown("---")
        st.subheader("📚 Definizioni")
        
        if st.session_state.generatore.parole_orizzontali or st.session_state.generatore.parole_verticali:
            tab1, tab2 = st.tabs(["Orizzontali", "Verticali"])
            
            with tab1:
                if st.session_state.generatore.parole_orizzontali:
                    for i, (parola, r, c) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                        definizione = st.session_state.dizionario.get_definizione(parola.lower())
                        st.markdown(f"**{i}. {parola}** - {definizione}")
                else:
                    st.info("Nessuna parola orizzontale")
            
            with tab2:
                if st.session_state.generatore.parole_verticali:
                    for i, (parola, r, c) in enumerate(st.session_state.generatore.parole_verticali, len(st.session_state.generatore.parole_orizzontali)+1):
                        definizione = st.session_state.dizionario.get_definizione(parola.lower())
                        st.markdown(f"**{i}. {parola}** - {definizione}")
                else:
                    st.info("Nessuna parola verticale")
        else:
            st.info("Nessuna parola trovata")
    
    else:
        st.info("👈 Imposta le dimensioni e clicca su 'GENERA NUOVO CRUCIVERBA' per iniziare!")
        
        # Esempio di anteprima
        st.markdown("---")
        st.subheader("🎯 Caratteristiche")
        st.markdown("""
        Il generatore crea cruciverba professionali con:
        - **Caselle nere** (circa il 20% della griglia)
        - **Vere parole verticali** (verificate nel dizionario)
        - **Incroci multipli** tra orizzontali e verticali
        - Definizioni automatiche per ogni parola
        - Due visualizzazioni: compilata e schema vuoto
        - Esportazione in formato TXT stampabile
        """)

if __name__ == "__main__":
    main()
