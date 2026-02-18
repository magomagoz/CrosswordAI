import streamlit as st
import requests
import random
import re

# --- Classi core (Dizionario e Logica Griglia) ---
class AssistenteCruciverba:
    def __init__(self):
        if 'parole_per_L' not in st.session_state:
            st.session_state.parole_per_L = {}
        self.ROWS = 13
        self.COLS = 9

    def carica_dizionario(self):
        tutte_parole = set()
        progress = st.progress(0)
        # Carichiamo un set di pagine per avere varietà di lunghezze
        for p in range(1, 12):
            try:
                resp = requests.get(f"https://www.listediparole.it/parole-italiane-pagina{p}.htm", timeout=5)
                parole = re.findall(r'\b[A-Z]{2,13}\b', resp.text)
                tutte_parole.update(parole)
            except: continue
            progress.progress(p/11)
        
        diz = {}
        for parola in tutte_parole:
            L = len(parola)
            if L not in diz: diz[L] = []
            diz[L].append(parola)
        st.session_state.parole_per_L = diz
        progress.empty()
        return len(tutte_parole)

    def trova_segmenti(self, griglia):
        """Trova tutti gli spazi bianchi (orizzontali) disponibili"""
        segmenti = []
        for r in range(13):
            riga_str = "".join(griglia[r])
            for m in re.finditer(r'[^#]+', riga_str):
                if len(m.group()) >= 2:
                    segmenti.append((r, m.start(), len(m.group())))
        return segmenti

def render_griglia(griglia):
    """Renderizza la griglia con stile compatto"""
    html = '<table style="border-collapse: collapse; margin: 0 auto; border: 2px solid #333;">'
    for riga in griglia:
        html += '<tr>'
        for cella in riga:
            bg = "black" if cella == "#" else "white"
            color = "black" if cella != "#" else "black"
            content = cella if cella not in ["#", " "] else "&nbsp;"
            html += f'<td style="border: 1px solid #999; width: 35px; height: 35px; text-align: center; font-weight: bold; background: {bg}; color: {color};">{content}</td>'
        html += '</tr>'
    return html + '</table>'

# --- Interfaccia Streamlit ---
def main():
    st.set_page_config(page_title="Editor Cruciverba 13x9", layout="centered")
    assistant = AssistenteCruciverba()

    st.title("🧩 Assistente Incastri 13x9")
    st.write("Genera lo schema una parola alla volta per completarlo insieme.")

    # Inizializzazione Session State
    if 'griglia' not in st.session_state:
        # Creiamo una griglia con caselle nere fisse (schema classico)
        g = [[' ' for _ in range(9)] for _ in range(13)]
        # Aggiungiamo alcune caselle nere simmetriche
        nere = [(1,1), (1,7), (3,3), (3,5), (6,4), (9,3), (9,5), (11,1), (11,7), (0,4), (12,4)]
        for r, c in nere: g[r][c] = '#'
        st.session_state.griglia = g
        st.session_state.parole_inserite = []
        st.session_state.diz_pronto = False

    # Sidebar per controllo dizionario
    if not st.session_state.diz_pronto:
        if st.button("📚 1. Carica Parole (Treccani/Base)"):
            num = assistant.carica_dizionario()
            st.session_state.diz_pronto = True
            st.success(f"{num} parole caricate!")
            st.rerun()
    
    # Area di lavoro
    if st.session_state.diz_pronto:
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.write("### Comandi")
            if st.button("➡️ Inserisci Prossima Parola", use_container_width=True):
                # Logica di ricerca parola singola
                segmenti = assistant.trova_segmenti(st.session_state.griglia)
                parola_trovata = False
                
                # Cerchiamo il primo segmento vuoto o parzialmente pieno
                for r, c_inizio, L in segmenti:
                    # Controlliamo se è già pieno
                    attuale = "".join(st.session_state.griglia[r][c_inizio:c_inizio+L])
                    if " " not in attuale: continue
                    
                    # Creiamo il pattern per la ricerca (es: "A.B..")
                    pattern_list = []
                    for i, char in enumerate(attuale):
                        if char != " ": pattern_list.append((i, char))
                    
                    candidati = st.session_state.parole_per_L.get(L, [])
                    random.shuffle(candidati)
                    
                    for p in candidati:
                        if p in st.session_state.parole_inserite: continue
                        # Verifica pattern
                        match = True
                        for pos, let in pattern_list:
                            if p[pos] != let:
                                match = False; break
                        
                        if match:
                            # Inseriamo la parola
                            for i in range(L):
                                st.session_state.griglia[r][c_inizio + i] = p[i]
                            st.session_state.parole_inserite.append(p)
                            parola_trovata = True
                            break
                    
                    if parola_trovata: break
                
                if not parola_trovata:
                    st.warning("⚠️ Nessun incrocio possibile trovato per i prossimi spazi!")
                else:
                    st.rerun()

            if st.button("🔄 Reset Griglia", type="secondary"):
                del st.session_state.griglia
                del st.session_state.parole_inserite
                st.rerun()

            st.write(f"**Parole in griglia:** {len(st.session_state.parole_inserite)}")
            for p in st.session_state.parole_inserite[-10:]: # Ultime 10
                st.text(f"✓ {p}")

        with col1:
            st.markdown(render_griglia(st.session_state.griglia), unsafe_allow_html=True)
            st.caption("Ogni click aggiunge una parola orizzontale incastrandola con le lettere esistenti.")

if __name__ == "__main__":
    main()
