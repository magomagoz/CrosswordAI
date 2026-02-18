import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreInterattivo:
    def __init__(self):
        self.dizionario = {}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        # Circa 22-25 caselle nere per creare segmenti definiti
        self.nere = [
            (0,4), (1,1), (1,7), (2,4),
            (3,0), (3,2), (3,6), (3,8),
            (5,1), (5,4), (5,7),
            (6,3), (6,5),
            (7,1), (7,4), (7,7),
            (9,0), (9,2), (9,6), (9,8),
            (10,4), (11,1), (11,7), (12,4)
        ]
        self.parole_inserite = []
        self.reset_griglia()

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        for r, c in self.nere:
            self.griglia[r][c] = '#'
        self.parole_inserite = []

    def carica_parole(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=10)
            linee = res.text.splitlines()
            for l in linee:
                p = l.strip().upper()
                if p.isalpha() and 2 < len(p) <= 13:
                    lung = len(p)
                    if lung not in self.dizionario: self.dizionario[lung] = []
                    self.dizionario[lung].append(p)
            return True
        except: return False

    def get_tutti_segmenti(self):
        segmenti = []
        # Orizzontali
        for r in range(ROWS):
            c = 0
            while c < COLS:
                if self.griglia[r][c] == '#':
                    c += 1
                    continue
                inizio = c
                while c < COLS and self.griglia[r][c] != '#':
                    c += 1
                if c - inizio > 1: segmenti.append(('O', r, inizio, c - inizio))
        # Verticali
        for c in range(COLS):
            r = 0
            while r < ROWS:
                if self.griglia[r][c] == '#':
                    r += 1
                    continue
                inizio = r
                while r < ROWS and self.griglia[r][c] != '#':
                    r += 1
                if r - inizio > 1: segmenti.append(('V', inizio, c, r - inizio))
        return segmenti

    def aggiungi_prossima_parola(self):
        segmenti = self.get_tutti_segmenti()
        # Filtriamo i segmenti che non sono ancora completi
        vuoti = []
        for s in segmenti:
            tipo, r_i, c_i, lung = s
            testo_attuale = ""
            for i in range(lung):
                testo_attuale += self.griglia[r_i + (i if tipo=='V' else 0)][c_i + (i if tipo=='O' else 0)]
            if ' ' in testo_attuale:
                vuoti.append((s, testo_attuale))
        
        if not vuoti:
            return False, "Griglia completata!"

        # Mischiamo per non andare sempre in ordine
        random.shuffle(vuoti)
        
        for (tipo, r_i, c_i, lung), pattern in vuoti:
            candidati = self.dizionario.get(lung, [])
            random.shuffle(candidati)
            
            for p in candidati[:500]:
                if all(pattern[i] == ' ' or pattern[i] == p[i] for i in range(lung)):
                    # Posizioniamo la parola
                    for i in range(lung):
                        self.griglia[r_i + (i if tipo=='V' else 0)][c_i + (i if tipo=='O' else 0)] = p[i]
                    self.parole_inserite.append(p)
                    return True, f"Inserita parola: {p}"
        
        return False, "Nessuna parola trovata per gli incroci attuali."

    def render_html(self):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 3px solid black;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#000" if val == "#" else "#fff"
                txt = val if val not in ["#", " "] else ""
                html += f'<td style="width:40px;height:40px;border:1px solid #444;background:{bg};text-align:center;font-family:sans-serif;font-weight:bold;font-size:20px;">{txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba Builder", layout="wide")
    st.markdown("<h2 style='text-align: center;'>🧩 Costruttore di Cruciverba Passo-Passo</h2>", unsafe_allow_html=True)

    if 'builder' not in st.session_state:
        st.session_state.builder = MotoreInterattivo()
        st.session_state.caricato = False
        st.session_state.log = "Inizia caricando il dizionario."

    col_dx, col_sx = st.columns([1, 2])

    with col_dx:
        st.subheader("Controlli")
        if not st.session_state.caricato:
            if st.button("📚 1. CARICA DIZIONARIO", use_container_width=True):
                if st.session_state.builder.carica_parole():
                    st.session_state.caricato = True
                    st.session_state.log = "Dizionario caricato. Clicca per aggiungere la prima parola."
                    st.rerun()
        else:
            if st.button("➕ AGGIUNGI PROSSIMA PAROLA", use_container_width=True):
                successo, msg = st.session_state.builder.aggiungi_prossima_parola()
                st.session_state.log = msg
                st.rerun()
            
            if st.button("🔄 RESET GRIGLIA", use_container_width=True):
                st.session_state.builder.reset_griglia()
                st.session_state.log = "Griglia resettata."
                st.rerun()
        
        st.info(f"**Stato:** {st.session_state.log}")
        
        if st.session_state.builder.parole_inserite:
            st.write("**Parole nello schema:**")
            st.write(", ".join(st.session_state.builder.parole_inserite))

    with col_sx:
        st.markdown(st.session_state.builder.render_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
