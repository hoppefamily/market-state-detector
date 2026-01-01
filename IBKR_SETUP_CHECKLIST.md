# IB Gateway / TWS Setup Checklist / Einrichtungs-Checkliste

You're getting a connection refused error. Here's what to check:
Verbindungsfehler - Das müssen Sie überprüfen:

## 1. Is IB Gateway / TWS Running? / Läuft IB Gateway / TWS?

- Launch IB Gateway or TWS / Starten Sie IB Gateway oder TWS
- Login with your credentials (paper or live account) / Melden Sie sich an (Demo- oder Live-Konto)
- Keep it running in the background / Lassen Sie es im Hintergrund laufen

## 2. Find Your Port Number / Port-Nummer finden

### In IB Gateway (Deutsch):
1. Klicken Sie auf **Konfigurieren** → **Einstellungen** (Zahnrad-Symbol)
2. Gehen Sie zu **API** → **Einstellungen**
3. Suchen Sie nach **Socket Port** (oder **Port**):
   - Demo-Trading (Paper): **4002**
   - Live-Trading: **4001**

### In IB Gateway (English):
1. Click **Configure** → **Settings** (gear icon)
2. Go to **API** → **Settings**
3. Look for **Socket port**:
   - Paper trading: **4002**
   - Live trading: **4001**

### In TWS:
1. Go to **File** / **Datei** → **Global Configuration** / **Globale Konfiguration** → **API** → **Settings** / **Einstellungen**
2. Look for **Socket port** / **Socket Port**:
   - Paper trading: **7497**
   - Live trading: **7496**

## 3. Enable API Connections / API-Verbindungen aktivieren

In the same settings window / Im selben Einstellungsfenster:

**Important / Wichtig:** In neueren Versionen kann die Bezeichnung abweichen. Suchen Sie nach:

1. ✓ **"Enable ActiveX and Socket Clients"**
   - OR / ODER: **"Socket-Clients aktivieren"**
   - OR / ODER: **"API aktivieren"**
   - OR / ODER: The option may be enabled by default / Möglicherweise standardmäßig aktiviert

2. ✓ **"Allow connections from localhost only"** / **"Nur Verbindungen von localhost erlauben"** (for security / für Sicherheit)

3. Optional: **"Read-Only API"** / **"Schreibgeschützte API"** (prevents accidental trades / verhindert versehentliche Trades)

4. Click **OK** / **Übernehmen** and restart IB Gateway/TWS / und IB Gateway/TWS neu starten

**Note / Hinweis:** If you don't see the "Enable ActiveX" option, the API might already be enabled by default. Just make sure the port number is correct.
Falls Sie die Option "Enable ActiveX" nicht sehen, ist die API möglicherweise bereits standardmäßig aktiviert. Stellen Sie einfach sicher, dass die Port-Nummer korrekt ist.

## 4. Test Connection

Once configured, run:

```bash
python check_ibkr_connection.py
```

Select your port when prompted.

## 5. Update Your Code

Use the correct port in your scripts:

```python
# For IB Gateway Paper Trading (port 4002)
data = fetch_ibkr_data('AAPL', days=30, port=4002)

# For IB Gateway Live Trading (port 4001)
data = fetch_ibkr_data('AAPL', days=30, port=4001)

# For TWS Paper Trading (port 7497)
data = fetch_ibkr_data('AAPL', days=30, port=7497)

# For TWS Live Trading (port 7496)
data = fetch_ibkr_data('AAPL', days=30, port=7496)
```

## Common Issues

### "Connection Refused" Error
- IB Gateway/TWS not running → Start it and login
- Wrong port number → Check settings (see step 2)
- API not enabled → Enable it (see step 3)
- Firewall blocking → Add exception for Python/IB Gateway

### "Not Connected" Error
- Call `connect()` before `fetch_daily_bars()`
- Or use context manager: `with IBKRDataFetcher(port=4002) as fetcher:`

### No Data Returned
- Symbol not found → Verify ticker symbol
- No market data subscription → Check IBKR subscriptions
- Requesting too much history → Reduce days parameter

## Quick Test

Try this command to test connectivity (replace 4002 with your port):

```bash
nc -zv 127.0.0.1 4002
```

If successful, you should see: "Connection to 127.0.0.1 port 4002 [tcp/*] succeeded!"

If it fails, the port is not open (IB Gateway not configured correctly).

## Still Having Issues?

1. Restart IB Gateway/TWS after changing settings
2. Check IB Gateway logs for errors
3. Verify you're using a funded account (paper or live)
4. Contact Interactive Brokers support for account issues
