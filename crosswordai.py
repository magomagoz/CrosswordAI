import streamlit as st
import requests
import re

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreArchitetto:
    def __init__(self):
        # Inizializziamo con un set vuoto, pronti per il carico massivo
        self.dizionario = {i: [] for i in range(2, 14)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []
        
    def carica_dizionario_massivo(self):
        """Estrae migliaia di parole da un database linguistico certificato"""
        # Utilizziamo un repository di riferimento per il lessico italiano (660k+ parole)
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                linee = res.text.splitlines()
                count = 0
                for l in linee:
                    p = l.strip().upper()
                    # Filtriamo solo parole puramente alfabetiche (niente accenti/simboli per il cruciverba)
                    if p.isalpha() and 2 <= len(p) <= 12:
                        self.set_parole.add(p)
                        L = len(p)
                        if L not in self.dizionario: self.dizionario[L] = []
                        self.dizionario[L].append(p)
                        count += 1
                return count
        except Exception as e:
            st.error(f"Errore di connessione al dizionario: {e}")
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
        
        # Una parola è "valida" per il dizionario se esiste nel set caricato
        if p_upper not in self.set_parole:
            return "NON_IN_DIZIONARIO"

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

    def render_html(self, anteprima=None):
        html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid black; background-color: white;">'
        temp_grid = [r[:] for r in self.griglia]
        
        if anteprima:
            p, r, c, o = anteprima['p'], anteprima['r'], anteprima['c'], anteprima['o']
            for i in range(len(p)):
                rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                if temp_grid[rr][cc] == ' ': 
                    temp_grid[rr][cc] = f'<span style="color:#007bff; font-weight:normal;">{p[i]}</span>'
        
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = temp_grid[r][c]
                bg = "black" if val == "#" else "white"
                # Pulizia per HTML: se è una stringa HTML (anteprima), la lasciamo, altrimenti &nbsp;
                display = val if (val != " " and val != "#") else "&nbsp;"
                html += f'<td style="border: 1px solid #444; width: 42px; height: 42px; text-align: center; font-weight: bold; font-family: Arial; background: {bg}; color: black; font-size: 22px;">{display}</td>'
            html += '</tr>'
        return html + '</table>'

def main():
    st.set_page_config(page_title="Editor Professionale 13x9", layout="wide")
    
    if 'm' not in st.session_state:
        st.session_state.m = MotoreArchitetto()
        st.session_state.caricato = False

    with st.sidebar:
        st.title("🛠️ Pannello")
        if st.button("📚 SCARICA DIZIONARIO ACCADEMICO", use_container_width=True):
            with st.spinner("Estrazione di migliaia di parole in corso..."):
                n = st.session_state.m.carica_dizionario_massivo()
                if n > 0:
                    st.session_state.caricato = True
                    st.success(f"Dizionario pronto: {n} lemmi caricati!")
                else:
                    st.error("Impossibile raggiungere il server del dizionario.")

        st.divider()
        st.subheader("⚫ Gestione Caselle Nere")
        c1, c2 = st.columns(2)
        r_n = c1.number_input("Riga", 1, ROWS, 1) - 1
        c_n = c2.number_input("Col", 1, COLS, 1) - 1
        if st.button("Metti/Togli Nera", use_container_width=True):
            st.session_state.m.toggle_nera(r_n, c_n)
            st.rerun()
            
        st.divider()
        st.subheader("✍️ Inserimento Parola")
        p_in = st.text_input("Inserisci parola:").upper().strip()
        
        anteprima_data = None
        if p_in and st.session_state.caricato:
            risultato = st.session_state.m.trova_incastri(p_in)
            
            if risultato == "NON_IN_DIZIONARIO":
                st.warning(f"'{p_in}' non è nel dizionario accademico.")
            elif risultato:
                idx = st.selectbox("Posizioni possibili:", range(len(risultato)), 
                                 format_func=lambda x: f"{risultato[x]['o']} - R{risultato[x]['r']+1}, C{risultato[x]['c']+1}")
                anteprima_data = {'p': p_in, 'r': risultato[idx]['r'], 'c': risultato[idx]['c'], 'o': risultato[idx]['o']}
                
                if st.button("🚀 CONFERMA E SCRIVI", use_container_width=True):
                    st.session_state.m.inserisci_parola(p_in, risultato[idx]['r'], risultato[idx]['c'], risultato[idx]['o'])
                    st.rerun()
            else:
                st.error("Nessun incastro trovato per questa parola.")

        if st.button("⬅️ ANNULLA", use_container_width=True):
            if st.session_state.m.annulla(): st.rerun()

    # AREA GRIGLIA
    st.markdown(st.session_state.m.render_html(anteprima_data), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
