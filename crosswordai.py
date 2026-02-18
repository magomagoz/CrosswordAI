import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreCruciverbaResiliente:
    def __init__(self):
        self.dizionario = {i: [] for i in range(2, 11)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.emergenza = ["CASA", "PANE", "SOLE", "MARE", "VITA", "CUORE", "RE", "AL", "SI", "NO"]

    def carica_parole(self):
        # Carica backup e tenta download
        for p in self.emergenza:
            self.dizionario[len(p)].append(p.upper())
            self.set_parole.add(p.upper())
        
        try:
            res = requests.get("https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt", timeout=3)
            if res.status_code == 200:
                for l in res.text.splitlines():
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 10:
                        self.dizionario[len(p)].append(p)
                        self.set_parole.add(p)
        except: pass
        return True

    def verifica_legalita(self, r, c, parola, orientamento):
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            if rr >= ROWS or cc >= COLS: return False
            if self.griglia[rr][cc] == '#': return False
            if self.griglia[rr][cc].isalpha() and self.griglia[rr][cc] != parola[i]:
                return False
        return True

    def inserisci(self, parola, r, c, orientamento):
        for i in range(len(parola)):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        self.parole_usate.add(parola)

    def aggiungi_mossa(self):
        # 1. TENTA INCROCIO STANDARD (Parole 3-6 lettere)
        coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
        random.shuffle(coords)
        
        for r, c, o in coords:
            for l in [5, 4, 3]:
                if self.verifica_legalita(r, c, " " * l, o): # Controlla solo spazio
                    patt = ""
                    for i in range(l):
                        rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                        patt += self.griglia[rr][cc]
                    
                    if ' ' in patt and any(ch.isalpha() for ch in patt): # C'è un incrocio
                        candidati = [p for p in self.dizionario[l] if p not in self.parole_usate and all(patt[j] == ' ' or patt[j] == p[j] for j in range(l))]
                        if candidati:
                            self.inserisci(random.choice(candidati), r, c, o)
                            return True, f"Parola trovata: {candidati[0]}"

        # 2. SE NON CI SONO SOLUZIONI: GESTISCI STALLO (Casella Nera o Parola Corta)
        return self.gestisci_stallo()

    def gestisci_stallo(self):
        """Si attiva quando il sistema non trova più incroci standard"""
        for r in range(ROWS):
            for c in range(COLS):
                if self.griglia[r][c] == ' ':
                    # Opzione A: Metti una parola di 2 lettere se possibile
                    for p2 in [p for p in self.dizionario[2] if p not in self.parole_usate]:
                        if self.verifica_legalita(r, c, p2, 'O'):
                            self.inserisci(p2, r, c, 'O')
                            return True, f"Sblocco con parola corta: {p2}"
                    
                    # Opzione B: Casella Nera strategica
                    self.griglia[r][c] = '#'
                    return True, "Sblocco con casella nera (nessuna parola compatibile)."
        
        return False, "Griglia completata o bloccata."

    def render(self):
        html = '<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;border:3px solid #333;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                v = self.griglia[r][c]
                bg = "#000" if v == "#" else "#fff"
                color = "#fff" if v == "#" else "#000"
                html += f'<td style="width:35px;height:35px;border:1px solid #ccc;background:{bg};color:{color};text-align:center;font-weight:bold;">{v if v not in ["#"," "] else ""}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba AI")
    st.title("🧩 Builder con Risoluzione di Stallo")

    if 'm' not in st.session_state:
        st.session_state.m = MotoreCruciverbaResiliente()
        st.session_state.m.carica_parole()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ PROSSIMA MOSSA", use_container_width=True):
            _, msg = st.session_state.m.aggiungi_mossa()
            st.session_state.log = msg
            st.rerun()
    with col2:
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.m.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
            st.session_state.m.parole_usate = set()
            st.rerun()

    st.markdown(st.session_state.m.render(), unsafe_allow_html=True)
    if 'log' in st.session_state:
        st.caption(f"Azione: {st.session_state.log}")

if __name__ == "__main__":
    main()
