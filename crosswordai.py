import streamlit as st
import requests
import random
from datetime import datetime
import io

# ==================== DIZIONARIO DA API IN TEMPO REALE ====================

class DizionarioAPIDedicata:
    def __init__(self):
        self.base_url = "https://api.vocabolario.it"  # Esempio
    
    def cerca_parole_per_pattern(self, pattern):
        """Cerca parole che corrispondono a un pattern"""
        # pattern esempio: "A???A" per parole di 5 lettere che iniziano e finiscono con A
        response = requests.get(f"{self.base_url}/cerca", params={
            'pattern': pattern,
            'lunghezza': 5,
            'lang': 'it'
        })
        return response.json()
    
    def _cerca_parole_per_pattern(self, pattern):
        """
        Cerca parole che corrispondono a un pattern usando API esterna
        Nota: In produzione useremmo un servizio dedicato come parole.vocabolario.it
        """
        # Simuliamo la ricerca con combinazioni casuali
        # In un'implementazione reale, qui chiameremmo un'API di ricerca
        lettere_comuni = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 
                         'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'Z']
        
        # Genera parole casuali e verifica se esistono
        for _ in range(50):  # Prova 50 combinazioni
            parola = ''.join(random.choice(lettere_comuni) for _ in range(5))
            if parola not in self.cache:
                if self._chiamata_api(parola):
                    self.cache[parola] = True
                    return parola
                else:
                    self.cache[parola] = False
        return None

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
            
            # Genera parola casuale che rispetta il pattern
            trovata = False
            for _ in range(100):  # 100 tentativi
                # Genera una parola di 5 lettere
                parola = [''] * 5
                # Metti le lettere fisse
                for pos, lett in pattern.items():
                    parola[pos] = lett
                # Completa le altre posizioni
                for i in range(5):
                    if parola[i] == '':
                        parola[i] = random.choice('ABCDEFGHILMNOPQRSTUVZ')
                
                parola_str = ''.join(parola)
                
                # Verifica se esiste
                if parola_str not in self.cache:
                    if self._chiamata_api(parola_str):
                        self.cache[parola_str] = True
                        verticali.append(parola_str)
                        trovata = True
                        break
                    else:
                        self.cache[parola_str] = False
            
            if not trovata:
                return None
        
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
            # Genera 3 parole orizzontali casuali
            orizzontali = []
            for _ in range(3):
                # Genera parola casuale
                parola = ''.join(random.choice('ABCDEFGHILMNOPQRSTUVZ') for _ in range(5))
                # Verifica se esiste
                if parola not in self.dizionario.cache:
                    if self.dizionario._chiamata_api(parola):
                        self.dizionario.cache[parola] = True
                    else:
                        self.dizionario.cache[parola] = False
                        return False
                elif not self.dizionario.cache[parola]:
                    return False
                orizzontali.append(parola)
            
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
        st.subheader("Cruciverba Compilato")
        st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        
        # Statistiche
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole Totali", "6")
        col2.metric("Orizzontali", "3")
        col3.metric("Verticali", "3")
        col4.metric("Caselle Nere", "4/25 (16%)")

if __name__ == "__main__":
    main()
