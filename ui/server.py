import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from core.data_fetcher import fetch_stock_data, search_ticker_by_name, validate_ticker
from core.analyzer import analyze_technical, scan_top_buy_stocks, analyze_with_enhanced_accuracy

class StockAnalyzerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        
        if url.path == '/api/analyze':
            self.handle_analyze()
        elif url.path == '/api/top-stocks':
            self.handle_top_stocks()
        elif url.path == '/' or url.path == '/index.html':
            # Serve the main UI
            self.serve_index()
        elif url.path == '/app.js':
            # Serve the JavaScript file
            self.serve_static_file('app.js', 'application/javascript')
        else:
            super().do_GET()
    
    def serve_static_file(self, filename, content_type):
        """Serve static files like CSS, JS, etc."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', f'{content_type}; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, f"{filename} not found")
    
    def serve_index(self):
        """Serve the main index.html file."""
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, "index.html not found")
    
    def handle_analyze(self):
        try:
            # Parse query parameters
            params = parse_qs(urlparse(self.path).query)
            query = params.get('query', [''])[0]
            
            if not query:
                self.send_error_response(400, "Query parameter required")
                return
            
            # Check if query is a ticker or company name
            ticker = query.upper()
            
            # First try to validate as direct ticker (handles cases like RHM.DE, AAPL, etc.)
            if validate_ticker(ticker):
                # It's a valid ticker, use it directly
                pass
            else:
                # Not a valid ticker, search by company name
                found_ticker = search_ticker_by_name(query)
                if found_ticker:
                    ticker = found_ticker
                else:
                    self.send_error_response(404, f"No ticker found for company '{query}'")
                    return
            
            # Fetch and analyze
            stock_data = fetch_stock_data(ticker)
            if not stock_data:
                self.send_error_response(404, f"No data found for ticker {ticker}")
                return
            
            analysis = analyze_with_enhanced_accuracy(ticker)
            
            # Get additional forecast data
            algo_forecast = None
            news_sentiment = None
            
            try:
                # Get algorithmic forecast
                from core.algo_forecast import AlgorithmicForecast
                algo_forecaster = AlgorithmicForecast()
                algo_forecast_result = algo_forecaster.predict_algorithmic_movements(stock_data)
                
                algo_forecast = {
                    'forecast_direction': algo_forecast_result.forecast_direction,
                    'confidence': algo_forecast_result.confidence,
                    'algo_triggers': algo_forecast_result.algo_triggers,
                    'reasoning': algo_forecast_result.reasoning,
                    'risk_factors': algo_forecast_result.risk_factors,
                    'pattern_scores': algo_forecast_result.pattern_scores
                }
            except Exception as e:
                print(f"Algorithmic forecast failed: {e}")
            
            try:
                # Get news sentiment (if available)
                from core.news_sentiment_analyzer import NewsSentimentForecaster
                news_forecaster = NewsSentimentForecaster()
                news_result = news_forecaster.analyze_news_sentiment_forecast(ticker, days_lookback=30)
                
                news_sentiment = {
                    'sentiment_score': news_result.sentiment_score,
                    'manipulation_risk': news_result.manipulation_risk,
                    'news_volume': news_result.news_volume,
                    'sentiment_trend': news_result.sentiment_trend,
                    'price_correlation': news_result.price_correlation,
                    'pump_dump_probability': news_result.pump_dump_probability,
                    'analysis_summary': news_result.analysis_summary
                }
            except Exception as e:
                print(f"News sentiment analysis failed: {e}")
            
            # Prepare enhanced response
            response = {
                'ticker': analysis.ticker,
                'rating': analysis.rating,
                'confidence': analysis.confidence,
                'current_price': stock_data.current_price,
                'daily_change': stock_data.daily_change,
                'daily_change_percent': stock_data.daily_change_percent,
                'indicators': {
                    'rsi': analysis.technical_indicators.rsi,
                    'sma_20': analysis.technical_indicators.sma_20,
                    'sma_50': analysis.technical_indicators.sma_50,
                    'macd': analysis.technical_indicators.macd,
                    'macd_signal': analysis.technical_indicators.macd_signal,
                    'macd_histogram': analysis.technical_indicators.macd_histogram
                },
                'reasoning': analysis.reasoning,
                'price_history': {
                    'dates': [d.isoformat() for d in stock_data.dates[-30:]],
                    'prices': stock_data.prices[-30:]
                },
                'algo_forecast': algo_forecast,
                'news_sentiment': news_sentiment,
                'forecast_enabled': True
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_top_stocks(self):
        try:
            # Scan for top buy-rated stocks
            top_stocks = scan_top_buy_stocks(10)
            
            response = {
                'stocks': top_stocks
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

if __name__ == '__main__':
    PORT = 8000
    print(f"Starting server on http://localhost:{PORT}")
    print("Open your browser and navigate to the URL above")
    
    httpd = HTTPServer(('localhost', PORT), StockAnalyzerHandler)
    httpd.serve_forever()