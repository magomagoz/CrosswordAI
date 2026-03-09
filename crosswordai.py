import streamlit as st
import requests
import re

class MotoreArchitetto:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.dizionario = {} 
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.parole_usate = set()
        self.storico = []
        
    def carica_dizionario_massivo(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code == 200:
                testo = res.content.decode('utf-8')
                linee = testo.splitlines()
                temp_set = set()
                for l in linee:
                    p = l.strip().upper()
                    # Accetta parole proporzionate alla griglia massima
                    if p.isalpha() and 2 <= len(p) <= max(self.rows, self.cols):
                        temp_set.add(p)
                
                for p in temp_set:
                    self.set_parole.add(p)
                    L = len(p)
                    if L not in self.dizionario: self.dizionario[L] = []
                    self.dizionario[L].append(p)
                return len(self.set_parole)
        except Exception as e:
            st.error(f"Errore: {str(e)}")
        return 0

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
        self.salva_stato()
        p = parola.upper()
        for i in range(len(p)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = p[i]
        self.parole_usate.add(p)

    def trova_incastri(self, parola):
        validi = []
        if not parola or len(parola) < 2: return validi
        L = len(parola); p_upper = parola.upper()
        
        vuota = not any(c.isalpha() for r in self.griglia for c in r)
        
        for r in range(self.rows):
            for c in range(self.cols):
                for o in ['O', 'V']:
                    if (o == 'O' and c + L > self.cols) or (o == 'V' and r + L > self.rows): continue
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

    def render_html(self, anteprima=None):
        html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid black; background-color: white;">'
        temp_grid = [r[:] for r in self.griglia]
        if anteprima:
            p, r, c, o = anteprima['p'], anteprima['r'], anteprima['c'], anteprima['o']
            for i in range(len(p)):
                rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                if temp_grid[rr][cc] == ' ': 
                    temp_grid[rr][cc] = f'<span style="color:#007bff; font-weight:normal;">{p[i]}</span>'
        
        for r in range(self.rows):
            html += '<tr>'
            for c in range(self.cols):
                val = temp_grid[r][c]
                bg = "black" if val == "#" else "white"
                display = val if (val != " " and val != "#") else "&nbsp;"
                html += f'<td style="border: 1px solid #444; width: 42px; height: 42px; text-align: center; font-weight: bold; font-family: Arial; background: {bg}; color: black; font-size: 22px;">{display}</td>'
            html += '</tr>'
        return html + '</table>'

def main():
    st.set_page_config(page_title="Custom Crossword Editor", layout="wide")
    
    # 1. SCELTA GRANDEZZA (In alto nella sidebar)
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
        
        if not st.session_state.caricato:
            if st.button("📚 SCARICA DIZIONARIO", use_container_width=True):
                with st.spinner("Scaricamento lemmi..."):
                    n = st.session_state.m.carica_dizionario_massivo()
                    if n > 0:
                        st.session_state.caricato = True
                        st.success(f"Dizionario pronto: {n} lemmi!")
        
        st.divider()
        st.subheader("⚫ Caselle Nere")
        c1, c2 = st.columns(2)
        r_n = c1.number_input("Riga", 1, self.rows, 1) - 1
        c_n = c2.number_input("Col", 1, self.cols, 1) - 1
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
