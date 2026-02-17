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
                ("qua", "Avverbio di luogo"),
                ("la", "Nota musicale"),
                ("ra", "Divinità egizia del sole"),
                
                # 4+ lettere
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
                ("mamma", "Madre, genitrice"),
                ("papà", "Padre, genitore"),
                ("nonno", "Padre del padre o della madre"),
                ("nonna", "Madre del padre o della madre"),
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
                ("corsa", "Movimento veloce"),
                ("salto", "Movimento per staccarsi da terra"),
                ("volo", "Spostamento nell'aria"),
                ("canto", "Emissione di suoni melodici"),
                ("suono", "Vibrazione percepita dall'orecchio"),
                ("voce", "Suono emesso dalla bocca"),
                ("carta", "Foglio per scrivere"),
                ("penna", "Strumento per scrivere"),
                ("banco", "Mobile scolastico"),
                ("sedia", "Mobile per sedersi"),
                ("tavolo", "Mobile con piano orizzontale"),
                ("letto", "Mobile per dormire"),
                ("cucina", "Stanza per cucinare"),
                ("bagno", "Stanza per l'igiene personale"),
                ("camera", "Stanza da letto"),
                ("giardino", "Area verde intorno alla casa"),
                ("orto", "Terreno coltivato a ortaggi"),
                ("campo", "Terreno agricolo"),
                ("prato", "Terreno coperto d'erba"),
                ("bosco", "Area alberata"),
                ("fiume", "Corso d'acqua naturale"),
                ("lago", "Specchio d'acqua circondato da terra"),
                ("isola", "Terra circondata dall'acqua"),
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

