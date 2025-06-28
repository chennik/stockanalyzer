# Handover Notes for Next Claude

## 🚀 Quick Start Guide

### Starting the Server
```bash
# Navigate to project directory
cd /Users/yannick/Documents/Code/stockanalyzer

# Start the server
python3 ui/server.py

# Server runs on: http://localhost:8000
# Check logs if issues: tail -f ui/server*.log
```

### Restarting After Code Changes
```bash
# Kill existing server
pkill -f "python.*server.py"

# Wait a moment
sleep 2

# Start fresh
python3 ui/server.py
```

## 📊 Current System Status

### What's Working Well ✅
- **Professional Analysis**: 65-75% confidence for quality stocks
- **Retail Level**: 60-69% confidence 
- **Risk/Reward Calculator**: EUR-based profit calculations
- **European Stocks**: Full integration in top 10 scanner
- **UI Features**: All tabs, calculators, and filters functional

### Known Issues 🔧
- **Confidence Levels**: Still need fine-tuning for edge cases
- **Institutional Level**: 85%+ rarely achieved (may need adjustment)
- **Some Stocks**: Showing 0% confidence due to data issues

## 📋 Priority TODO List

### High Priority
1. **Improve Confidence Calculation**
   - Current: Capped around 75% even with all enhancements
   - Target: Should reach 80-85% for exceptional setups
   - Files: `core/analyzer.py:367-393` (calculate_confidence function)

2. **Fine-tune Quality Thresholds**
   - Review thresholds in `core/quality_standards.py:463-479`
   - Professional requires 65% but validation requires 75%
   - Consider adjusting for more realistic targets

3. **Fix Zero Confidence Issues**
   - Some stocks (NVDA, TSLA) showing 0% confidence
   - Check data fetching and calculation pipeline
   - May be related to missing data or calculation errors

### Medium Priority
4. **Optimize Algorithm Weights**
   - Review scoring weights in analyzer.py
   - Consider market regime adjustments
   - Test with volatile vs stable market conditions

5. **Enhance News Sentiment Impact**
   - Currently minimal impact on confidence
   - Consider boosting weight for major news events
   - File: `core/news_sentiment_analyzer.py`

6. **Add More European Exchanges**
   - Currently covers major exchanges
   - Consider adding Nordic, Eastern European markets
   - File: `core/data_fetcher.py:538-576`

### Low Priority
7. **Performance Optimization**
   - Top stocks scan takes 10-15 seconds
   - Consider caching or reducing parallel requests
   - Monitor API rate limits

8. **UI Polish**
   - Add loading animations
   - Improve mobile responsiveness
   - Consider dark mode

## 🔍 Key Files to Review

### Core Analysis Engine
- `core/analyzer.py` - Main technical analysis (confidence calculation)
- `core/professional_analyzer.py` - Professional wrapper with quality standards
- `core/quality_standards.py` - Thresholds and validation logic

### Confidence Boosters
- `core/multi_timeframe_analyzer.py` - Should add 5-15% confidence
- `core/institutional_indicators.py` - Should add 10-15% confidence
- `core/algo_forecast.py` - Pattern detection and forecasting

### UI Components
- `ui/app.js` - Frontend logic and display
- `ui/server.py` - API endpoints and data processing
- `ui/index.html` - UI structure and styling

## 🧪 Testing Approach

### Test Confidence Levels
```python
from core.professional_analyzer import ProfessionalStockAnalyzer
from core.quality_standards import QualityLevel

# Test different quality levels
analyzer = ProfessionalStockAnalyzer(QualityLevel.PROFESSIONAL)
result = analyzer.analyze_stock_professional('AAPL')
print(f"Confidence: {result.confidence}, Quality: {result.quality_assurance.quality_level}")
```

### Debug Low Confidence
```python
# Check each component's contribution
from core.analyzer import analyze_technical
from core.data_fetcher import fetch_stock_data

data = fetch_stock_data('AAPL')
result = analyze_technical(data)
print(f"Base confidence: {result.confidence}")
# Then check multi-timeframe and institutional boosts
```

## 💡 Improvement Ideas

1. **Dynamic Confidence Adjustment**
   - Boost confidence during strong trends
   - Reduce during high volatility/uncertainty
   - Consider VIX levels for market regime

2. **Machine Learning Integration**
   - Train on historical success rates
   - Adjust weights based on outcomes
   - Already have database tracking predictions

3. **Sector-Specific Analysis**
   - Tech stocks need different thresholds
   - Energy stocks correlate with commodities
   - Biotech needs news sentiment weight

## 🛠️ Development Tips

1. **Always Test UI Changes**
   - Changes to server.py need restart
   - Browser cache can cause issues (hard refresh)
   - Check browser console for JS errors

2. **Monitor Server Logs**
   - Delisted stocks show errors (normal)
   - Watch for timeout issues
   - API rate limits can cause failures

3. **Database Maintenance**
   - SQLite database tracks predictions
   - Located at `ui/stock_forecaster_results.db`
   - Can query for accuracy analysis

## 📈 Success Metrics

Target improvements:
- Professional level: 65% → 75-80% confidence
- Reduce "insufficient quality" rejections by 50%
- Institutional level: Make achievable for top 5% of setups
- Risk/Reward: More stocks with 1.5+ ratios

## 🎯 Where to Start

1. Run the server and test current state
2. Analyze why confidence is limited to ~75%
3. Review the confidence calculation pipeline
4. Test with high-momentum stocks that should score higher
5. Adjust thresholds based on findings

Good luck! The system is well-structured and close to optimal performance. Focus on fine-tuning the confidence calculations and thresholds to make all quality levels more practical and achievable.