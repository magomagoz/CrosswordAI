import streamlit as st

class MotoreArchitetto:
    """
    La classe ora contiene solo funzioni pure o metodi statici.
    Non memorizza dati al suo interno, ma riceve e restituisce lo stato attuale.
    """
    @staticmethod
    def inizializza_stato(rows, cols):
        return {
            'rows': rows,
            'cols': cols,
            'griglia': [[' ' for _ in range(cols)] for _ in range(rows)],
            'parole_usate': [],
            'storico_undo': [],
            'storico_redo': []
        }

    @staticmethod
    def salva_stato(stato):
        # Crea una copia pulita dello stato attuale prima di modificarlo
        copia_griglia = [r[:] for r in stato['griglia']]
        copia_parole = list(stato['parole_usate'])
        stato['storico_undo'].append({'griglia': copia_griglia, 'parole_usate': copia_parole})
        stato['storico_redo'] = []

    @staticmethod
    def annulla(stato):
        if stato['storico_undo']:
            copia_griglia = [r[:] for r in stato['griglia']]
            copia_parole = list(stato['parole_usate'])
            stato['storico_redo'].append({'griglia': copia_griglia, 'parole_usate': copia_parole})
            
            ultimo = stato['storico_undo'].pop()
            stato['griglia'] = ultimo['griglia']
            stato['parole_usate'] = ultimo['parole_usate']
            return True
        return False

    @staticmethod
    def ripristina(stato):
        if stato['storico_redo']:
            copia_griglia = [r[:] for r in stato['griglia']]
            copia_parole = list(stato['parole_usate'])
            stato['storico_undo'].append({'griglia': copia_griglia, 'parole_usate': copia_parole})
            
            prossimo = stato['storico_redo'].pop()
            stato['griglia'] = prossimo['griglia']
            stato['parole_usate'] = prossimo['parole_usate']
            return True
        return False

    @staticmethod
    def inserisci_parola(stato, parola, r, c, orient):
        MotoreArchitetto.salva_stato(stato)
        p = parola.upper()
        
        # Aggiunge alla lista delle parole usate se non presente
        if not any(item['p'] == p and item['r'] == r+1 and item['c'] == c+1 for item in stato['parole_usate']):
            stato['parole_usate'].append({'p': p, 'o': orient, 'r': r+1, 'c': c+1})
            
        # Scrive fisicamente sulla griglia
        for i in range(len(p)):
            rr, cc = (r+i, c) if orient == 'V' else (r, c+i)
            stato['griglia'][rr][cc] = p[i]

    @staticmethod
    def toggle_nera(stato, r, c):
        MotoreArchitetto.salva_stato(stato)
        stato['griglia'][r][c] = '#' if stato['griglia'][r][c] != '#' else ' '

    @staticmethod
    def elimina_parola(stato, parola_da_eliminare):
        MotoreArchitetto.salva_stato(stato)
        p = parola_da_eliminare.upper()
        nuova_lista = [item for item in stato['parole_usate'] if item['p'] != p]
        
        if len(nuova_lista) == len(stato['parole_usate']):
            return False
            
        stato['parole_usate'] = nuova_lista
        # Ricostruisce la griglia da zero usando le caselle nere rimaste e le parole rimaste
        # (Per semplicità riascolta la griglia mantenendo solo le nere attuali)
        for r in range(stato['rows']):
            for c in range(stato['cols']):
                if stato['griglia'][r][c] != '#':
                    stato['griglia'][r][c] = ' '
                    
        for item in stato['parole_usate']:
            p_curr, orient, r_curr, c_curr = item['p'], item['o'], item['r']-1, item['c']-1
            for i in range(len(p_curr)):
                rr, cc = (r_curr+i, c_curr) if orient == 'V' else (r_curr, c_curr+i)
                stato['griglia'][rr][cc] = p_curr[i]
        return True

    @staticmethod
    def trova_incastri(stato, parola):
        validi = []
        L = len(parola)
        p_upper = parola.upper()
        vuota = not any(c.isalpha() for r in stato['griglia'] for c in r)
        
        for r in range(stato['rows']):
            for c in range(stato['cols']):
                for o in ['O', 'V']:
                    if (o == 'O' and c + L > stato['cols']) or (o == 'V' and r + L > stato['rows']): 
                        continue
                    match, incrocio = True, False
                    for i in range(L):
                        rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                        cel = stato['griglia'][rr][cc]
                        if cel == '#': 
                            match = False
                            break
                        if cel.isalpha():
                            if cel != p_upper[i]: 
                                match = False
                                break
                            incrocio = True
                    if match and (vuota or incrocio):
                        validi.append({'r': r, 'c': c, 'o': o})
        return validi

    @staticmethod
    def calcola_numeri(stato):
        numeri = {}
        contatore = 1
        for r in range(stato['rows']):
            for c in range(stato['cols']):
                if stato['griglia'][r][c] == '#':
                    continue
                inizio_o = (c == 0 or stato['griglia'][r][c-1] == '#') and (c + 1 < stato['cols'] and stato['griglia'][r][c+1] != '#')
                inizio_v = (r == 0 or stato['griglia'][r-1][c] == '#') and (r + 1 < stato['rows'] and stato['griglia'][r+1][c] != '#')
                if inizio_o or inizio_v:
                    numeri[(r, c)] = contatore
                    contatore += 1
        return numeri

    @staticmethod
    def render_html(stato, anteprima=None):
        numeri = MotoreArchitetto.calcola_numeri(stato)
        html = '<table style="border-collapse: collapse; margin: 0 auto; border: 3px solid black; background-color: white;">'
        
        temp_grid = [r[:] for r in stato['griglia']]
        if anteprima:
            p, r, c, o = anteprima['p'], anteprima['r'], anteprima['c'], anteprima['o']
            for i in range(len(p)):
                rr, cc = (r+i, c) if o == 'V' else (r, c+i)
                if 0 <= rr < stato['rows'] and 0 <= cc < stato['cols']:
                    temp_grid[rr][cc] = f'<span style="color:#007bff;">{p[i]}</span>'
        
        for r in range(stato['rows']):
            html += '<tr>'
            for c in range(stato['cols']):
                val = temp_grid[r][c]
                bg = "black" if val == "#" else "white"
                display = val if (val != " " and val != "#") else "&nbsp;"
                
                numero_html = f'<div style="position: absolute; top: 2px; left: 2px; font-size: 9px; color: #555;">{numeri[(r,c)]}</div>' if (r,c) in numeri else ""
                html += f'<td style="border: 1px solid #444; width: 40px; height: 40px; text-align: center; font-weight: bold; background: {bg}; position: relative; padding: 0;"><div style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">{numero_html}<span>{display}</span></div></td>'
            html += '</tr>'
        html += '</table>'
        return html

