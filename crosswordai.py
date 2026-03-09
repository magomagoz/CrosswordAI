import streamlit as st
import requests
import re

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreArchitetto:
    def __init__(self):
        # Parole di backup per garantire il caricamento
        self.dizionario = {i: ["CASA", "SOLE", "MARE", "MONTE", "LIBRO"] for i in range(2, 14)}
        self.set_parole = set(["CASA", "SOLE", "MARE", "MONTE", "LIBRO"])
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []
        
    def carica_dizionario(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                linee = res.text.splitlines()
                count = 0
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 12:
                        self.set_parole.add(p)
                        L = len(p)
                        if L not in self.dizionario: self.dizionario[L] = []
                        self.dizionario[L].append(p)
                        count += 1
                return count
        except: pass
        return len(self.set_parole)

    def salva_stato(self):
        self.storico.append({'griglia': [r[:] for r in self.griglia], 'parole_usate': set(self.parole_usate)})

    def annulla(self):
        if self.storico:
            stato = self.storico.pop()
            self.griglia = stato['griglia']; self.parole_usate = stato['parole_usate']
            return True
        return False

    def toggle_nera(self, r, c):
        self.salva_stato()
        self.griglia[r][c] = '#' if self.griglia[r][c] != '#' else ' '

    def inserisci_parola(self, parola, r, c, orient):
        self.salva_stato()
        for i in range(len(parola)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola.upper()[i]
        self.parole_usate.add(parola.upper())

    def trova_incastri(self, parola):
        validi = []
        if not parola or len(parola) < 2: return validi
        L = len(parola); parola = parola.upper()
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
                            if cel != parola[i]: match = False; break
                            incrocio = True
                    if match and (vuota or incrocio):
                        validi.append({'r': r, 'c': c, 'o': o})
        return validi

    def render_html(self, anteprima=None):
        html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid black;">'
        temp_grid = [r[:] for r in self.griglia]
        if anteprima:
            p, r, c, o = anteprima['p'], anteprima['r'], anteprima['c'], anteprima['o']
            for i in range(len(p)):
                rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                if temp_grid[rr][cc] == ' ': temp_grid[rr][cc] = f'<span style="color:#1E90FF;opacity:0.5">{p[i]}</span>'
        
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = temp_grid[r][c]
                bg = "black" if val == "#" else "white"
                html += f'<td style="border: 1px solid #999; width: 40px; height: 40px; text-align: center; font-weight: bold; font-family: sans-serif; background: {bg}; color: black; font-size: 20px;">{val if val not in ["#", " "] else "&nbsp;"}</td>'
            html += '</tr>'
        return html + '</table>'

def main():
    st.set_page_config(page_title="Architect 13x9", layout="wide")
    if 'm' not in st.session_state:
        st.session_state.m = MotoreArchitetto()
        st.session_state.caricato = False

    with st.sidebar:
        st.header("⚙️ Pannello")
        if st.button("📚 CARICA DIZIONARIO", use_container_width=True):
            n = st.session_state.m.carica_dizionario()
            st.session_state.caricato = True
            st.success(f"Dizionario pronto! ({n} parole)")

        st.divider()
        st.subheader("⚫ Nere")
        c1, c2 = st.columns(2)
        r_n, c_n = c1.number_input("R", 1, ROWS, 1)-1, c2.number_input("C", 1, COLS, 1)-1
        if st.button("Metti/Togli Nera", use_container_width=True):
            st.session_state.m.toggle_nera(r_n, c_n); st.rerun()
            
        st.divider()
        st.subheader("✍️ Incastro")
        p_in = st.text_input("Parola:").upper().strip()
        anteprima_data = None
        if p_in:
            opts = st.session_state.m.trova_incastri(p_in)
            if opts:
                idx = st.selectbox("Posizioni:", range(len(opts)), format_func=lambda x: f"{opts[x]['o']} - R{opts[x]['r']+1}, C{opts[x]['c']+1}")
                anteprima_data = {'p': p_in, 'r': opts[idx]['r'], 'c': opts[idx]['c'], 'o': opts[idx]['o']}
                if st.button("🚀 CONFERMA", use_container_width=True):
                    st.session_state.m.inserisci_parola(p_in, opts[idx]['r'], opts[idx]['c'], opts[idx]['o']); st.rerun()
            else: st.error("Nessun incastro!")

        if st.button("⬅️ ANNULLA", use_container_width=True):
            if st.session_state.m.annulla(): st.rerun()

    st.markdown(st.session_state.m.render_html(anteprima_data), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
