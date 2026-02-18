import streamlit as st
import requests
import random

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreDinamicoCorretto:
    def __init__(self):
        self.dizionario = {}
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_inserite = []
        self.reset_griglia()

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
                # Parole tra 3 e 8 lettere per garantire mobilità
                if p.isalpha() and 3 <= len(p) <= 8:
                    lung = len(p)
                    if lung not in self.dizionario: self.dizionario[lung] = []
                    self.dizionario[lung].append(p)
            return True
        except: return False

    def può_stare(self, parola, r, c, orientamento):
        lung = len(parola)
        
        # 1. Verifica confini
        if orientamento == 'O':
            if c + lung > COLS: return False
        else:
            if r + lung > ROWS: return False

        # 2. Verifica caselle nere e sovrapposizioni
        ha_incrocio = False
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            cella = self.griglia[curr_r][curr_c]
            
            if cella == '#': return False # Non può sovrascrivere una nera
            if cella.isalpha():
                if cella != parola[i]: return False # Lettera diversa: conflitto
                ha_incrocio = True # Trovata lettera uguale: incrocio valido
        
        # 3. Regola d'oro: Se non è la prima parola, DEVE incrociare qualcosa
        if len(self.parole_inserite) > 0 and not ha_incrocio:
            return False
            
        return True

    def inserisci(self, parola, r, c, orientamento):
        lung = len(parola)
        # Inserimento lettere
        for i in range(lung):
            curr_r = r + (i if orientamento == 'V' else 0)
            curr_c = c + (i if orientamento == 'O' else 0)
            self.griglia[curr_r][curr_c] = parola[i]
        
        # Inserimento caselle nere di delimitazione (se possibile)
        if orientamento == 'O':
            if c - 1 >= 0: self.griglia[r][c-1] = '#'
            if c + lung < COLS: self.griglia[r][c+lung] = '#'
        else:
            if r - 1 >= 0: self.griglia[r-1][c] = '#'
            if r + lung < ROWS: self.griglia[r+lung][c] = '#'
            
        self.parole_inserite.append(parola)

    def aggiungi_parola(self):
        # Cerchiamo tra diverse lunghezze
        lunghezze = [3, 4, 5, 6, 7, 8]
        random.shuffle(lunghezze)
        
        for l in lunghezze:
            candidati = self.dizionario.get(l, [])
            if not candidati: continue
            
            # Prendiamo un campione per non appesantire
            campione = random.sample(candidati, min(len(candidati), 200))
            
            # Tutte le posizioni possibili sulla griglia
            posizioni = [(r, c, o) for r in range(ROWS) for c in range(COLS) for o in ['O', 'V']]
            random.shuffle(posizioni)
            
            for r, c, o in posizioni:
                if self.può_stare(p := random.choice(campione), r, c, o):
                    self.inserisci(p, r, c, o)
                    return True, f"Inserita parola: {p}"
        
        return False, "Impossibile trovare un incrocio valido."

    def render_html(self):
        html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 2px solid black;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "#000" if val == "#" else "#fff"
                color = "#fff" if val == "#" else "#000"
                txt = val if val != "#" else ""
                html += f'<td style="width:40px;height:40px;border:1px solid #ddd;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:20px;font-family:sans-serif;">{txt}</td>'
            html += '</tr>'
        return html + "</table></div>"

def main():
    st.set_page_config(page_title="Cruciverba Dinamico", layout="wide")
    st.title("🧩 Costruttore Cruciverba Organico")

    if 'motore' not in st.session_state:
        st.session_state.motore = MotoreDinamicoCorretto()
        st.session_state.caricato = False
        st.session_state.msg = "Inizia caricando il vocabolario."

    col1, col2 = st.columns([1, 2])

    with col1:
        if not st.session_state.caricato:
            if st.button("📚 1. CARICA DIZIONARIO", use_container_width=True):
                if st.session_state.motore.carica_parole():
                    st.session_state.caricato = True
                    st.session_state.msg = "Dizionario pronto! Clicca per inserire la prima parola."
                    st.rerun()
        else:
            if st.button("➕ AGGIUNGI UNA PAROLA", use_container_width=True):
                successo, m = st.session_state.motore.aggiungi_parola()
                st.session_state.msg = m
                st.rerun()
            
            if st.button("🔄 RESET TOTALE", use_container_width=True):
                st.session_state.motore.reset_griglia()
                st.session_state.msg = "Griglia svuotata."
                st.rerun()
        
        st.info(f"**Log:** {st.session_state.msg}")
        st.write(f"**Parole nello schema:** {len(st.session_state.motore.parole_inserite)}")
        st.write(", ".join(st.session_state.motore.parole_inserite))

    with col2:
        st.markdown(st.session_state.motore.render_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
