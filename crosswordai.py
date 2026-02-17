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
            # Parole di 3 lettere
            parole_3 = [
                ("re", "Sovrano di uno stato"),
                ("tre", "Numero successivo al due"),
                ("sei", "Numero successivo al cinque"),
                ("casa", "Edificio adibito ad abitazione familiare"),
                ("cane", "Animale domestico a quattro zampe, fedele all'uomo"),
                ("gatto", "Felino domestico, abile cacciatore di topi"),
                ("libro", "Insieme di fogli stampati e rilegati formanti un volume"),
                ("sole", "Stella centrale del sistema solare, fonte di luce e calore"),
                ("luna", "Satellite naturale della Terra, visibile nel cielo notturno"),
                ("mare", "Grande distesa d'acqua salata che ricopre gran parte della Terra"),
                ("monte", "Rilievo naturale della superficie terrestre elevato oltre i 600-700 metri"),
                ("fiore", "Parte della pianta che contiene gli organi della riproduzione"),
                ("albero", "Pianta perenne con fusto legnoso e chioma di rami e foglie"),
                ("auto", "Veicolo a motore per il trasporto su strada"),
                ("treno", "Mezzo di trasporto su rotaie, composto da locomotive e vagoni"),
                ("pane", "Alimento ottenuto dalla cottura di pasta lievitata di farina e acqua"),
                ("vino", "Bevanda alcolica ottenuta dalla fermentazione dell'uva"),
                ("acqua", "Liquido trasparente, incolore, inodore e insapore, essenziale per la vita"),
                ("fuoco", "Fiamma che produce calore e luce, generata dalla combustione"),
                ("terra", "Pianeta su cui viviamo, terzo in ordine di distanza dal Sole"),
                ("aria", "Miscuglio di gas che costituisce l'atmosfera terrestre"),
                ("amico", "Persona legata a un'altra da affetto reciproco e stima"),
                ("scuola", "Istituto dove si impartisce l'istruzione e l'educazione"),
                ("amore", "Sentimento di profondo affetto, attrazione e dedizione verso qualcuno"),
                ("tempo", "Durata delle cose soggette a mutamento, successione di istanti"),
                ("vita", "Condizione degli esseri organizzati, che nascono, crescono e si riproducono"),
                ("morte", "Cessazione irreversibile delle funzioni vitali di un organismo"),
                ("notte", "Periodo di oscurità compreso tra il tramonto e l'alba"),
                ("giorno", "Periodo di luce compreso tra l'alba e il tramonto"),
                ("estate", "Stagione più calda dell'anno, compresa tra la primavera e l'autunno"),
                ("inverno", "Stagione più fredda dell'anno, compresa tra l'autunno e la primavera"),
                ("primavera", "Stagione che segue l'inverno e precede l'estate"),
                ("autunno", "Stagione che segue l'estate e precede l'inverno"),
                ("ciao", "Saluto informale, usato sia per incontri che per congedi"),
                ("grazie", "Espressione di ringraziamento e riconoscenza"),
                ("prego", "Formula di cortesia in risposta a grazie o per invitare a fare qualcosa"),
                ("buongiorno", "Saluto che si usa al mattino o nelle prime ore del pomeriggio"),
                ("buonasera", "Saluto che si usa dalla sera fino a notte inoltrata"),
                ("arrivederci", "Saluto formale di commiato, con l'aspettativa di rivedersi"),
                ("italia", "Stato dell'Europa meridionale, con forma di stivale"),
                ("roma", "Capitale d'Italia, città ricca di storia e monumenti antichi"),
                ("milano", "Città italiana, capoluogo della Lombardia, centro finanziario e della moda"),
                ("napoli", "Città italiana, capoluogo della Campania, famosa per il golfo e la pizza"),
                ("torino", "Città italiana, capoluogo del Piemonte, prima capitale d'Italia"),
                ("firenze", "Città italiana, capoluogo della Toscana, culla del Rinascimento"),
                ("venezia", "Città italiana costruita su palafitte, famosa per i canali e il Carnevale"),
                ("bologna", "Città universitaria, capoluogo dell'Emilia-Romagna"),
                ("genova", "Importante città portuale della Liguria"),
                ("palermo", "Capoluogo della Sicilia"),
                ("catania", "Città siciliana ai piedi dell'Etna"),
                ("napoli", "Città partenopea famosa per il golfo"),
                ("calcio", "Sport praticato con un pallone"),
                ("tennis", "Sport che si gioca con racchetta e pallina"),
                ("pizza", "Tipico piatto italiano"),
                ("pasta", "Alimento base della cucina italiana"),
                ("caffè", "Bevanda nera e amara"),
                ("cioccolato", "Dolce derivato dal cacao"),
                ("gelato", "Dolce freddo tipico italiano"),
                ("musica", "Arte dei suoni"),
                ("pittura", "Arte di dipingere"),
                ("danza", "Arte del movimento"),
                ("teatro", "Luogo di rappresentazioni artistiche"),
                ("cinema", "Arte delle immagini in movimento"),
                ("fotografia", "Arte di catturare immagini"),
                ("computer", "Macchina elettronica per elaborare dati"),
                ("telefono", "Dispositivo per comunicare a distanza"),
                ("internet", "Rete globale di computer"),
                ("sito", "Luogo o pagina web"),
                ("posta", "Servizio di invio corrispondenza"),
                ("lettera", "Messaggio scritto su carta"),
                ("giornale", "Pubblicazione quotidiana di notizie"),
                ("rivista", "Pubblicazione periodica"),
            ]
            
            for parola, definizione in parole_3:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO parole (parola, definizione, lunghezza, validata) VALUES (?, ?, ?, 1)",
                        (parola, definizione, len(parola))
                    )
                except:
                    pass
            
            altre_parole = ["mamma", "papà", "fratello", "sorella", "nonno", "nonna", 
                           "zio", "zia", "cugino", "cugina", "nipote", "marito", "moglie",
                           "rosso", "blu", "verde", "giallo", "bianco", "nero", "marrone",
                           "grande", "piccolo", "alto", "basso", "lungo", "corto", "veloce",
                           "lento", "bello", "brutto", "nuovo", "vecchio", "giovane", "anziano",
                           "mattina", "sera", "pomeriggio", "mezzogiorno", "mezzanotte",
                           "lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica",
                           "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
                           "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
            
            for parola in altre_parole:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO parole (parola, lunghezza, validata) VALUES (?, ?, 1)",
                        (parola, len(parola))
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
        self.cursor.execute("SELECT 1 FROM parole WHERE parola=? AND validata=1", (parola,))
        return self.cursor.fetchone() is not None
    
    def get_definizione(self, parola):
        """Restituisce la definizione di una parola."""
        self.cursor.execute("SELECT definizione FROM parole WHERE parola=?", (parola,))
        risultato = self.cursor.fetchone()
        if risultato and risultato[0]:
            return risultato[0]
        else:
            return f"(Definizione di '{parola}' non disponibile)"

# ==================== GENERATORE CRUCIVERBA Denso ====================
class CruciverbaGeneratorDenso:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]
        self.parole_inserite = []
        self.definizioni = {}
        
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
                if cella == '.':
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: black;">&nbsp;</td>'
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
                if self.griglia[i][j] != '.':
                    inizio_orizzontale = (j == 0 or self.griglia[i][j-1] == '.') and (j < self.colonne-1 and self.griglia[i][j+1] != '.')
                    inizio_verticale = (i == 0 or self.griglia[i-1][j] == '.') and (i < self.righe-1 and self.griglia[i+1][j] != '.')
                    
                    if inizio_orizzontale or inizio_verticale:
                        if (i, j) not in numeri_posizioni:
                            numeri_posizioni[(i, j)] = numero
                            numero += 1
        
        # Crea HTML
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 16px; margin: 0 auto;">'
        for i in range(self.righe):
            html += '<tr>'
            for j in range(self.colonne):
                if self.griglia[i][j] == '.':
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: black;">&nbsp;</td>'
                elif (i, j) in numeri_posizioni:
                    html += f'<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: white; position: relative;"><span style="font-size: 11px; position: absolute; top: 2px; left: 2px; font-weight: bold;">{numeri_posizioni[(i, j)]}</span>&nbsp;</td>'
                else:
                    html += '<td style="border: 1px solid black; width: 35px; height: 35px; text-align: center; background-color: white;">&nbsp;</td>'
            html += '</tr>'
        html += '</table>'
        
        return html, numeri_posizioni

    def _trova_parole_orizzontali(self):
        """Trova tutte le parole orizzontali nella griglia"""
        parole = []
        for i in range(self.righe):
            parola_corrente = ""
            inizio = 0
            for j in range(self.colonne):
                if self.griglia[i][j] != '.':
                    if parola_corrente == "":
                        inizio = j
                    parola_corrente += self.griglia[i][j]
                else:
                    if len(parola_corrente) > 1:
                        parole.append((parola_corrente, i, inizio, 'orizzontale'))
                    parola_corrente = ""
            if len(parola_corrente) > 1:
                parole.append((parola_corrente, i, inizio, 'orizzontale'))
        return parole
    
    def _trova_parole_verticali(self):
        """Trova tutte le parole verticali nella griglia"""
        parole = []
        for j in range(self.colonne):
            parola_corrente = ""
            inizio = 0
            for i in range(self.righe):
                if self.griglia[i][j] != '.':
                    if parola_corrente == "":
                        inizio = i
                    parola_corrente += self.griglia[i][j]
                else:
                    if len(parola_corrente) > 1:
                        parole.append((parola_corrente, inizio, j, 'verticale'))
                    parola_corrente = ""
            if len(parola_corrente) > 1:
                parole.append((parola_corrente, inizio, j, 'verticale'))
        return parole

    def _parole_compatibili(self, parola, riga, col, orientamento):
        """Verifica se una parola può essere inserita nella posizione data"""
        if orientamento == 'orizzontale':
            if col + len(parola) > self.colonne:
                return False
            for k, lettera in enumerate(parola):
                cella = self.griglia[riga][col + k]
                if cella != '.' and cella != lettera:
                    return False
            return True
        else:  # verticale
            if riga + len(parola) > self.righe:
                return False
            for k, lettera in enumerate(parola):
                cella = self.griglia[riga + k][col]
                if cella != '.' and cella != lettera:
                    return False
            return True

    def _inserisci_parola(self, parola, riga, col, orientamento):
        """Inserisce una parola nella griglia"""
        if orientamento == 'orizzontale':
            for k, lettera in enumerate(parola):
                self.griglia[riga][col + k] = lettera
        else:  # verticale
            for k, lettera in enumerate(parola):
                self.griglia[riga + k][col] = lettera
        self.parole_inserite.append((parola, riga, col, orientamento))

    def genera(self):
        """Genera un cruciverba denso con molti incroci"""
        try:
            self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_inserite = []
            
            # Prepara dizionario per lunghezza
            parole_disponibili = {}
            for lunghezza in range(2, max(self.righe, self.colonne) + 1):
                parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                if parole:
                    parole_disponibili[lunghezza] = parole
            
            if not parole_disponibili:
                return False
            
            # PASSO 1: Inserisci una parola orizzontale centrale
            centro_riga = self.righe // 2
            lunghezza_max = min(self.colonne, 8)
            if lunghezza_max in parole_disponibili and parole_disponibili[lunghezza_max]:
                parola_iniziale = random.choice(parole_disponibili[lunghezza_max]).upper()
                col_inizio = (self.colonne - len(parola_iniziale)) // 2
                self._inserisci_parola(parola_iniziale, centro_riga, col_inizio, 'orizzontale')
            
            # PASSO 2: Per ogni lettera della parola iniziale, prova a inserire parole verticali
            for j in range(self.colonne):
                if self.griglia[centro_riga][j] != '.':
                    lettera = self.griglia[centro_riga][j]
                    
                    # Cerca parole verticali che iniziano con questa lettera
                    for lunghezza in range(3, min(self.righe, 8)):
                        if lunghezza in parole_disponibili:
                            # Filtra parole che iniziano con la lettera
                            parole_candidate = [p for p in parole_disponibili[lunghezza] 
                                              if p[0].upper() == lettera]
                            
                            if parole_candidate:
                                parola = random.choice(parole_candidate).upper()
                                # Calcola posizione di partenza per centrare la parola
                                riga_inizio = centro_riga - (lunghezza // 2)
                                if riga_inizio < 0:
                                    riga_inizio = 0
                                if riga_inizio + lunghezza > self.righe:
                                    riga_inizio = self.righe - lunghezza
                                
                                if self._parole_compatibili(parola, riga_inizio, j, 'verticale'):
                                    self._inserisci_parola(parola, riga_inizio, j, 'verticale')
            
            # PASSO 3: Riempi altre righe con parole orizzontali
            for i in range(self.righe):
                if i == centro_riga:
                    continue  # Già piena
                
                # Trova spazi vuoti su questa riga
                j = 0
                while j < self.colonne:
                    if self.griglia[i][j] == '.':
                        # Trova la lunghezza dello spazio vuoto
                        spazio = 0
                        while j + spazio < self.colonne and self.griglia[i][j + spazio] == '.':
                            spazio += 1
                        
                        if spazio >= 3:
                            # Cerca una parola di lunghezza <= spazio
                            for lunghezza in range(min(spazio, 8), 2, -1):
                                if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                                    # Filtra parole che possono incrociarsi
                                    parola = random.choice(parole_disponibili[lunghezza]).upper()
                                    if self._parole_compatibili(parola, i, j, 'orizzontale'):
                                        self._inserisci_parola(parola, i, j, 'orizzontale')
                                        break
                        j += spazio
                    else:
                        j += 1
            
            # PASSO 4: Prova a riempire colonne rimaste vuote
            for j in range(self.colonne):
                # Cerca spazi verticali vuoti
                i = 0
                while i < self.righe:
                    if self.griglia[i][j] == '.':
                        spazio = 0
                        while i + spazio < self.righe and self.griglia[i + spazio][j] == '.':
                            spazio += 1
                        
                        if spazio >= 3:
                            for lunghezza in range(min(spazio, 8), 2, -1):
                                if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                                    parola = random.choice(parole_disponibili[lunghezza]).upper()
                                    if self._parole_compatibili(parola, i, j, 'verticale'):
                                        self._inserisci_parola(parola, i, j, 'verticale')
                                        break
                        i += spazio
                    else:
                        i += 1
            
            # Calcola se abbiamo abbastanza parole
            tutte_parole = self._trova_parole_orizzontali() + self._trova_parole_verticali()
            return len(tutte_parole) >= 3  # Almeno 3 parole totali
            
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
                if generatore.griglia[i][j] == '.':
                    riga += "█ "  # Blocco per casella nera
                else:
                    riga += "□ "  # Quadrato vuoto
            output.write(riga + "\n")
    
    # Aggiungi definizioni
    output.write("\n\nDEFINIZIONI\n")
    output.write("="*40 + "\n\n")
    
    orizzontali = generatore._trova_parole_orizzontali()
    verticali = generatore._trova_parole_verticali()
    
    if orizzontali:
        output.write("ORIZZONTALI:\n")
        for parola, r, c, orient in orizzontali:
            definizione = generatore.dizionario.get_definizione(parola.lower())
            output.write(f"  • {parola}: {definizione}\n")
    
    if verticali:
        output.write("\nVERTICALI:\n")
        for parola, r, c, orient in verticali:
            definizione = generatore.dizionario.get_definizione(parola.lower())
            output.write(f"  • {parola}: {definizione}\n")
    
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
        
        righe = st.number_input("Numero di righe", min_value=5, max_value=15, value=8, step=1)
        colonne = st.number_input("Numero di colonne", min_value=5, max_value=15, value=8, step=1)
        
        st.markdown("---")
        
        if st.button("🎲 GENERA NUOVO CRUCIVERBA", use_container_width=True):
            with st.spinner("Generazione in corso..."):
                st.session_state.generatore = CruciverbaGeneratorDenso(righe, colonne, st.session_state.dizionario)
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
            st.markdown("Griglia con le lettere:")
            st.markdown(st.session_state.generatore.griglia_html(), unsafe_allow_html=True)
        
        with col2:
            st.subheader("🔢 Schema Vuoto con Numeri")
            st.markdown("Griglia da riempire (ideale per stampare):")
            griglia_vuota, numeri = st.session_state.generatore.griglia_vuota_html()
            st.markdown(griglia_vuota, unsafe_allow_html=True)
        
        # Statistiche
        st.markdown("---")
        st.subheader("📊 Statistiche")
        
        tutte_parole = st.session_state.generatore._trova_parole_orizzontali() + st.session_state.generatore._trova_parole_verticali()
        celle_piene = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella != '.')
        totale_celle = righe * colonne
        percentuale = (celle_piene / totale_celle) * 100
        
        # Conta gli incroci (celle dove passano due parole)
        incroci = 0
        for i in range(righe):
            for j in range(colonne):
                if st.session_state.generatore.griglia[i][j] != '.':
                    # Verifica se la cella è parte di una parola orizzontale E verticale
                    orizzontale = (j > 0 and st.session_state.generatore.griglia[i][j-1] != '.') or \
                                  (j < colonne-1 and st.session_state.generatore.griglia[i][j+1] != '.')
                    verticale = (i > 0 and st.session_state.generatore.griglia[i-1][j] != '.') or \
                                (i < righe-1 and st.session_state.generatore.griglia[i+1][j] != '.')
                    if orizzontale and verticale:
                        incroci += 1
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Parole Totali", len(tutte_parole))
        col2.metric("Orizzontali", len(st.session_state.generatore._trova_parole_orizzontali()))
        col3.metric("Verticali", len(st.session_state.generatore._trova_parole_verticali()))
        col4.metric("Incroci", incroci)
        col5.metric("Celle Piene", f"{celle_piene}/{totale_celle} ({percentuale:.1f}%)")
        
        # Definizioni
        st.markdown("---")
        st.subheader("📚 Definizioni")
        
        tab1, tab2 = st.tabs(["Orizzontali", "Verticali"])
        
        with tab1:
            for parola, r, c, orient in st.session_state.generatore._trova_parole_orizzontali():
                definizione = st.session_state.dizionario.get_definizione(parola.lower())
                st.markdown(f"**{parola}** - {definizione}")
        
        with tab2:
            for parola, r, c, orient in st.session_state.generatore._trova_parole_verticali():
                definizione = st.session_state.dizionario.get_definizione(parola.lower())
                st.markdown(f"**{parola}** - {definizione}")
    
    else:
        st.info("👈 Imposta le dimensioni e clicca su 'GENERA NUOVO CRUCIVERBA' per iniziare!")
        
        # Esempio di anteprima
        st.markdown("---")
        st.subheader("🎯 Anteprima")
        st.markdown("""
        Il generatore creerà cruciverba con:
        - **Alta densità** di parole
        - **Numerosi incroci** tra orizzontali e verticali
        - Parole casuali dal database italiano (oltre 100 parole)
        - Definizioni automatiche
        - Due visualizzazioni: compilata e schema vuoto
        - Esportazione in formato TXT
        """)

if __name__ == "__main__":
    main()
