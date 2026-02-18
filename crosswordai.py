import streamlit as st
import requests
import random
from datetime import datetime
import io

# ==================== DIZIONARIO DA API IN TEMPO REALE ====================
class DizionarioAPI:
    def __init__(self):
        self.cache = {}  # Cache per evitare chiamate ripetute
        self.base_url = "https://api.dictionaryapi.dev/api/v2/entries/it/"
    
    def _chiamata_api(self, parola):
        """Verifica se una parola esiste tramite API gratuita"""
        try:
            url = f"{self.base_url}{parola.lower()}"
            response = requests.get(url, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def _cerca_parole_per_pattern(self, pattern):
        """
        Genera parole casuali che corrispondono a un pattern
        pattern: dizionario con {posizione: lettera}
        """
        lettere_comuni = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 
                         'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'Z']
        
        for _ in range(100):  # 100 tentativi
            # Genera parola di 5 lettere
            parola = [''] * 5
            
            # Metti le lettere fisse del pattern
            for pos, lett in pattern.items():
                if pos < 5:
                    parola[pos] = lett
            
            # Completa le altre posizioni
            for i in range(5):
                if parola[i] == '':
                    parola[i] = random.choice(lettere_comuni)
            
            parola_str = ''.join(parola)
            
            # Verifica se esiste (controlla cache o API)
            if parola_str in self.cache:
                if self.cache[parola_str]:
                    return parola_str
            else:
                if self._chiamata_api(parola_str):
                    self.cache[parola_str] = True
                    return parola_str
                else:
                    self.cache[parola_str] = False
        
        return None

    def genera_parole_orizzontali(self):
        """Genera 3 parole orizzontali valide"""
        orizzontali = []
        for _ in range(3):
            # Cerca una parola senza pattern fisso
            parola = self._cerca_parole_per_pattern({})
            if not parola:
                return None
            orizzontali.append(parola)
        return orizzontali
    
    def get_parole_per_incrocio(self, orizzontali):
        """Trova parole verticali che incrociano le orizzontali"""
        verticali = []
        
        for col in [0, 2, 4]:  # Colonne senza caselle nere
            # Costruisci il pattern delle lettere già fisse
            pattern = {}
            if col == 0:
                pattern = {0: orizzontali[0][0], 2: orizzontali[1][0], 4: orizzontali[2][0]}
            elif col == 2:
                pattern = {0: orizzontali[0][2], 2: orizzontali[1][2], 4: orizzontali[2][2]}
            elif col == 4:
                pattern = {0: orizzontali[0][4], 2: orizzontali[1][4], 4: orizzontali[2][4]}
            
            # Cerca parola che rispetta il pattern
            parola = self._cerca_parole_per_pattern(pattern)
            if not parola:
                return None
            verticali.append(parola)
        
        return verticali

# ==================== GENERATORE CON SCHEMA FISSO ====================
class CruciverbaSchemaFisso:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.caselle_nere = [(1, 1), (1, 3), (3, 1), (3, 3)]
        
    def griglia_html(self, mostra_lettere=True):
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 20px; margin: 0 auto;">'
        
        for i in range(5):
            html += '<tr>'
            for j in range(5):
                if (i, j) in self.caselle_nere:
                    html += '<td style="border: 2px solid black; width: 50px; height: 50px; background: black;">&nbsp;</td>'
                elif mostra_lettere:
                    html += f'<td style="border: 2px solid black; width: 50px; height: 50px; text-align: center; font-weight: bold;">{self.griglia[i][j]}</td>'
                else:
                    html += '<td style="border: 2px solid black; width: 50px; height: 50px;">&nbsp;</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def genera(self):
        """Genera cruciverba usando solo API"""
        try:
            # Genera 3 parole orizzontali
            orizzontali = self.dizionario.genera_parole_orizzontali()
            if not orizzontali:
                return False
            
            # Trova verticali che incrociano
            verticali = self.dizionario.get_parole_per_incrocio(orizzontali)
            if not verticali:
                return False
            
            # Costruisci griglia
            self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
            
            # Inserisci orizzontali
            for idx, parola in enumerate(orizzontali):
                riga = idx * 2
                for col in range(5):
                    self.griglia[riga][col] = parola[col]
            
            # Inserisci verticali
            for idx, parola in enumerate(verticali):
                col = idx * 2
                for riga in range(5):
                    if (riga, col) not in self.caselle_nere:
                        self.griglia[riga][col] = parola[riga]
            
            # Inserisci caselle nere
            for r, c in self.caselle_nere:
                self.griglia[r][c] = '#'
            
            self.parole_orizzontali = [(orizzontali[0], 0, 0), (orizzontali[1], 2, 0), (orizzontali[2], 4, 0)]
            self.parole_verticali = [(verticali[0], 0, 0), (verticali[1], 0, 2), (verticali[2], 0, 4)]
            
            return True
            
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
        for i in range(5):
            riga_str = "| "
            for j in range(5):
                if (i, j) in generatore.caselle_nere:
                    riga_str += "█ | "
                else:
                    riga_str += "  | "
            output.write(riga_str + "\n")
    
    # Definizioni
    output.write("\n\nDEFINIZIONI\n")
    output.write("="*30 + "\n\n")
    
    output.write("ORIZZONTALI:\n")
    for i, (parola, r, c) in enumerate(generatore.parole_orizzontali, 1):
        output.write(f"{i}. {parola}\n")
    
    output.write("\nVERTICALI:\n")
    for i, (parola, r, c) in enumerate(generatore.parole_verticali, 4):
        output.write(f"{i}. {parola}\n")
    
    return output.getvalue()

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
        st.session_state.dizionario = DizionarioAPI()
    
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5")
    st.markdown("### Parole verificate in tempo reale")
    st.markdown("Posizioni: B2, B4, D2, D4")
    
    if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
        with st.spinner("Generazione cruciverba con API..."):
            st.session_state.generatore = CruciverbaSchemaFisso(st.session_state.dizionario)
            if st.session_state.generatore.genera():
                st.success("✅ Cruciverba generato con successo!")
            else:
                st.error("❌ Riprova - clicca ancora")
    
    if st.session_state.generatore:
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📋 Compilato", "🔢 Schema Vuoto"])
        
        with tab1:
            st.subheader("Cruciverba Compilato")
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Schema da Riempire")
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        # Statistiche
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole Totali", "6")
        col2.metric("Orizzontali", "3")
        col3.metric("Verticali", "3")
        col4.metric("Caselle Nere", "4/25 (16%)")
        
        # Mostra le parole
        st.markdown("---")
        st.subheader("📚 Parole generate")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Orizzontali:**")
            for i, (parola, riga, _) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                st.write(f"{i}. Riga {riga+1}: **{parola}**")
        
        with col2:
            st.write("**Verticali:**")
            for i, (parola, _, col) in enumerate(st.session_state.generatore.parole_verticali, 4):
                st.write(f"{i}. Colonna {col+1}: **{parola}**")
        
        # Esportazione
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            txt = genera_txt(st.session_state.generatore, True)
            st.download_button("📄 TXT Compilato", data=txt,
                             file_name=f"cruciverba_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with col2:
            txt2 = genera_txt(st.session_state.generatore, False)
            st.download_button("📄 TXT Vuoto", data=txt2,
                             file_name=f"schema_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")

if __name__ == "__main__":
    main()
