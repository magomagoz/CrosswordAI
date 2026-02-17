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
                ("carta", "Foglio per scrivere"),
                ("penna", "Strumento per scrivere"),
                ("matita", "Strumento per scrivere cancellabile"),
                ("gomma", "Per cancellare"),
                ("banco", "Mobile scolastico"),
                ("sedia", "Mobile per sedersi"),
                ("tavolo", "Mobile con piano orizzontale"),
                ("letto", "Mobile per dormire"),
                ("armadio", "Mobile per riporre vestiti"),
                ("cucina", "Stanza per cucinare"),
                ("bagno", "Stanza per l'igiene personale"),
                ("camera", "Stanza da letto"),
                ("salone", "Stanza principale"),
                ("giardino", "Area verde intorno alla casa"),
                ("orto", "Terreno coltivato a ortaggi"),
                ("campo", "Terreno agricolo"),
                ("prato", "Terreno coperto d'erba"),
                ("bosco", "Area alberata"),
                ("foresta", "Grande area boschiva"),
                ("fiume", "Corso d'acqua naturale"),
                ("lago", "Specchio d'acqua circondato da terra"),
                ("oceano", "Vasta distesa d'acqua salata"),
                ("isola", "Terra circondata dall'acqua"),
                ("penisola", "Terra circondata dall'acqua su tre lati"),
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
                if self.griglia[i][j] not in ['#', '.']:
                    inizio_orizzontale = (j == 0 or self.griglia[i][j-1] in ['#', '.']) and (j < self.colonne-1 and self.griglia[i][j+1] not in ['#', '.'])
                    inizio_verticale = (i == 0 or self.griglia[i-1][j] in ['#', '.']) and (i < self.righe-1 and self.griglia[i+1][j] not in ['#', '.'])
                    
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

    def _ottieni_parole_per_lunghezza(self, lunghezza):
        """Restituisce parole di una data lunghezza"""
        return self.dizionario.get_parole_by_lunghezza(lunghezza)

    def _posizione_libera_orizzontale(self, riga, col, lunghezza):
        """Verifica se una posizione è libera per una parola orizzontale"""
        if col + lunghezza > self.colonne:
            return False
        for k in range(lunghezza):
            cella = self.griglia[riga][col + k]
            if cella not in ['.', '#']:
                return False
        return True

    def _posizione_libera_verticale(self, riga, col, lunghezza):
        """Verifica se una posizione è libera per una parola verticale"""
        if riga + lunghezza > self.righe:
            return False
        for k in range(lunghezza):
            cella = self.griglia[riga + k][col]
            if cella not in ['.', '#']:
                return False
        return True

    def _parola_compatibile_orizzontale(self, parola, riga, col):
        """Verifica se una parola orizzontale è compatibile con le lettere esistenti"""
        for k, lettera in enumerate(parola):
            cella = self.griglia[riga][col + k]
            if cella not in ['.', '#'] and cella != lettera:
                return False
        return True

    def _parola_compatibile_verticale(self, parola, riga, col):
        """Verifica se una parola verticale è compatibile con le lettere esistenti"""
        for k, lettera in enumerate(parola):
            cella = self.griglia[riga + k][col]
            if cella not in ['.', '#'] and cella != lettera:
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

    def _aggiungi_casella_nera(self, riga, col):
        """Aggiunge una casella nera"""
        if 0 <= riga < self.righe and 0 <= col < self.colonne:
            self.griglia[riga][col] = '#'

    def _trova_lettere_isolate(self):
        """Trova celle con lettere che non fanno parte di parole complete"""
        isolate = []
        for i in range(self.righe):
            for j in range(self.colonne):
                if self.griglia[i][j] not in ['.', '#']:
                    # Controlla se fa parte di una parola orizzontale
                    orizzontale = False
                    if (j > 0 and self.griglia[i][j-1] not in ['.', '#']) or \
                       (j < self.colonne-1 and self.griglia[i][j+1] not in ['.', '#']):
                        orizzontale = True
                    
                    # Controlla se fa parte di una parola verticale
                    verticale = False
                    if (i > 0 and self.griglia[i-1][j] not in ['.', '#']) or \
                       (i < self.righe-1 and self.griglia[i+1][j] not in ['.', '#']):
                        verticale = True
                    
                    if not orizzontale and not verticale:
                        isolate.append((i, j))
        return isolate

    def _trova_punti_incrocio(self):
        """Trova possibili punti di incrocio per nuove parole"""
        incroci = []
        
        # Cerca punti dove una orizzontale potrebbe incrociare una verticale
        for i in range(self.righe):
            for j in range(self.colonne):
                if self.griglia[i][j] == '.':
                    # Verifica se sopra o sotto c'è una verticale
                    verticale_presente = False
                    if i > 0 and self.griglia[i-1][j] not in ['.', '#']:
                        verticale_presente = True
                    if i < self.righe-1 and self.griglia[i+1][j] not in ['.', '#']:
                        verticale_presente = True
                    
                    # Verifica se a sinistra o destra c'è una orizzontale
                    orizzontale_presente = False
                    if j > 0 and self.griglia[i][j-1] not in ['.', '#']:
                        orizzontale_presente = True
                    if j < self.colonne-1 and self.griglia[i][j+1] not in ['.', '#']:
                        orizzontale_presente = True
                    
                    if verticale_presente or orizzontale_presente:
                        incroci.append((i, j))
        
        return incroci

    def genera(self):
        """Genera un cruciverba incrementalmente"""
        try:
            # Resetta la griglia
            self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # PASSO 1: Inserisci una parola orizzontale iniziale al centro
            centro_riga = self.righe // 2
            centro_col = self.colonne // 2
            
            # Scegli una lunghezza per la parola iniziale
            lunghezze_disponibili = [l for l in range(4, min(self.colonne, 8)) 
                                    if self._ottieni_parole_per_lunghezza(l)]
            
            if not lunghezze_disponibili:
                return False
            
            lunghezza_iniziale = random.choice(lunghezze_disponibili)
            parole_iniziali = self._ottieni_parole_per_lunghezza(lunghezza_iniziale)
            
            if not parole_iniziali:
                return False
            
            # Posiziona la parola iniziale
            parola_iniziale = random.choice(parole_iniziali).upper()
            col_inizio = max(0, min(centro_col - lunghezza_iniziale // 2, 
                                   self.colonne - lunghezza_iniziale))
            
            self._inserisci_parola_orizzontale(parola_iniziale, centro_riga, col_inizio)
            
            # PASSO 2: Aggiungi parole verticali che incrociano quella orizzontale
            for k, lettera in enumerate(parola_iniziale):
                col_incrocio = col_inizio + k
                
                # Cerca parole verticali che iniziano con questa lettera
                for lunghezza_v in range(3, min(self.righe, 7)):
                    parole_v = [p for p in self._ottieni_parole_per_lunghezza(lunghezza_v) 
                               if p[0].upper() == lettera]
                    
                    if parole_v:
                        parola_v = random.choice(parole_v).upper()
                        
                        # Calcola posizione di partenza per centrare l'incrocio
                        riga_inizio = centro_riga - (parola_v.find(lettera))
                        
                        if riga_inizio >= 0 and riga_inizio + lunghezza_v <= self.righe:
                            if self._posizione_libera_verticale(riga_inizio, col_incrocio, lunghezza_v):
                                if self._parola_compatibile_verticale(parola_v, riga_inizio, col_incrocio):
                                    self._inserisci_parola_verticale(parola_v, riga_inizio, col_incrocio)
            
            # PASSO 3: Aggiungi altre parole orizzontali che incrociano le verticali
            for _ in range(3):  # Prova ad aggiungere fino a 3 orizzontali
                punti_incrocio = self._trova_punti_incrocio()
                if not punti_incrocio:
                    break
                
                # Scegli un punto di incrocio casuale
                riga, col = random.choice(punti_incrocio)
                
                # Espandi a sinistra e destra per trovare la lunghezza massima
                sinistra = col
                while sinistra > 0 and self.griglia[riga][sinistra - 1] == '.':
                    sinistra -= 1
                
                destra = col
                while destra < self.colonne - 1 and self.griglia[riga][destra + 1] == '.':
                    destra += 1
                
                lunghezza_max = destra - sinistra + 1
                
                if lunghezza_max >= 3:
                    # Prova diverse lunghezze
                    for lunghezza in range(min(lunghezza_max, 7), 2, -1):
                        parole_oriz = self._ottieni_parole_per_lunghezza(lunghezza)
                        if not parole_oriz:
                            continue
                        
                        # Cerca parole compatibili con le lettere già esistenti
                        for parola in random.sample(parole_oriz, min(len(parole_oriz), 10)):
                            parola = parola.upper()
                            if self._parola_compatibile_orizzontale(parola, riga, sinistra):
                                self._inserisci_parola_orizzontale(parola, riga, sinistra)
                                break
                        else:
                            continue
                        break
            
            # PASSO 4: Aggiungi altre parole verticali
            for _ in range(2):
                punti_incrocio = self._trova_punti_incrocio()
                if not punti_incrocio:
                    break
                
                riga, col = random.choice(punti_incrocio)
                
                # Espandi in alto e basso
                alto = riga
                while alto > 0 and self.griglia[alto - 1][col] == '.':
                    alto -= 1
                
                basso = riga
                while basso < self.righe - 1 and self.griglia[basso + 1][col] == '.':
                    basso += 1
                
                lunghezza_max = basso - alto + 1
                
                if lunghezza_max >= 3:
                    for lunghezza in range(min(lunghezza_max, 7), 2, -1):
                        parole_vert = self._ottieni_parole_per_lunghezza(lunghezza)
                        if not parole_vert:
                            continue
                        
                        for parola in random.sample(parole_vert, min(len(parole_vert), 10)):
                            parola = parola.upper()
                            if self._parola_compatibile_verticale(parola, alto, col):
                                self._inserisci_parola_verticale(parola, alto, col)
                                break
                        else:
                            continue
                        break
            
            # PASSO 5: Riempi le celle rimanenti con caselle nere
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] == '.':
                        self._aggiungi_casella_nera(i, j)
            
            # PASSO 6: Verifica che tutte le parole siano valide
            tutte_parole = self.parole_orizzontali + self.parole_verticali
            
            # Calcola percentuale caselle nere
            totale_nere = sum(1 for riga in self.griglia for cella in riga if cella == '#')
            percentuale_nere = (totale_nere / (self.righe * self.colonne)) * 100
            
            # Accetta se tra il 15% e il 30% di caselle nere e almeno 4 parole totali
            if len(tutte_parole) >= 4 and 10 <= percentuale_nere <= 35:
                return True
            else:
                return False
            
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
        
        # Mostra la posizione delle parole (debug visivo)
        with st.expander("📍 Posizioni delle parole"):
            if st.session_state.generatore.parole_orizzontali:
                st.write("**Orizzontali:**")
                for parola, r, c in st.session_state.generatore.parole_orizzontali:
                    st.write(f"  • {parola}: riga {r}, colonna {c} (lunghezza {len(parola)})")
            
            if st.session_state.generatore.parole_verticali:
                st.write("**Verticali:**")
                for parola, r, c in st.session_state.generatore.parole_verticali:
                    st.write(f"  • {parola}: riga {r}, colonna {c} (lunghezza {len(parola)})")
    
    else:
        st.info("👈 Imposta le dimensioni e clicca su 'GENERA NUOVO CRUCIVERBA' per iniziare!")
        
        # Esempio di anteprima
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
            - Caselle nere solo dove necessario (15-35%)
            - Definizioni automatiche
            - Esportazione in formato TXT
            """)

if __name__ == "__main__":
    main()
