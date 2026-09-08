import socket #gestisce comunicazione rete e trasmissione dati
import threading #fornisce meccanismi sincronizzazione e permette esecuzione concorrente con i thread nello stesso spazio di memoria
import time
import random

# simulazione prezzi di mercato
market_data = {
    "ENI": 25.50,
    "AAPL": 280.0,
    "TSLA": 400.0,
    "NVDA": 200.0,
    "MSFT": 250.0
}
# creo mutex (Lock) per evitare race condition durante modifica dei prezzi
market_lock = threading.Lock()

# thread in background per fluttuazione dei prezzi
def simulate_market():
    while True:
        time.sleep(2) #esegue fluttuazione ogni 2 secondi
        with market_lock:
            for stock in market_data: 
                change = random.uniform(-0.02, 0.02) # per ogni titolo calcolo una percentuale in questo intervallo
                new_price = market_data[stock] * (1 + change)
                market_data[stock] = max(0.01, new_price) #limite minimo a 0.01

# gestione della comunicazione concorrente con il singolo client
def handle_client(client_socket, client_address): #parametri: socket connessione e ip/porta
    print(f"[CONNESSIONE] Nuova connessione stabilita con {client_address}")
    balance = 10000.0  #budget
    portfolio = {ticker: 0 for ticker in market_data} # crea portafoglio dello user

    try:
        while True: #ciclo continuo per continuare a ricevere comandi dal client fino a quando si disconnette
            data = client_socket.recv(1024).decode('utf-8') #converte da dati binari a stringa
            if not data:
                break #se il pacchetto è vuoto, il socket lato client è stato chiuso. chiude il ciclo
            
            command = data.strip().split() #rimuove spazi vuoti e caratteri di invio agli estremi, e split spezza il mess
            if not command:
                continue
            
            action = command[0].upper() # prende prima parola del command e la mette in MAIUSC
            
            if action == "PRICES":
                with market_lock:
                    prices_str = ", ".join([f"{ticker}: ${price:.2f}" for ticker, price in market_data.items()])
                    response = f"PREZZI CORRENTI -> {prices_str}"
            
            elif action == "BUY":
                if len(command) < 3: #controlla se utente ha inserito almeno 3 argomenti
                    response = "ERRORE: Sintassi corretta: BUY <ticker> <quantità>"
                else:
                    ticker = command[1].upper()
                    try:
                        quantity = int(command[2])
                        if quantity <= 0:
                            response = "ERRORE: La quantità deve essere almeno 1."
                        elif ticker not in market_data:
                            response = f"ERRORE: Ticker non esistente. Disponibili: {', '.join(market_data.keys())}"
                        else:
                            with market_lock:
                                price = market_data[ticker]
                            tot_cost = price * quantity #calcola costo acquisto
                            
                            if balance >= tot_cost:
                                balance -= tot_cost
                                portfolio[ticker] += quantity
                                response = f"SUCCESSO: Acquistate {quantity} quote di {ticker}. Bilancio rimanente: ${balance:.2f}"
                            else:
                                response = "ERRORE: Fondi insufficienti."
                    except ValueError:
                        response = "ERRORE: La quantità deve essere un numero intero >= 1."

            elif action == "SELL":
                if len(command) < 3:
                    response = "ERRORE: Sintassi corretta: SELL <ticker> <quantità>"
                else:
                    ticker = command[1].upper()
                    try:
                        quantity = int(command[2])
                        if quantity <= 0:
                            response = "ERRORE: La quantità deve essere un numero intero positivo."
                        elif ticker not in market_data:
                            response = f"ERRORE: Ticker non esistente. Disponibili: {', '.join(market_data.keys())}"
                        elif portfolio[ticker] < quantity:
                            response = f"ERRORE: Non possiedi abbastanza quote di {ticker}. Possedute: {portfolio[ticker]}"
                        else:
                            with market_lock:
                                price = market_data[ticker]
                            total_revenue = price * quantity
                            
                            balance += total_revenue
                            portfolio[ticker] -= quantity
                            response = f"SUCCESSO: Vendute {quantity} quote di {ticker} per ${total_revenue:.2f}. Bilancio attuale: ${balance:.2f}"
                    except ValueError:
                        response = "ERRORE: La quantità deve essere un numero intero."
            
            elif action == "PORTFOLIO":
                response = f"IL TUO PORTAFOGLIO -> Bilancio: ${balance:.2f} | Asset: {portfolio}"
                
            elif action == "QUIT":
                response = "Broker in chiusura..."
                client_socket.send(response.encode('utf-8')) #converte str di saluto in binario e la invia al client tramite socket
                break
            else:
                response = "ERRORE: Comando sconosciuto. Usa i comandi: PRICES, BUY, SELL, PORTFOLIO o QUIT."
            
            client_socket.send(response.encode('utf-8')) #prende response e la converte in binario e la trasmette al client
            
    except ConnectionResetError: # sollevata automaticamente dal SO se TCP cade
        print(f"[DISCONNESSIONE] Il client {client_address} ha chiuso la connessione bruscamente.")
    finally:
        client_socket.close() #chiude porta e socket di un client
        print(f"[DISCONNESSIONE] Connessione chiusa con {client_address}")

def start_server():
    #il server rimane in ascolto su questo IP e su questa PORT
    server_ip = "127.0.0.1"
    server_port = 50001
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #inizializza oggetto socket principale del server
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #permette di riutilizzare subito IP e PORT senza attendere SO che liberi la socket
    server.bind((server_ip, server_port)) #associa la socket all'IP e alla PORT
    server.listen() #pone socket del sevrer in ascolto passivo, rendendolo pronto ad accogliere richieste
    print(f"[AVVIO] Server finanziario in ascolto su {server_ip}:{server_port}")
    
    market_thread = threading.Thread(target=simulate_market, daemon=True) #nuovo thread daemon per la func simulate_market
    market_thread.start() #avvia thread market thread
    
    while True: #mantiene server in funzione in grado di accettare altri client
        client_socket, client_address = server.accept() #accept mette in pausa sevrer finche un client non si connette
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address)) #crea un thread per il client appena arrivato
        client_thread.start() #avvia thread del client

if __name__ == "__main__":
    start_server()