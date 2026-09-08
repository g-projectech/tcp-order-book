import socket

def run_client(): #esecuzione client
    server_ip = "127.0.0.1" #coordinate server a cui connettersi
    server_port = 50001
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # crea oggetto socket del client. {AF_inet è ipv4; SOCK_STREAM protocollo TCP}
    
    try:
        client.connect((server_ip, server_port)) #tenta di stabilire connessione tra server e client
        print("[CONNESSIONE] Connesso al server.")
        print("Comandi disponibili: PRICES | BUY <ticker> <quantità> | SELL <ticker> <quantità> | PORTFOLIO | QUIT")
        
        while True:
            message = input("\nInserisci comando: ")
            if not message.strip():
                continue
                
            client.send(message.encode('utf-8')) #converte str e la invia al server
            
            response = client.recv(1024).decode('utf-8') #la risposta del server viene convertita in una str
            print(f"[SERVER]: {response}")
            
            if message.upper().strip() == "QUIT":
                break
                
    except ConnectionRefusedError:
        print("[ERRORE] Impossibile connettersi. Il server è avviato?")
    finally: #eseguito sempre
        client.close() #chiude socket del client
        print("[INFO] Connessione terminata.")

if __name__ == "__main__":
    run_client()