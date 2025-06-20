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
        else:
            super().do_GET()
    
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
            
            # Prepare response
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
                }
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