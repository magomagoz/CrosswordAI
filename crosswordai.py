import streamlit as st
import random
from datetime import datetime
import io

# ==================== DIZIONARIO ITALIANO ====================
class DizionarioItaliano:
    def __init__(self):
        # Parole italiane vere di 5 lettere
        self.parole_5 = [
            "AMORE", "VITA", "MORTE", "TEMPO", "NOTTE", "GIORNO", "SOLE", "LUNA",
            "FIORE", "ALBERO", "ACQUA", "TERRA", "ARIA", "FUOCO", "PANE", "VINO",
            "LIBRO", "CANE", "GATTO", "CASA", "SCUOLA", "ESTATE", "INVERNO",
            "PRIMA", "DOPO", "BIANCO", "NERO", "ROSSO", "VERDE", "GIALLO",
            "GRANDE", "PICCOLO", "NUOVO", "VECCHIO", "DOLCE", "AMARO",
            "PORTA", "CARTA", "PENNA", "BANCO", "SEDIA", "TAVOLO", "LETTO",
            "MONTE", "MARE", "FIUME", "LAGO", "ISOLE", "PONTE", "STRADA",
            "SQUOLA", "TEATRO", "CINEMA", "MUSICA", "DANZA", "CANTO",
            "COLORE", "DISEGNO", "PITTURA", "FOTO", "LIBRO", "RIVISTA",
            "MEDICO", "DOTTORE", "INFERMIERE", "OSPEDALE", "FARMACIA",
            "PROFUMO", "SAPORE", "ODORE", "RUMORE", "SILENZIO", "VOCE"
        ]
        
        # Parole di 3 lettere (per completamento)
        self.parole_3 = ["RE", "VIA", "IRA", "ERA", "ORA", "DUE", "TRE", "SEI", "UNO"]
        
        self.tutte_parole = set(self.parole_5 + self.parole_3)
    
    def parola_esiste(self, parola):
        return parola.upper() in self.tutte_parole
    
    def get_parole_5(self, exclude=None):
        parole = self.parole_5.copy()
        if exclude:
            parole = [p for p in parole if p not in exclude]
        return parole

# ==================== GENERATORE CON SCHEMA FISSO ====================
class CruciverbaSchemaFisso:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        
        # Schema fisso: caselle nere in B2(0,1), B4(0,3), D2(2,1), D4(2,3)
        # Coordinate (riga, colonna) con indici 0-4
        self.caselle_nere = [(1,0), (3,0), (1,2), (3,2)]  # B2, B4, D2, D4
        
    def griglia_html(self, mostra_lettere=True):
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 20px; margin: 0 auto;">'
        
        # Numeri per definizioni (solo per schema vuoto)
        numeri = {}
        if not mostra_lettere:
            # Orizzontali: righe 0,2,4
            numeri[(0,0)] = 1
            numeri[(2,0)] = 2
            numeri[(4,0)] = 3
            # Verticali: colonne 0,2,4
            numeri[(0,0)] = 1  # Già presente
            numeri[(0,2)] = 4
            numeri[(0,4)] = 5
        
        for i in range(5):
            html += '<tr>'
            for j in range(5):
                if (i, j) in self.caselle_nere:
                    html += '<td style="border: 2px solid black; width: 50px; height: 50px; background: black;">&nbsp;</td>'
                elif not mostra_lettere and (i, j) in numeri:
                    html += f'<td style="border: 2px solid black; width: 50px; height: 50px; text-align: center; font-weight: bold; color: #c41e3a;">{numeri[(i, j)]}</td>'
                elif not mostra_lettere:
                    html += '<td style="border: 2px solid black; width: 50px; height: 50px;">&nbsp;</td>'
                else:
                    html += f'<td style="border: 2px solid black; width: 50px; height: 50px; text-align: center; font-weight: bold;">{self.griglia[i][j]}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def genera(self):
        """Genera il cruciverba con schema fisso"""
        # Parole orizzontali (righe 0, 2, 4)
        orizzontali = [
            self.dizionario.get_parole_5(),  # riga 0
            self.dizionario.get_parole_5(),  # riga 2
            self.dizionario.get_parole_5()   # riga 4
        ]
        
        # Prova diverse combinazioni
        for _ in range(100):  # 100 tentativi
            # Scegli 3 parole orizzontali diverse
            parole_scelte = []
            for i in range(3):
                if orizzontali[i]:
                    parola = random.choice(orizzontali[i])
                    orizzontali[i] = [p for p in orizzontali[i] if p != parola]
                    parole_scelte.append(parola)
                else:
                    parole_scelte.append(None)
            
            if None in parole_scelte:
                continue
            
            # Posiziona orizzontali
            self.griglia[0] = list(parole_scelte[0])  # riga 0
            self.griglia[2] = list(parole_scelte[1])  # riga 2
            self.griglia[4] = list(parole_scelte[2])  # riga 4
            
            # Inserisci caselle nere
            for r, c in self.caselle_nere:
                self.griglia[r][c] = '#'
            
            # Costruisci parole verticali
            verticali = []
            for col in [0, 2, 4]:  # colonne senza caselle nere
                parola = ""
                for riga in range(5):
                    if (riga, col) not in self.caselle_nere:
                        parola += self.griglia[riga][col]
                
                if len(parola) == 5:  # Deve essere 5 lettere
                    verticali.append(parola)
            
            # Verifica che tutte le verticali siano parole valide
            tutte_valide = True
            for parola in verticali:
                if not self.dizionario.parola_esiste(parola):
                    tutte_valide = False
                    break
            
            if tutte_valide:
                # Registra le parole
                self.parole_orizzontali = [
                    (parole_scelte[0], 0, 0),
                    (parole_scelte[1], 2, 0),
                    (parole_scelte[2], 4, 0)
                ]
                self.parole_verticali = [
                    (verticali[0], 0, 0),
                    (verticali[1], 0, 2),
                    (verticali[2], 0, 4)
                ]
                return True
        
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
    st.set_page_config(page_title="Cruciverba 5x5 Schema Fisso", page_icon="🧩", layout="centered")
    
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
    
    st.title("🧩 Cruciverba 5x5 Schema Fisso")
    st.markdown("### 4 caselle nere - 6 parole da 5 lettere")
    st.markdown("Posizioni fisse: B2, B4, D2, D4")
    
    if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
        with st.spinner("Generazione cruciverba..."):
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
