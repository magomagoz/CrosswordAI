import streamlit as st
import requests
import re

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreArchitetto:
    def __init__(self, rows, cols):
        self.rows = rows  # <--- CORRETTO: usa il parametro dinamico
        self.cols = cols  # <--- CORRETTO: usa il parametro dinamico

        self.dizionario = {} 
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.parole_usate = set()
        self.storico = []

# 1. Funzione cache per il dizionario (risolve il problema della connessione)
@st.cache_data
def scarica_dizionario_sicuro():
    url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
    try:
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return set(p.strip().upper() for p in res.text.splitlines() if p.isalpha())
    except:
        return set()
    return set()

class MotoreArchitetto:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.griglia = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.parole_usate = [] 
        self.storico = []
        
    def salva_stato(self):
        self.storico.append({'griglia': [r[:] for r in self.griglia], 'parole_usate': set(self.parole_usate)})

    def annulla(self):
        if self.storico:
            stato = self.storico.pop()
            self.griglia = stato['griglia']
            self.parole_usate = stato['parole_usate']
            return True
        return False

    def toggle_nera(self, r, c):
        self.salva_stato()
        self.griglia[r][c] = '#' if self.griglia[r][c] != '#' else ' '

    def inserisci_parola(self, parola, r, c, orient):
        p = parola.upper()
        self.parole_usate.append({'p': p, 'o': orient, 'r': r+1, 'c': c+1})
        for i in range(len(p)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = p[i]

    def trova_incastri(self, parola):
        validi = []
        if not parola or len(parola) < 2: return validi
        L = len(parola); p_upper = parola.upper()
        
        vuota = not any(c.isalpha() for r in self.griglia for c in r)
        
        for r in range(ROWS):
            for c in range(COLS):
                for o in ['O', 'V']:
                    if (o == 'O' and c + L > COLS) or (o == 'V' and r + L > ROWS): continue
                    match, incrocio = True, False
                    for i in range(L):
                        rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                        cel = self.griglia[rr][cc]
                        if cel == '#': match = False; break
                        if cel.isalpha():
                            if cel != p_upper[i]: match = False; break
                            incrocio = True
                    if match and (vuota or incrocio):
                        validi.append({'r': r, 'c': c, 'o': o})
        return validi
        
    def render_html(self):
        # Genera tabella HTML base
        html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid black;">'
        for r in range(self.rows):
            html += '<tr>'
            for c in range(self.cols):
                val = self.griglia[r][c]
                html += f'<td style="border: 1px solid #444; width: 40px; height: 40px; text-align: center;">{val}</td>'
            html += '</tr>'
        return html + '</table>'

def main():
    st.set_page_config(page_title="Editor Professionale", layout="wide")
    
    # Inizializzazione sicura
    if 'm' not in st.session_state:
        st.session_state.m = MotoreArchitetto(13, 9)
    
    # Sidebar configurazione
    with st.sidebar:
        if st.button("📚 SCARICA DIZIONARIO"):
            st.session_state.dizionario = scarica_dizionario_sicuro()
            st.success("Dizionario pronto!")
            
    # Visualizzazione
    st.markdown(st.session_state.m.render_html(), unsafe_allow_html=True)
    
    # Liste parole sotto la griglia
    col1, col2 = st.columns(2)
    with col1: st.subheader("Orizzontali"); # Logica per filtrare
    with col2: st.subheader("Verticali");   # Logica per filtrare
        
    with st.sidebar:
        st.title("📐 Configurazione")
        new_rows = st.slider("Righe", 3, 25, 13)
        new_cols = st.slider("Colonne", 3, 25, 9)
        
        # Inizializzazione o Reset se cambiano le dimensioni
        if 'm' not in st.session_state or st.session_state.m.rows != new_rows or st.session_state.m.cols != new_cols:
            st.session_state.m = MotoreArchitetto(new_rows, new_cols)
            st.session_state.caricato = False
            st.toast(f"Griglia impostata a {new_rows}x{new_cols}")

        st.divider()
        
        st.title("🛠️ Pannello")
        if st.button("📚 SCARICA DIZIONARIO", use_container_width=True):
            n = st.session_state.m.carica_dizionario_massivo()
            st.session_state.caricato = True
            st.success(f"Dizionario pronto: {n} lemmi!")

        st.divider()
        st.subheader("⚫ Caselle Nere")
        c1, c2 = st.columns(2)
        r_n = c1.number_input("Riga", 1, st.session_state.m.rows, 1) - 1
        c_n = c2.number_input("Col", 1, st.session_state.m.cols, 1) - 1
        if st.button("Metti/Togli Nera", use_container_width=True):
            st.session_state.m.toggle_nera(r_n, c_n); st.rerun()
            
        st.divider()
        st.subheader("✍️ Inserimento Parola")
        p_in = st.text_input("Inserisci parola:").upper().strip()
        anteprima_data = None
        if p_in:
            risultato = st.session_state.m.trova_incastri(p_in)
            if risultato:
                idx = st.selectbox("Posizioni possibili:", range(len(risultato)), 
                                 format_func=lambda x: f"{risultato[x]['o']} - R{risultato[x]['r']+1}, C{risultato[x]['c']+1}")
                anteprima_data = {'p': p_in, 'r': risultato[idx]['r'], 'c': risultato[idx]['c'], 'o': risultato[idx]['o']}
                if st.button("🚀 CONFERMA E SCRIVI", use_container_width=True):
                    st.session_state.m.inserisci_parola(p_in, risultato[idx]['r'], risultato[idx]['c'], risultato[idx]['o']); st.rerun()
            else:
                st.error("Nessun incastro trovato.")

        if st.button("⬅️ ANNULLA", use_container_width=True):
            if st.session_state.m.annulla(): st.rerun()

    st.markdown(st.session_state.m.render_html(anteprima_data), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
