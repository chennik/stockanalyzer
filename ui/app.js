let priceChart = null;

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const input = document.getElementById('tickerInput').value.trim();
    if (!input) return;
    
    // UI state
    document.getElementById('errorMsg').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = true;
    
    try {
        console.log('Fetching analysis for:', input);
        const response = await fetch(`/api/analyze?query=${encodeURIComponent(input)}`);
        const data = await response.json();
        
        console.log('API response received:', data);
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        console.log('About to call displayResults');
        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
});

function displayResults(data) {
    console.log('displayResults called with data:', data);
    
    // Basic info
    document.getElementById('stockName').textContent = data.ticker;
    document.getElementById('rating').textContent = data.rating;
    document.getElementById('rating').className = `rating ${data.rating}`;
    document.getElementById('confidence').textContent = `${(data.confidence * 100).toFixed(0)}%`;
    
    // Current stats
    document.getElementById('currentPrice').textContent = `$${data.current_price.toFixed(2)}`;
    const changeColor = data.daily_change >= 0 ? 'green' : 'red';
    document.getElementById('dailyChange').innerHTML = 
        `<span style="color: ${changeColor}">${data.daily_change >= 0 ? '+' : ''}${data.daily_change.toFixed(2)} (${data.daily_change_percent.toFixed(2)}%)</span>`;
    
    // Indicators
    document.getElementById('rsi').textContent = data.indicators.rsi.toFixed(1);
    document.getElementById('macd').textContent = data.indicators.macd_histogram > 0 ? 'Bullish' : 'Bearish';
    
    // Reasoning
    const reasoningList = document.getElementById('reasoning');
    reasoningList.innerHTML = '';
    data.reasoning.forEach(reason => {
        const li = document.createElement('li');
        li.textContent = reason;
        reasoningList.appendChild(li);
    });
    
    // Update chart
    updateChart(data.price_history);
    
    // Show results
    document.getElementById('results').style.display = 'block';
    
    // Initialize tabs if not already done
    initializeTabs();
    
    // Populate forecast data if available
    if (data.algo_forecast) {
        console.log('Calling displayForecastResults with:', data.algo_forecast);
        displayForecastResults(data);
    } else {
        console.log('No algo_forecast data received');
    }
    
    // Populate news sentiment if available
    if (data.news_sentiment) {
        console.log('Calling displayNewsSentiment with:', data.news_sentiment);
        displayNewsSentiment(data.news_sentiment);
    } else {
        console.log('No news_sentiment data received');
    }
    
    // Update summary tab
    console.log('Calling updateSummaryTab');
    updateSummaryTab(data);
    
    // DIRECT TAB POPULATION FIX - populate tabs directly here
    if (data.algo_forecast) {
        try {
            const af = data.algo_forecast;
            const patterns = af.pattern_scores || {};
            
            // Mean Reversion
            const meanRev = patterns.mean_reversion || 0;
            document.getElementById('meanReversionDirection').textContent = 
                meanRev > 0.1 ? 'UP' : meanRev < -0.1 ? 'DOWN' : 'NEUTRAL';
            document.getElementById('meanReversionConfidence').textContent = 
                `${(Math.abs(meanRev) * 100).toFixed(0)}% confidence`;
            
            // Momentum
            const momentum = patterns.momentum_breakout || 0;
            document.getElementById('momentumDirection').textContent = 
                momentum > 0.1 ? 'UP' : momentum < -0.1 ? 'DOWN' : 'NEUTRAL';
            document.getElementById('momentumConfidence').textContent = 
                `${(Math.abs(momentum) * 100).toFixed(0)}% confidence`;
            
            // Support/Resistance
            const support = patterns.support_resistance || 0;
            document.getElementById('supportDirection').textContent = 
                support > 0.1 ? 'UP' : support < -0.1 ? 'DOWN' : 'NEUTRAL';
            document.getElementById('supportConfidence').textContent = 
                `${(Math.abs(support) * 100).toFixed(0)}% confidence`;
            
            // Trigger levels
            const triggerList = document.getElementById('triggerList');
            if (af.algo_triggers && af.algo_triggers.length > 0) {
                triggerList.innerHTML = af.algo_triggers.slice(0, 5).map(trigger => 
                    `<span class="trigger-badge">$${trigger.toFixed(2)}</span>`
                ).join('');
            }
            
            console.log('Direct algo forecast population completed');
        } catch (e) {
            console.error('Error populating algo forecast:', e);
        }
    }
    
    // Direct news sentiment population
    if (data.news_sentiment) {
        try {
            const ns = data.news_sentiment;
            
            // Sentiment score
            const sentEl = document.getElementById('sentimentScore');
            if (ns.sentiment_score > 0.1) {
                sentEl.textContent = 'POSITIVE';
                sentEl.style.color = '#28a745';
            } else if (ns.sentiment_score < -0.1) {
                sentEl.textContent = 'NEGATIVE';
                sentEl.style.color = '#dc3545';
            } else {
                sentEl.textContent = 'NEUTRAL';
                sentEl.style.color = '#6c757d';
            }
            
            document.getElementById('sentimentTrend').textContent = `Trend: ${ns.sentiment_trend || 'STABLE'}`;
            document.getElementById('manipulationRisk').textContent = `${(ns.manipulation_risk * 100).toFixed(0)}% Risk`;
            document.getElementById('newsVolume').textContent = `${ns.news_volume || 0} articles`;
            document.getElementById('pumpDumpRisk').textContent = `${(ns.pump_dump_probability * 100).toFixed(0)}% Risk`;
            
            console.log('Direct news sentiment population completed');
        } catch (e) {
            console.error('Error populating news sentiment:', e);
        }
    }
    
    // Direct summary tab population
    try {
        document.getElementById('summaryTechnical').textContent = data.rating || 'N/A';
        document.getElementById('summaryTechnicalConf').textContent = `${(data.confidence * 100).toFixed(0)}% confidence`;
        
        if (data.algo_forecast) {
            document.getElementById('summaryAlgorithm').textContent = data.algo_forecast.forecast_direction || 'N/A';
            document.getElementById('summaryAlgorithmConf').textContent = `${(data.algo_forecast.confidence * 100).toFixed(0)}% confidence`;
        }
        
        // Overall prediction
        const overallPred = data.rating === 'BUY' ? 'BUY' : data.rating === 'SELL' ? 'SELL' : 'HOLD';
        document.getElementById('summaryOverall').textContent = overallPred;
        document.getElementById('summaryOverallConf').textContent = `${(data.confidence * 100).toFixed(0)}% overall`;
        
        console.log('Direct summary population completed');
    } catch (e) {
        console.error('Error populating summary:', e);
    }
}

