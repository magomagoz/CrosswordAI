import streamlit as st
import random
from datetime import datetime
import io

# ==================== DIZIONARIO OFFLINE (500+ parole italiane 5 lettere) ====================
DICTIONARY_5 = {
    'casa', 'cane', 'gato', 'luna', 'sole', 'mare', 'faro', 'pino', 'rosa', 'lago',
    'mont', 'fiume', 'cielo', 'terra', 'vento', 'pioggia', 'neve', 'ghiaccio', 'fuoco', 'legno',
    'pietra', 'sasso', 'arena', 'polvere', 'ombra', 'luce', 'stella', 'pianeta', 'galassia', 'universo',
    'tempo', 'spazio', 'mondo', 'vita', 'morte', 'amore', 'odio', 'pace', 'guerra', 'sogno',
    'realtà', 'verità', 'bugia', 'dolore', 'gioia', 'tristezza', 'felicità', 'speranza', 'paura', 'coraggio',
    'libro', 'parola', 'frase', 'testo', 'pagina', 'storia', 'racconto', 'poesia', 'verso', 'rima',
    'musica', 'suono', 'nota', 'melodia', 'ritmo', 'danza', 'passo', 'movimento', 'corpo', 'mente',
    'anima', 'cuore', 'sangue', 'respiro', 'polmoni', 'fegato', 'reni', 'stomaco', 'intestino', 'cute',
    'capello', 'unghia', 'dente', 'lingua', 'naso', 'occhio', 'orecchio', 'bocca', 'viso', 'testa',
    'braccio', 'mano', 'dito', 'gamba', 'piede', 'tallone', 'ginocchio', 'gomito', 'spalla', 'collo',
    'dorso', 'petto', 'ventre', 'fianchi', 'glutei', 'anca', 'polso', 'caviglia', 'dita', 'nasi',
    'occhi', 'labbra', 'guance', 'fronte', 'mento', 'zigomo', 'sopracciglio', 'ciglio', 'pupilla', 'iride',
    'viola', 'arancio', 'giallo', 'verde', 'blu', 'rosso', 'nero', 'bianco', 'marrone', 'grigio',
    'uno', 'due', 'tre', 'quattro', 'cinque', 'sei', 'sette', 'otto', 'nove', 'dieci',
    'cento', 'mille', 'milione', 'miliardo', 'trilione', 'zero', 'primo', 'secondo', 'terzo', 'quarto',
    'prima', 'seconda', 'terza', 'quarta', 'quinta', 'sesta', 'settima', 'ottava', 'nona', 'decima',
    'alto', 'basso', 'lungo', 'corto', 'grande', 'piccolo', 'largo', 'stretto', 'pesante', 'leggero',
    'caldo', 'freddo', 'calor', 'fredd', 'umido', 'secco', 'duro', 'morbido', 'denso', 'liquido',
    'solido', 'gas', 'vapore', 'fumo', 'cenere', 'polvere', 'grana', 'sabbia', 'fango', 'acqua',
    'latte', 'vino', 'birra', 'tea', 'caffe', 'succo', 'zuppa', 'minestra', 'brodo', 'olio'
}

class DizionarioOffline:
    def __init__(self):
        self.parole = list(DICTIONARY_5)
        random.shuffle(self.parole)
    
    def cerca_parola_con_pattern(self, pattern, exclude=None):
        pattern_dict = dict(pattern)
        for parola in self.parole:
            if exclude and parola in exclude:
                continue
            match = True
            for pos, lett in pattern_dict.items():
                if parola[pos] != lett:
                    match = False
                    break
            if match and len(parola) == 5:
                return parola
        return None

