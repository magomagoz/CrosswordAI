import streamlit as st
import random
from datetime import datetime
import io

# ==================== DIZIONARIO ITALIANO COMPLETO ====================
class DizionarioItaliano:
    def __init__(self):
        # Dizionario ricco di parole italiane
        self.parole = {
            3: ["RE", "TRE", "SEI", "ORO", "VIA", "IRA", "ERA", "ORA", "DUE", "QUA", "LA", "RA", "UNO", "CHE", "CHI", "NEL", "DEL", "CON", "PER", "TRA", "FRA", "NON", "MAI", "PIU", "GIA", "QUI", "LUI", "LEI", "NOI", "VOI", "SOLE", "LUNA"],
            
            4: ["CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", "FIORE", "ALBERO", "AUTO", "TRENO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", "ARIA", "AMICO", "SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ANNO", "MESE", "PORTA", "CARTA", "PENNA", "BANCO", "BELLO", "BRUTTO", "CALDO", "FREDDO", "DOLCE", "AMARO", "SALE", "PASTA", "PIZZA", "MAMMA", "PAPA", "NONNO", "NONNA", "GARA", "CORSA", "VOLO", "CANTO", "VOCE", "SUONO", "VERDE", "ROSSO", "BLU", "NERO", "BIANCO", "GIALLO"],
            
            5: ["SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", "INVERNO", "PRIMAVERA", "AUTUNNO", "CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", "FIORE", "ALBERO", "AUTO", "TRENO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", "ARIA", "AMICO", "GIARDINO", "CUCINA", "BAGNO", "CAMERA", "SALONE", "LETTO", "SEDIA", "TAVOLO", "PORTA", "FINESTRA", "MURO", "TETTO", "PIANO", "SCALA", "BIANCO", "NERO", "ROSSO", "VERDE", "GIALLO", "BLU", "MARRONE"],
            
            6: ["GIARDINO", "CUCINA", "BAGNO", "CAMERA", "SALONE", "SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", "INVERNO", "PRIMAVERA", "AUTUNNO", "BIANCO", "NERO", "ROSSO", "VERDE", "GIALLO", "BLU", "MARRONE", "GRANDE", "PICCOLO", "NUOVO", "VECCHIO", "GIOVANE", "ANZIANO", "MATTINA", "SERA", "POMERIGGIO", "MEZZANOTTE", "RUMORE", "SILENZIO", "PAROLA", "FRASE", "DISCORSO", "PENSIERO"],
            
            7: ["GIARDINO", "CUCINA", "BAGNO", "CAMERA", "SALONE", "SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", "INVERNO", "PRIMAVERA", "AUTUNNO", "BIANCO", "NERO", "ROSSO", "VERDE", "GIALLO", "BLU", "MARRONE", "RUMORE", "SILENZIO", "PAROLA", "FRASE", "DISCORSO", "PENSIERO", "PROFESSORE", "STUDENTE", "UNIVERSITA"],
            
            8: ["GIARDINO", "CUCINA", "BAGNO", "CAMERA", "SALONE", "PROFESSORE", "STUDENTE", "UNIVERSITA", "BIBLIOTECA", "LABORATORIO", "OSPEDALE", "DOTTORE", "INFERMIERE", "FARMACIA", "INGEGNERE", "ARCHITETTO"],
            
            9: ["PROFESSORE", "STUDENTE", "UNIVERSITA", "BIBLIOTECA", "LABORATORIO", "OSPEDALE", "DOTTORE", "INFERMIERE", "FARMACIA", "INGEGNERE", "ARCHITETTO"],
            
            10: ["PROFESSORE", "UNIVERSITA", "BIBLIOTECA", "LABORATORIO", "OSPEDALE", "INGEGNERE", "ARCHITETTO"],
        }
        
        # Definizioni
        self.definizioni = {
            "AMORE": "Sentimento di profondo affetto",
            "VITA": "Condizione degli esseri organizzati",
            "TEMPO": "Durata delle cose soggette a mutamento",
            "MORTE": "Cessazione della vita",
            "NOTTE": "Periodo di oscurità",
            "GIORNO": "Periodo di luce",
            "ESTATE": "Stagione più calda",
            "INVERNO": "Stagione più fredda",
            "CASA": "Edificio adibito ad abitazione",
            "CANE": "Animale domestico",
            "GATTO": "Felino domestico",
            "LIBRO": "Insieme di fogli stampati",
            "SOLE": "Stella centrale del sistema solare",
            "LUNA": "Satellite naturale della Terra",
            "MARE": "Grande distesa d'acqua salata",
            "ACQUA": "Liquido essenziale per la vita",
            "TERRA": "Pianeta su cui viviamo",
            "ARIA": "Miscuglio di gas",
            "FUOCO": "Fiamma che produce calore",
            "BIANCO": "Colore della neve",
            "NERO": "Colore della notte",
            "ROSSO": "Colore del sangue",
            "VERDE": "Colore dell'erba",
            "GIALLO": "Colore del limone",
            "BLU": "Colore del cielo",
            "MARRONE": "Colore del legno",
            "RUMORE": "Suono confuso e sgradevole",
            "SILENZIO": "Assenza di rumore",
            "PAROLA": "Unità linguistica dotata di significato",
            "FRASE": "Insieme di parole con senso compiuto",
            "SCUOLA": "Istituto dove si impartisce l'istruzione",
            "AMICO": "Persona legata da affetto",
            "FIORE": "Parte della pianta che contiene gli organi riproduttivi",
            "ALBERO": "Pianta perenne con fusto legnoso",
            "AUTO": "Veicolo a motore",
            "TRENO": "Mezzo di trasporto su rotaie",
            "PANE": "Alimento dalla cottura di pasta lievitata",
            "VINO": "Bevanda alcolica da uva fermentata",
            "PASTA": "Alimento base della cucina italiana",
            "PIZZA": "Tipico piatto italiano",
            "MAMMA": "Madre, genitrice",
            "PAPA": "Padre, genitore",
            "NONNO": "Padre del padre o della madre",
            "NONNA": "Madre del padre o della madre",
        }
        
    def get_parole_by_lunghezza(self, lunghezza):
        """Restituisce parole di una data lunghezza"""
        if lunghezza in self.parole:
            return self.parole[lunghezza]
        # Cerca la lunghezza più vicina
        for l in range(lunghezza-1, lunghezza+2):
            if l in self.parole:
                return self.parole[l]
        return []
    
    def parola_esiste(self, parola):
        """Verifica se una parola esiste nel dizionario"""
        parole_lunghezza = self.get_parole_by_lunghezza(len(parola))
        return parola.upper() in [p.upper() for p in parole_lunghezza]
    
    def get_definizione(self, parola):
        """Restituisce la definizione di una parola"""
        p = parola.upper()
        if p in self.definizioni:
            return self.definizioni[p]
        return f"(Definizione di '{parola}' non disponibile)"

