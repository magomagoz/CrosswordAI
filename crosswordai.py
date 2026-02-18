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
            temp_diz = {}
            for l in linee:
                p = l.strip().upper()
                if p.isalpha() and 3 <= len(p) <= 9:
                    lung = len(p)
                    if lung not in temp_diz: temp_diz[lung] = []
                    temp_diz[lung].append(p)
            self.dizionario = temp_diz
            return True if self.dizionario else False
        except:
            return False

    def inserisci_fisicamente(self, parola, r, c, orientamento):
        lung = len(parola)
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            self.griglia[curr_r][curr_c] = parola[i]
        
        # Aggiunge caselle nere ai bordi della parola
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
        
        self.parole_inserite.append(parola)

    def aggiungi_parola(self):
        if not self.dizionario:
            return False, "Dizionario vuoto! Caricalo prima."

        # --- PRIMA PAROLA ---
        if not self.parole_inserite:
            # Cerca una lunghezza disponibile partendo da 7 a scendere
            for l_start in [7, 6, 5, 4, 3]:
                if l_start in self.dizionario:
                    p = random.choice(self.dizionario[l_start])
                    r_start, c_start = ROWS // 2, (COLS - l_start) // 2
                    self.inserisci_fisicamente(p, r_start, c_start, 'O')
                    return True, f"Inizio con: {p}"
            return False, "Nessuna parola adatta trovata nel dizionario."

        # --- PAROLE SUCCESSIVE ---
        # Prova lunghezze diverse per trovare un incrocio
        lunghezze_disponibili = list(self.dizionario.keys())
        random.shuffle(lunghezze_disponibili)
        
        for lung in lunghezze_disponibili:
            candidati = random.sample(self.dizionario[lung], min(len(self.dizionario[lung]), 100))
            for p in candidati:
                # Scansione casuale della griglia per trovare un incrocio
                coords = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
                random.shuffle(coords)
                for r, c, o in coords:
                    if self.valida_incrocio(p, r, c, o):
                        self.inserisci_fisicamente(p, r, c, o)
                        return True, f"Incrociato: {p}"
        
        return False, "Nessun incrocio trovato."

    def valida_incrocio(self, parola, r, c, orientamento):
        lung = len(parola)
        if orientamento == 'O':
            if c + lung > COLS: return False
            # Verifica che non ci siano lettere adiacenti che corrompono altre parole
            if c > 0 and self.griglia[r][c-1].isalpha(): return False
            if c + lung < COLS and self.griglia[r][c+lung].isalpha(): return False
        else:
            if r + lung > ROWS: return False
            if r > 0 and self.griglia[r-1][c].isalpha(): return False
            if r + lung < ROWS and self.griglia[r+lung][c].isalpha(): return False
        
        ha_incrocio = False
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            cella = self.griglia[curr_r][curr_c]
            
            if cella == '#': return False # Non può sovrascrivere una nera
            if cella.isalpha():
                if cella != parola[i]: return False # Conflitto
                ha_incrocio = True # Punto di incrocio valido
            else:
                # Se la cella è vuota, controlla che i vicini non siano lettere (evita parole attaccate)
                if orientamento == 'O':
                    if (curr_r > 0 and self.griglia[curr_r-1][curr_c].isalpha()) or \
                       (curr_r < ROWS-1 and self.griglia[curr_r+1][curr_c].isalpha()):
                        # Eccezione: va bene se è proprio l'incrocio che stiamo verificando
                        pass 
        return ha_incrocio

    def render_html(self):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 2px solid #333;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#222" if val == "#" else "#fff"
                color = "#fff" if val == "#" else "#000"
                txt = val if val not in ["#", " "] else ""
                html += f'<td style="width:40px;height:40px;border:1px solid #ccc;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:20px;">{txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba 13x9 Builder", layout="wide")
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
                    st.success("Dizionario caricato!")
                    st.rerun()
                else:
                    st.error("Errore nel caricamento del dizionario.")
        else:
            if st.button("➕ AGGIUNGI PAROLA", use_container_width=True):
                successo, msg = st.session_state.m.aggiungi_parola()
                st.session_state.log = msg
                st.rerun()
            
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.m.reset_griglia()
                st.session_state.log = "Griglia resettata."
                st.rerun()
        
        st.info(f"**Log:** {st.session_state.log}")
        st.write(f"**Parole inserite:** {', '.join(st.session_state.m.parole_inserite)}")

    with col2:
        st.markdown(st.session_state.m.render_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
