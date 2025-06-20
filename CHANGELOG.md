# Stock Forecaster Changelog


## [Auto-Check] - 2025-06-20 21:40
- Documentation auto-updated
- Codebase scanned for changes

## [2.0.0] - 2025-06-20 - Major Enhancement Release

### 🚀 New Features

#### European Stock Support
- **Added full European market support** - Now supports stocks from all major EU exchanges
- **Company name translation** - Search "rheinmetall" automatically finds RHM.DE
- **Exchange suffixes supported**: .DE (Germany), .AS (Netherlands), .PA (France), .SW (Switzerland), .MI (Italy), .MC (Spain), .L (UK)
- **Enhanced company database** - Added 100+ European company name mappings

#### RISKY_BUY Rating System
- **New rating type: RISKY_BUY** - Identifies high-risk/high-reward opportunities
- **Risk warnings** - Clear explanations of what makes trades risky
- **Opportunity highlights** - Shows potential upside scenarios
- **Visual indicators** - Orange pulsing animation for RISKY_BUY in UI

#### Enhanced Trading Algorithm
- **Momentum scoring (0-5 scale)** - Measures short-term price momentum
- **Volume surge detection** - Identifies unusual trading activity (2x+ normal volume)
- **News event analysis** - Detects earnings, gaps, and volatility spikes
- **Market timing factors** - Power hour and opening hour optimizations
- **Parallel processing** - 86% faster scanning (from 18s to 2.5s)

#### Educational Explanations
- **WHY explanations for all indicators** - Every technical signal now explains its significance
- **Trading education built-in** - Learn why RSI, MACD, and trend patterns matter
- **Risk context** - Understand what makes certain trades risky
- **Professional insights** - Trade like institutions with detailed reasoning

#### UI/UX Improvements
- **Click-to-analyze interface** - Click any top 10 stock to see analysis below
- **Smooth scrolling** - Automatic scroll to detailed analysis
- **Visual rating indicators** - 🔥 RISKY_BUY, 🟢 BUY, 🟡 HOLD, 🔴 SELL
- **Active stock highlighting** - Blue border shows selected stock
- **Refresh button** - Quick rescan for latest opportunities
- **Daily % changes** - See price movements at a glance

### 🔧 Technical Improvements

#### Performance
- **Concurrent analysis** - ThreadPoolExecutor with 8-10 workers
- **Reduced data fetching** - 5-day instead of 1-month periods for speed
- **Smart pre-screening** - Skip stocks without momentum early
- **Optimized stock universe** - Focus on high-volatility tradeable stocks

#### Algorithm Enhancements
- **Multi-factor scoring**: Momentum (30%) + News (20%) + Volume (15%) + Price Action (15%) + Technicals (10%) + Timing (10%)
- **Aggressive thresholds**: BUY at 0.55 score (was 0.7), more opportunities
- **Fallback system**: Always shows 10 results even in neutral markets
- **German market optimization**: Prioritizes stocks accessible via German brokers

### 📊 Current Capabilities

1. **Analyze ANY stock**: US, European, Asian markets supported
2. **Real-time data**: Live prices, volumes, and technical indicators
3. **Risk assessment**: Clear warnings for volatile trades
4. **Educational value**: Learn trading while using the tool
5. **Fast scanning**: 10 opportunities in under 3 seconds
6. **Mobile-friendly**: Responsive design works on all devices

### 🐛 Bug Fixes
- Fixed European ticker validation (RHM.DE now works correctly)
- Fixed partial name matching (no more "rheinmetall" → "META" errors)  
- Fixed BUY rating generation (was too conservative)
- Fixed UI scrolling issues
- Fixed delisted stock warnings (SQ, SPLK, PXD)

### 📈 Stock Universe Updates
- Removed delisted stocks (SQ, SPLK, PXD)
- Added high-volatility stocks (RIOT, MARA, COIN, PLTR)
- Added biotech opportunities (MRNA, BNTX, GILD)
- Added meme stocks (GME, AMC, BB)
- Added Chinese ADRs (BABA, NIO, XPEV)

---

## [1.0.0] - 2025-06-19 - Initial Release
- Basic technical analysis (RSI, MACD, SMA)
- US stock support only
- Simple BUY/HOLD/SELL ratings
- Basic web interface
- Manual stock entry required