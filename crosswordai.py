import sqlite3
import random
from database import DizionarioItaliano
from generatore import CruciverbaGenerator

class DizionarioItaliano:
    def __init__(self, db_path='parole_italiane.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cri

    def get_parole_by_lunghezza(self, lunghezza):
        """Restituisce tutte le parole di una data lunghezza."""
        self.cursor.execute("SELECT parola FROM parole WHERE LENGTH(parola)=? AND validata=1", (lunghezza,))
        return [row[0] for row in self.cursor.fetchall()]

    def parola_esiste(self, parola):
        """Controlla se una parola esiste nel dizionario."""
        self.cursor.execute("SELECT 1 FROM parole WHERE parola=?", (parola,))
        return self.cursor.fetchone() is not None

class CruciverbaGenerator:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        # Griglia: matrice di caratteri, '.' rappresenta una cella vuota
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]

    def stampa_griglia(self):
        for riga in self.griglia:
            print(' '.join(riga))

    def _parole_esistenti(self):
        """Estrae le parole già formate (orizzontali e verticali) dalla griglia."""
        # Questa funzione è complessa: deve scorrere righe e colonne
        # e ricostruire le parole come stringhe, fermandosi agli spazi vuoti.
        pass

    def genera(self):
        """Avvia il processo di generazione."""
        # 1. Scegli una parola orizzontale di partenza a caso e posizionala.
        # 2. Chiama la funzione ricorsiva di risoluzione.
        # 3. Se la funzione fallisce, riprova con un'altra parola iniziale.
        pass

    def _risolvi(self, posizione):
        """Funzione ricorsiva di backtracking."""
        # 1. Se la griglia è piena, abbiamo finito!
        # 2. Altrimenti, trova la prossima cella vuota.
        # 3. Prova a inserire una lettera che sia valida per tutte le parole (orizzontali e verticali) che la attraversano.
        # 4. Se la lettera è valida, chiama _risolvi(posizione+1).
        # 5. Se la chiamata fallisce, prova la lettera successiva.
        # 6. Se nessuna lettera funziona, fai backtracking (torna indietro).
        pass

if __name__ == "__main__":
    print("=== GENERATORE DI CRUCIVERBA ITALIANI ===")
    try:
        righe = int(input("Inserisci il numero di righe: "))
        colonne = int(input("Inserisci il numero di colonne: "))
    except ValueError:
        print("Per favore, inserisci numeri validi.")
        exit()

    print(f"\nGenerazione griglia {righe}x{colonne} in corso...")

    # Inizializza il dizionario
    dizionario = DizionarioItaliano()
    
    # Crea e avvia il generatore
    generatore = CruciverbaGenerator(righe, colonne, dizionario)
    
    # QUI VA INSERITA LA LOGICA DI GENERAZIONE (es. generatore.genera())
    # Per ora, simuliamo un output.
    
    print("\n--- Griglia Generata (Esempio) ---")
    # generatore.stampa_griglia()
    print("Funzione non ancora implementata, ma l'architettura è pronta!")
