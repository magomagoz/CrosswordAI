import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreCruciverbaParziale:
    def __init__(self):
        self.dizionario = {}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        # Circa 22/25 caselle nere
        self.nere = [
            (0,4), (1,1), (1,7), (2,4),
            (3,0), (3,2), (3,6), (3,8),
            (5,1), (5,4), (5,7),
            (6,3), (6,5),
            (7,1), (7,4), (7,7),
            (9,0), (9,2), (9,6), (9,8),
            (10,4), (11,1), (11,7), (12,4)
        ]
        self.reset_griglia()

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        for r, c in self.nere:
            self.griglia[r][c] = '#'

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

    def get_segmenti(self):
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

    def tenta_riempimento(self, seg):
        tipo, r_i, c_i, lung = seg
        pattern = ""
        for i in range(lung):
            pattern += self.griglia[r_i + (i if tipo=='V' else 0)][c_i + (i if tipo=='O' else 0)]
        
        candidati = self.dizionario.get(lung, [])
        random.shuffle(candidati)
        
        for p in candidati[:200]:
            if all(pattern[i] == ' ' or pattern[i] == p[i] for i in range(lung)):
                for i in range(lung):
                    self.griglia[r_i + (i if tipo=='V' else 0)][c_i + (i if tipo=='O' else 0)] = p[i]
                return True
        return False

    def genera(self):
        self.reset_griglia()
        segmenti = self.get_segmenti()
        # Ordiniamo per lunghezza decrescente per dare priorità alle parole lunghe
        segmenti.sort(key=lambda x: x[3], reverse=True)
        
        completato = True
        for s in segmenti:
            if not self.tenta_riempimento(s):
                completato = False # Segna che non è perfetto, ma continua a riempire il resto
        return completato

    def render_html(self, mostra=True):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 2px solid black;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#000" if val == "#" else "#fff"
                # Se la cella è vuota in soluzione, mettiamo un grigio leggero
                txt = val if (mostra and val != "#") else ""
                display_txt = txt if txt != ' ' else "?" 
                html += f'<td style="width:35px;height:35px;border:1px solid #ddd;background:{bg};text-align:center;font-family:monospace;font-weight:bold;font-size:18px;">{display_txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba Live", layout="wide")
    st.markdown("<h2 style='text-align: center;'>🧩 Cruciverba $9 \\times 13$ Parziale</h2>", unsafe_allow_html=True)

    if 'motore' not in st.session_state:
        st.session_state.motore = MotoreCruciverbaParziale()
        st.session_state.caricato = False
        st.session_state.stato = "vuoto" # vuoto, parziale, completo

    if not st.session_state.caricato:
        if st.button("📚 CARICA VOCABOLARIO", use_container_width=True):
            with st.spinner("Caricamento..."):
                if st.session_state.motore.carica_parole():
                    st.session_state.caricato = True
                    st.rerun()
    else:
        if st.button("🎲 GENERA / AGGIORNA SCHEMA", use_container_width=True):
            with st.spinner("Elaborazione incroci..."):
                completato = st.session_state.motore.genera()
                st.session_state.stato = "completo" if completato else "parziale"
                if not completato:
                    st.info("⚠️ Riempimento parziale: alcuni incroci non hanno trovato parole adatte.")
                else:
                    st.success("✅ Schema completato con successo!")

    # Mostra sempre la griglia se è stato fatto almeno un tentativo
    if st.session_state.stato != "vuoto":
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🔍 Vista Soluzione (anche parziale)")
            st.write(st.session_state.motore.render_html(True), unsafe_allow_html=True)
            st.caption("I simboli '?' indicano celle che l'algoritmo non è riuscito a riempire.")
        with c2:
            st.markdown("### 📝 Schema da gioco")
            st.write(st.session_state.motore.render_html(False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
