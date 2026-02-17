import sqlite3

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

# Esempio di creazione tabella (da eseguire una tantum)
# CREATE TABLE parole (id INTEGER PRIMARY KEY, parola TEXT UNIQUE, validata BOOLEAN DEFAULT 1);
