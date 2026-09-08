# Order Book - TCP Socket

The program allows multiple clients to connect simultaneously to a financial server to view simulated stock prices, buy shares, sell assets, and monitor their portfolios.

## Technical Specifications

* **Network Communication:** Implemented via low-level TCP sockets (`AF_INET`, `SOCK_STREAM`).
* **Multi-threaded Architecture:** Concurrent management of connected clients via dedicated threads.
* **Thread Safety (Synchronization):** Use of mutexes (`threading.Lock`) to prevent race conditions during the updating and reading of market prices.
* **Zero External Dependencies:** Developed exclusively using native modules from the Python Standard Library (`socket`, `threading`, `time`, `random`).

---

## Prerequisites

* Python 3.8 or later installed (no `pip` installations required).

## How to Run the Project

Commands should be run from the repository's root directory.

### 1. Start the Server

Open a terminal and start the server:

```bash
python src/server.py
```

The server will listen on `127.0.0.1:50001` and start the price fluctuation thread.

### 2. Start One or More Clients

Open one or more separate terminals and run the following in each one:

```bash
python src/client.py
```

## Commands Available in the Client

Once the connection is established, you can type:

| **Command** | **Description** |
| --- | --- |
| `PRICES` | Displays stock prices (updated in real time) |
| `BUY <ticker> <quantity>` | Buys a specified number of shares of a stock (e.g., `BUY AAPL 5`) |
| `SELL <ticker> <quantity>` | Sells the shares held in the portfolio (e.g., `SELL AAPL 2`) |
| `PORTFOLIO` | Displays remaining cash and held shares |
| `QUIT` | Ends the session and closes the connection with the broker |

---

> **Note:** Stock prices are hardcoded in memory and fluctuate randomly. No external APIs or web requests are used.
