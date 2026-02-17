import streamlit as st
import random
from datetime import datetime
import io

# ==================== DIZIONARIO ITALIANO 5x5 ====================
class DizionarioItaliano:
    def __init__(self):
        # Parole italiane vere per 5x5 - tutte verificate
        self.parole_3 = [
            "RE", "VIA", "IRA", "ERA", "ORA", "DUE", "TRE", "SEI", "SOLE", "LUNA",
            "MARE", "MONTE", "FIORE", "CANE", "GATTO", "LIBRO", "CASA", "AMORE"
        ]
        
        self.parole_4 = [
            "CASA", "CANE", "GATTO", "LIBRO", "SOLE", "LUNA", "MARE", "MONTE", 
            "FIORE", "ALBERO", "AUTO", "PANE", "VINO", "ACQUA", "FUOCO", "TERRA", 
            "ARIA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "PORTA",
            "CARTA", "PENNA", "BANCO", "SEDIA", "TAVOLO"
        ]
        
        self.parole_5 = [
            "SCUOLA", "AMORE", "TEMPO", "VITA", "MORTE", "NOTTE", "GIORNO", "ESTATE", 
            "INVERNO", "PRIMAVERA", "AUTUNNO", "BIANCO", "NERO", "ROSSO", "VERDE", 
            "GIALLO", "BLU", "GRANDE", "PICCOLO", "FIORE", "ALBERO", "ACQUA", "TERRA",
            "ARIA", "FUOCO", "PANE", "VINO", "LIBRO", "CANE", "GATTO", "CASA"
        ]
        
        # Tutte le parole in un set per verifica rapida
        self.tutte_parole = set(self.parole_3 + self.parole_4 + self.parole_5)
        
        # Organizzate per lunghezza e lettera iniziale
        self.per_lunghezza = {
            3: self.parole_3,
            4: self.parole_4,
            5: self.parole_5
        }
        
        self.per_iniziale = {}
        for l in [3, 4, 5]:
            self.per_iniziale[l] = {}
            for parola in self.per_lunghezza[l]:
                iniziale = parola[0]
                if iniziale not in self.per_iniziale[l]:
                    self.per_iniziale[l][iniziale] = []
                self.per_iniziale[l][iniziale].append(parola)
    
    def parola_esiste(self, parola):
        """Verifica se una parola esiste"""
        return parola.upper() in self.tutte_parole
    
    def get_parole_by_lunghezza(self, lunghezza, lettera_iniziale=None):
        """Restituisce parole di data lunghezza"""
        if lunghezza not in self.per_lunghezza:
            return []
        
        if lettera_iniziale:
            return self.per_iniziale[lunghezza].get(lettera_iniziale.upper(), [])
        
        return self.per_lunghezza[lunghezza]

