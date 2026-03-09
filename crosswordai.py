import streamlit as st
import requests
import random
import re

# --- CONFIGURAZIONE ---
ROWS = 13
COLS = 9

class MotoreInterattivo:
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
                for l in linee:
                    p = l.strip().upper()
                    if p.isalpha() and 2 <= len(p) <= 12:
                        self.set_parole.add(p)
                        self.dizionario[len(p)].append(p)
                return True
        except: pass
        return False

    def salva_stato(self):
        self.storico.append({
            'griglia': [r[:] for r in self.griglia],
            'parole_usate': set(self.parole_usate)
        })

    def toggle_nera(self, r, c):
        self.salva_stato()
        self.griglia[r][c] = '#' if self.griglia[r][c] != '#' else ' '

    def annulla(self):
        if self.storico:
            stato = self.storico.pop()
            self.griglia = stato['griglia']
            self.parole_usate = stato['parole_usate']
            return True
        return False

    def inserisci_parola(self, parola, r, c, orient):
        self.salva_stato()
        parola = parola.upper()
        for i in range(len(parola)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            self.griglia[rr][cc] = parola[i]
        self.parole_usate.add(parola)

    def verifica_legalita(self, r, c, parola, orient):
        L = len(parola)
        if orient == 'O' and c + L > COLS: return False
        if orient == 'V' and r + L > ROWS: return False
        
        # Controllo sovrapposizione e collisioni
        ha_incrocio = False
        for i in range(L):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            cella_attuale = self.griglia[rr][cc]
            if cella_attuale == '#': return False
            if cella_attuale.isalpha():
                if cella_attuale != parola[i]: return False
                ha_incrocio = True
        
        # Se la griglia non è vuota, pretendiamo un incrocio (opzionale)
        if len(self.parole_usate) > 0 and not ha_incrocio:
            return False
            
        return True

    def trova_tutti_incastri(self, parola):
        parola = parola.upper()
        L = len(parola)
        validi = []
        for r in range(ROWS):
            for c in range(COLS):
                for o in ['O', 'V']:
                    if self.verifica_legalita(r, c, parola, o):
                        validi.append({'r': r, 'c': c, 'o': o})
        return validi

def main():
    st.set_page_config(page_title="Crossword Architect", layout="wide")
    
    if 'm' not in st.session_state:
        st.session_state.m = MotoreInterattivo()
        st.session_state.diz_pronto = False

    st.image("banner.png")
    #st.title("🧩 Architect 13x9: Incastro Manuale")

    with st.sidebar:
        if not st.session_state.diz_pronto:
            if st.button("📚 Carica Dizionario"):
                st.session_state.m.carica_dizionario()
                st.session_state.diz_pronto = True
                st.rerun()
        
        st.divider()
        st.subheader("✍️ Inserimento Manuale")
        input_parola = st.text_input("Scrivi la parola:").upper()
        
        if input_parola:
            opzioni = st.session_state.m.trova_tutti_incastri(input_parola)
            if opzioni:
                st.success(f"Trovati {len(opzioni)} incastri possibili!")
                scelta = st.selectbox("Scegli posizione:", range(len(opzioni)), 
                                    format_func=lambda x: f"{opzioni[x]['o']} a Riga {opzioni[x]['r']+1}, Col {opzioni[x]['c']+1}")
                if st.button("✅ Inserisci in Griglia"):
                    pos = opzioni[scelta]
                    st.session_state.m.inserisci_parola(input_parola, pos['r'], pos['c'], pos['o'])
                    st.rerun()
            else:
                st.error("Nessun incastro legale possibile.")

        #st.divider()
        if st.button("⬅️ Annulla"):
            st.session_state.m.annulla()
            st.rerun()

        st.divider()
        
        # Gestione Caselle Nere tramite coordinate per non rompere la griglia
        st.subheader("⬛ Gestione Caselle Nere")
        c1, c2 = st.columns(2)
        r_nera = c1.number_input("Riga", 1, ROWS, 1) - 1
        c_nera = c2.number_input("Colonna", 1, COLS, 1) - 1
        if st.button("Metti/Togli Nera", use_container_width=True):
            st.session_state.m.toggle_nera(r_nera, c_nera)
            st.rerun()

    
    # Visualizzazione Griglia
    col1, col2 = st.columns([3, 1])
    with col1:
        # Generiamo la visualizzazione HTML
        html = '<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;border:3px solid #000;">'
        for r in range(ROWS):
            html += '<tr>'
            for c in range(COLS):
                v = st.session_state.m.griglia[r][c]
                bg = "#000" if v == "#" else "#fff"
                color = "#000"
                html += f'<td style="width:40px;height:40px;border:1px solid #ccc;background:{bg};color:{color};text-align:center;font-weight:bold;font-size:20px;">{v if v != " " else "&nbsp;"}</td>'
            html += '</tr>'
        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)
        
    with col2:
        st.write("**Parole inserite:**")
        for p in st.session_state.m.parole_usate:
            st.write(f"- {p}")

if __name__ == "__main__":
    main()
