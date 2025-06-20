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
        const response = await fetch(`/api/analyze?query=${encodeURIComponent(input)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
});

function displayResults(data) {
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
    document.getElementById('results').style.display = 'grid';
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

// Load top stocks when page loads
window.addEventListener('load', loadTopStocks);