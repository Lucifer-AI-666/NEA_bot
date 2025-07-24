import os
import json

def carica_memoria(percorso):
    with open(percorso, 'r') as f:
        return json.load(f)

def main():
    modello = os.getenv("OLLAMA_MODEL", "gpt")
    print(f"Jarbot avviato con modello: {modello}")
    # Logica semplificata: lettura della memoria e stampa vocazione
    memoria = carica_memoria("etica_scrittore.json")
    print("Vocazione:", memoria.get("vocazione"))

if __name__ == "__main__":
    main()
