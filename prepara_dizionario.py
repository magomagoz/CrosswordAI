import requests
import json

def genera_json():
    url = "https://raw.githubusercontent.com/napolux/paroleitaliane/master/parole_italiane.txt"
    print("Scaricamento dizionario in corso...")
    
    try:
        response = requests.get(url)
        # Pulisce, converte in maiuscolo e filtra solo parole con almeno 2 lettere
        parole = [p.strip().upper() for p in response.text.splitlines() if p.strip().isalpha() and len(p.strip()) >= 2]
        
        # Rimuove duplicati trasformando in set e poi torna lista
        parole_uniche = sorted(list(set(parole)))
        
        # Salva in formato JSON
        with open("dizionario.json", "w", encoding="utf-8") as f:
            json.dump({"parole": parole_uniche}, f, ensure_ascii=False)
            
        print(f"✅ Fatto! File 'dizionario.json' creato con {len(parole_uniche)} parole.")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    genera_json()
