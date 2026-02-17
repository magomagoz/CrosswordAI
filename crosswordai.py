import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import random
from fpdf import FPDF
import os
from datetime import datetime

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
        # Conta quante parole ci sono già
        self.cursor.execute("SELECT COUNT(*) FROM parole")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            parole_con_definizioni = [
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
                ("bologna", "Città italiana, capoluogo dell'Emilia-Romagna, sede dell'università più antica"),
                ("genova", "Città italiana, capoluogo della Liguria, importante porto sul Mar Ligure"),
                ("palermo", "Città italiana, capoluogo della Sicilia, ricca di arte e cultura"),
                ("bari", "Città italiana, capoluogo della Puglia, centro economico del Mezzogiorno"),
                ("catania", "Città italiana sulla costa orientale della Sicilia, ai piedi dell'Etna"),
            ]
            
            for parola, definizione in parole_con_definizioni:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO parole (parola, definizione, lunghezza, validata) VALUES (?, ?, ?, 1)",
                        (parola, definizione, len(parola))
                    )
                except:
                    pass
            
            # Aggiungi altre parole senza definizione (solo per completare)
            altre_parole = ["re", "mamma", "papà", "fratello", "sorella", "nonno", "nonna", 
                           "zio", "zia", "cugino", "cugina", "nipote", "marito", "moglie",
                           "rosso", "blu", "verde", "giallo", "bianco", "nero", "marrone",
                           "grande", "piccolo", "alto", "basso", "lungo", "corto", "veloce",
                           "lento", "bello", "brutto", "nuovo", "vecchio", "giovane", "anziano",
                           "mangiare", "bere", "dormire", "correre", "saltare", "leggere", "scrivere",
                           "parlare", "ascoltare", "guardare", "sentire", "toccare", "odorare",
                           "felice", "triste", "arrabbiato", "calmo", "nervoso", "stanco", "energico",
                           "oggi", "domani", "ieri", "settimana", "mese", "anno", "secolo"]
            
            for parola in altre_parole:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO parole (parola, lunghezza, validata) VALUES (?, ?, 1)",
                        (parola, len(parola))
                    )
                except:
                    pass
            
            self.conn.commit()
            print(f"Dizionario popolato con {len(parole_con_definizioni) + len(altre_parole)} parole")

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