# ==================== GENERATORE CRUCIVERBA INCREMENTALE ====================
class CruciverbaGeneratorIncrementale:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
    def stampa_griglia(self):
        """Restituisce la griglia come stringa formattata"""
        risultato = ""
        for riga in self.griglia:
            riga_str = ""
            for cella in riga:
                if cella == '#':
                    riga_str += "█ "
                elif cella == '.':
                    riga_str += ". "
                else:
                    riga_str += f"{cella} "
            risultato += riga_str + "\n"
        return risultato
    
    def griglia_html(self):
        """Restituisce la griglia in formato HTML"""
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
        numeri_posizioni = {}
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

    def _ottieni_parole_per_lunghezza(self, lunghezza):
        """Restituisce parole di una data lunghezza"""
        return self.dizionario.get_parole_by_lunghezza(lunghezza)

    def _verifica_confini_orizzontali(self, riga, col, lunghezza):
        """Verifica che ai lati della parola ci siano bordi o caselle nere"""
        if col > 0 and self.griglia[riga][col - 1] not in ['#', '.']:
            return False
        if col + lunghezza < self.colonne and self.griglia[riga][col + lunghezza] not in ['#', '.']:
            return False
        return True
    
    def _verifica_confini_verticali(self, riga, col, lunghezza):
        """Verifica che sopra e sotto la parola ci siano bordi o caselle nere"""
        if riga > 0 and self.griglia[riga - 1][col] not in ['#', '.']:
            return False
        if riga + lunghezza < self.righe and self.griglia[riga + lunghezza][col] not in ['#', '.']:
            return False
        return True
    
    def _inserisci_parola_orizzontale(self, parola, riga, col):
        """Inserisce una parola orizzontale con caselle nere ai lati"""
        for k, lettera in enumerate(parola):
            self.griglia[riga][col + k] = lettera
        
        if col > 0 and self.griglia[riga][col - 1] == '.':
            self.griglia[riga][col - 1] = '#'
        
        if col + len(parola) < self.colonne and self.griglia[riga][col + len(parola)] == '.':
            self.griglia[riga][col + len(parola)] = '#'
        
        self.parole_orizzontali.append((parola, riga, col))
    
    def _inserisci_parola_verticale(self, parola, riga, col):
        """Inserisce una parola verticale con caselle nere sopra e sotto"""
        for k, lettera in enumerate(parola):
            self.griglia[riga + k][col] = lettera
        
        if riga > 0 and self.griglia[riga - 1][col] == '.':
            self.griglia[riga - 1][col] = '#'
        
        if riga + len(parola) < self.righe and self.griglia[riga + len(parola)][col] == '.':
            self.griglia[riga + len(parola)][col] = '#'
        
        self.parole_verticali.append((parola, riga, col))

    def genera(self):
        """Genera un cruciverba incrementalmente con caselle nere ai bordi"""
        try:
            # Resetta la griglia
            self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # PASSO 1: Inserisci una parola orizzontale iniziale al centro
            centro_riga = self.righe // 2
            centro_col = self.colonne // 2
            
            lunghezze_disponibili = [l for l in range(4, min(self.colonne, 8)) 
                                    if self._ottieni_parole_per_lunghezza(l)]
            
            if not lunghezze_disponibili:
                return False
            
            lunghezza_iniziale = random.choice(lunghezze_disponibili)
            parole_iniziali = self._ottieni_parole_per_lunghezza(lunghezza_iniziale)
            
            if not parole_iniziali:
                return False
            
            parola_iniziale = random.choice(parole_iniziali).upper()
            col_inizio = max(0, min(centro_col - lunghezza_iniziale // 2, 
                                   self.colonne - lunghezza_iniziale))
            
            self._inserisci_parola_orizzontale(parola_iniziale, centro_riga, col_inizio)
            
            # PASSO 2: Aggiungi parole verticali che incrociano quella orizzontale
            for k, lettera in enumerate(parola_iniziale):
                col_incrocio = col_inizio + k
                
                for lunghezza_v in range(3, min(self.righe, 7)):
                    parole_v = self._ottieni_parole_per_lunghezza(lunghezza_v)
                    
                    parole_candidate = []
                    for p in parole_v:
                        p_upper = p.upper()
                        for pos, lett in enumerate(p_upper):
                            if lett == lettera:
                                parole_candidate.append((p_upper, pos))
                    
                    if parole_candidate:
                        parola_v, pos_lettera = random.choice(parole_candidate)
                        riga_inizio = centro_riga - pos_lettera
                        
                        if riga_inizio >= 0 and riga_inizio + lunghezza_v <= self.righe:
                            libero = True
                            for idx in range(lunghezza_v):
                                cella = self.griglia[riga_inizio + idx][col_incrocio]
                                if cella != '.' and cella != parola_v[idx]:
                                    libero = False
                                    break
                            
                            if libero and self._verifica_confini_verticali(riga_inizio, col_incrocio, lunghezza_v):
                                self._inserisci_parola_verticale(parola_v, riga_inizio, col_incrocio)
            
            # PASSO 3: Aggiungi altre parole orizzontali
            for _ in range(3):
                punti_incrocio = []
                for i in range(self.righe):
                    for j in range(self.colonne):
                        if self.griglia[i][j] not in ['.', '#']:
                            sinistra = j
                            while sinistra > 0 and self.griglia[i][sinistra - 1] == '.':
                                sinistra -= 1
                            
                            destra = j
                            while destra < self.colonne - 1 and self.griglia[i][destra + 1] == '.':
                                destra += 1
                            
                            if destra - sinistra + 1 >= 3:
                                punti_incrocio.append((i, sinistra, destra - sinistra + 1))
                
                if not punti_incrocio:
                    break
                
                riga, col_inizio, lunghezza_max = random.choice(punti_incrocio)
                
                for lunghezza in range(min(lunghezza_max, 7), 2, -1):
                    parole_oriz = self._ottieni_parole_per_lunghezza(lunghezza)
                    if not parole_oriz:
                        continue
                    
                    pattern = []
                    for k in range(lunghezza):
                        cella = self.griglia[riga][col_inizio + k]
                        if cella not in ['.', '#']:
                            pattern.append((k, cella))
                    
                    parole_candidate = []
                    for p in parole_oriz:
                        p_upper = p.upper()
                        compatibile = True
                        for pos, lettera in pattern:
                            if p_upper[pos] != lettera:
                                compatibile = False
                                break
                        if compatibile:
                            parole_candidate.append(p_upper)
                    
                    if parole_candidate and self._verifica_confini_orizzontali(riga, col_inizio, lunghezza):
                        parola_scelta = random.choice(parole_candidate)
                        self._inserisci_parola_orizzontale(parola_scelta, riga, col_inizio)
                        break
            
            # PASSO 4: Riempi le celle rimanenti con caselle nere
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] == '.':
                        self.griglia[i][j] = '#'
            
            # PASSO 5: Raccogli tutte le parole valide
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
                        if len(parola) >= 3 and self.dizionario.parola_esiste(parola):
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
                        if len(parola) >= 3 and self.dizionario.parola_esiste(parola):
                            self.parole_verticali.append((parola, inizio, j))
                    else:
                        i += 1
            
            tutte_parole = self.parole_orizzontali + self.parole_verticali
            return len(tutte_parole) >= 4
            
        except Exception as e:
            st.error(f"Errore nella generazione: {e}")
            return False

