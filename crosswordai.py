import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreDinamicoStepByStep:
    def __init__(self):
        self.dizionario = {}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_inserite = []

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
                # Filtriamo parole di lunghezza gestibile (3-7 lettere)
                if p.isalpha() and 3 <= len(p) <= 7:
                    lung = len(p)
                    if lung not in self.dizionario: self.dizionario[lung] = []
                    self.dizionario[lung].append(p)
            return True
        except: return False

    def inserisci_fisicamente(self, parola, r, c, orientamento):
        lung = len(parola)
        # 1. Inserisce le lettere
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            self.griglia[curr_r][curr_c] = parola[i]
        
        # 2. Mette le caselle nere di delimitazione
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
        
        self.parole_inserite.append(parola)

    def aggiungi_parola(self):
        # --- CASO 1: PRIMA PAROLA (Fissata per sicurezza) ---
        if not self.parole_inserite:
            lunghezza_start = 5
            p = random.choice(self.dizionario[lunghezza_start])
            # La piazziamo a metà altezza, centrata orizzontalmente
            r_start, c_start = 6, (COLS - lunghezza_start) // 2
            self.inserisci_fisicamente(p, r_start, c_start, 'O')
            return True, f"Prima parola inserita: {p}"

        # --- CASO 2: PAROLE SUCCESSIVE (Incrocio obbligatorio) ---
        lunghezze = [3, 4, 5, 6, 7]
        random.shuffle(lunghezze)
        
        for l in lunghezze:
            candidati = random.sample(self.dizionario[l], min(len(self.dizionario[l]), 300))
            for p in candidati:
                # Cerchiamo un incrocio su tutta la griglia
                for r in range(ROWS):
                    for c in range(COLS):
                        for o in ['O', 'V']:
                            if self.valida_incrocio(p, r, c, o):
                                self.inserisci_fisicamente(p, r, c, o)
                                return True, f"Incrociata parola: {p}"
        
        return False, "Nessun incrocio trovato. Prova a resettare o clicca di nuovo."

    def valida_incrocio(self, parola, r, c, orientamento):
        lung = len(parola)
        if orientamento == 'O' and c + lung > COLS: return False
        if orientamento == 'V' and r + lung > ROWS: return False
        
        ha_incrocio = False
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            cella = self.griglia[curr_r][curr_c]
            
            if cella == '#': return False
            if cella.isalpha():
                if cella != parola[i]: return False
                ha_incrocio = True
        
        return ha_incrocio

    def render_html(self):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 3px solid #000;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#000" if val == "#" else "#fff"
                txt = val if val not in ["#", " "] else ""
                html += f'<td style="width:40px;height:40px;border:1px solid #ccc;background:{bg};text-align:center;font-weight:bold;font-size:20px;color:black;">{txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Step-by-Step Builder", layout="wide")
    st.title("🧩 Builder Cruciverba $13 \\times 9$")

    if 'm' not in st.session_state:
        st.session_state.m = MotoreDinamicoStepByStep()
        st.session_state.caricato = False
        st.session_state.log = "Carica il dizionario."

    col1, col2 = st.columns([1, 2])

    with col1:
        if not st.session_state.caricato:
            if st.button("📚 CARICA DIZIONARIO", use_container_width=True):
                if st.session_state.m.carica_parole():
                    st.session_state.caricato = True
                    st.rerun()
        else:
            if st.button("➕ AGGIUNGI PAROLA", use_container_width=True):
                successo, msg = st.session_state.m.aggiungi_parola()
                st.session_state.log = msg
                st.rerun()
            
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.m.reset_griglia()
                st.session_state.log = "Reset effettuato."
                st.rerun()
        
        st.info(st.session_state.log)
        st.write(f"Parole: {', '.join(st.session_state.m.parole_inserite)}")

    with col2:
        st.markdown(st.session_state.m.render_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