def main():
    st.set_page_config(page_title="Editor Blindato", layout="wide")
    
    # Inizializzazione dello stato nativo (Dizionario)
    if 'schema' not in st.session_state:
        st.session_state.schema = MotoreArchitetto.inizializza_stato(13, 9)
    
    stato = st.session_state.schema

    with st.sidebar:
        st.title("⚙️ Pannello di controllo")
        st.header("📐 Seleziona Schema")
        
        formati = {
            "Incroci obbligati": (13, 9),
            "Ricerca di parole crociate": (12, 14),
            "Parole crociate senza schema": (12, 22),
            "Parole crociate bifrontali": (12, 18)
        }
        
        scelta = st.selectbox("Scegli formato:", list(formati.keys()))
        rows, cols = formati[scelta]
        
        if st.button("Applica Schema"):
            st.session_state.schema = MotoreArchitetto.inizializza_stato(rows, cols)
            st.rerun()

        st.divider()
        st.subheader("✍️ Inserimento Parola")
        p_in = st.text_input("Parola (libera):", key="input_parola").upper().strip()
        anteprima_data = None
        
        if p_in:
            risultato = MotoreArchitetto.trova_incastri(stato, p_in)
            if risultato:
                idx = st.selectbox("Posizioni:", range(len(risultato)), format_func=lambda x: f"{risultato[x]['o']} - R{risultato[x]['r']+1}, C{risultato[x]['c']+1}")
                anteprima_data = {'p': p_in, 'r': risultato[idx]['r'], 'c': risultato[idx]['c'], 'o': risultato[idx]['o']}
                
                if st.button("🚀 CONFERMA E SCRIVI"):
                    MotoreArchitetto.inserisci_parola(stato, p_in, risultato[idx]['r'], risultato[idx]['c'], risultato[idx]['o'])
                    st.rerun()
            else: 
                st.error("Nessun incastro possibile.")

        st.divider()
        st.subheader("⬛ Caselle Nere")
        c1, c2 = st.columns(2)
        r_n = c1.number_input("Riga", 1, stato['rows'], 1) - 1
        c_n = c2.number_input("Col", 1, stato['cols'], 1) - 1
        
        if st.button("Metti/Togli Nera"):
            MotoreArchitetto.toggle_nera(stato, r_n, c_n)
            st.rerun()
        
        st.divider()
        st.subheader("🔄 Controllo Mosse")
        c1, c2 = st.columns(2)
        if c1.button("⬅️ ANNULLA"):
            if MotoreArchitetto.annulla(stato): 
                st.rerun()
        if c2.button("➡️ RIPRISTINA"):
            if MotoreArchitetto.ripristina(stato): 
                st.rerun()
    
        st.divider()
        st.subheader("🗑️ Elimina Parola")
        p_del = st.text_input("Scrivi parola da rimuovere:", key="del_parola").upper().strip()
        if st.button("Rimuovi dallo schema"):
            if MotoreArchitetto.elimina_parola(stato, p_del):
                st.success(f"Parola '{p_del}' rimossa!")
                st.session_state["del_parola"] = "" 
                st.rerun()
            else:
                st.error("Parola non trovata!")
    
        st.divider()

    st.title("🧩 Griglia Cruciverba")
    
    # Rendering HTML pulito dentro un flex-box nativo per i numeretti
    codice_tabella = MotoreArchitetto.render_html(stato, anteprima_data)
    st.markdown(codice_tabella, unsafe_allow_html=True)
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1: 
        st.subheader("Orizzontali")
        orizzontali = [item for item in stato['parole_usate'] if item['o'] == 'O']
        if orizzontali:
            for item in orizzontali:
                st.write(f"R{item['r']} C{item['c']}: **{item['p']}**")
        else:
            st.write("Nessuna parola.")

    with col2: 
        st.subheader("Verticali")
        verticali = [item for item in stato['parole_usate'] if item['o'] == 'V']
        if verticali:
            for item in verticali:
                st.write(f"R{item['r']} C{item['c']}: **{item['p']}**")
        else:
            st.write("Nessuna parola.")

if __name__ == "__main__":
    main()