function updateChart(priceHistory) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: priceHistory.dates.map(d => new Date(d).toLocaleDateString()),
            datasets: [{
                label: 'Close Price',
                data: priceHistory.prices,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

function showError(message) {
    const errorEl = document.getElementById('errorMsg');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

// Load top stocks on page load
async function loadTopStocks() {
    try {
        const response = await fetch('/api/top-stocks');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load top stocks');
        }
        
        displayTopStocks(data.stocks);
    } catch (error) {
        console.error('Error loading top stocks:', error);
        document.getElementById('topStocksLoading').textContent = 'Failed to load top stocks';
    }
}

function displayTopStocks(stocks) {
    const grid = document.getElementById('topStocksGrid');
    grid.innerHTML = '';
    
    stocks.forEach((stock, index) => {
        const item = document.createElement('div');
        item.className = 'stock-item';
        item.id = `stock-item-${index}`;
        
        // Add emoji based on rating
        const emoji = stock.rating === 'RISKY_BUY' ? '🔥' : 
                     stock.rating === 'BUY' ? '🟢' : 
                     stock.rating === 'HOLD' ? '🟡' : '🔴';
        
        item.innerHTML = `
            <h4>${emoji} ${stock.ticker}</h4>
            <div class="stock-rating ${stock.rating}">${stock.rating}</div>
            <div class="stock-confidence">Confidence: ${(stock.confidence * 100).toFixed(0)}%</div>
            <div class="stock-change">${stock.daily_change_percent >= 0 ? '+' : ''}${stock.daily_change_percent.toFixed(1)}%</div>
        `;
        
        item.onclick = () => {
            // Remove active class from all items
            document.querySelectorAll('.stock-item').forEach(el => el.classList.remove('active'));
            // Add active class to clicked item
            item.classList.add('active');
            
            // Analyze the stock
            document.getElementById('tickerInput').value = stock.ticker;
            document.getElementById('searchForm').dispatchEvent(new Event('submit'));
            
            // Smooth scroll to results after a short delay
            setTimeout(() => {
                document.getElementById('results').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 500);
        };
        
        grid.appendChild(item);
    });
    
    document.getElementById('topStocksLoading').style.display = 'none';
    document.getElementById('analysisHint').style.display = 'block';
    grid.style.display = 'grid';
}

// Tab Management Functions
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log('Initializing tabs:', tabButtons.length, 'buttons found');
    
    // Only add event listeners if they haven't been added already
    tabButtons.forEach((button, index) => {
        if (!button.hasAttribute('data-listener-added')) {
            console.log('Adding listener to tab:', button.dataset.tab);
            
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTab = button.dataset.tab;
                console.log('Tab clicked:', targetTab);
                
                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                const targetContent = document.getElementById(`${targetTab}-tab`);
                if (targetContent) {
                    targetContent.classList.add('active');
                    console.log('Activated tab:', targetTab);
                } else {
                    console.error('Target tab content not found:', `${targetTab}-tab`);
                }
            });
            button.setAttribute('data-listener-added', 'true');
        }
    });
}

