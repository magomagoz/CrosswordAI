import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreUltraStabile:
    def __init__(self):
        self.dizionario = {i: [] for i in range(3, 10)}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_inserite = []
        # Parole di emergenza se il download fallisce
        self.fallback = ["CASA", "PANE", "SOLE", "MARE", "LIBRO", "GATTO", "MONTE", "STRADA", "AMORE", "CITTA"]

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_inserite = []

    def carica_parole(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                linee = res.text.splitlines()
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 3 <= len(p) <= 9:
                        self.dizionario[len(p)].append(p)
                return True
        except:
            pass
        # Se fallisce, usa fallback
        for p in self.fallback:
            self.dizionario[len(p)].append(p)
        return True

    def inserisci(self, parola, r, c, orientamento):
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        
        # Caselle nere
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
        self.parole_inserite.append(parola)

    def aggiungi_parola(self):
        # 1. PRIMA PAROLA
        if not self.parole_inserite:
            # Trova la prima lunghezza disponibile nel dizionario
            for l in [5, 4, 6, 3, 7]:
                if self.dizionario[l]:
                    p = random.choice(self.dizionario[l])
                    self.inserisci(p, 6, (COLS - l) // 2, 'O')
                    return True, f"Inizio con: {p}"
            return False, "Dizionario vuoto!"

        # 2. INCROCI
        coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
        random.shuffle(coords)
        
        lunghezze = [3, 4, 5, 6, 7]
        random.shuffle(lunghezze)

        for r, c, o in coords:
            for l in lunghezze:
                if not self.dizionario[l]: continue
                
                # Verifica spazio e incrocio esistente
                patt = ""
                ha_incrocio = False
                fuori_limiti = False
                
                for i in range(l):
                    rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                    if rr >= ROWS or cc >= COLS:
                        fuori_limiti = True; break
                    char = self.griglia[rr][cc]
                    if char == '#': fuori_limiti = True; break
                    if char.isalpha(): ha_incrocio = True
                    patt += char
                
                if fuori_limiti or not ha_incrocio: continue
                
                # Cerca parola compatibile
                candidati = [p for p in self.dizionario[l] if all(patt[i] == ' ' or patt[i] == p[i] for i in range(l))]
                if candidati:
                    self.inserisci(random.choice(candidati), r, c, o)
                    return True, f"Incrociato: {candidati[0]}"
        
        return False, "Nessun incrocio trovato."

    def render(self):
        html = '<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;border:2px solid #000;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                v = self.griglia[r][c]
                bg = "black" if v == "#" else "white"
                color = "white" if v == "#" else "black"
                disp = v if v not in ["#", " "] else ""
                html += f'<td style="width:35px;height:35px;border:1px solid #ccc;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:18px;">{disp}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba Builder", layout="centered")
    st.title("🧩 Builder Cruciverba $13 \\times 9$")

    if 'm' not in st.session_state:
        st.session_state.m = MotoreUltraStabile()
        st.session_state.caricato = False
        st.session_state.log = "Carica il dizionario."

    if not st.session_state.caricato:
        if st.button("📚 CARICA DIZIONARIO", use_container_width=True):
            st.session_state.m.carica_parole()
            st.session_state.caricato = True
            st.rerun()
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ AGGIUNGI PAROLA", use_container_width=True):
                _, msg = st.session_state.m.aggiungi_parola()
                st.session_state.log = msg
                st.rerun()
        with col2:
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.m.reset_griglia()
                st.session_state.log = "Griglia resettata."
                st.rerun()
        
        st.markdown(st.session_state.m.render(), unsafe_allow_html=True)
        st.caption(f"Log: {st.session_state.log}")
        st.write(f"Parole: {', '.join(st.session_state.m.parole_inserite)}")

if __name__ == "__main__":
    main()