# ==================== GENERATORE CRUCIVERBA PERFETTO ====================
class CruciverbaPerfetto:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['#' for _ in range(colonne)] for _ in range(righe)]  # Inizia tutto nero
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

    def _verifica_parola_orizzontale(self, riga, col, lunghezza):
        """Verifica se una parola orizzontale è valida (esiste e ha incroci validi)"""
        if col + lunghezza > self.colonne:
            return False
        
        # Estrai la parola
        parola = ""
        for k in range(lunghezza):
            parola += self.griglia[riga][col + k]
        
        # Verifica che non ci siano spazi vuoti
        if '.' in parola:
            return False
        
        # Verifica che esista nel dizionario
        if not self.dizionario.parola_esiste(parola):
            return False
        
        # Verifica che ogni lettera faccia parte di una parola verticale valida
        for k in range(lunghezza):
            # Trova la parola verticale che passa per questa cella
            verticale = ""
            inizio_v = riga
            while inizio_v > 0 and self.griglia[inizio_v - 1][col + k] != '#':
                inizio_v -= 1
            
            fine_v = riga
            while fine_v < self.righe - 1 and self.griglia[fine_v + 1][col + k] != '#':
                fine_v += 1
            
            for v in range(inizio_v, fine_v + 1):
                verticale += self.griglia[v][col + k]
            
            # Se la parola verticale è lunga almeno 3 lettere, deve esistere nel dizionario
            if len(verticale) >= 3 and not self.dizionario.parola_esiste(verticale):
                return False
        
        return True

    def _verifica_parola_verticale(self, riga, col, lunghezza):
        """Verifica se una parola verticale è valida"""
        if riga + lunghezza > self.righe:
            return False
        
        parola = ""
        for k in range(lunghezza):
            parola += self.griglia[riga + k][col]
        
        if '.' in parola:
            return False
        
        if not self.dizionario.parola_esiste(parola):
            return False
        
        # Verifica ogni incrocio orizzontale
        for k in range(lunghezza):
            orizzontale = ""
            inizio_o = col
            while inizio_o > 0 and self.griglia[riga + k][inizio_o - 1] != '#':
                inizio_o -= 1
            
            fine_o = col
            while fine_o < self.colonne - 1 and self.griglia[riga + k][fine_o + 1] != '#':
                fine_o += 1
            
            for o in range(inizio_o, fine_o + 1):
                orizzontale += self.griglia[riga + k][o]
            
            if len(orizzontale) >= 3 and not self.dizionario.parola_esiste(orizzontale):
                return False
        
        return True

    def _inserisci_blocco(self, parole):
        """Inserisce un blocco di parole incrociate"""
        if not parole:
            return False
        
        # Scegli una parola centrale
        parola_centrale = random.choice(parole)
        lunghezza = len(parola_centrale)
        
        # Posiziona al centro
        riga = self.righe // 2
        col = (self.colonne - lunghezza) // 2
        
        if col < 0 or col + lunghezza > self.colonne:
            return False
        
        # Inserisci la parola
        for k, lettera in enumerate(parola_centrale):
            self.griglia[riga][col + k] = lettera
        
        self.parole_orizzontali.append((parola_centrale, riga, col))
        
        # Per ogni lettera, cerca di inserire una verticale
        for k, lettera in enumerate(parola_centrale):
            col_v = col + k
            
            # Cerca parole verticali che iniziano con questa lettera
            for lunghezza_v in range(3, min(7, self.righe)):
                parole_v = self.dizionario.get_parole_by_lunghezza(lunghezza_v)
                parole_v = [p for p in parole_v if p[0] == lettera]
                
                if not parole_v:
                    continue
                
                parola_v = random.choice(parole_v)
                riga_inizio = riga
                
                # Verifica che possa essere inserita
                if riga_inizio + lunghezza_v <= self.righe:
                    # Controlla compatibilità
                    compatibile = True
                    for vk in range(lunghezza_v):
                        cella = self.griglia[riga_inizio + vk][col_v]
                        if cella != '#' and cella != parola_v[vk]:
                            compatibile = False
                            break
                    
                    if compatibile:
                        # Inserisci
                        for vk, lettera_v in enumerate(parola_v):
                            self.griglia[riga_inizio + vk][col_v] = lettera_v
                        self.parole_verticali.append((parola_v, riga_inizio, col_v))
                        break
        
        return True

    def _completa_griglia(self):
        """Completa la griglia assicurando che ogni cella sia valida"""
        # Per ogni riga, completa le parole orizzontali
        for i in range(self.righe):
            j = 0
            while j < self.colonne:
                if self.griglia[i][j] != '#':
                    inizio = j
                    # Trova la lunghezza
                    while j < self.colonne and self.griglia[i][j] != '#':
                        j += 1
                    lunghezza = j - inizio
                    
                    if lunghezza >= 3:
                        # Verifica se la parola è già valida
                        parola = ""
                        for k in range(lunghezza):
                            parola += self.griglia[i][inizio + k]
                        
                        if not self.dizionario.parola_esiste(parola):
                            # Cerca una parola compatibile
                            parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                            for p in parole:
                                compatibile = True
                                for k in range(lunghezza):
                                    cella = self.griglia[i][inizio + k]
                                    if cella != p[k] and cella != '#':
                                        compatibile = False
                                        break
                                if compatibile:
                                    # Inserisci
                                    for k, lettera in enumerate(p):
                                        self.griglia[i][inizio + k] = lettera
                                    self.parole_orizzontali.append((p, i, inizio))
                                    break
                else:
                    j += 1
        
        # Per ogni colonna, completa le parole verticali
        for j in range(self.colonne):
            i = 0
            while i < self.righe:
                if self.griglia[i][j] != '#':
                    inizio = i
                    while i < self.righe and self.griglia[i][j] != '#':
                        i += 1
                    lunghezza = i - inizio
                    
                    if lunghezza >= 3:
                        parola = ""
                        for k in range(lunghezza):
                            parola += self.griglia[inizio + k][j]
                        
                        if not self.dizionario.parola_esiste(parola):
                            parole = self.dizionario.get_parole_by_lunghezza(lunghezza)
                            for p in parole:
                                compatibile = True
                                for k in range(lunghezza):
                                    cella = self.griglia[inizio + k][j]
                                    if cella != p[k] and cella != '#':
                                        compatibile = False
                                        break
                                if compatibile:
                                    for k, lettera in enumerate(p):
                                        self.griglia[inizio + k][j] = lettera
                                    self.parole_verticali.append((p, inizio, j))
                                    break
                else:
                    i += 1

    def genera(self):
        """Genera un cruciverba perfetto senza caselle bianche"""
        try:
            # Resetta griglia (tutto nero)
            self.griglia = [['#' for _ in range(self.colonne)] for _ in range(self.righe)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # Prepara parole per lunghezza
            parole_disponibili = {}
            for l in range(3, min(self.colonne, 10) + 1):
                parole_disponibili[l] = self.dizionario.get_parole_by_lunghezza(l)
            
            # Inserisci blocco centrale
            for lunghezza in range(min(8, self.colonne), 3, -1):
                if lunghezza in parole_disponibili and parole_disponibili[lunghezza]:
                    if self._inserisci_blocco(parole_disponibili[lunghezza]):
                        break
            
            # Completa la griglia
            self._completa_griglia()
            
            # Raccogli tutte le parole finali
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
                        if len(parola) >= 3 and self.dizionario.parola_esiste(parola):
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
                        if len(parola) >= 3 and self.dizionario.parola_esiste(parola):
                            self.parole_verticali.append((parola, inizio, j))
                    else:
                        i += 1
            
            # Verifica che non ci siano celle bianche
            for i in range(self.righe):
                for j in range(self.colonne):
                    if self.griglia[i][j] == '.':
                        self.griglia[i][j] = '#'
            
            return len(self.parole_orizzontali) + len(self.parole_verticali) >= 4
            
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
            st.session_state.dizionario = DizionarioItaliano()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba Italiano Perfetto")
    st.markdown("### Nessuna casella bianca - solo lettere o nere")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        righe = st.number_input("Righe", min_value=5, max_value=15, value=8, step=1)
    with col2:
        colonne = st.number_input("Colonne", min_value=5, max_value=15, value=10, step=1)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
            with st.spinner("Generazione cruciverba perfetto..."):
                st.session_state.generatore = CruciverbaPerfetto(righe, colonne, st.session_state.dizionario)
                if st.session_state.generatore.genera():
                    st.success("✅ Cruciverba generato con successo!")
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
        
        # Esportazione
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button("📄 Scarica TXT Compilato", data=txt,
                             file_name=f"cruciverba_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             use_container_width=True)
        with col2:
            txt2 = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button("📄 Scarica TXT Vuoto", data=txt2,
                             file_name=f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             use_container_width=True)

if __name__ == "__main__":
    main()