function displayForecastResults(data) {
    console.log('displayForecastResults called with data:', data);
    const algoForecast = data.algo_forecast;
    if (!algoForecast) {
        console.log('No algoForecast in data');
        return;
    }
    console.log('Processing algoForecast:', algoForecast);
    
    // Update individual pattern forecasts
    const patterns = algoForecast.pattern_scores || {};
    
    // Mean Reversion
    const meanRevScore = patterns.mean_reversion || 0;
    document.getElementById('meanReversionDirection').textContent = 
        meanRevScore > 0.1 ? 'UP' : meanRevScore < -0.1 ? 'DOWN' : 'NEUTRAL';
    document.getElementById('meanReversionDirection').className = 
        `forecast-direction ${meanRevScore > 0.1 ? 'UP' : meanRevScore < -0.1 ? 'DOWN' : 'SIDEWAYS'}`;
    document.getElementById('meanReversionConfidence').textContent = 
        `${(Math.abs(meanRevScore) * 100).toFixed(0)}% confidence`;
    
    // Momentum Breakout
    const momentumScore = patterns.momentum_breakout || 0;
    document.getElementById('momentumDirection').textContent = 
        momentumScore > 0.1 ? 'UP' : momentumScore < -0.1 ? 'DOWN' : 'NEUTRAL';
    document.getElementById('momentumDirection').className = 
        `forecast-direction ${momentumScore > 0.1 ? 'UP' : momentumScore < -0.1 ? 'DOWN' : 'SIDEWAYS'}`;
    document.getElementById('momentumConfidence').textContent = 
        `${(Math.abs(momentumScore) * 100).toFixed(0)}% confidence`;
    
    // Support/Resistance
    const supportScore = patterns.support_resistance || 0;
    document.getElementById('supportDirection').textContent = 
        supportScore > 0.1 ? 'UP' : supportScore < -0.1 ? 'DOWN' : 'NEUTRAL';
    document.getElementById('supportDirection').className = 
        `forecast-direction ${supportScore > 0.1 ? 'UP' : supportScore < -0.1 ? 'DOWN' : 'SIDEWAYS'}`;
    document.getElementById('supportConfidence').textContent = 
        `${(Math.abs(supportScore) * 100).toFixed(0)}% confidence`;
    
    // Algorithm triggers
    const triggerList = document.getElementById('triggerList');
    triggerList.innerHTML = '';
    
    if (algoForecast.algo_triggers && algoForecast.algo_triggers.length > 0) {
        algoForecast.algo_triggers.slice(0, 8).forEach(trigger => {
            const badge = document.createElement('div');
            badge.className = 'trigger-badge';
            badge.textContent = `$${trigger.toFixed(2)}`;
            triggerList.appendChild(badge);
        });
    } else {
        triggerList.innerHTML = '<span style="color: #666;">No significant trigger levels detected</span>';
    }
}

