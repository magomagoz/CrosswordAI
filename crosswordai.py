import streamlit as st
import random
from datetime import datetime
import io

# ==================== DIZIONARIO ITALIANO ====================
class DizionarioItaliano:
    def __init__(self):
        # Parole italiane vere organizzate per lunghezza
        self.parole = {
            3: ["RE", "VIA", "IRA", "ERA", "ORA", "DUE", "TRE", "SEI", "UNO", "NON", "MAI", "PIU"],
            4: ["CASA", "CANE", "SOLE", "LUNA", "MARE", "DOPO", "SOLE", "LUNA", 
                "AUTO", "PANE", "VINO", "ARIA", "VITA"],
            5: ["MORTE", "TEMPO", "PRIMA", "FIORE", "ACQUA", "TERRA",
                "FUOCO", "AMORE", "NOTTE", "ROSSO", "VERDE",
        }
        
        # Per ricerca rapida
        self.tutte_parole = set()
        for lista in self.parole.values():
            self.tutte_parole.update(lista)
    
    def parola_esiste(self, parola):
        return parola.upper() in self.tutte_parole
    
    def get_parole_by_lunghezza(self, lunghezza, inizia_con=None):
        if lunghezza not in self.parole:
            return []
        parole = self.parole[lunghezza]
        if inizia_con:
            parole = [p for p in parole if p.startswith(inizia_con.upper())]
        return parole

# ==================== GENERATORE A PARTIRE DA PAROLA INIZIALE ====================
class CruciverbaCostruttore:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [['#' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
    def griglia_html(self, mostra_lettere=True):
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 20px; margin: 0 auto;">'
        
        # Calcola numeri
        numeri = {}
        if not mostra_lettere:
            num = 1
            for i in range(5):
                for j in range(5):
                    if self.griglia[i][j] != '#':
                        inizio_oriz = (j == 0 or self.griglia[i][j-1] == '#') and (j < 4 and self.griglia[i][j+1] != '#')
                        inizio_vert = (i == 0 or self.griglia[i-1][j] == '#') and (i < 4 and self.griglia[i+1][j] != '#')
                        if inizio_oriz or inizio_vert:
                            if (i, j) not in numeri:
                                numeri[(i, j)] = num
                                num += 1
        
        for i in range(5):
            html += '<tr>'
            for j in range(5):
                cella = self.griglia[i][j]
                if cella == '#':
                    html += '<td style="border: 2px solid black; width: 50px; height: 50px; background: black;">&nbsp;</td>'
                elif not mostra_lettere and (i, j) in numeri:
                    html += f'<td style="border: 2px solid black; width: 50px; height: 50px; text-align: center; font-weight: bold; color: #c41e3a;">{numeri[(i, j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid black; width: 50px; height: 50px;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 2px solid black; width: 50px; height: 50px; text-align: center; font-weight: bold;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def _posiziona_parola_iniziale(self):
        """Sceglie e posiziona la parola iniziale"""
        parole_5 = self.dizionario.get_parole_by_lunghezza(5)
        if not parole_5:
            return None
        
        parola = random.choice(parole_5)
        riga = 2  # Riga centrale
        col = 0   # Parte da sinistra
        
        # Inserisci
        for k, lettera in enumerate(parola):
            self.griglia[riga][col + k] = lettera
        
        self.parole_orizzontali.append((parola, riga, col))
        return parola, riga, col

    def _costruisci_verticali(self, parola_iniziale, riga, col_inizio):
        """Costruisce parole verticali a partire dalla parola iniziale"""
        for k, lettera in enumerate(parola_iniziale):
            col = col_inizio + k
            
            # Trova spazio verticale
            spazio_su = 0
            while riga - spazio_su - 1 >= 0 and self.griglia[riga - spazio_su - 1][col] == '#':
                spazio_su += 1
            
            spazio_giu = 0
            while riga + spazio_giu + 1 < 5 and self.griglia[riga + spazio_giu + 1][col] == '#':
                spazio_giu += 1
            
            lunghezza_tot = spazio_su + 1 + spazio_giu
            
            if lunghezza_tot >= 3:
                # Cerca parole verticali che hanno questa lettera nella posizione giusta
                for lung in range(3, lunghezza_tot + 1):
                    parole = self.dizionario.get_parole_by_lunghezza(lung)
                    for parola in parole:
                        # Trova la posizione della lettera nella parola
                        for pos, lett in enumerate(parola):
                            if lett == lettera:
                                # Calcola la riga di inizio
                                riga_inizio = riga - pos
                                if riga_inizio >= 0 and riga_inizio + lung <= 5:
                                    # Verifica che lo spazio sia libero
                                    compatibile = True
                                    for vk in range(lung):
                                        cella = self.griglia[riga_inizio + vk][col]
                                        if cella != '#' and cella != parola[vk]:
                                            compatibile = False
                                            break
                                    
                                    if compatibile:
                                        # Inserisci
                                        for vk, lett_v in enumerate(parola):
                                            self.griglia[riga_inizio + vk][col] = lett_v
                                        self.parole_verticali.append((parola, riga_inizio, col))
                                        break
                        else:
                            continue
                        break

    def _aggiungi_altre_orizzontali(self):
        """Aggiunge altre parole orizzontali dove possibile"""
        for riga in range(5):
            col = 0
            while col < 5:
                if self.griglia[riga][col] == '#':
                    col += 1
                    continue
                
                # Trova spazio orizzontale
                inizio = col
                while col < 5 and self.griglia[riga][col] != '#':
                    col += 1
                lunghezza = col - inizio
                
                if lunghezza >= 3:
                    # Costruisci pattern delle lettere già presenti
                    lettere_fisse = {}
                    for k in range(lunghezza):
                        cella = self.griglia[riga][inizio + k]
                        if cella != '#':
                            lettere_fisse[k] = cella
                    
                    # Cerca parola compatibile
                    for lung in range(lunghezza, 2, -1):
                        parole = self.dizionario.get_parole_by_lunghezza(lung)
                        for parola in parole:
                            match = True
                            for pos, lett in lettere_fisse.items():
                                if pos < lung and parola[pos] != lett:
                                    match = False
                                    break
                            if match:
                                # Verifica che non sia già usata
                                if parola not in [p for p,_,_ in self.parole_orizzontali]:
                                    for k, lett in enumerate(parola):
                                        self.griglia[riga][inizio + k] = lett
                                    self.parole_orizzontali.append((parola, riga, inizio))
                                    break
                        break

    def genera(self):
        """Genera il cruciverba partendo da una parola iniziale"""
        try:
            # Pulisci griglia
            self.griglia = [['#' for _ in range(5)] for _ in range(5)]
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # Passo 1: Posiziona parola iniziale
            risultato = self._posiziona_parola_iniziale()
            if not risultato:
                return False
            
            parola_iniziale, riga, col_inizio = risultato
            
            # Passo 2: Costruisci verticali
            self._costruisci_verticali(parola_iniziale, riga, col_inizio)
            
            # Passo 3: Aggiungi altre orizzontali
            self._aggiungi_altre_orizzontali()
            
            # Passo 4: Raccogli tutte le parole finali
            self.parole_orizzontali = []
            self.parole_verticali = []
            
            # Orizzontali
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
            
            # Verticali
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
            
            # Verifica che tutte le parole siano valide
            tutte_ok = True
            for parola, _, _ in self.parole_orizzontali + self.parole_verticali:
                if not self.dizionario.parola_esiste(parola):
                    tutte_ok = False
                    break
            
            return tutte_ok and len(self.parole_verticali) >= 2
            
        except Exception as e:
            return False

# ==================== MAIN ====================
def main():
    st.set_page_config(page_title="Cruciverba 5x5", page_icon="🧩", layout="centered")
    
    st.markdown("""
        <style>
        .stButton button {
            font-size: 24px !important;
            padding: 20px !important;
            width: 100%;
            background-color: #c41e3a;
            color: white;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioItaliano()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5")
    st.markdown("### Costruito da parola iniziale")
    
    if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
        with st.spinner("Costruzione cruciverba..."):
            for _ in range(10):  # 10 tentativi
                st.session_state.generatore = CruciverbaCostruttore(st.session_state.dizionario)
                if st.session_state.generatore.genera():
                    st.success("✅ Cruciverba generato!")
                    break
            else:
                st.error("❌ Riprova")
    
    if st.session_state.generatore:
        st.markdown("---")
        tab1, tab2 = st.tabs(["📋 Compilato", "🔢 Vuoto"])
        
        with tab1:
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        with tab2:
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        # Statistiche
        tot = len(st.session_state.generatore.parole_orizzontali) + len(st.session_state.generatore.parole_verticali)
        nere = sum(1 for r in st.session_state.generatore.griglia for c in r if c == '#')
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole", tot)
        col2.metric("Orizzontali", len(st.session_state.generatore.parole_orizzontali))
        col3.metric("Verticali", len(st.session_state.generatore.parole_verticali))
        col4.metric("Caselle Nere", f"{nere}/25 ({nere*4}%)")

if __name__ == "__main__":
    main()
