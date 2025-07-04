# Stock Analyzer Server Guide

## Quick Start/Stop Scripts

```bash
# Start the server
./start_server.sh

# Stop the server
./stop_server.sh
```

## Manual Commands

### Starting the Server

```bash
python3 ui/server.py
```

The server will start on **http://localhost:8000**

### Stopping the Server

**Option 1:** Press `Ctrl+C` in the terminal where the server is running

**Option 2:** Kill all Python server processes:
```bash
pkill -f "python.*server.py"
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Then restart server
python3 ui/server.py
```

### Running in Background
```bash
# Start in background
nohup python3 ui/server.py > server.log 2>&1 &

# Check if running
ps aux | grep server.py

# View logs
tail -f server.log
```

### Browser Can't Connect
- Use `http://` not `https://`
- Try `http://127.0.0.1:8000` instead of localhost
- Clear browser cache or use incognito mode
- Check firewall settings

### Quick Status Check
```bash
# Test if server responds
curl -I http://localhost:8000
```