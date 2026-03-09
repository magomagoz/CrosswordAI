import streamlit as st
import json
import os
import sqlite3

class MotoreArchitetto:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.griglia = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.parole_usate = []
        self.storico = []
        self.dizionario_valido = self._carica_dizionario()

    def _carica_dizionario(self):
        # Carica il dizionario JSON locale all'avvio
        if os.path.exists("dizionario.json"):
            with open("dizionario.json", "r", encoding="utf-8") as f:
                return set(json.load(f).get("parole", []))
        return set()

    def salva_stato(self):
        self.storico.append({'griglia': [r[:] for r in self.griglia], 'parole_usate': list(self.parole_usate)})

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
        if not any(item['p'] == p and item['r'] == r+1 and item['c'] == c+1 for item in self.parole_usate):
            self.parole_usate.append({'p': p, 'o': orient, 'r': r+1, 'c': c+1})
        for i in range(len(p)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = p[i]

    def verifica_parola(self, parola):
        conn = sqlite3.connect("dizionario.db")
        c = conn.cursor()
        c.execute("SELECT 1 FROM parole WHERE testo = ?", (parola.upper(),))
        esiste = c.fetchone() is not None
        conn.close()
        return esiste

    def trova_incastri(self, parola):
        validi = []
        L = len(parola)
        p_upper = parola.upper()
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
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    temp_grid[rr][cc] = f'<span style="color:#007bff;">{p[i]}</span>'
        
        for r in range(self.rows):
            html += '<tr>'
            for c in range(self.cols):
                val = temp_grid[r][c]
                bg = "black" if val == "#" else "white"
                display = val if (val != " " and val != "#") else "&nbsp;"
                html += f'<td style="border: 1px solid #444; width: 40px; height: 40px; text-align: center; font-weight: bold; background: {bg};">{display}</td>'
            html += '</tr>'
        return html + '</table>'

def main():
    st.set_page_config(page_title="Editor Professionale", layout="wide")
    st.image("banner.png")
    
    if 'm' not in st.session_state: st.session_state.m = MotoreArchitetto(13, 9)
    
    with st.sidebar:
        st.title("⚙️ Pannello di controllo")

        st.header("📐 Crea la griglia")
        new_rows = st.slider("Righe", 3, 25, st.session_state.m.rows)
        new_cols = st.slider("Colonne", 3, 25, st.session_state.m.cols)
        if st.session_state.m.rows != new_rows or st.session_state.m.cols != new_cols:
            st.session_state.m = MotoreArchitetto(new_rows, new_cols); st.rerun()

        st.divider()
        st.subheader("⬛ Caselle Nere")
        c1, c2 = st.columns(2)
        r_n = c1.number_input("Riga", 1, st.session_state.m.rows, 1) - 1
        c_n = c2.number_input("Col", 1, st.session_state.m.cols, 1) - 1
        if st.button("Metti/Togli Nera"):
            st.session_state.m.toggle_nera(r_n, c_n); st.rerun()

        st.divider()
        st.subheader("✍️ Inserimento Parola")
        p_in = st.text_input("Parola:", key="input_parola").upper().strip()
        anteprima_data = None
        
        if p_in:
            if p_in not in st.session_state.m.dizionario_valido:
                st.warning(f"⚠️ '{p_in}' non presente nel dizionario!")
            
            risultato = st.session_state.m.trova_incastri(p_in)
            if risultato:
                idx = st.selectbox("Posizioni:", range(len(risultato)), format_func=lambda x: f"{risultato[x]['o']} - R{risultato[x]['r']+1}, C{risultato[x]['c']+1}")
                anteprima_data = {'p': p_in, 'r': risultato[idx]['r'], 'c': risultato[idx]['c'], 'o': risultato[idx]['o']}
                if st.button("🚀 CONFERMA E SCRIVI"):
                    st.session_state.m.inserisci_parola(p_in, risultato[idx]['r'], risultato[idx]['c'], risultato[idx]['o'])
                    st.session_state.input_parola = ""
                    st.rerun()
            else: st.error("Nessun incastro.")

        if st.button("⬅️ ANNULLA"):
            if st.session_state.m.annulla(): st.rerun()
        
    st.divider()
    st.title("🧩 Griglia Cruciverba")
    st.markdown(st.session_state.m.render_html(anteprima_data), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("Orizzontali")
        for item in st.session_state.m.parole_usate:
            if item['o'] == 'O': st.write(f"R{item['r']} C{item['c']}: **{item['p']}**")
    with col2: 
        st.subheader("Verticali")
        for item in st.session_state.m.parole_usate:
            if item['o'] == 'V': st.write(f"R{item['r']} C{item['c']}: **{item['p']}**")

if __name__ == "__main__":
    main()