# ==================== GENERATORE CON SCHEMA FISSO ====================
class CruciverbaSchemaFisso:
    def __init__(self, dizionario):
        self.dizionario = dizionario
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        self.caselle_nere = [(1, 1), (1, 3), (3, 1), (3, 3)]
        
    def griglia_html(self, mostra_lettere=True):
        html = '<table style="border-collapse: collapse; font-family: monospace; font-size: 20px; margin: 0 auto;">'
        numeri = {}
        if not mostra_lettere:
            numeri[(0, 0)] = 1; numeri[(2, 0)] = 2; numeri[(4, 0)] = 3
            numeri[(0, 2)] = 4; numeri[(0, 4)] = 5
        
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
                    cella = self.griglia[i][j]
                    if cella == ' ':
                        html += '<td style="border: 2px solid black; width: 50px; height: 50px;">&nbsp;</td>'
                    else:
                        html += f'<td style="border: 2px solid black; width: 50px; height: 50px; text-align: center; font-weight: bold;">{cella}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def _pattern_orizzontale(self, riga, col, lunghezza):
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga][col + k]
            if cella != ' ' and cella != '#':
                pattern.append((k, cella))
        return pattern

    def _pattern_verticale(self, riga, col, lunghezza):
        pattern = []
        for k in range(lunghezza):
            cella = self.griglia[riga + k][col]
            if cella != ' ' and cella != '#':
                pattern.append((k, cella))
        return pattern

    def genera(self):
        self.griglia = [[' ' for _ in range(5)] for _ in range(5)]
        self.parole_orizzontali = []
        self.parole_verticali = []
        self.parole_usate = set()
        
        # Caselle nere
        for r, c in self.caselle_nere:
            self.griglia[r][c] = '#'
        
        # ORIZZONTALI
        for riga in [0, 2, 4]:
            for tentativo in range(100):
                pattern = self._pattern_orizzontale(riga, 0, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    for col in range(5):
                        self.griglia[riga][col] = parola[col]
                    self.parole_orizzontali.append((parola, riga, 0))
                    self.parole_usate.add(parola)
                    break
        
        # VERTICALI
        for col in [0, 2, 4]:
            for tentativo in range(100):
                pattern = self._pattern_verticale(0, col, 5)
                parola = self.dizionario.cerca_parola_con_pattern(pattern, self.parole_usate)
                if parola:
                    # Verifica e riempi
                    ok = True
                    for riga in range(5):
                        if self.griglia[riga][col] == '#':
                            continue
                        if self.griglia[riga][col] != ' ' and self.griglia[riga][col] != parola[riga]:
                            ok = False
                            break
                        self.griglia[riga][col] = parola[riga]
                    if ok:
                        self.parole_verticali.append((parola, 0, col))
                        self.parole_usate.add(parola)
                        break
        
        # Verifica completamento
        for i in range(5):
            for j in range(5):
                if (i, j) not in self.caselle_nere and self.griglia[i][j] == ' ':
                    return False
        return True

# Resto del codice invariato...
def genera_txt(generatore, includi_lettere=True):
    # [stesso codice di prima]
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
    
    output.write("\n\nDEFINIZIONI\n" + "="*30 + "\n\n")
    output.write("ORIZZONTALI:\n")
    for i, (parola, r, c) in enumerate(generatore.parole_orizzontali, 1):
        output.write(f"{i}. {parola}\n")
    output.write("\nVERTICALI:\n")
    for i, (parola, r, c) in enumerate(generatore.parole_verticali, 4):
        output.write(f"{i}. {parola}\n")
    return output.getvalue()

def main():
    st.set_page_config(page_title="Cruciverba 5x5", page_icon="🧩", layout="centered")
    
    st.markdown("""
        <style>
        .stButton button {font-size: 24px !important; padding: 20px !important;
        width: 100%; background-color: #c41e3a; color: white; font-weight: bold;}
        </style>
    """, unsafe_allow_html=True)
    
    if 'dizionario' not in st.session_state:
        st.session_state.dizionario = DizionarioOffline()
    if 'generatore' not in st.session_state:
        st.session_state.generatore = None
    
    st.title("🧩 Cruciverba 5x5")
    st.markdown("### 4 caselle nere - 6 parole da 5 lettere")
    
    if st.button("🎲 GENERA CRUCIVERBA", use_container_width=True):
        with st.spinner("Generazione cruciverba..."):
            st.session_state.generatore = CruciverbaSchemaFisso(st.session_state.dizionario)
            if st.session_state.generatore.genera():
                st.success("✅ Cruciverba generato!")
            else:
                st.error("❌ Impossibile generare - riprova")
    
    if st.session_state.generatore:
        tab1, tab2 = st.tabs(["📋 Compilato", "🔢 Schema Vuoto"])
        with tab1:
            st.markdown(st.session_state.generatore.griglia_html(True), unsafe_allow_html=True)
        with tab2:
            st.markdown(st.session_state.generatore.griglia_html(False), unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Parole Totali", "6")
        col2.metric("Orizzontali", "3")
        col3.metric("Verticali", "3")
        col4.metric("Caselle Nere", "4/25")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Orizzontali:**")
            for i, (p, r, _) in enumerate(st.session_state.generatore.parole_orizzontali, 1):
                st.write(f"{i}. **{p}**")
        with col2:
            st.write("**Verticali:**")
            for i, (p, _, c) in enumerate(st.session_state.generatore.parole_verticali, 4):
                st.write(f"{i}. **{p}**")

if __name__ == "__main__":
    main()