# ==================== GENERATORE CRUCIVERBA ====================
class CruciverbaGenerator:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]
        self.parole_inserite = []  # Lista di tuple (parola, riga, colonna, orientamento)
        self.definizioni = {}  # Dizionario con le definizioni
        
    def stampa_griglia(self):
        risultato = ""
        for riga in self.griglia:
            risultato += ' '.join(riga) + '\n'
        return risultato
    
    def griglia_con_numeri(self):
        """Restituisce la griglia con i numeri per le definizioni"""
        risultato = ""
        numero = 1
        numeri_posizioni = {}
        
        for i in range(self.righe):
            for j in range(self.colonne):
                if self.griglia[i][j] != '.':
                    # Controlla se è inizio di parola orizzontale
                    inizio_orizzontale = (j == 0 or self.griglia[i][j-1] == '.') and (j < self.colonne-1 and self.griglia[i][j+1] != '.')
                    # Controlla se è inizio di parola verticale
                    inizio_verticale = (i == 0 or self.griglia[i-1][j] == '.') and (i < self.righe-1 and self.griglia[i+1][j] != '.')
                    
                    if inizio_orizzontale or inizio_verticale:
                        if (i, j) not in numeri_posizioni:
                            numeri_posizioni[(i, j)] = numero
                            numero += 1
        
        # Seconda passata per stampare con i numeri
        for i in range(self.righe):
            riga_str = ""
            for j in range(self.colonne):
                if (i, j) in numeri_posizioni:
                    riga_str += f"{numeri_posizioni[(i, j)]:2d} "
                elif self.griglia[i][j] == '.':
                    riga_str += " ■ "
                else:
                    riga_str += "   "
            risultato += riga_str + '\n'
        
        return risultato, numeri_posizioni

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
                    if len(parola_corrente) > 1:  # Parola di almeno 2 lettere
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

    def genera(self, difficolta='media'):
        """Genera un cruciverba con parole casuali"""
        # Pulisci griglia
        self.griglia = [['.' for _ in range(self.colonne)] for _ in range(self.righe)]
        self.parole_inserite = []
        
        # Lista di parole possibili per diverse lunghezze
        parole_disponibili = {}
        for lunghezza in range(2, max(self.righe, self.colonne) + 1):
            parole_disponibili[lunghezza] = self.dizionario.get_parole_by_lunghezza(lunghezza)
        
        # Strategia: inserisci prima le parole più lunghe
        parole_inserite = 0
        tentativi = 0
        max_tentativi = 1000
        
        # Inserisci alcune parole orizzontali
        for i in range(0, self.righe, 2):  # Una riga sì e una no
            if tentativi > max_tentativi:
                break
                
            lunghezza = random.randint(3, min(self.colonne, 8))
            if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                parola = random.choice(parole_disponibili[lunghezza]).upper()
                # Cerca una posizione valida
                for _ in range(10):
                    j = random.randint(0, self.colonne - lunghezza)
                    # Controlla se la posizione è libera
                    libera = True
                    for k in range(lunghezza):
                        if self.griglia[i][j + k] != '.':
                            libera = False
                            break
                    if libera:
                        # Inserisci la parola
                        for k, lettera in enumerate(parola):
                            self.griglia[i][j + k] = lettera
                        self.parole_inserite.append((parola, i, j, 'orizzontale'))
                        parole_inserite += 1
                        break
            tentativi += 1
        
        # Inserisci alcune parole verticali
        for j in range(1, self.colonne, 2):  # Una colonna sì e una no
            if tentativi > max_tentativi:
                break
                
            lunghezza = random.randint(3, min(self.righe, 8))
            if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                parola = random.choice(parole_disponibili[lunghezza]).upper()
                # Cerca una posizione valida
                for _ in range(10):
                    i = random.randint(0, self.righe - lunghezza)
                    # Controlla se la posizione è libera
                    libera = True
                    # Controlla anche che le lettere corrispondano se ci sono incroci
                    for k in range(lunghezza):
                        cella = self.griglia[i + k][j]
                        if cella != '.' and cella != parola[k]:
                            libera = False
                            break
                        elif cella == '.':
                            # OK, libera
                            pass
                    if libera:
                        # Inserisci la parola
                        for k, lettera in enumerate(parola):
                            self.griglia[i + k][j] = lettera
                        self.parole_inserite.append((parola, i, j, 'verticale'))
                        parole_inserite += 1
                        break
            tentativi += 1
        
        # Raccogli tutte le parole finali e le loro definizioni
        tutte_parole = self._trova_parole_orizzontali() + self._trova_parole_verticali()
        for parola, r, c, orient in tutte_parole:
            self.definizioni[(r, c, orient)] = {
                'parola': parola,
                'definizione': self.dizionario.get_definizione(parola.lower())
            }
        
        return len(tutte_parole) > 0

# ==================== GENERATORE PDF ====================
class PDFCruciverba(FPDF):
    def __init__(self, titolo="Cruciverba"):
        super().__init__()
        self.titolo = titolo
        
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.titolo, 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def esporta_pdf_compilato(generatore, filename, titolo="Cruciverba Compilato"):
    """Esporta il cruciverba compilato in PDF"""
    pdf = PDFCruciverba(titolo)
    pdf.add_page()
    pdf.set_font('Courier', '', 12)
    
    # Griglia compilata
    pdf.cell(0, 10, "Griglia Compilata:", 0, 1)
    pdf.ln(5)
    
    griglia_str = generatore.stampa_griglia()
    for riga in griglia_str.split('\n'):
        if riga.strip():
            pdf.cell(0, 8, riga, 0, 1)
    
    # Parole inserite
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Parole Inserite:", 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for i, (parola, r, c, orient) in enumerate(generatore.parole_inserite, 1):
        pdf.cell(0, 6, f"{i}. {parola} ({orient}, posizione: [{r},{c}])", 0, 1)
    
    # Definizioni
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Definizioni:", 0, 1)
    pdf.set_font('Arial', '', 10)
    
    # Raccogli tutte le parole con definizioni
    tutte_parole = generatore._trova_parole_orizzontali() + generatore._trova_parole_verticali()
    for parola, r, c, orient in tutte_parole:
        definizione = generatore.dizionario.get_definizione(parola.lower())
        pdf.multi_cell(0, 6, f"{parola} ({orient}): {definizione}")
    
    pdf.output(filename)

