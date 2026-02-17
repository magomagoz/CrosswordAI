import streamlit as st
import random
import requests
import time
from datetime import datetime
import io

# ==================== DIZIONARIO ITALIANO ====================
class DizionarioItaliano:
    def __init__(self):
        # Parole italiane vere per 5x5
        self.parole_3 = ["RE", "ERA", "ORA", "VIA", "SOLE", "LUNA", "MARE", "MONTE", "FIORE"]
        self.parole_4 = ["CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", "FIORE", 
                        "ALBERO", "AUTO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", "ARIA", 
                        "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "PORTA", "CARTA"]
        self.parole_5 = ["SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", 
                        "INVERNO", "PRIMAVERA", "AUTUNNO", "BIANCO", "NERO", "ROSSO", "VERDE", 
                        "GIALLO", "GRANDE", "PICCOLO", "FIORE", "ALBERO", "ACQUA", "TERRA", "ARIA"]
        
        # Verifica rapida (senza API per velocità)
        self.parole_valide = set(self.parole_3 + self.parole_4 + self.parole_5)
        
    def parola_esiste(self, parola):
        """Verifica se una parola esiste (cache locale)"""
        return parola.upper() in self.parole_valide
    
    def get_parole_by_lunghezza(self, lunghezza, lettera_iniziale=None, exclude=None):
        """Restituisce parole di data lunghezza"""
        if lunghezza == 3:
            parole = self.parole_3
        elif lunghezza == 4:
            parole = self.parole_4
        elif lunghezza == 5:
            parole = self.parole_5
        else:
            return []
        
        if lettera_iniziale:
            parole = [p for p in parole if p.startswith(lettera_iniziale.upper())]
        
        if exclude:
            parole = [p for p in parole if p not in exclude]
        
        return parole

# ==================== GENERATORE 5x5 PERFETTO ====================
class Cruciverba5x5:
    def __init__(self, dizionario):
        self.righe = 5
        self.colonne = 5
        self.dizionario = dizionario
        self.griglia = [['#' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        
    def griglia_html(self, mostra_lettere=True):
        """Restituisce la griglia in formato HTML"""
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 20px; margin: 0 auto; background-color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
        
        # Calcola numeri
        numeri_posizioni = {}
        if not mostra_lettere:
            numero = 1
            for i in range(5):
                for j in range(5):
                    if self.griglia[i][j] != '#':
                        inizio_orizzontale = (j == 0 or self.griglia[i][j-1] == '#') and (j < 4 and self.griglia[i][j+1] != '#')
                        inizio_verticale = (i == 0 or self.griglia[i-1][j] == '#') and (i < 4 and self.griglia[i+1][j] != '#')
                        if inizio_orizzontale or inizio_verticale:
                            if (i, j) not in numeri_posizioni:
                                numeri_posizioni[(i, j)] = numero
                                numero += 1
        
        for i in range(5):
            html += '<tr>'
            for j in range(5):
                cella = self.griglia[i][j]
                if cella == '#':
                    html += '<td style="border: 2px solid #333; width: 50px; height: 50px; text-align: center; background-color: #222;">&nbsp;</td>'
                elif not mostra_lettere and (i, j) in numeri_posizioni:
                    html += f'<td style="border: 2px solid #333; width: 50px; height: 50px; text-align: center; background-color: white; font-size: 18px; font-weight: bold; color: #c41e3a;">{numeri_posizioni[(i, j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid #333; width: 50px; height: 50px; text-align: center; background-color: white;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 2px solid #333; width: 50px; height: 50px; text-align: center; background-color: white; font-weight: bold; font-size: 22px; color: #333;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def _verifica_parola_orizzontale(self, riga, col, parola):
        """Verifica se una parola orizzontale può essere inserita"""
        if col + len(parola) > 5:
            return False
        
        # Verifica che ai lati ci siano bordi o nere
        if col > 0 and self.griglia[riga][col-1] != '#':
            return False
        if col + len(parola) < 5 and self.griglia[riga][col + len(parola)] != '#':
            return False
        
        # Verifica compatibilità lettere
        for k, lettera in enumerate(parola):
            cella = self.griglia[riga][col + k]
            if cella != '#' and cella != lettera:
                return False
        return True

    def _verifica_parola_verticale(self, riga, col, parola):
        """Verifica se una parola verticale può essere inserita"""
        if riga + len(parola) > 5:
            return False
        
        if riga > 0 and self.griglia[riga-1][col] != '#':
            return False
        if riga + len(parola) < 5 and self.griglia[riga + len(parola)][col] != '#':
            return False
        
        for k, lettera in enumerate(parola):
            cella = self.griglia[riga + k][col]
            if cella != '#' and cella != lettera:
                return False
        return True

    def _inserisci_orizzontale(self, parola, riga, col):
        """Inserisce una parola orizzontale"""
        for k, lettera in enumerate(parola):
            self.griglia[riga][col + k] = lettera
        self.parole_orizzontali.append((parola, riga, col))
        self.parole_usate.add(parola)

    def _inserisci_verticale(self, parola, riga, col):
        """Inserisce una parola verticale"""
        for k, lettera in enumerate(parola):
            self.griglia[riga + k][col] = lettera
        self.parole_verticali.append((parola, riga, col))
        self.parole_usate.add(parola)

    def genera(self):
        """Genera un cruciverba 5x5 perfetto"""
        try:
            # Prova diversi pattern di caselle nere
            patterns_nere = [
                [(2,2)],  # 1 nera al centro
                [(1,1), (3,3)],  # 2 nere diagonali
                [(1,2), (3,2)],  # 2 nere verticali
                [(2,1), (2,3)],  # 2 nere orizzontali
                [(0,2), (2,0), (4,2)],  # 3 nere a croce
                [(1,1), (3,3), (1,3), (3,1)],  # 4 nere
            ]
            
            for pattern in patterns_nere:
                # Resetta griglia
                self.griglia = [['#' for _ in range(5)] for _ in range(5)]
                self.parole_usate.clear()
                self.parole_orizzontali = []
                self.parole_verticali = []
                
                # Applica pattern (lascia '.' per le lettere)
                for i in range(5):
                    for j in range(5):
                        if (i, j) in pattern:
                            self.griglia[i][j] = '#'
                        else:
                            self.griglia[i][j] = '.'
                
                # Trova spazi orizzontali
                spazi_oriz = []
                for i in range(5):
                    j = 0
                    while j < 5:
                        if self.griglia[i][j] == '.':
                            inizio = j
                            lunghezza = 0
                            while j < 5 and self.griglia[i][j] == '.':
                                lunghezza += 1
                                j += 1
                            if lunghezza >= 3:
                                spazi_oriz.append((i, inizio, lunghezza))
                        else:
                            j += 1
                
                # Trova spazi verticali
                spazi_vert = []
                for j in range(5):
                    i = 0
                    while i < 5:
                        if self.griglia[i][j] == '.':
                            inizio = i
                            lunghezza = 0
                            while i < 5 and self.griglia[i][j] == '.':
                                lunghezza += 1
                                i += 1
                            if lunghezza >= 3:
                                spazi_vert.append((inizio, j, lunghezza))
                        else:
                            i += 1
                
                # Riempi orizzontali
                for riga, col, lunghezza in spazi_oriz:
                    parole = self.dizionario.get_parole_by_lunghezza(lunghezza, exclude=self.parole_usate)
                    for parola in parole:
                        if self._verifica_parola_orizzontale(riga, col, parola):
                            self._inserisci_orizzontale(parola, riga, col)
                            break
                
                # Riempi verticali
                for riga, col, lunghezza in spazi_vert:
                    parole = self.dizionario.get_parole_by_lunghezza(lunghezza, exclude=self.parole_usate)
                    for parola in parole:
                        if self._verifica_parola_verticale(riga, col, parola):
                            self._inserisci_verticale(parola, riga, col)
                            break
                
                # Verifica che tutte le celle siano piene
                completo = True
                for i in range(5):
                    for j in range(5):
                        if self.griglia[i][j] == '.':
                            completo = False
                            break
                    if not completo:
                        break
                
                if completo:
                    # Raccogli parole finali
                    self.parole_orizzontali = []
                    self.parole_verticali = []
                    
                    for i in range(5):
                        j = 0
                        while j < 5:
                            if self.griglia[i][j] != '#':
                                inizio = j
                                parola = ""
                                while j < 5 and self.griglia[i][j] != '#':
                                    parola += self.griglia[i][j]
                                    j += 1
                                if len(parola) >= 3:
                                    self.parole_orizzontali.append((parola, i, inizio))
                            else:
                                j += 1
                    
                    for j in range(5):
                        i = 0
                        while i < 5:
                            if self.griglia[i][j] != '#':
                                inizio = i
                                parola = ""
                                while i < 5 and self.griglia[i][j] != '#':
                                    parola += self.griglia[i][j]
                                    i += 1
                                if len(parola) >= 3:
                                    self.parole_verticali.append((parola, inizio, j))
                            else:
                                i += 1
                    
                    # Verifica che ogni parola sia valida
                    tutte_valide = True
                    for parola, _, _ in self.parole_orizzontali + self.parole_verticali:
                        if not self.dizionario.parola_esiste(parola):
                            tutte_valide = False
                            break
                    
                    if tutte_valide and len(self.parole_orizzontali) >= 2 and len(self.parole_verticali) >= 2:
                        return True
            
            return False
            
        except Exception as e:
            st.error(f"Errore: {e}")
            return False

# ==================== FUNZIONI ESPORTAZIONE ====================
def genera_txt(generatore, includi_lettere=True):
    output = io.StringIO()
    
    if includi_lettere:
        output.write("CRUCIVERBA 5x5 COMPILATO\n")
        output.write("="*30 + "\n\n")
        for riga in generatore.griglia:
            riga_str = "| "
            for cella in riga:
                if cella == '#':
                    riga_str += "█ | "
                else:
                    riga_str += f"{cella} | "
            output.write(riga_str + "\n")
    else:
        output.write("SCHEMA 5x5 VUOTO\n")
        output.write("="*30 + "\n\n")
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
    output.write("="*30 + "\n\n")
    
    if generatore.parole_orizzontali:
        output.write("ORIZZONTALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_orizzontali, 1):
            output.write(f"{i}. {parola}\n")
    
    if generatore.parole_verticali:
        output.write("\nVERTICALI:\n")
        for i, (parola, r, c) in enumerate(generatore.parole_verticali, len(generatore.parole_orizzontali)+1):
            output.write(f"{i}. {parola}\n")
    
    return output.getvalue()

# ==================== MAIN ====================
def main():
    st.set_page_config(
        page_title="Cruciverba 5x5 Perfetto",
        page_icon="🧩",
        layout="centered"
    )
    
    st.markdown("""
        <style>
        .stButton button {
            font-size: 24px !important;
            padding: 20px !important;
            width: 100%;
            background-color: #c41e3a;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        with st.spinner("Caricamento dizionario italiano..."):
            st.session_state.dizionario = DizionarioItaliano()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5 Perfetto")
    st.markdown("### Solo 3-5 caselle nere - Tutte parole vere")
    st.markdown("---")
    
    if st.button("🎲 GENERA CRUCIVERBA 5x5", use_container_width=True):
        with st.spinner("Generazione cruciverba perfetto..."):
            st.session_state.generatore = Cruciverba5x5(st.session_state.dizionario)
            if st.session_state.generatore.genera():
                st.success("✅ Cruciverba perfetto generato!")
            else:
                st.error("❌ Riprova - generazione")
    
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
        celle_nere = sum(1 for riga in st.session_state.generatore.griglia for cella in riga if cella == '#')
        totale_parole = len(st.session_state.generatore.parole_orizzontali) + len(st.session_state.generatore.parole_verticali)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole Totali", totale_parole)
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Caselle Nere", f"{celle_nere}/25 ({celle_nere*4}%)")
        
        # Esportazione
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button("📄 TXT Compilato", data=txt,
                             file_name=f"cruciverba_5x5_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with col2:
            txt2 = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button("📄 TXT Vuoto", data=txt2,
                             file_name=f"schema_5x5_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

if __name__ == "__main__":
    main()
