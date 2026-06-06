import streamlit as st

class MotoreArchitetto:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.griglia = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.parole_usate = []
        self.storico_undo = []
        self.storico_redo = []

    def salva_stato(self):
        self.storico_undo.append({'griglia': [r[:] for r in self.griglia], 'parole_usate': list(self.parole_usate)})
        self.storico_redo = []

    def annulla(self):
        if self.storico_undo:
            self.storico_redo.append({'griglia': [r[:] for r in self.griglia], 'parole_usate': list(self.parole_usate)})
            stato = self.storico_undo.pop()
            self.griglia = stato['griglia']
            self.parole_usate = stato['parole_usate']
            return True
        return False

    def ripristina(self):
        if self.storico_redo:
            self.storico_undo.append({'griglia': [r[:] for r in self.griglia], 'parole_usate': list(self.parole_usate)})
            stato = self.storico_redo.pop()
            self.griglia = stato['griglia']
            self.parole_usate = stato['parole_usate']
            return True
        return False

    def elimina_parola(self, parola_da_eliminare):
        if not parola_da_eliminare: return False
        self.salva_stato()
        p = parola_da_eliminare.upper()
        nuova_lista = [item for item in self.parole_usate if item['p'] != p]
        if len(nuova_lista) == len(self.parole_usate): return False
        self.parole_usate = nuova_lista
        self.griglia = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        for item in self.parole_usate:
            self._scrivi_forzato(item['p'], item['r']-1, item['c']-1, item['o'])
        return True

    def _scrivi_forzato(self, p, r, c, orient):
        for i in range(len(p)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = p[i]

    def toggle_nera(self, r, c):
        self.salva_stato()
        self.griglia[r][c] = '#' if self.griglia[r][c] != '#' else ' '

    def inserisci_parola(self, parola, r, c, orient):
        self.salva_stato()
        p = parola.upper()
        self.parole_usate.append({'p': p, 'o': orient, 'r': r+1, 'c': c+1})
        self._scrivi_forzato(p, r, c, orient)

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
        numeri = self.calcola_numeri()
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
                num = numeri.get((r, c), "")
                n_html = f'<div style="position: absolute; top: 0px; left: 2px; font-size: 9px; color: #555;">{num}</div>' if num else ""
                html += f'''<td style="border: 1px solid #444; width: 40px; height: 40px; text-align: center; font-weight: bold; background: {bg}; position: relative;">{n_html}<div style="margin-top: 10px;">{display}</div></td>'''
            html += '</tr>'
        return html + '</table>'

    def calcola_numeri(self):
        numeri, cont = {}, 1
        for r in range(self.rows):
            for c in range(self.cols):
                if self.griglia[r][c] == '#': continue
                io = (c == 0 or self.griglia[r][c-1] == '#') and (c + 1 < self.cols and self.griglia[r][c+1] != '#')
                iv = (r == 0 or self.griglia[r-1][c] == '#') and (r + 1 < self.rows and self.griglia[r+1][c] != '#')
                if io or iv:
                    numeri[(r, c)] = cont
                    cont += 1
        return numeri

def main():
    st.set_page_config(page_title="Editor Professionale", layout="wide")
    if 'm' not in st.session_state: st.session_state.m = MotoreArchitetto(13, 9)
    
    with st.sidebar:
        st.title("⚙️ Pannello Controllo")
        if st.selectbox("Formato:", ["13x9", "13x13", "12x22", "8x12"]):
            if st.button("Applica"): st.session_state.m = MotoreArchitetto(13, 9); st.rerun()

        p_in = st.text_input("Parola:")
        if p_in:
            res = st.session_state.m.trova_incastri(p_in)
            if res:
                idx = st.selectbox("Posizioni:", range(len(res)), format_func=lambda x: f"{res[x]['o']} - R{res[x]['r']+1}, C{res[x]['c']+1}")
                if st.button("CONFERMA"):
                    st.session_state.m.inserisci_parola(p_in, res[idx]['r'], res[idx]['c'], res[idx]['o'])
                    st.rerun()
        
        if st.button("⬅️ ANNULLA"): 
            if st.session_state.m.annulla(): st.rerun()
            
        p_del = st.text_input("Elimina parola:")
        if st.button("Elimina"):
            if st.session_state.m.elimina_parola(p_del): st.rerun()

    st.title("🧩 Griglia")
    st.markdown(st.session_state.m.render_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
