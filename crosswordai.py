import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreCruciverbaV3:
    def __init__(self):
        self.dizionario = {}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        # Circa 22 caselle nere distribuite per spezzare le parole
        self.nere = [
            (1,1), (1,4), (1,7),
            (3,0), (3,3), (3,5), (3,8),
            (5,2), (5,6),
            (6,4),
            (7,2), (7,6),
            (9,0), (9,3), (9,5), (9,8),
            (11,1), (11,4), (11,7),
            (12,2), (12,6), (0,4)
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

    def get_segmenti(self, orientamento="O"):
        """Trova gli spazi vuoti tra caselle nere o bordi"""
        segmenti = []
        if orientamento == "O":
            for r in range(ROWS):
                c = 0
                while c < COLS:
                    if self.griglia[r][c] == '#':
                        c += 1
                        continue
                    inizio = c
                    while c < COLS and self.griglia[r][c] != '#':
                        c += 1
                    lung = c - inizio
                    if lung > 1: segmenti.append(('O', r, inizio, lung))
        else:
            for c in range(COLS):
                r = 0
                while r < ROWS:
                    if self.griglia[r][c] == '#':
                        r += 1
                        continue
                    inizio = r
                    while r < ROWS and self.griglia[r][c] != '#':
                        r += 1
                    lung = r - inizio
                    if lung > 1: segmenti.append(('V', inizio, c, lung))
        return segmenti

    def riempi_segmento(self, tipo, r_o_inizio, c_o_inizio, lung):
        pattern = ""
        for i in range(lung):
            if tipo == 'O': pattern += self.griglia[r_o_inizio][c_o_inizio + i]
            else: pattern += self.griglia[r_o_inizio + i][c_o_inizio]
        
        candidati = self.dizionario.get(lung, [])
        random.shuffle(candidati)
        
        for p in candidati[:300]:
            if all(pattern[i] == ' ' or pattern[i] == p[i] for i in range(lung)):
                for i in range(lung):
                    if tipo == 'O': self.griglia[r_o_inizio][c_o_inizio + i] = p[i]
                    else: self.griglia[r_o_inizio + i][c_o_inizio] = p[i]
                return True
        return False

    def genera_completo(self):
        self.reset_griglia()
        # 1. Riempiamo prima i segmenti orizzontali lunghi
        seg_o = sorted(self.get_segmenti("O"), key=lambda x: x[3], reverse=True)
        for s in seg_o:
            if not self.riempi_segmento(*s): return False
        
        # 2. Riempiamo i verticali verificando gli incroci
        seg_v = sorted(self.get_segmenti("V"), key=lambda x: x[3], reverse=True)
        for s in seg_v:
            if not self.riempi_segmento(*s): return False
        return True

    def render_html(self, mostra=True):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 2px solid black;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#000" if val == "#" else "#fff"
                color = "#000"
                txt = val if (mostra and val != "#") else ""
                html += f'<td style="width:38px;height:38px;border:1px solid #999;background:{bg};text-align:center;font-family:sans-serif;font-weight:bold;color:{color};">{txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba Pro 9x13", layout="wide")
    st.markdown("<h2 style='text-align: center;'>🧩 Cruciverba $9 \\times 13$ (Vocabolario Esteso)</h2>", unsafe_allow_html=True)

    if 'motore' not in st.session_state:
        st.session_state.motore = MotoreCruciverbaV3()
        st.session_state.caricato = False
        st.session_state.pronto = False

    if not st.session_state.caricato:
        if st.button("📚 1. CARICA TUTTO IL VOCABOLARIO ITALIANO", use_container_width=True):
            with st.spinner("Caricamento lemmi..."):
                if st.session_state.motore.carica_parole():
                    st.session_state.caricato = True
                    st.rerun()
    else:
        if st.button("🎲 2. GENERA SCHEMA CON INCROCI", use_container_width=True):
            successo = False
            with st.spinner("Ricerca incroci ottimali (3, 5, 7, 9, 13 lettere)..."):
                for _ in range(25): # Più tentativi per la complessità aumentata
                    if st.session_state.motore.genera_completo():
                        successo = True
                        break
            if successo: st.session_state.pronto = True
            else: st.warning("Incrocio non riuscito. Clicca di nuovo per riprovare!")

    if st.session_state.pronto:
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🔓 Soluzione")
            st.write(st.session_state.motore.render_html(True), unsafe_allow_html=True)
        with c2:
            st.markdown("### 📝 Schema Vuoto")
            st.write(st.session_state.motore.render_html(False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
