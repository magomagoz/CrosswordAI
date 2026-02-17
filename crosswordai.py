import sqlite3
import random

class DizionarioItaliano:
    def __init__(self, db_path='parole_italiane.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._crea_tabella()

    def _crea_tabella(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parole (
                id INTEGER PRIMARY KEY, 
                parola TEXT UNIQUE, 
                validata BOOLEAN DEFAULT 1
            )
        ''')
        self.conn.commit()

    def get_parole_by_lunghezza(self, lunghezza):
        self.cursor.execute("SELECT parola FROM parole WHERE LENGTH(parola)=? AND validata=1", (lunghezza,))
        return [row[0] for row in self.cursor.fetchall()]

    def parola_esiste(self, parola):
        self.cursor.execute("SELECT 1 FROM parole WHERE parola=?", (parola,))
        return self.cursor.fetchone() is not None

class CruciverbaGenerator:
    def __init__(self, righe, colonne, dizionario):
        self.righe = righe
        self.colonne = colonne
        self.dizionario = dizionario
        self.griglia = [['.' for _ in range(colonne)] for _ in range(righe)]

    def stampa_griglia(self):
        for riga in self.griglia:
            print(' '.join(riga))

    def _parole_esistenti(self):
        pass

    def genera(self):
        pass

    def _risolvi(self, posizione):
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
    dizionario = DizionarioItaliano()
    generatore = CruciverbaGenerator(righe, colonne, dizionario)
    
    print("\n--- Griglia Generata (Esempio) ---")
    print("Funzione non ancora implementata, ma l'architettura è pronta!")
