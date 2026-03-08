import streamlit as st
import requests
import re

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreArchitetto:
    def __init__(self):
        self.dizionario = {i: [] for i in range(2, 14)}
        self.set_parole = set()
        self.griglia = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.parole_usate = set()
        self.storico = []
        
    def carica_dizionario(self):
        url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                linee = res.text.splitlines()
                count = 0
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 12:
                        self.set_parole.add(p)
                        self.dizionario[len(p)].append(p)
                        count += 1
                return count
        except: pass
        return 0

    def salva_stato(self):
        self.storico.append({
            'griglia': [r[:] for r in self.griglia],
            'parole_usate': set(self.parole_usate)
        })

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
        parola = parola.upper()
        for i in range(len(parola)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        self.parole_usate.add(parola)

    def trova_incastri(self, parola):
        validi = []
        if not parola or len(parola) < 2: return validi
        L = len(parola)
        for r in range(ROWS):
            for c in range(COLS):
                for o in ['O', 'V']:
                    # Verifica confini
                    if o == 'O' and c + L > COLS: continue
                    if o == 'V' and r + L > ROWS: continue
                    
                    match = True
                    incrocio = False
                    for i in range(L):
                        rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                        cella = self.griglia[rr][cc]
                        if cella == '#': match = False; break
                        if cella.isalpha():
                            if cella != parola[i]: match = False; break
                            incrocio = True
                    
                    if match and (len(self.parole_usate) == 0 or incrocio):
                        validi.append({'r': r, 'c': c, 'o': o})
        return validi

    def render_html(self):
        """Genera la tabella HTML compatta come nel vecchio stile"""
        html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid black;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                val = self.griglia[r][c]
                bg = "black" if val == "#" else "white"
                color = "white" if val == "#" else "black"
                char = val if val not in ["#", " "] else "&nbsp;"
                html += f'<td style="border: 1px solid #999; width: 40px; height: 40px; text-align: center; font-weight: bold; font-family: sans-serif; background: {bg}; color: {color}; font-size: 20px;">{char}</td>'
            html += '</tr>'
        html += '</table>'
        return html

def main():
    st.set_page_config(page_title="Editor Cruciverba 13x9", layout="wide")
    
    if 'm' not in st.session_state:
        st.session_state.m = MotoreArchitetto()
        st.session_state.caricato = False

    st.title("🧩 Architect 13x9: Design Compatto")

    with st.sidebar:
        st.header("⚙️ Pannello Controllo")
        
        if not st.session_state.caricato:
            if st.button("📚 CARICA DIZIONARIO", use_container_width=True):
                n = st.session_state.m.carica_dizionario()
                if n > 0:
                    st.session_state.caricato = True
                    st.success(f"Dizionario caricato: {n} parole!")
                    st.rerun()
        else:
            st.success("✅ Dizionario Pronto")

        st.divider()
        
        # Gestione Caselle Nere tramite coordinate per non rompere la griglia
        st.subheader("⚫ Gestione Caselle Nere")
        c1, c2 = st.columns(2)
        r_nera = c1.number_input("Riga", 1, ROWS, 1) - 1
        c_nera = c2.number_input("Colonna", 1, COLS, 1) - 1
        if st.button("Metti/Togli Nera", use_container_width=True):
            st.session_state.m.toggle_nera(r_nera, c_nera)
            st.rerun()
            
        st.divider()
        
        st.subheader("✍️ Incastro Parole")
        parola_input = st.text_input("Parola:").upper()
        if parola_input and st.session_state.caricato:
            opzioni = st.session_state.m.trova_incastri(parola_input)
            if opzioni:
                scelta = st.selectbox("Posizioni trovate:", range(len(opzioni)), 
                                    format_func=lambda x: f"{opzioni[x]['o']} - R{opzioni[x]['r']+1}, C{opzioni[x]['c']+1}")
                if st.button("🚀 INSERISCI PAROLA", use_container_width=True):
                    p = opzioni[scelta]
                    st.session_state.m.inserisci_parola(parola_input, p['r'], p['c'], p['o'])
                    st.rerun()
            else:
                st.warning("Nessun incastro trovato.")

        st.divider()
        if st.button("⬅️ ANNULLA ULTIMA AZIONE", use_container_width=True):
            if st.session_state.m.annulla():
                st.rerun()

    # --- AREA GRIGLIA ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Visualizzazione della griglia vecchia maniera (UNITA)
        st.markdown(st.session_state.m.render_html(), unsafe_allow_html=True)
        st.caption("Usa il pannello a sinistra per inserire parole o caselle nere.")
        
    with col2:
        st.write("**Parole nello schema:**")
        if st.session_state.m.parole_usate:
            for p in sorted(st.session_state.m.parole_usate):
                st.write(f"- {p}")
        else:
            st.write("_Nessuna parola inserita_")

if __name__ == "__main__":
    main()