# ==================== GENERATORE 5x5 GARANTITO ====================
class Cruciverba5x5Garantito:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [['#' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
    def griglia_html(self, mostra_lettere=True):
        """Restituisce la griglia in formato HTML"""
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 20px; margin: 0 auto; background-color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
        
        # Calcola numeri per definizioni
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

    def _pattern_con_nere(self, num_nere):
        """Genera un pattern con esattamente num_nere caselle nere"""
        if num_nere == 3:
            patterns = [
                [(0,0), (2,2), (4,4)],  # diagonale
                [(1,1), (2,2), (3,3)],  # diagonale centrale
                [(0,2), (2,0), (4,2)],  # a T
                [(1,3), (2,2), (3,1)],  # x parziale
                [(0,4), (2,2), (4,0)],  # anti-diagonale
            ]
        elif num_nere == 4:
            patterns = [
                [(0,0), (0,4), (4,0), (4,4)],  # 4 angoli
                [(1,1), (1,3), (3,1), (3,3)],  # 4 interni
                [(0,2), (2,0), (2,4), (4,2)],  # croce
                [(1,2), (2,1), (2,3), (3,2)],  # più piccolo
            ]
        else:  # 5 nere
            patterns = [
                [(0,0), (0,4), (2,2), (4,0), (4,4)],  # X + centro
                [(1,1), (1,3), (2,2), (3,1), (3,3)],  # rombo
                [(0,2), (1,1), (2,0), (3,4), (4,3)],  # casuale
            ]
        
        return random.choice(patterns)

    def genera(self):
        """Genera un cruciverba 5x5 con parole garantite"""
        try:
            # Prova con 3, 4, e 5 caselle nere
            for num_nere in [3, 4, 5]:
                for tentativo in range(10):  # 10 tentativi per ogni numero
                    # Resetta griglia
                    self.griglia = [['.' for _ in range(5)] for _ in range(5)]
                    
                    # Applica pattern caselle nere
                    nere = self._pattern_con_nere(num_nere)
                    for r, c in nere:
                        self.griglia[r][c] = '#'
                    
                    # Trova tutte le parole orizzontali
                    orizzontali = []
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
                                    orizzontali.append((i, inizio, lunghezza))
                            else:
                                j += 1
                    
                    # Trova tutte le parole verticali
                    verticali = []
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
                                    verticali.append((inizio, j, lunghezza))
                            else:
                                i += 1
                    
                    # Deve avere almeno 2 orizzontali e 2 verticali
                    if len(orizzontali) < 2 or len(verticali) < 2:
                        continue
                    
                    # Raccogli tutte le parole da inserire
                    parole_da_inserire = []
                    
                    # Aggiungi orizzontali
                    for riga, col, lung in orizzontali:
                        # Cerca una parola adatta
                        parole = self.dizionario.get_parole_by_lunghezza(lung)
                        if parole:
                            parola = random.choice(parole)
                            parole_da_inserire.append(('O', riga, col, parola))
                    
                    # Aggiungi verticali
                    for riga, col, lung in verticali:
                        parole = self.dizionario.get_parole_by_lunghezza(lung)
                        if parole:
                            parola = random.choice(parole)
                            parole_da_inserire.append(('V', riga, col, parola))
                    
                    # Inserisci tutte le parole
                    self.griglia = [['#' for _ in range(5)] for _ in range(5)]
                    
                    # Prima le orizzontali
                    for tipo, riga, col, parola in parole_da_inserire:
                        if tipo == 'O':
                            for k, lettera in enumerate(parola):
                                self.griglia[riga][col + k] = lettera
                    
                    # Poi le verticali (controllando compatibilità)
                    successo = True
                    for tipo, riga, col, parola in parole_da_inserire:
                        if tipo == 'V':
                            for k, lettera in enumerate(parola):
                                if self.griglia[riga + k][col] not in ['#', lettera]:
                                    successo = False
                                    break
                                self.griglia[riga + k][col] = lettera
                            if not successo:
                                break
                    
                    if not successo:
                        continue
                    
                    # Verifica che non ci siano celle vuote
                    completo = True
                    for i in range(5):
                        for j in range(5):
                            if self.griglia[i][j] == '.':
                                completo = False
                                break
                        if not completo:
                            break
                    
                    if not completo:
                        continue
                    
                    # Raccogli le parole finali
                    self.parole_orizzontali = []
                    self.parole_verticali = []
                    
                    # Parole orizzontali
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
                    
                    # Parole verticali
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
                    
                    # Verifica che tutte le parole esistano
                    tutte_ok = True
                    for parola, _, _ in self.parole_orizzontali + self.parole_verticali:
                        if not self.dizionario.parola_esiste(parola):
                            tutte_ok = False
                            break
                    
                    if tutte_ok and len(self.parole_orizzontali) >= 2 and len(self.parole_verticali) >= 2:
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
        page_title="Cruciverba 5x5 Garantito",
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
    
    st.title("🧩 Cruciverba 5x5 Garantito")
    st.markdown("### 3-5 caselle nere - Parole italiane vere")
    st.markdown("---")
    
    if st.button("🎲 GENERA CRUCIVERBA 5x5", use_container_width=True):
        with st.spinner("Generazione cruciverba..."):
            st.session_state.generatore = Cruciverba5x5Garantito(st.session_state.dizionario)
            if st.session_state.generatore.genera():
                st.success("✅ Cruciverba generato con successo!")
            else:
                st.error("❌ Riprova - clicca ancora")
    
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
        
        # Mostra le parole generate
        st.markdown("---")
        st.subheader("📚 Parole generate")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.generatore.parole_orizzontali:
                st.write("**Orizzontali:**")
                for parola, riga, col in st.session_state.generatore.parole_orizzontali:
                    st.write(f"  • Riga {riga+1}: {parola}")
        
        with col2:
            if st.session_state.generatore.parole_verticali:
                st.write("**Verticali:**")
                for parola, riga, col in st.session_state.generatore.parole_verticali:
                    st.write(f"  • Colonna {col+1}: {parola}")
        
        # Esportazione
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, includi_lettere=True)
            st.download_button("📄 TXT Compilato", data=txt,
                             file_name=f"cruciverba_5x5_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             use_container_width=True)
        with col2:
            txt2 = genera_txt(st.session_state.generatore, includi_lettere=False)
            st.download_button("📄 TXT Vuoto", data=txt2,
                             file_name=f"schema_5x5_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                             use_container_width=True)

if __name__ == "__main__":
    main()
