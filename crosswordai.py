import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreDinamico:
    def __init__(self):
        self.dizionario = {}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_inserite = []
        self.reset_griglia()

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_inserite = []

    def carica_parole(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=10)
            linee = res.text.splitlines()
            for l in linee:
                p = l.strip().upper()
                # Filtriamo parole che stiano nella griglia (max 11 per lasciare spazio alle nere)
                if p.isalpha() and 2 < len(p) <= (max(ROWS, COLS) - 2):
                    lung = len(p)
                    if lung not in self.dizionario: self.dizionario[lung] = []
                    self.dizionario[lung].append(p)
            return True
        except: return False

    def può_stare(self, parola, r, c, orientamento):
        lung = len(parola)
        
        # Controllo bordi e spazio per caselle nere (prima e dopo)
        if orientamento == 'O':
            if c + lung > COLS: return False
            # Controllo caselle nere adiacenti
            c_prima, c_dopo = c - 1, c + lung
            if c_prima >= 0 and self.griglia[r][c_prima].isalpha(): return False
            if c_dopo < COLS and self.griglia[r][c_dopo].isalpha(): return False
        else:
            if r + lung > ROWS: return False
            r_prima, r_dopo = r - 1, r + lung
            if r_prima >= 0 and self.griglia[r_prima][c].isalpha(): return False
            if r_dopo < ROWS and self.griglia[r_dopo][c].isalpha(): return False

        # Verifica sovrapposizione caratteri
        incrocio = False
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            cella = self.griglia[curr_r][curr_c]
            
            if cella == '#': return False # Non può sovrascrivere una nera
            if cella.isalpha():
                if cella != parola[i]: return False # Conflitto
                incrocio = True
        
        return incrocio if self.parole_inserite else True

    def inserisci(self, parola, r, c, orientamento):
        lung = len(parola)
        # Casella nera prima
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
            for i in range(lung): self.griglia[r][c+i] = parola[i]
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
            for i in range(lung): self.griglia[r+i][c] = parola[i]
        self.parole_inserite.append(parola)

    def aggiungi_parola(self):
        # Scegliamo una lunghezza a caso tra 3 e 7 per facilitare incroci
        lunghezze = [3, 4, 5, 6, 7]
        random.shuffle(lunghezze)
        
        for l in lunghezze:
            candidati = self.dizionario.get(l, [])
            random.shuffle(candidati)
            
            for p in candidati[:100]:
                # Cerchiamo una posizione
                posizioni = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
                random.shuffle(posizioni)
                
                for r, c, o in posizioni:
                    if self.può_stare(p, r, c, o):
                        self.inserisci(p, r, c, o)
                        return True, f"Aggiunta: {p}"
        return False, "Nessun incrocio trovato."

    def render_html(self):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 3px solid black;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#222" if val == "#" else "#fff"
                color = "#fff" if val == "#" else "#000"
                txt = val if val != "#" else ""
                html += f'<td style="width:40px;height:40px;border:1px solid #ccc;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:20px;">{txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Step-by-Step Builder", layout="wide")
    st.title("🧩 Costruttore Cruciverba Dinamico $13 \\times 9$")

    if 'motore' not in st.session_state:
        st.session_state.motore = MotoreDinamico()
        st.session_state.caricato = False
        st.session_state.msg = "Carica il dizionario per iniziare."

    col1, col2 = st.columns([1, 2])

    with col1:
        if not st.session_state.caricato:
            if st.button("📚 1. CARICA DIZIONARIO", use_container_width=True):
                if st.session_state.motore.carica_parole():
                    st.session_state.caricato = True
                    st.session_state.msg = "Dizionario pronto! Premi il tasto sotto."
                    st.rerun()
        else:
            if st.button("➕ AGGIUNGI UNA PAROLA", use_container_width=True):
                successo, m = st.session_state.motore.aggiungi_parola()
                st.session_state.msg = m
                st.rerun()
            
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.motore.reset_griglia()
                st.session_state.msg = "Griglia pulita."
                st.rerun()
        
        st.success(st.session_state.msg)
        st.write("**Parole inserite:**", len(st.session_state.motore.parole_inserite))
        st.write(", ".join(st.session_state.motore.parole_inserite))

    with col2:
        st.markdown(st.session_state.motore.render_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
