import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreAvanzato:
    def __init__(self):
        self.dizionario = {i: [] for i in range(2, 11)}
        self.set_parole = set() # Per ricerca rapida esistenza
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.fallback = ["CASA", "PANE", "SOLE", "MARE", "LIBRO", "GATTO", "MONTE", "STRADA", "AMORE"]

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()

    def carica_parole(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                linee = res.text.splitlines()
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 10:
                        self.dizionario[len(p)].append(p)
                        self.set_parole.add(p)
                return True
        except: pass
        for p in self.fallback:
            self.dizionario[len(p)].append(p)
            self.set_parole.add(p)
        return True

    def verifica_legalita_incroci(self, r, c, parola, orientamento):
        """Controlla che i nuovi segmenti creati siano parole italiane valide"""
        temp_griglia = [r[:] for r in self.griglia]
        lung = len(parola)
        
        # Inserimento temporaneo
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            temp_griglia[rr][cc] = parola[i]

        # Controlla i segmenti perpendicolari creati
        check_orient = 'O' if orientamento == 'V' else 'V'
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            # Estrai il segmento che passa per (rr, cc)
            seg = self.estrai_segmento(temp_griglia, rr, cc, check_orient)
            if len(seg) > 1 and ' ' not in seg:
                if seg not in self.set_parole:
                    return False
        return True

    def estrai_segmento(self, griglia, r, c, orient):
        """Estrae la parola completa che passa per una coordinata"""
        res = ""
        if orient == 'O':
            # Vai a sinistra
            c_start = c
            while c_start > 0 and griglia[r][c_start-1] != '#': c_start -= 1
            # Vai a destra
            c_end = c
            while c_end < COLS - 1 and griglia[r][c_end+1] != '#': c_end += 1
            for j in range(c_start, c_end + 1): res += griglia[r][j]
        else:
            # Vai su
            r_start = r
            while r_start > 0 and griglia[r_start-1][c] != '#': r_start -= 1
            # Vai giù
            r_end = r
            while r_end < ROWS - 1 and griglia[r_end+1][c] != '#': r_end += 1
            for j in range(r_start, r_end + 1): res += griglia[j][c]
        return res

    def inserisci(self, parola, r, c, orientamento):
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        
        # Delimitazione con nere
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
        self.parole_usate.add(parola)

    def aggiungi_parola(self):
        # 1. Prima parola
        if not self.parole_usate:
            p = random.choice(self.dizionario[7])
            self.inserisci(p, 6, 1, 'O')
            return True, f"Inizio: {p}"

        # 2. Tentativo Incrocio Intelligente
        coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
        random.shuffle(coords)
        
        for r, c, o in coords:
            for l in [3, 4, 5, 6]:
                patt = ""
                ha_incrocio = False
                valido = True
                for i in range(l):
                    rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                    if rr >= ROWS or cc >= COLS or self.griglia[rr][cc] == '#':
                        valido = False; break
                    char = self.griglia[rr][cc]
                    if char.isalpha(): ha_incrocio = True
                    patt += char
                
                if not valido or not ha_incrocio: continue

                candidati = [p for p in self.dizionario[l] if p not in self.parole_usate and all(patt[j] == ' ' or patt[j] == p[j] for j in range(l))]
                
                for p_cand in candidati[:20]: # Controlla i primi 20 per velocità
                    if self.verifica_legalita_incroci(r, c, p_cand, o):
                        self.inserisci(p_cand, r, c, o)
                        return True, f"Inserito: {p_cand}"

        # 3. Se bloccato, prova a mettere una casella nera in un punto vuoto strategico
        for _ in range(5):
            br, bc = random.randint(0, ROWS-1), random.randint(0, COLS-1)
            if self.griglia[br][bc] == ' ':
                self.griglia[br][bc] = '#'
                return True, "Casella nera posizionata per sbloccare lo schema."
                
        return False, "Nessuna mossa valida trovata."

    def render(self):
        html = '<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;border:3px solid #000;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                v = self.griglia[r][c]
                bg = "#000" if v == "#" else "#fff"
                color = "#fff" if v == "#" else "#000"
                disp = v if v not in ["#", " "] else ""
                html += f'<td style="width:38px;height:38px;border:1px solid #999;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:18px;">{disp}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba AI", layout="centered")
    st.title("🧩 Builder Intelligente $13 \\times 9$")

    if 'm' not in st.session_state:
        st.session_state.m = MotoreAvanzato()
        st.session_state.caricato = False
        st.session_state.log = "Carica il dizionario."

    if not st.session_state.caricato:
        if st.button("📚 1. CARICA E INDICIZZA DIZIONARIO", use_container_width=True):
            st.session_state.m.carica_parole()
            st.session_state.caricato = True
            st.rerun()
    else:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ AGGIUNGI PAROLA / NERA", use_container_width=True):
                _, msg = st.session_state.m.aggiungi_parola()
                st.session_state.log = msg
                st.rerun()
        with c2:
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.m.reset_griglia()
                st.session_state.log = "Reset."
                st.rerun()
        
        st.markdown(st.session_state.m.render(), unsafe_allow_html=True)
        st.info(f"Log: {st.session_state.log}")
        st.write(f"Parole usate ({len(st.session_state.m.parole_usate)}): {', '.join(list(st.session_state.m.parole_usate)[-10:])}")

if __name__ == "__main__":
    main()
