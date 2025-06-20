# Team Structure
- **Architect**: Claude – Defines system scope and tech stack decisions
- **Developer**: Claude – Implements enhancements per roadmap phases  
- **Reviewer**: Claude – Validates accuracy, safety, and performance

---

# Project Status - Stock Forecaster Pro v2.1.0

## Current Capabilities
- **Multi-timeframe analysis** (Daily, 4-hour, 1-hour confluence scoring)
- **60.6% validated accuracy** across 160 historical signals
- **European + US market support** (20+ exchanges)
- **RISKY_BUY detection** for high-volatility opportunities
- **Real-time prediction logging** with SQLite database
- **Enhanced confidence scoring** (+5-8% boost for EU stocks)
- **Educational explanations** (WHY each indicator matters)

## Architecture Overview
```
core/
├── analyzer.py (458 lines) - Main analysis engine + enhanced accuracy
├── multi_timeframe_analyzer.py (320 lines) - 3-timeframe confluence
├── results_database.py (380 lines) - Prediction tracking & analytics
├── data_fetcher.py (180 lines) - yfinance + company name mapping
├── models.py (35 lines) - Type-safe data structures
├── indicators.py (65 lines) - RSI, MACD, SMA calculations
└── news_analyzer.py (140 lines) - Event detection & market timing

ui/
├── server.py (95 lines) - HTTP API endpoints
├── index.html (180 lines) - Interactive web interface
└── app.js (150 lines) - Click-to-analyze frontend

validation/
├── backtest_engine.py (400 lines) - Historical accuracy testing
└── technical_validator.py (350 lines) - Mathematical verification
```

---

# Project Goals
- **Target accuracy**: Scale from 60.6% to 85%+ through roadmap implementation
- **Multi-timeframe analysis**: ✅ COMPLETED (+5-15% accuracy improvement)
- **Regional optimization**: ✅ COMPLETED (+5-8% EU market confidence)
- **Prediction tracking**: ✅ COMPLETED (SQLite logging system)
- **Cost efficiency**: Maintain <$200/month operational costs while scaling accuracy
- **Token conservation**: <3K responses, ~16K/day budget

---

# Enhancement Roadmap Status

## ✅ PHASE 1: COMPLETED (Free Improvements)
- **Multi-timeframe analysis**: 3-timeframe confluence scoring implemented
- **Regional market optimization**: EU P/E adjustments and confidence boosts
- **Results database**: Prediction logging with accuracy tracking
- **Validation framework**: 60.6% accuracy confirmed through backtesting

## 🔄 PHASE 2: IN PROGRESS (Cost: ~$150/month)
- **Market regime detection**: VIX-based volatility classification
- **Sector context integration**: Industry-specific P/E bands
- **Advanced volume analysis**: Order flow and institutional detection
- **News sentiment API**: Real-time event impact scoring

## 📋 PHASE 3: PLANNED (Cost: ~$500/month)
- **Machine learning ensemble**: Random Forest + LSTM neural networks
- **Options flow integration**: Put/call ratios and unusual activity
- **Market microstructure**: Level 2 order book analysis
- **Adaptive learning**: Auto-threshold adjustment based on results

---

# Technical Specifications

## Analysis Algorithm
```
Final Score = Multi-timeframe Confluence × (
  30% Momentum + 20% News/Events + 15% Volume + 
  15% Price Action + 10% Technical + 10% Market Timing
) + Regional Adjustments
```

## Rating Thresholds (Post-Validation Optimization)
- **BUY**: Score ≥ 0.65 (more conservative after 50% BUY accuracy)
- **RISKY_BUY**: High volatility + momentum + volume surge
- **HOLD**: 0.35 < score < 0.65 (61.1% validated accuracy)
- **SELL**: Score ≤ 0.30 (more conservative threshold)

## Performance Metrics (Validated)
- **Overall accuracy**: 60.6% directional (160 historical signals)
- **HOLD strategy**: 61.1% accuracy (capital protection working)
- **Technical indicators**: 83.3% mathematically verified
- **Database storage**: <1GB limit with auto-cleanup

---

# Implementation Protocols

## Phase-Based Development
- **Phase 2 features**: Implement market regime + sector context first
- **Cost monitoring**: Track API costs vs. accuracy improvements
- **A/B testing**: Compare enhanced vs. baseline accuracy on same stocks
- **Database analytics**: Weekly performance trend analysis

## Code Quality Standards
- **Type hints**: All functions have proper typing
- **Educational reasoning**: WHY explanations for all trading logic
- **Error handling**: Graceful fallbacks for data/API issues
- **Performance**: Sub-3 second analysis for individual stocks
- **Documentation**: Auto-update system tracks all changes

## Accuracy Improvement Protocol
1. **Baseline measurement**: Document current 60.6% accuracy
2. **Feature implementation**: Add one enhancement at a time
3. **Validation testing**: Measure accuracy impact on 50+ historical signals
4. **ROI analysis**: Cost vs. accuracy improvement assessment
5. **Threshold optimization**: Adjust BUY/SELL criteria based on results

---

# Database & Analytics

## Prediction Logging (SQLite)
```sql
predictions: ticker, rating, confidence, price, technical_score, 
            momentum_score, multi_timeframe_score, confluence_score
            
prediction_results: actual returns (1d, 3d, 7d), direction accuracy,
                   max drawdown, max gain

performance_metrics: weekly accuracy trends, rating-specific performance
```

## Analytics Dashboard Capabilities
- **Accuracy tracking**: By time period, rating type, market conditions
- **Top performers**: Stocks with highest prediction accuracy
- **Trend analysis**: Weekly/monthly performance patterns
- **Cost tracking**: API usage and ROI metrics

---

# Approval Process
- **Architect**: Defines roadmap priorities and technical approaches
- **Developer**: Implements features with validation testing
- **Reviewer**: Validates accuracy improvements and cost-effectiveness
- **Manual approval**: Required for API cost increases >$50/month

---

# Communication Protocols
- **Feature implementation**: "Implement Phase 2: Market Regime Detection"
- **Accuracy validation**: "Test accuracy impact of [feature] on 50 historical signals"
- **Performance review**: "Analyze prediction database for last 30 days"
- **Roadmap updates**: "Update roadmap based on [specific accuracy/cost results]"

---

# Success Metrics & Targets

## Accuracy Targets by Phase
- **Current (Phase 1)**: 60.6% baseline ✅
- **Phase 2 target**: 70-75% (+10-15 percentage points)
- **Phase 3 target**: 85%+ (+25 percentage points)

## Cost Efficiency Targets
- **Phase 2**: <$150/month for 70%+ accuracy
- **Phase 3**: <$500/month for 85%+ accuracy
- **ROI threshold**: Accuracy improvement must justify cost increase

## Database Limits
- **Storage**: <1GB total (50k prediction limit with auto-cleanup)
- **Performance**: <3 second individual analysis
- **Retention**: 90 days of detailed prediction results

---

# Current State Documentation
Last updated: 2025-06-20 23:38  
Active features: Multi-timeframe analysis, Database logging, Regional optimization  
Codebase: 9 Python files, 2,278+ total lines of code  
Validation status: 60.6% accuracy confirmed on real historical data