let priceChart = null;

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const input = document.getElementById('tickerInput').value.trim();
    if (!input) return;
    
    // Get selected quality level
    const qualityLevel = document.querySelector('input[name="quality"]:checked').value;
    
    // UI state
    document.getElementById('errorMsg').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = true;
    
    try {
        console.log('Fetching analysis for:', input, 'at quality level:', qualityLevel);
        
        // Always use professional analysis API with quality parameter
        const response = await fetch(`/api/analyze-professional?query=${encodeURIComponent(input)}&quality=${qualityLevel}`);
        const data = await response.json();
        
        console.log('Professional API response received:', data);
        
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
    const currentPrice = data.price_at_analysis || data.current_price;
    document.getElementById('currentPrice').textContent = `$${currentPrice.toFixed(2)}`;
    
    // Calculate daily change if not provided
    let dailyChange = 0;
    let dailyChangePercent = 0;
    if (data.daily_change !== undefined) {
        dailyChange = data.daily_change;
        dailyChangePercent = data.daily_change_percent;
    }
    
    const changeColor = dailyChange >= 0 ? 'green' : 'red';
    document.getElementById('dailyChange').innerHTML = 
        `<span style="color: ${changeColor}">${dailyChange >= 0 ? '+' : ''}${dailyChange.toFixed(2)} (${dailyChangePercent.toFixed(2)}%)</span>`;
    
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
    if (data.price_history) {
        updateChart(data.price_history);
    }
    
    // Display professional analysis if available
    if (data.analysis_type === 'professional') {
        displayProfessionalAnalysis(data);
    }
    
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
// Global variable to track risk/reward filter
let currentRiskRewardFilter = 1.0;

async function loadTopStocks(applyRiskReward = false) {
    try {
        // Get selected quality level for top stocks
        const qualityLevel = document.querySelector('input[name="topStocksQuality"]:checked')?.value || 'research';
        const riskRewardThreshold = applyRiskReward ? currentRiskRewardFilter : 0;
        
        document.getElementById('topStocksLoading').style.display = 'block';
        document.getElementById('topStocksGrid').style.display = 'none';
        
        let loadingText = `Scanning US & European markets for ${qualityLevel} quality opportunities...`;
        if (applyRiskReward) {
            loadingText = `Finding opportunities with R:R ≥ 1:${riskRewardThreshold} in US & European markets...`;
        }
        document.getElementById('topStocksLoading').textContent = loadingText;
        
        const response = await fetch(`/api/top-stocks?quality=${qualityLevel}&min_rr=${riskRewardThreshold}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load top stocks');
        }
        
        displayTopStocks(data.stocks, data.quality_level, data.scan_method);
    } catch (error) {
        console.error('Error loading top stocks:', error);
        document.getElementById('topStocksLoading').textContent = 'Failed to load top stocks';
    }
}

function displayTopStocks(stocks, qualityLevel, scanMethod) {
    const grid = document.getElementById('topStocksGrid');
    grid.innerHTML = '';
    
    // Add quality level info header
    if (qualityLevel && scanMethod) {
        const headerInfo = document.createElement('div');
        headerInfo.style.cssText = 'text-align: center; margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 6px; font-size: 0.9rem; color: #666;';
        headerInfo.innerHTML = `
            Markets: <strong>US & Europe</strong> | 
            Quality Level: <strong>${qualityLevel.toUpperCase()}</strong> | 
            Found: <strong>${stocks.length}</strong> opportunities
        `;
        grid.appendChild(headerInfo);
    }
    
    if (stocks.length === 0) {
        const noResults = document.createElement('div');
        noResults.style.cssText = 'text-align: center; padding: 40px; color: #666; font-style: italic;';
        noResults.textContent = `No stocks found meeting ${qualityLevel} quality standards. Try a lower quality level.`;
        grid.appendChild(noResults);
        document.getElementById('topStocksLoading').style.display = 'none';
        document.getElementById('topStocksGrid').style.display = 'block';
        return;
    }
    
    stocks.forEach((stock, index) => {
        const item = document.createElement('div');
        item.className = 'stock-item';
        item.id = `stock-item-${index}`;
        
        // Add emoji based on rating
        const emoji = stock.rating === 'RISKY_BUY' ? '🔥' : 
                     stock.rating === 'BUY' ? '🟢' : 
                     stock.rating === 'HOLD' ? '🟡' : '🔴';
        
        // All quality levels now use professional analysis format
        const qualityInfo = stock.quality_level;
        const riskScore = stock.risk_score || 0;
        const riskRewardRatio = stock.risk_reward_ratio || 0;
        
        // Show consistent professional format for all quality levels
        let additionalInfo = `
            <div class="stock-quality">Quality: ${qualityInfo || 'EXPERIMENTAL'}</div>
            <div class="stock-risk">Risk: ${(riskScore * 100).toFixed(0)}%</div>
        `;
        
        // Add risk/reward ratio if available
        if (riskRewardRatio > 0) {
            const rrColor = riskRewardRatio >= 2 ? '#28a745' : riskRewardRatio >= 1.5 ? '#ffc107' : '#dc3545';
            additionalInfo += `<div class="stock-rr" style="color: ${rrColor}; font-weight: 500;">R:R 1:${riskRewardRatio.toFixed(1)}</div>`;
            
            // Add warning if below threshold
            if (stock.below_rr_threshold) {
                additionalInfo += `<div style="color: #ff6b6b; font-size: 0.75rem; font-style: italic;">Below R:R filter</div>`;
            }
        }
        
        item.innerHTML = `
            <h4>${emoji} ${stock.ticker}</h4>
            <div class="stock-rating ${stock.rating}">${stock.rating}</div>
            <div class="stock-confidence">Confidence: ${(stock.confidence * 100).toFixed(0)}%</div>
            ${additionalInfo}
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

function displayProfessionalAnalysis(data) {
    console.log('Displaying professional analysis:', data);
    
    // Remove existing professional analysis section if present
    const existingSection = document.querySelector('.professional-analysis');
    if (existingSection) {
        existingSection.remove();
    }
    
    // Create professional analysis section
    const professionalSection = document.createElement('div');
    professionalSection.className = 'professional-analysis';
    
    // Quality Status
    const qualityStatus = `
        <div class="quality-status">
            <div>
                <h3>Quality Level: <span class="quality-level ${data.quality_assurance.quality_level}">${data.quality_assurance.quality_level}</span></h3>
                <p>Statistical Confidence: ${(data.quality_assurance.statistical_confidence * 100).toFixed(1)}%</p>
            </div>
            <div>
                <h4>Standards: ${data.meets_standards ? '✅ PASSED' : '❌ FAILED'}</h4>
                <p>Target: ${data.quality_level.toUpperCase()}</p>
            </div>
        </div>
    `;
    
    // Risk Management Section
    const riskManagement = `
        <h3>💰 Risk Management</h3>
        <div class="risk-management">
            <div class="risk-metric">
                <div class="risk-metric-label">Stop Loss</div>
                <div class="risk-metric-value">$${data.risk_management.stop_loss_price.toFixed(2)}</div>
                <div class="risk-metric-label">${data.risk_management.stop_loss_percent.toFixed(1)}% risk</div>
            </div>
            <div class="risk-metric">
                <div class="risk-metric-label">Take Profit</div>
                <div class="risk-metric-value">$${data.risk_management.take_profit_price.toFixed(2)}</div>
                <div class="risk-metric-label">${data.risk_management.risk_reward_ratio.toFixed(1)}:1 R/R</div>
            </div>
            <div class="risk-metric">
                <div class="risk-metric-label">Position Size</div>
                <div class="risk-metric-value">${data.risk_management.position_size_percent.toFixed(1)}%</div>
                <div class="risk-metric-label">of portfolio</div>
            </div>
            <div class="risk-metric">
                <div class="risk-metric-label">Time Horizon</div>
                <div class="risk-metric-value">${data.risk_management.time_horizon_days}</div>
                <div class="risk-metric-label">days</div>
            </div>
        </div>
    `;
    
    // Entry/Exit Criteria with Profit Calculator
    const entryPrice = data.entry_exit_criteria.entry_price;
    const stopLossPrice = data.entry_exit_criteria.stop_loss_price;
    const takeProfitPrice = data.entry_exit_criteria.take_profit_price;
    const trailingStopPercent = data.entry_exit_criteria.trailing_stop_percent;
    
    // Calculate potential profit/loss percentages
    const potentialProfitPercent = ((takeProfitPrice - entryPrice) / entryPrice * 100);
    const potentialLossPercent = ((stopLossPrice - entryPrice) / entryPrice * 100);
    
    const entryExitCriteria = `
        <div class="entry-exit-criteria">
            <h3>🎯 Entry/Exit Criteria</h3>
            <div class="entry-exit-grid">
                <div class="price-level">
                    <div class="price-level-label">Entry Price</div>
                    <div class="price-level-value">$${entryPrice.toFixed(2)}</div>
                </div>
                <div class="price-level">
                    <div class="price-level-label">Stop Loss</div>
                    <div class="price-level-value">$${stopLossPrice.toFixed(2)}</div>
                    <div class="price-level-percent" style="color: #dc3545">${potentialLossPercent.toFixed(1)}%</div>
                </div>
                <div class="price-level">
                    <div class="price-level-label">Take Profit</div>
                    <div class="price-level-value">$${takeProfitPrice.toFixed(2)}</div>
                    <div class="price-level-percent" style="color: #28a745">+${potentialProfitPercent.toFixed(1)}%</div>
                </div>
                <div class="price-level">
                    <div class="price-level-label">Trailing Stop</div>
                    <div class="price-level-value">${trailingStopPercent.toFixed(1)}%</div>
                </div>
            </div>
            
            <!-- Profit Calculator -->
            <div class="profit-calculator">
                <h4>💰 Profit Calculator</h4>
                <div class="calculator-input">
                    <label>Investment Amount (EUR):</label>
                    <input type="number" id="investmentAmount" placeholder="1000" value="1000" min="0" step="100">
                    <button onclick="calculateProfit(${entryPrice}, ${takeProfitPrice}, ${stopLossPrice})">Calculate</button>
                </div>
                <div id="profitResults" class="profit-results" style="display: none;">
                    <!-- Results will be displayed here -->
                </div>
            </div>
        </div>
    `;
    
    // Statistical Validation
    const statisticalValidation = `
        <div class="statistical-validation">
            <h3>📊 Statistical Validation</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-label">P-Value</div>
                    <div class="stat-value">${data.statistical_validation.p_value.toFixed(4)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Sample Size</div>
                    <div class="stat-value">${data.statistical_validation.sample_size}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Confidence Interval</div>
                    <div class="stat-value">±${(data.statistical_validation.confidence_interval * 100).toFixed(1)}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Statistical Power</div>
                    <div class="stat-value">${(data.statistical_validation.statistical_power * 100).toFixed(0)}%</div>
                </div>
            </div>
        </div>
    `;
    
    // Cross-Module Validation
    const crossValidation = `
        <div class="cross-validation">
            <h3>🔄 Cross-Module Validation</h3>
            <p>Overall Consistency: <span class="consistency-indicator consistency-${data.cross_module_validation.overall_consistency}">${data.cross_module_validation.overall_consistency}</span></p>
            ${data.cross_module_validation.conflicts !== 'None' ? `<p><strong>Conflicts:</strong> ${data.cross_module_validation.conflicts}</p>` : ''}
            ${data.cross_module_validation.confirmations !== 'None' ? `<p><strong>Confirmations:</strong> ${data.cross_module_validation.confirmations}</p>` : ''}
        </div>
    `;
    
    // Quality Warnings (if any)
    let qualityWarnings = '';
    if (data.quality_assurance.validation_flags && data.quality_assurance.validation_flags.length > 0) {
        qualityWarnings = `
            <div class="quality-warning">
                <h4>⚠️ Quality Warnings</h4>
                <ul class="warning-flags">
                    ${data.quality_assurance.validation_flags.map(flag => `<li>${flag}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Combine all sections
    professionalSection.innerHTML = qualityStatus + riskManagement + entryExitCriteria + statisticalValidation + crossValidation + qualityWarnings;
    
    // Insert after the main analysis results
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        resultsSection.appendChild(professionalSection);
    }
}

// Load top stocks when page loads
window.addEventListener('load', () => {
    loadTopStocks();
    initializeTabs(); // Initialize tabs on page load
    
    // Add event listeners for top stocks quality selector
    const qualityInputs = document.querySelectorAll('input[name="topStocksQuality"]');
    qualityInputs.forEach(input => {
        input.addEventListener('change', () => {
            console.log('Top stocks quality changed to:', input.value);
            loadTopStocks();
        });
    });
});

// Also initialize tabs when DOM is ready
document.addEventListener('DOMContentLoaded', initializeTabs);

// Risk/Reward Filter Functions
function updateRiskRewardDisplay(value) {
    document.getElementById('riskRewardValue').textContent = parseFloat(value).toFixed(1);
    currentRiskRewardFilter = parseFloat(value);
}

function applyRiskRewardFilter() {
    loadTopStocks(true);
}

// Profit Calculator Function
function calculateProfit(entryPrice, takeProfitPrice, stopLossPrice) {
    const investmentEUR = parseFloat(document.getElementById('investmentAmount').value) || 1000;
    
    // Calculate number of shares (assuming USD/EUR rate of ~1.08)
    const usdToEurRate = 1.08; // Approximate rate
    const investmentUSD = investmentEUR * usdToEurRate;
    const numShares = investmentUSD / entryPrice;
    
    // Calculate potential profit
    const profitUSD = numShares * (takeProfitPrice - entryPrice);
    const profitEUR = profitUSD / usdToEurRate;
    const profitPercent = (profitEUR / investmentEUR) * 100;
    
    // Calculate potential loss
    const lossUSD = numShares * (entryPrice - stopLossPrice);
    const lossEUR = lossUSD / usdToEurRate;
    const lossPercent = (lossEUR / investmentEUR) * 100;
    
    // Calculate risk/reward ratio (reward divided by risk)
    const riskRewardRatio = Math.abs(profitEUR / lossEUR);
    
    // Display results
    const resultsDiv = document.getElementById('profitResults');
    resultsDiv.innerHTML = `
        <div class="profit-calculation-results">
            <div class="calc-result positive">
                <div class="calc-label">Potential Profit (Target Hit)</div>
                <div class="calc-value">€${profitEUR.toFixed(2)}</div>
                <div class="calc-percent">+${profitPercent.toFixed(1)}%</div>
            </div>
            <div class="calc-result negative">
                <div class="calc-label">Potential Loss (Stop Hit)</div>
                <div class="calc-value">-€${lossEUR.toFixed(2)}</div>
                <div class="calc-percent">-${lossPercent.toFixed(1)}%</div>
            </div>
            <div class="calc-result ${riskRewardRatio >= 2 ? 'positive' : riskRewardRatio >= 1 ? '' : 'negative'}">
                <div class="calc-label">Risk/Reward Ratio</div>
                <div class="calc-value">1:${riskRewardRatio.toFixed(2)}</div>
                <div class="calc-percent">${riskRewardRatio >= 2 ? 'Excellent' : riskRewardRatio >= 1.5 ? 'Good' : riskRewardRatio >= 1 ? 'Fair' : 'Poor'}</div>
            </div>
            <div class="calc-details">
                <small>
                    Shares: ${numShares.toFixed(2)} | 
                    Entry: $${entryPrice.toFixed(2)} | 
                    EUR/USD: ${(1/usdToEurRate).toFixed(3)}
                </small>
                <div style="margin-top: 10px; font-style: italic; color: #6c757d;">
                    <small>Risk/Reward 1:${riskRewardRatio.toFixed(2)} means: For every €1 you risk, you could gain €${riskRewardRatio.toFixed(2)}</small>
                </div>
            </div>
        </div>
    `;
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}