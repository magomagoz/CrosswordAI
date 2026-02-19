import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreCorazzato:
    def __init__(self):
        self.dizionario = {i: [] for i in range(2, 11)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []
        
        self.emergenza = [
            "CASA", "PANE", "SOLE", "MARE", "LIBRO", "GATTO", "MONTE", "STRADA", "AMORE", "CITTA",
            "UOMO", "DONNA", "VITA", "CUORE", "FIUME", "NOTTE", "ERBA", "MELA", "PORTA", "VINO"
        ]

    def reset_griglia(self):
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []

    def carica_parole(self):
        for p in self.emergenza:
            p = p.upper()
            if p not in self.set_parole:
                self.dizionario[len(p)].append(p)
                self.set_parole.add(p)
        
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                linee = res.text.splitlines()
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 10:
                        if p not in self.set_parole:
                            self.dizionario[len(p)].append(p)
                            self.set_parole.add(p)
        except: pass
        return True

    def salva_stato(self):
        """Salva lo stato corrente nello storico per l'UNDO"""
        stato_attuale = {
            'griglia': [r[:] for r in self.griglia],
            'parole_usate': set(self.parole_usate)
        }
        self.storico.append(stato_attuale)

    def inserisci_manuale(self, r, c, valore):
        """Inserisce un singolo carattere o casella nera cliccando"""
        self.salva_stato()
        self.griglia[r][c] = valore

    def inserisci(self, parola, r, c, orientamento):
        self.salva_stato()
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        
        if orientamento == 'O':
            if c - 1 >= 0 and self.griglia[r][c-1] == ' ': self.griglia[r][c-1] = '#'
            if c + lung < COLS and self.griglia[r][c+lung] == ' ': self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0 and self.griglia[r-1][c] == ' ': self.griglia[r-1][c] = '#'
            if r + lung < ROWS and self.griglia[r+lung][c] == ' ': self.griglia[r+lung][c] = '#'
        self.parole_usate.add(parola)

    def annulla(self):
        if self.storico:
            ultimo_stato = self.storico.pop()
            self.griglia = ultimo_stato['griglia']
            self.parole_usate = ultimo_stato['parole_usate']
            return True
        return False

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
        temp_griglia = [row[:] for row in self.griglia]
        lung = len(parola)
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            if temp_griglia[rr][cc].isalpha() and temp_griglia[rr][cc] != parola[i]: return False
            if temp_griglia[rr][cc] == '#': return False
            temp_griglia[rr][cc] = parola[i]

        check_orient = 'O' if orientamento == 'V' else 'V'
        for i in range(lung):
            rr, cc = (r+i, c) if orientamento == 'V' else (r, c+i)
            seg = self.estrai_segmento(temp_griglia, rr, cc, check_orient)
            if len(seg) > 1 and ' ' not in seg:
                if seg not in self.set_parole: return False
        return True

    def aggiungi_mossa(self):
        if not self.parole_usate:
            for lung in [7, 6, 5]:
                if self.dizionario[lung]:
                    p = random.choice(self.dizionario[lung])
                    self.inserisci(p, 6, (COLS - lung) // 2, 'O')
                    return True, f"Inizio con: {p}"
            return False, "Dizionario vuoto!"

        coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
        random.shuffle(coords)
        for r, c, o in coords:
            for l in [6, 5, 4, 3]:
                if not self.dizionario[l]: continue
                patt = ""
                ha_incrocio = False
                spazio_libero = True
                for i in range(l):
                    rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                    if rr >= ROWS or cc >= COLS or self.griglia[rr][cc] == '#':
                        spazio_libero = False; break
                    char = self.griglia[rr][cc]
                    if char.isalpha(): ha_incrocio = True
                    patt += char
                if not spazio_libero or not ha_incrocio: continue
                candidati = [p for p in self.dizionario[l] if p not in self.parole_usate and all(patt[j] == ' ' or patt[j] == p[j] for j in range(l))]
                random.shuffle(candidati)
                for p_cand in candidati[:20]:
                    if self.verifica_legalita(r, c, p_cand, o):
                        self.inserisci(p_cand, r, c, o)
                        return True, f"Aggiunta: {p_cand}"
        return False, "Nessun incrocio trovato."

def main():
    st.set_page_config(page_title="Cruciverba Pro", layout="centered")
    st.markdown("<h2 style='text-align: center;'>🧩 Builder Cruciverba 13x9</h2>", unsafe_allow_html=True)

    if 'm' not in st.session_state:
        st.session_state.m = MotoreCorazzato()
        st.session_state.caricato = False
        st.session_state.log = "Carica il dizionario."

    if not st.session_state.caricato:
        if st.button("📚 1. CARICA DIZIONARIO", use_container_width=True):
            st.session_state.m.carica_parole()
            st.session_state.caricato = True
            st.rerun()
    else:
        # --- SEZIONE CONTROLLI MANUALI ---
        with st.expander("🛠️ Strumenti Manuali", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                tipo_inserimento = st.radio("Cosa vuoi inserire?", ["Casella Nera ⚫", "Lettera ✍️"], horizontal=True)
            with c2:
                lettera = st.selectbox("Scegli lettera:", list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ"), index=1)

        # --- PULSANTI AZIONE ---
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ AUTO-AGGIUNGI", use_container_width=True):
                _, msg = st.session_state.m.aggiungi_mossa()
                st.session_state.log = msg
                st.rerun()
        with col2:
            if st.button("⬅️ UNDO", use_container_width=True):
                if st.session_state.m.annulla():
                    st.session_state.log = "Annullato."
                else:
                    st.warning("Vuoto.")
                st.rerun()
        with col3:
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.m.reset_griglia()
                st.session_state.log = "Reset."
                st.rerun()

        # --- GRIGLIA INTERATTIVA ---
        # Usiamo CSS per rendere i bottoni quadrati e simili a un cruciverba
        st.markdown("""
            <style>
            div.stButton > button {
                width: 100%;
                height: 45px;
                padding: 0px;
                font-weight: bold;
                border: 1px solid #ccc;
            }
            </style>
        """, unsafe_allow_html=True)

        for r in range(ROWS):
            cols = st.columns(COLS)
            for c in range(COLS):
                val = st.session_state.m.griglia[r][c]
                # Stile: Nero per '#', Bianco per lettere/vuoto
                btn_type = "primary" if val == "#" else "secondary"
                label = " " if val in ["#", " "] else val
                
                if cols[c].button(label, key=f"cell_{r}_{c}", type=btn_type):
                    if tipo_inserimento == "Casella Nera ⚫":
                        nuovo = "#" if val != "#" else " "
                        st.session_state.m.inserisci_manuale(r, c, nuovo)
                    else:
                        st.session_state.m.inserisci_manuale(r, c, lettera.strip() if lettera.strip() else " ")
                    st.rerun()

        st.info(f"Log: {st.session_state.log}")
        if st.session_state.m.parole_usate:
            st.write(f"**Parole inserite:** {', '.join(st.session_state.m.parole_usate)}")

if __name__ == "__main__":
    main()
