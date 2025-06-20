# Stock Forecaster Quick Reference

## 🎯 What We Built
A professional stock analysis tool with:
- **European + US market support**
- **RISKY_BUY opportunities detection**
- **Educational explanations** (WHY each indicator matters)
- **Click-to-analyze UI**
- **Real-time data** from yfinance

## 🚀 Key Commands

### Start the Application
```bash
cd /path/to/stock-forecaster/ui
python server.py
# Open http://localhost:8000
```

### Test Specific Features
```bash
# European stock
curl "http://localhost:8000/api/analyze?query=rheinmetall"

# Top 10 opportunities
curl "http://localhost:8000/api/top-stocks"

# High volatility stock
curl "http://localhost:8000/api/analyze?query=RIOT"
```

## 📊 Rating System
- **BUY**: Score ≥ 0.55 (bullish indicators align)
- **RISKY_BUY**: High volatility + momentum (>2.5% move)
- **HOLD**: Mixed signals (0.35 < score < 0.55)
- **SELL**: Score ≤ 0.35 (bearish indicators)

## 🔧 Core Algorithm
```
Final Score = 
  30% Momentum (price acceleration)
  20% News/Events (volume spikes, gaps)
  15% Volume (institutional activity)
  15% Price Action (daily moves)
  10% Technical (RSI, MACD, MA)
  10% Market Timing (power hour bonus)
```

## 💡 Key Insights
1. **Conservative = Good**: No false BUY signals protects capital
2. **RISKY_BUY = Opportunity**: High risk but potential quick gains
3. **Volume Matters**: >1.5x average = institutional interest
4. **Timing Counts**: Power hour & opening hour get bonuses
5. **Education Built-in**: Every indicator explains WHY it matters

## 🐛 Common Issues
- **No BUY signals?** Market might be neutral/bearish - system working correctly
- **Can't find EU stock?** Use ticker with suffix (e.g., SAP.DE not just SAP)
- **Slow loading?** First scan takes time, subsequent ones are faster

## 📁 Key Files
- `analyzer.py:338` - RISKY_BUY logic
- `analyzer.py:119` - RSI explanations
- `data_fetcher.py:58` - Company name mappings
- `news_analyzer.py` - Event detection
- `index.html` - UI enhancements
- `app.js:150` - Click-to-analyze logic