def esporta_pdf_schema_vuoto(generatore, filename, titolo="Schema Cruciverba"):
    """Esporta solo lo schema vuoto con caselle nere in PDF"""
    pdf = PDFCruciverba(titolo)
    pdf.add_page()
    pdf.set_font('Courier', '', 14)
    
    pdf.cell(0, 10, "Schema Cruciverba:", 0, 1)
    pdf.ln(5)
    
    # Ottieni griglia con numeri
    griglia_numeri, posizioni_numeri = generatore.griglia_con_numeri()
    
    # Stampa la griglia vuota
    for riga in griglia_numeri.split('\n'):
        if riga.strip():
            pdf.cell(0, 8, riga, 0, 1)
    
    # Definizioni orizzontali e verticali
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Definizioni:", 0, 1)
    pdf.set_font('Arial', '', 10)
    
    # Separa orizzontali e verticali
    orizzontali = generatore._trova_parole_orizzontali()
    verticali = generatore._trova_parole_verticali()
    
    # Dizionario per mappare posizioni a numeri
    numero_posizione = {}
    num = 1
    for i in range(generatore.righe):
        for j in range(generatore.colonne):
            if generatore.griglia[i][j] != '.':
                inizio_orizzontale = (j == 0 or generatore.griglia[i][j-1] == '.') and (j < generatore.colonne-1 and generatore.griglia[i][j+1] != '.')
                inizio_verticale = (i == 0 or generatore.griglia[i-1][j] == '.') and (i < generatore.righe-1 and generatore.griglia[i+1][j] != '.')
                if inizio_orizzontale or inizio_verticale:
                    if (i, j) not in numero_posizione:
                        numero_posizione[(i, j)] = num
                        num += 1
    
    if orizzontali:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Orizzontali:", 0, 1)
        pdf.set_font('Arial', '', 10)
        for parola, r, c, orient in orizzontali:
            if (r, c) in numero_posizione:
                num = numero_posizione[(r, c)]
                definizione = generatore.dizionario.get_definizione(parola.lower())
                pdf.cell(0, 6, f"{num}. {definizione}", 0, 1)
    
    if verticali:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Verticali:", 0, 1)
        pdf.set_font('Arial', '', 10)
        for parola, r, c, orient in verticali:
            if (r, c) in numero_posizione:
                num = numero_posizione[(r, c)]
                definizione = generatore.dizionario.get_definizione(parola.lower())
                pdf.cell(0, 6, f"{num}. {definizione}", 0, 1)
    
    pdf.output(filename)