function displayNewsSentiment(newsSentiment) {
    if (!newsSentiment) return;
    
    // Overall sentiment
    const sentimentScore = newsSentiment.sentiment_score || 0;
    const sentimentEl = document.getElementById('sentimentScore');
    if (sentimentScore > 0.1) {
        sentimentEl.textContent = 'POSITIVE';
        sentimentEl.style.color = '#28a745';
    } else if (sentimentScore < -0.1) {
        sentimentEl.textContent = 'NEGATIVE';
        sentimentEl.style.color = '#dc3545';
    } else {
        sentimentEl.textContent = 'NEUTRAL';
        sentimentEl.style.color = '#6c757d';
    }
    
    document.getElementById('sentimentTrend').textContent = 
        `Trend: ${newsSentiment.sentiment_trend || 'STABLE'}`;
    
    // Manipulation risk
    const manipRisk = newsSentiment.manipulation_risk || 0;
    document.getElementById('manipulationRisk').textContent = 
        `${(manipRisk * 100).toFixed(0)}% Risk`;
    document.getElementById('newsVolume').textContent = 
        `${newsSentiment.news_volume || 0} articles analyzed`;
    
    // Pump/dump risk
    const pumpDumpRisk = newsSentiment.pump_dump_probability || 0;
    document.getElementById('pumpDumpRisk').textContent = 
        `${(pumpDumpRisk * 100).toFixed(0)}% Risk`;
    document.getElementById('priceCorrelation').textContent = 
        `Correlation: ${(newsSentiment.price_correlation || 0).toFixed(2)}`;
    
    // News summary
    const summaryList = document.getElementById('newsSummaryList');
    summaryList.innerHTML = '';
    
    if (newsSentiment.analysis_summary && newsSentiment.analysis_summary.length > 0) {
        newsSentiment.analysis_summary.forEach(summary => {
            const li = document.createElement('li');
            li.textContent = summary;
            summaryList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No significant news patterns detected';
        summaryList.appendChild(li);
    }
}

function updateSummaryTab(data) {
    // Technical Rating
    document.getElementById('summaryTechnical').textContent = data.rating || '-';
    document.getElementById('summaryTechnical').className = 
        `combined-prediction ${data.rating}`;
    document.getElementById('summaryTechnicalConf').textContent = 
        `${((data.confidence || 0) * 100).toFixed(0)}% confidence`;
    
    // Algorithm Forecast
    const algoDirection = data.algo_forecast?.forecast_direction || 'UNKNOWN';
    document.getElementById('summaryAlgorithm').textContent = algoDirection;
    document.getElementById('summaryAlgorithm').className = 
        `combined-prediction ${algoDirection === 'UP' ? 'UP' : algoDirection === 'DOWN' ? 'DOWN' : 'SIDEWAYS'}`;
    document.getElementById('summaryAlgorithmConf').textContent = 
        `${((data.algo_forecast?.confidence || 0) * 100).toFixed(0)}% confidence`;
    
    // Overall Prediction (combination)
    const overallPrediction = determineOverallPrediction(data);
    document.getElementById('summaryOverall').textContent = overallPrediction.direction;
    document.getElementById('summaryOverall').className = 
        `combined-prediction ${overallPrediction.direction}`;
    document.getElementById('summaryOverallConf').textContent = 
        `${(overallPrediction.confidence * 100).toFixed(0)}% overall confidence`;
    
    // Key insights
    const insightsList = document.getElementById('summaryInsights');
    insightsList.innerHTML = '';
    
    const insights = generateKeyInsights(data);
    insights.forEach(insight => {
        const li = document.createElement('li');
        li.textContent = insight;
        insightsList.appendChild(li);
    });
}

function determineOverallPrediction(data) {
    const technical = data.rating;
    const algoDirection = data.algo_forecast?.forecast_direction;
    const techConfidence = data.confidence || 0;
    const algoConfidence = data.algo_forecast?.confidence || 0;
    
    // Simple weighted combination
    let direction = 'HOLD';
    let confidence = (techConfidence + algoConfidence) / 2;
    
    // If both agree
    if ((technical === 'BUY' && algoDirection === 'UP') || 
        (technical === 'RISKY_BUY' && algoDirection === 'UP')) {
        direction = 'BUY';
        confidence = Math.min(1.0, confidence + 0.1); // Boost for agreement
    } else if (technical === 'SELL' && algoDirection === 'DOWN') {
        direction = 'SELL';
        confidence = Math.min(1.0, confidence + 0.1);
    } else if (technical === 'BUY' || algoDirection === 'UP') {
        direction = 'WEAK BUY';
    } else if (technical === 'SELL' || algoDirection === 'DOWN') {
        direction = 'WEAK SELL';
    }
    
    return { direction, confidence };
}

function generateKeyInsights(data) {
    const insights = [];
    
    // Technical insights
    if (data.confidence > 0.7) {
        insights.push(`High confidence technical signal (${(data.confidence * 100).toFixed(0)}%)`);
    }
    
    // Algorithm insights
    if (data.algo_forecast?.confidence > 0.6) {
        insights.push(`Strong algorithmic trading patterns detected`);
    }
    
    // RSI insights
    const rsi = data.indicators?.rsi;
    if (rsi < 30) {
        insights.push('RSI indicates oversold conditions - potential reversal opportunity');
    } else if (rsi > 70) {
        insights.push('RSI indicates overbought conditions - caution advised');
    }
    
    // Volatility insights
    if (data.daily_change_percent && Math.abs(data.daily_change_percent) > 5) {
        insights.push('High volatility detected - increased risk and opportunity');
    }
    
    // News insights
    if (data.news_sentiment?.manipulation_risk > 0.5) {
        insights.push('⚠️ Elevated manipulation risk detected in news sentiment');
    }
    
    // Combined insights
    const technical = data.rating;
    const algoDirection = data.algo_forecast?.forecast_direction;
    
    if (technical === 'BUY' && algoDirection === 'UP') {
        insights.push('✅ Technical and algorithmic signals align - strong consensus');
    } else if ((technical === 'BUY' && algoDirection === 'DOWN') || 
               (technical === 'SELL' && algoDirection === 'UP')) {
        insights.push('⚠️ Mixed signals detected - proceed with caution');
    }
    
    // Default insight if none found
    if (insights.length === 0) {
        insights.push('Analysis complete - see individual tabs for detailed breakdown');
    }
    
    return insights.slice(0, 6); // Limit to 6 insights
}

// Load top stocks when page loads
window.addEventListener('load', () => {
    loadTopStocks();
    initializeTabs(); // Initialize tabs on page load
});

// Also initialize tabs when DOM is ready
document.addEventListener('DOMContentLoaded', initializeTabs);