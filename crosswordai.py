import streamlit as st
import os

class MotoreArchitetto:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.griglia = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.parole_usate = []
        self.storico = []

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

    def trova_incastri(self, parola):
        validi = []
        L = len(parola)
        p_upper = parola.upper()
        # Per ora disabilitiamo il controllo dizionario per blindare l'app
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
    st.set_page_config(page_title="Editor Blindato", layout="wide")
    
    if 'm' not in st.session_state: st.session_state.m = MotoreArchitetto(13, 9)
    
    with st.sidebar:
        st.title("⚙️ Pannello di controllo")
        
        st.header("📐 Seleziona Schema")
        
        # Dizionario con i formati predefiniti
        formati = {
            "Incroci obbligati": (13, 9),
            "Ricerca di parole crociate": (12, 14),
            "Parole crociate senza schema": (12, 22),
            "Parole crociate bifrontali": (12, 18)
        }
        
        # Scelta tramite Selectbox
        scelta = st.selectbox("Scegli formato:", list(formati.keys()))
        rows, cols = formati[scelta]
        
        # Bottone per applicare il cambio schema
        if st.button("Applica Schema"):
            st.session_state.m = MotoreArchitetto(rows, cols)
            st.rerun()
        
        st.divider()
        st.subheader("⬛ Caselle Nere")
        c1, c2 = st.columns(2)
        r_n = c1.number_input("Riga", 1, st.session_state.m.rows, 1) - 1
        c_n = c2.number_input("Col", 1, st.session_state.m.cols, 1) - 1
        if st.button("Metti/Togli Nera"):
            st.session_state.m.toggle_nera(r_n, c_n); st.rerun()

        st.subheader("✍️ Inserimento Parola")
        p_in = st.text_input("Parola (libera):", key="input_parola").upper().strip()
        anteprima_data = None
        
        if p_in:
            risultato = st.session_state.m.trova_incastri(p_in)
            if risultato:
                idx = st.selectbox("Posizioni:", range(len(risultato)), format_func=lambda x: f"{risultato[x]['o']} - R{risultato[x]['r']+1}, C{risultato[x]['c']+1}")
                anteprima_data = {'p': p_in, 'r': risultato[idx]['r'], 'c': risultato[idx]['c'], 'o': risultato[idx]['o']}
                if st.button("🚀 CONFERMA E SCRIVI"):
                    st.session_state.m.inserisci_parola(p_in, risultato[idx]['r'], risultato[idx]['c'], risultato[idx]['o'])
                    st.rerun()
            else: st.error("Nessun incastro possibile.")

    st.image("banner.png")
    st.title("🧩 Griglia Cruciverba")
    st.markdown(st.session_state.m.render_html(anteprima_data), unsafe_allow_html=True)

    st.divider()
    # Creiamo due colonne sotto la griglia per dividere le liste
    col1, col2 = st.columns(2)
    
    with col1: 
        st.subheader("Orizzontali")
        # Filtriamo solo le parole con orientamento 'O'
        orizzontali = [item for item in st.session_state.m.parole_usate if item['o'] == 'O']
        if orizzontali:
            for item in orizzontali:
                st.write(f"R{item['r']} C{item['c']}: **{item['p']}**")
        else:
            st.write("Nessuna parola.")

    with col2: 
        st.subheader("Verticali")
        # Filtriamo solo le parole con orientamento 'V'
        verticali = [item for item in st.session_state.m.parole_usate if item['o'] == 'V']
        if verticali:
            for item in verticali:
                st.write(f"R{item['r']} C{item['c']}: **{item['p']}**")
        else:
            st.write("Nessuna parola.")

if __name__ == "__main__":
    main()
