import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreDefinitivo:
    def __init__(self):
        # Inizializza con liste vuote per ogni lunghezza
        self.dizionario = {i: [] for i in range(2, 11)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        
        # Parole di emergenza integrate (Garantiscono il funzionamento sempre)
        self.backup = [
            "CASA", "PANE", "SOLE", "MARE", "LIBRO", "GATTO", "MONTE", "STRADA", "AMORE", 
            "CITTA", "UOMO", "DONNA", "VITA", "CUORE", "FIUME", "NOTTE", "ERBA", "MELA",
            "PORTA", "VINO", "ARTE", "MARE", "TAVOLO", "SEDIA", "PIANO", "CARTA"
        ]

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()

    def carica_parole(self):
        # Proviamo diverse sorgenti per il dizionario
        urls = [
            "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt",
            "https://raw.githubusercontent.com/dofine/ita-wordlist/master/parole.txt"
        ]
        
        successo = False
        for url in urls:
            try:
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    linee = res.text.splitlines()
                    for l in linee:
                        p = l.strip().upper()
                        if p.isalpha() and 2 <= len(p) <= 10:
                            self.dizionario[len(p)].append(p)
                            self.set_parole.add(p)
                    successo = True
                    break
            except:
                continue
        
        # Aggiungiamo sempre il backup per sicurezza
        for p in self.backup:
            if p not in self.set_parole:
                self.dizionario[len(p)].append(p)
                self.set_parole.add(p)
        return True

    def estrai_segmento(self, griglia, r, c, orient):
        res = ""
        if orient == 'O':
            c_start = c
            while c_start > 0 and griglia[r][c_start-1] != '#': c_start -= 1
            c_end = c
            while c_end < COLS - 1 and griglia[r][c_end+1] != '#': c_end += 1
            for j in range(c_start, c_end + 1): res += griglia[r][j]
        else:
            r_start = r
            while r_start > 0 and griglia[r_start-1][c] != '#': r_start -= 1
            r_end = r
            while r_end < ROWS - 1 and griglia[r_end+1][c] != '#': r_end += 1
            for j in range(r_start, r_end + 1): res += griglia[j][c]
        return res

    def verifica_legalita(self, r, c, parola, orientamento):
        temp_griglia = [r[:] for r in self.griglia]
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            temp_griglia[rr][cc] = parola[i]

        check_orient = 'O' if orientamento == 'V' else 'V'
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            seg = self.estrai_segmento(temp_griglia, rr, cc, check_orient)
            if len(seg) > 1 and ' ' not in seg:
                if seg not in self.set_parole:
                    return False
        return True

    def inserisci(self, parola, r, c, orientamento):
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        
        # Aggiunge nere di contorno
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
        self.parole_usate.add(parola)

    def aggiungi_mossa(self):
        # 1. Caso base: prima parola
        if not self.parole_usate:
            lunghezze = [7, 6, 5, 4]
            for l in lunghezze:
                if self.dizionario[l]:
                    p = random.choice(self.dizionario[l])
                    self.inserisci(p, 6, (COLS-l)//2, 'O')
                    return True, f"Partenza: {p}"

        # 2. Ricerca incrocio
        coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
        random.shuffle(coords)
        
        for r, c, o in coords:
            for l in [3, 4, 5, 6]:
                if not self.dizionario[l]: continue
                
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
                random.shuffle(candidati)
                
                for p_cand in candidati[:15]:
                    if self.verifica_legalita(r, c, p_cand, o):
                        self.inserisci(p_cand, r, c, o)
                        return True, f"Incrocio: {p_cand}"

        # 3. Fallback: Casella nera
        for _ in range(10):
            br, bc = random.randint(0, ROWS-1), random.randint(0, COLS-1)
            if self.griglia[br][bc] == ' ':
                self.griglia[br][bc] = '#'
                return True, "Blocco nero inserito."
                
        return False, "Fine spazio disponibile."

    def render(self):
        html = '<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;border:3px solid #000;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                v = self.griglia[r][c]
                bg = "#111" if v == "#" else "#fff"
                color = "#fff" if v == "#" else "#000"
                disp = v if v not in ["#", " "] else ""
                html += f'<td style="width:38px;height:38px;border:1px solid #aaa;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:19px;">{disp}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba Builder", layout="centered")
    st.markdown("<h2 style='text-align: center;'>🧩 Builder Cruciverba 13x9</h2>", unsafe_allow_html=True)

    if 'm' not in st.session_state:
        st.session_state.m = MotoreDefinitivo()
        st.session_state.caricato = False
        st.session_state.log = "Carica il dizionario per iniziare."

    if not st.session_state.caricato:
        if st.button("📚 CARICA DIZIONARIO (WEB + BACKUP)", use_container_width=True):
            st.session_state.m.carica_parole()
            st.session_state.caricato = True
            st.rerun()
    else:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ AGGIUNGI (PAROLA O NERA)", use_container_width=True):
                _, msg = st.session_state.m.aggiungi_mossa()
                st.session_state.log = msg
                st.rerun()
        with c2:
            if st.button("🔄 RICOMINCIA DA CAPO", use_container_width=True):
                st.session_state.m.reset_griglia()
                st.session_state.log = "Schema pulito."
                st.rerun()
        
        st.markdown(st.session_state.m.render(), unsafe_allow_html=True)
        st.info(f"Stato: {st.session_state.log}")
        st.write(f"Parole nello schema: {len(st.session_state.m.parole_usate)}")

if __name__ == "__main__":
    main()