# ==================== FUNZIONI PER ESPORTAZIONE ====================
def genera_txt(generatore, includi_lettere=True):
    """Genera un file TXT con il cruciverba"""
    output = io.StringIO()
    
    if includi_lettere:
        output.write("CRUCIVERBA COMPILATO\n")
        output.write("="*40 + "\n\n")
        output.write(generatore.stampa_griglia())
    else:
        output.write("SCHEMA CRUCIVERBA VUOTO\n")
        output.write("="*40 + "\n\n")
        
        for i in range(generatore.righe):
            riga = ""
            for j in range(generatore.colonne):
                if generatore.griglia[i][j] == '#':
                    riga += "█ "
                else:
                    riga += "□ "
            output.write(riga + "\n")
    
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
    
    if 'dizionario' not in st.session_state:
        with st.spinner("Inizializzazione database..."):
            st.session_state.dizionario = DizionarioItaliano()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Generatore di Cruciverba Italiani")
    st.markdown("### Parole dall'Accademia della Crusca e Treccani")
    st.markdown("---")
    
    with st.sidebar:
        st.header("⚙️ Impostazioni")
        
        righe = st.number_input("Numero di righe", min_value=5, max_value=12, value=8, step=1)
        colonne = st.number_input("Numero di colonne", min_value=5, max_value=12, value=8, step=1)
        
        st.markdown("---")
        
        if st.button("🎲 GENERA NUOVO CRUCIVERBA", use_container_width=True):
            with st.spinner("Costruzione incrementale del cruciverba..."):
                st.session_state.generatore = CruciverbaGeneratorIncrementale(righe, colonne, st.session_state.dizionario)
                successo = st.session_state.generatore.genera()
                if successo:
                    st.success("Cruciverba generato con successo!")
                else:
                    st.error("Impossibile generare il cruciverba. Riprova con dimensioni diverse.")
        
        st.markdown("---")
        
        if st.session_state.generatore:
            st.header("📥 Esportazione")
            
            txt_compilato = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button(
                label="📄 Scarica TXT Compilato",
                data=txt_compilato,
                file_name=f"cruciverba_compilato_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            txt_vuoto = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button(
                label="📄 Scarica TXT Schema Vuoto",
                data=txt_vuoto,
                file_name=f"cruciverba_vuoto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
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
        
        st.markdown("---")
        st.subheader("📊 Statistiche")
        
        tutte_parole = st.session_state.generatore.parole_orizzontali + st.session_state.generatore.parole_verticali
        celle_piene = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella not in ['#', '.'])
        celle_nere = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella == '#')
        totale_celle = righe * colonne
        percentuale_piene = (celle_piene / totale_celle) * 100
        percentuale_nere = (celle_nere / totale_celle) * 100
        
        incroci = 0
        for i in range(righe):
            for j in range(colonne):
                if st.session_state.generatore.griglia[i][j] not in ['#', '.']:
                    orizzontale = (j > 0 and st.session_state.generatore.griglia[i][j-1] not in ['#', '.']) or \
                                 (j < colonne-1 and st.session_state.generatore.griglia[i][j+1] not in ['#', '.'])
                    verticale = (i > 0 and st.session_state.generatore.griglia[i-1][j] not in ['#', '.']) or \
                               (i < righe-1 and st.session_state.generatore.griglia[i+1][j] not in ['#', '.'])
                    if orizzontale and verticale:
                        incroci += 1
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Parole Totali", len(tutte_parole))
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Incroci", incroci)
        col5.metric("Celle Piene", f"{celle_piene} ({percentuale_piene:.1f}%)")
        col6.metric("Caselle Nere", f"{celle_nere} ({percentuale_nere:.1f}%)")
        
        st.markdown("---")
        st.subheader("📚 Definizioni")
        
        if st.session_state.generatore.parole_orizzontali or st.session_state.generatore.parole_verticali:
            tab1, tab2 = st.tabs(["Orizzontali", "Verticali"])
            
            with tab1:
                if st.session_state.generatore.parole_orizzontali:
                    for i, (parola, r, c) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                        definizione = st.session_state.dizionario.get_definizione(parola.lower())
                        st.markdown(f"**{i}. {parola}** - {definizione}")
            
            with tab2:
                if st.session_state.generatore.parole_verticali:
                    for i, (parola, r, c) in enumerate(st.session_state.generatore.parole_verticali, len(st.session_state.generatore.parole_orizzontali)+1):
                        definizione = st.session_state.dizionario.get_definizione(parola.lower())
                        st.markdown(f"**{i}. {parola}** - {definizione}")
    
    else:
        st.info("👈 Imposta le dimensioni e clicca su 'GENERA NUOVO CRUCIVERBA' per iniziare!")
        
        st.markdown("---")
        st.subheader("🎯 Come funziona")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Algoritmo incrementale:**
            1. Parte da una **parola orizzontale** centrale
            2. Aggiunge **parole verticali** che la incrociano
            3. Aggiunge altre **parole orizzontali** che incrociano le verticali
            4. Le celle vuote diventano **caselle nere**
            """)
        
        with col2:
            st.markdown("""
            **Caratteristiche:**
            - Parole verificate nel dizionario italiano
            - Incroci reali tra orizzontali e verticali
            - Caselle nere solo dove necessario
            - Definizioni automatiche
            - Esportazione in formato TXT
            """)

if __name__ == "__main__":
    main()