# ==================== INTERFACCIA GRAFICA ====================
class CruciverbaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generatore di Cruciverba Italiani")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variabili
        self.righe_var = tk.IntVar(value=10)
        self.colonne_var = tk.IntVar(value=10)
        self.difficolta_var = tk.StringVar(value="media")
        self.dizionario = DizionarioItaliano()
        self.generatore = None
        
        # Colori e stili
        self.root.configure(bg='#f0f0f0')
        
        # Crea l'interfaccia
        self._crea_widgets()
        
    def _crea_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo con stile
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="🧩 GENERATORE DI CRUCIVERBA ITALIANI", 
                               font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Parole dall'Accademia della Crusca e Treccani", 
                                  font=('Arial', 10, 'italic'), bg='#f0f0f0', fg='#7f8c8d')
        subtitle_label.pack()
        
        # Linea separatrice
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Frame per input
        input_frame = ttk.LabelFrame(main_frame, text=" Dimensioni Cruciverba ", padding="15")
        input_frame.pack(fill=tk.X, pady=10)
        
        # Griglia per input
        input_grid = ttk.Frame(input_frame)
        input_grid.pack()
        
        # Righe
        ttk.Label(input_grid, text="Numero di righe:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='w')
        righe_spinbox = ttk.Spinbox(input_grid, from_=5, to=25, textvariable=self.righe_var, width=10, font=('Arial', 11))
        righe_spinbox.grid(row=0, column=1, padx=10, pady=8)
        
        # Colonne
        ttk.Label(input_grid, text="Numero di colonne:", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=8, sticky='w')
        colonne_spinbox = ttk.Spinbox(input_grid, from_=5, to=25, textvariable=self.colonne_var, width=10, font=('Arial', 11))
        colonne_spinbox.grid(row=1, column=1, padx=10, pady=8)
        
        # Difficoltà
        ttk.Label(input_grid, text="Difficoltà:", font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=8, sticky='w')
        difficolta_combo = ttk.Combobox(input_grid, textvariable=self.difficolta_var, values=["facile", "media", "difficile"], 
                                        width=10, state="readonly", font=('Arial', 11))
        difficolta_combo.grid(row=2, column=1, padx=10, pady=8)
        
        # Frame pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        # Pulsante Crea Cruciverba
        self.create_button = tk.Button(button_frame, text="✏️ CREA NUOVO CRUCIVERBA", 
                                       command=self.crea_cruciverba,
                                       bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                                       padx=20, pady=10, cursor='hand2', relief=tk.FLAT)
        self.create_button.pack(side=tk.LEFT, padx=5)
        
        # Pulsante Esporta PDF Compilato
        self.export_compiled_button = tk.Button(button_frame, text="📄 ESPORTA PDF COMPILATO", 
                                                command=self.esporta_pdf_compilato,
                                                bg='#27ae60', fg='white', font=('Arial', 11),
                                                padx=15, pady=8, cursor='hand2', relief=tk.FLAT,
                                                state=tk.DISABLED)
        self.export_compiled_button.pack(side=tk.LEFT, padx=5)
        
        # Pulsante Esporta PDF Schema Vuoto
        self.export_empty_button = tk.Button(button_frame, text="📄 ESPORTA PDF SCHEMA VUOTO", 
                                             command=self.esporta_pdf_schema_vuoto,
                                             bg='#e67e22', fg='white', font=('Arial', 11),
                                             padx=15, pady=8, cursor='hand2', relief=tk.FLAT,
                                             state=tk.DISABLED)
        self.export_empty_button.pack(side=tk.LEFT, padx=5)
        
        # Area risultati
        result_frame = ttk.LabelFrame(main_frame, text=" Cruciverba Generato ", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget con scrollbar
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.griglia_text = tk.Text(text_frame, height=15, font=('Courier', 12), 
                                     wrap=tk.NONE, bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.griglia_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar verticale
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.griglia_text.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.griglia_text.config(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar orizzontale
        h_scrollbar = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.griglia_text.xview)
        h_scrollbar.pack(fill=tk.X)
        self.griglia_text.config(xscrollcommand=h_scrollbar.set)
        
        # Frame definizioni
        def_frame = ttk.LabelFrame(main_frame, text=" Definizioni ", padding="10")
        def_frame.pack(fill=tk.X, pady=10)
        
        self.def_text = tk.Text(def_frame, height=8, font=('Arial', 10), wrap=tk.WORD)
        self.def_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5,0))
        
        self.status_label = tk.Label(status_frame, text="✅ Pronto - Database connesso", 
                                      font=('Arial', 9), bg='#f0f0f0', fg='#27ae60', anchor='w')
        self.status_label.pack(side=tk.LEFT)
        
        # Stats label
        self.stats_label = tk.Label(status_frame, text="", font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', anchor='e')
        self.stats_label.pack(side=tk.RIGHT)
        
    def crea_cruciverba(self):
        """Crea un nuovo cruciverba"""
        righe = self.righe_var.get()
        colonne = self.colonne_var.get()
        difficolta = self.difficolta_var.get()
        
        # Pulisci le aree di testo
        self.griglia_text.delete(1.0, tk.END)
        self.def_text.delete(1.0, tk.END)
        
        # Mostra messaggio
        self.griglia_text.insert(tk.END, f"Generazione cruciverba {righe}x{colonne} (difficoltà: {difficolta})...\n\n")
        self.root.update()
        
        try:
            # Crea generatore
            self.generatore = CruciverbaGenerator(righe, colonne, self.dizionario)
            
            # Genera cruciverba
            successo = self.generatore.genera(difficolta)
            
            if successo:
                # Mostra la griglia
                griglia_string = self.generatore.stampa_griglia()
                self.griglia_text.insert(tk.END, "GRIGLIA COMPILATA:\n")
                self.griglia_text.insert(tk.
