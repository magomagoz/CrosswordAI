import streamlit as st
import requests
import random
import re

class AssistenteCruciverba:
    def __init__(self):
        self.ROWS = 13
        self.COLS = 9
        # Parole di emergenza se il download fallisce
        self.fallback_dict = {
            4: ["CASA", "MARE", "SOLE", "LUCE"],
            9: ["SETTIMANA", "CRUCIVERBA", "AVVENTURA"]
        }

    def carica_dizionario(self):
        tutte_parole = set()
        progress = st.progress(0)
        # Proviamo a caricare più pagine per essere sicuri
        for p in range(1, 15):
            try:
                # URL aggiornato per maggiore compatibilità
                url = f"https://www.listediparole.it/5lettereparolepagina{p}.htm" if p < 5 else f"https://www.listediparole.it/parole-italiane-pagina{p}.htm"
                resp = requests.get(url, timeout=5)
                parole = re.findall(r'\b[A-Z]{2,13}\b', resp.text.upper())
                tutte_parole.update(parole)
            except: continue
            progress.progress(p/14)
        
        diz = {}
        for parola in tutte_parole:
            L = len(parola)
            if L not in diz: diz[L] = []
            diz[L].append(parola)
        
        # Uniamo con fallback
        for k, v in self.fallback_dict.items():
            if k not in diz: diz[k] = v
            else: diz[k].extend(v)
            
        st.session_state.parole_per_L = diz
        progress.empty()
        return len(tutte_parole)

    def trova_segmenti(self, griglia):
        segmenti = []
        for r in range(self.ROWS):
            riga_str = "".join(griglia[r])
            # Trova sequenze di spazi che non siano caselle nere
            for m in re.finditer(r'[^#]+', riga_str):
                lunghezza = len(m.group())
                if lunghezza >= 2:
                    segmenti.append({'r': r, 'c': m.start(), 'L': lunghezza, 'testo': m.group()})
        return segmenti

def render_griglia(griglia):
    html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid #000; background: white;">'
    for riga in griglia:
        html += '<tr>'
        for cella in riga:
            bg = "#000" if cella == "#" else "#fff"
            color = "#000"
            content = cella if cella not in ["#", " "] else "&nbsp;"
            html += f'<td style="border: 1px solid #444; width: 40px; height: 40px; text-align: center; font-family: sans-serif; font-size: 20px; font-weight: bold; background: {bg}; color: {color};">{content}</td>'
        html += '</tr>'
    return html + '</table>'

def main():
    st.set_page_config(page_title="Pro Cruciverba 13x9", layout="wide")
    assistant = AssistenteCruciverba()

    st.title("🧩 Assistente Cruciverba 13x9")

    if 'griglia' not in st.session_state:
        g = [[' ' for _ in range(9)] for _ in range(13)]
        # Schema caselle nere dell'immagine fornita
        nere = [(0,4), (1,1), (1,7), (3,3), (3,5), (6,4), (9,3), (9,5), (11,1), (11,7), (12,4)]
        for r, c in nere: g[r][c] = '#'
        st.session_state.griglia = g
        st.session_state.parole_inserite = []
        st.session_state.diz_pronto = False
        st.session_state.parole_per_L = {}

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("Comandi")
        if not st.session_state.diz_pronto:
            if st.button("📚 CARICA DIZIONARIO", use_container_width=True):
                num = assistant.carica_dizionario()
                if num > 0 or st.session_state.parole_per_L:
                    st.session_state.diz_pronto = True
                    st.success(f"Dizionario pronto!")
                    st.rerun()
                else:
                    st.error("Errore nel caricamento. Riprova.")
        else:
            if st.button("➡️ INSERISCI PAROLA", use_container_width=True, type="primary"):
                segmenti = assistant.trova_segmenti(st.session_state.griglia)
                parola_trovata = False
                
                # Mischiamo i segmenti per non riempire sempre dall'alto
                random.shuffle(segmenti)

                for seg in segmenti:
                    attuale = seg['testo']
                    if " " not in attuale: continue # Già pieno
                    
                    L = seg['L']
                    pattern_str = attuale.replace(" ", ".")
                    regex_pattern = re.compile(f"^{pattern_str}$")
                    
                    candidati = st.session_state.parole_per_L.get(L, [])
                    # Filtro veloce
                    possibili = [p for p in candidati if regex_pattern.match(p) and p not in st.session_state.parole_inserite]
                    
                    if possibili:
                        scelta = random.choice(possibili)
                        for i in range(L):
                            st.session_state.griglia[seg['r']][seg['c'] + i] = scelta[i]
                        st.session_state.parole_inserite.append(scelta)
                        parola_trovata = True
                        break
                
                if not parola_trovata:
                    st.warning("Nessuna parola trovata per gli spazi rimasti.")
                else:
                    st.rerun()

            if st.button("🔄 RESET"):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()

        st.write(f"Parole inserite: {len(st.session_state.parole_inserite)}")
        for p in reversed(st.session_state.parole_inserite[-5:]):
            st.text(f"• {p}")

    with col1:
        st.markdown(render_griglia(st.session_state.griglia), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
