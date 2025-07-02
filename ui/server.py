import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from typing import List, Dict
from core.data_fetcher import fetch_stock_data, search_ticker_by_name, validate_ticker
from core.analyzer import analyze_technical, scan_top_buy_stocks, analyze_with_enhanced_accuracy
from core.professional_analyzer import ProfessionalStockAnalyzer
from core.quality_standards import QualityLevel

class StockAnalyzerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        
        if url.path == '/api/analyze':
            self.handle_analyze()
        elif url.path == '/api/analyze-professional':
            self.handle_analyze_professional()
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
            # Look for files in the ui directory
            ui_path = os.path.join(os.path.dirname(__file__), filename)
            with open(ui_path, 'r', encoding='utf-8') as f:
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
            # Look for index.html in the ui directory
            index_path = os.path.join(os.path.dirname(__file__), 'index.html')
            with open(index_path, 'r', encoding='utf-8') as f:
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
            
            # Input sanitization - limit length and strip whitespace
            query = str(query).strip()[:50]  # Limit to 50 chars for safety
            
            if not query:
                self.send_error_response(400, "Invalid query parameter")
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
    
    def handle_analyze_professional(self):
        """Handle professional-grade analysis with quality standards and risk management."""
        try:
            # Parse query parameters
            params = parse_qs(urlparse(self.path).query)
            query = params.get('query', [''])[0]
            quality_level = params.get('quality', ['professional'])[0].lower()
            
            if not query:
                self.send_error_response(400, "Query parameter required")
                return
            
            # Map risk parameter to QualityLevel enum
            quality_mapping = {
                'low_risk': QualityLevel.LOW_RISK,
                'moderate_risk': QualityLevel.MODERATE_RISK,
                'high_risk': QualityLevel.HIGH_RISK,
                'aggressive': QualityLevel.AGGRESSIVE,
                # Legacy mappings for backward compatibility
                'institutional': QualityLevel.LOW_RISK,
                'professional': QualityLevel.MODERATE_RISK,
                'retail': QualityLevel.HIGH_RISK,
                'experimental': QualityLevel.AGGRESSIVE
            }
            
            target_quality = quality_mapping.get(quality_level, QualityLevel.MODERATE_RISK)
            
            # Check if query is a ticker or company name
            ticker = query.upper()
            
            # First try to validate as direct ticker
            if validate_ticker(ticker):
                pass
            else:
                # Search by company name
                found_ticker = search_ticker_by_name(query)
                if found_ticker:
                    ticker = found_ticker
                else:
                    self.send_error_response(404, f"No ticker found for company '{query}'")
                    return
            
            # Initialize professional analyzer
            professional_analyzer = ProfessionalStockAnalyzer(quality_level=target_quality)
            
            # Get stock data for price history
            from core.data_fetcher import fetch_stock_data
            stock_data = fetch_stock_data(ticker)
            
            # Perform professional analysis
            analysis = professional_analyzer.analyze_stock_professional(
                ticker=ticker,
                include_algo_forecast=True,
                include_news_analysis=True
            )
            
            # Prepare professional response with all quality metrics
            response = {
                'ticker': analysis.ticker,
                'rating': analysis.rating,
                'confidence': analysis.confidence,
                'analysis_date': analysis.analysis_date.isoformat(),
                'price_at_analysis': analysis.price_at_analysis,
                
                # Technical indicators
                'indicators': {
                    'rsi': analysis.technical_indicators.rsi,
                    'sma_20': analysis.technical_indicators.sma_20,
                    'sma_50': analysis.technical_indicators.sma_50,
                    'macd': analysis.technical_indicators.macd,
                    'macd_signal': analysis.technical_indicators.macd_signal,
                    'macd_histogram': analysis.technical_indicators.macd_histogram
                },
                
                # Enhanced reasoning with risk context
                'reasoning': analysis.reasoning,
                
                # Price history for chart
                'price_history': {
                    'dates': [d.isoformat() for d in stock_data.dates[-30:]] if stock_data else [],
                    'prices': stock_data.prices[-30:] if stock_data else []
                },
                
                # Professional risk management
                'risk_management': {
                    'stop_loss_price': round(analysis.risk_management.stop_loss_price, 2),
                    'stop_loss_percent': round(analysis.risk_management.stop_loss_percent * 100, 1),
                    'take_profit_price': round(analysis.risk_management.take_profit_price, 2),
                    'position_size_percent': round(analysis.risk_management.position_size_percent * 100, 1),
                    'risk_reward_ratio': round(analysis.risk_management.risk_reward_ratio, 1),
                    'max_drawdown_limit': round(analysis.risk_management.max_drawdown_limit * 100, 1),
                    'time_horizon_days': analysis.risk_management.time_horizon_days,
                    'trailing_stop_percent': round(analysis.risk_management.trailing_stop_percent * 100, 1)
                },
                
                # Quality assurance metrics
                'quality_assurance': {
                    'quality_level': analysis.quality_assurance.quality_level,
                    'statistical_confidence': round(analysis.quality_assurance.statistical_confidence, 3),
                    'p_value': round(analysis.quality_assurance.p_value, 4),
                    'sample_size': analysis.quality_assurance.sample_size,
                    'error_margin': round(analysis.quality_assurance.error_margin, 3),
                    'risk_score': round(analysis.quality_assurance.risk_score, 3),
                    'validation_flags': analysis.quality_assurance.validation_flags
                },
                
                # Entry/exit criteria with specific price levels
                'entry_exit_criteria': {
                    'entry_price': round(analysis.entry_exit_criteria['entry_price'], 2),
                    'stop_loss_price': round(analysis.entry_exit_criteria['stop_loss_price'], 2),
                    'take_profit_price': round(analysis.entry_exit_criteria['take_profit_price'], 2),
                    'trailing_stop_percent': round(analysis.entry_exit_criteria['trailing_stop_percent'] * 100, 1)
                },
                
                # Statistical validation
                'statistical_validation': {
                    'p_value': round(analysis.statistical_validation['p_value'], 4),
                    'confidence_interval': round(analysis.statistical_validation['confidence_interval'], 3),
                    'statistical_power': round(analysis.statistical_validation['statistical_power'], 3),
                    'sample_size': analysis.statistical_validation['sample_size']
                },
                
                # Cross-module validation
                'cross_module_validation': {
                    'overall_consistency': analysis.cross_module_validation['overall_consistency'],
                    'conflicts': analysis.cross_module_validation['conflicts'],
                    'confirmations': analysis.cross_module_validation['confirmations']
                },
                
                # Professional analysis flag
                'analysis_type': 'professional',
                'quality_level': target_quality.value,
                'meets_standards': analysis.quality_assurance.quality_level not in ['SUBSTANDARD', 'ERROR'],
                
                # Algorithm and news data
                'algo_forecast': analysis.algo_forecast,
                'news_sentiment': analysis.news_sentiment
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Professional analysis error: {e}")
            self.send_error_response(500, str(e))
    
    def handle_top_stocks(self):
        try:
            # Parse parameters
            url = urlparse(self.path)
            query_params = parse_qs(url.query)
            quality_param = query_params.get('quality', ['research'])[0].lower()
            min_risk_reward = float(query_params.get('min_rr', ['0'])[0])
            
            # Map quality parameter to QualityLevel
            quality_mapping = {
                'aggressive': QualityLevel.AGGRESSIVE,
                'research': QualityLevel.AGGRESSIVE,  # Default for research
                'high_risk': QualityLevel.HIGH_RISK,
                'moderate_risk': QualityLevel.MODERATE_RISK,
                'low_risk': QualityLevel.LOW_RISK,
                # Legacy mappings for backward compatibility
                'experimental': QualityLevel.AGGRESSIVE,
                'retail': QualityLevel.HIGH_RISK,
                'professional': QualityLevel.MODERATE_RISK,
                'institutional': QualityLevel.LOW_RISK
            }
            
            target_quality = quality_mapping.get(quality_param, QualityLevel.AGGRESSIVE)
            
            # Always include both US and European stocks for best opportunities
            top_stocks = self.scan_top_professional_stocks(10, target_quality, include_europe=True, min_risk_reward=min_risk_reward)
            
            response = {
                'stocks': top_stocks,
                'quality_level': target_quality.value,
                'scan_method': 'professional' if target_quality != QualityLevel.AGGRESSIVE else 'basic'
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def scan_top_professional_stocks(self, max_stocks: int, quality_level: QualityLevel, include_europe: bool = False, min_risk_reward: float = 0) -> List[Dict]:
        """Scan for top stocks using professional analysis with quality filtering."""
        import concurrent.futures
        from core.analyzer import get_top_stocks_for_scanning
        from core.data_fetcher import get_top_stocks_for_scanning_with_europe
        
        analyzer = ProfessionalStockAnalyzer(quality_level)
        opportunities = []
        
        # Get candidate stocks
        if include_europe:
            tickers = get_top_stocks_for_scanning_with_europe()[:50]  # More stocks when including Europe
        else:
            tickers = get_top_stocks_for_scanning()[:30]  # Scan fewer for professional analysis
        
        def analyze_professional_stock(ticker: str) -> Dict:
            """Analyze stock with professional standards."""
            try:
                result = analyzer.analyze_stock_professional(ticker)
                
                # Adjust filtering based on quality level
                meets_standards = False
                if quality_level == QualityLevel.AGGRESSIVE:
                    # Be more permissive for aggressive - include any meaningful rating
                    meets_standards = (result.rating in ['BUY', 'RISKY_BUY', 'HOLD'] and 
                                     result.confidence > 0.45)  # Lower threshold for aggressive
                else:
                    # Stricter standards for higher quality levels
                    meets_standards = (result.quality_assurance.quality_level != 'SUBSTANDARD' and 
                                     result.rating in ['BUY', 'RISKY_BUY'] and 
                                     result.confidence > 0.0)
                
                if meets_standards:
                    # Calculate risk/reward ratio
                    entry_price = result.entry_exit_criteria['entry_price']
                    stop_loss = result.entry_exit_criteria['stop_loss_price']
                    take_profit = result.entry_exit_criteria['take_profit_price']
                    
                    potential_loss = abs(entry_price - stop_loss)
                    potential_gain = abs(take_profit - entry_price)
                    risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 0
                    
                    return {
                        'ticker': ticker,
                        'rating': result.rating,
                        'confidence': round(result.confidence, 3),
                        'quality_level': result.quality_assurance.quality_level,
                        'current_price': result.price_at_analysis,
                        'reasoning': result.reasoning[:2],  # First 2 reasons
                        'risk_score': result.quality_assurance.risk_score,
                        'risk_reward_ratio': round(risk_reward_ratio, 2),
                        'entry_price': round(entry_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'take_profit': round(take_profit, 2)
                    }
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
            return None
        
        # Parallel analysis
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(analyze_professional_stock, ticker) for ticker in tickers]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    opportunities.append(result)
        
        # Apply risk/reward filter if specified
        if min_risk_reward > 0:
            # Filter for stocks meeting minimum risk/reward threshold
            filtered_opportunities = [stock for stock in opportunities if stock.get('risk_reward_ratio', 0) >= min_risk_reward]
            
            # Sort by risk/reward ratio (best first)
            filtered_opportunities.sort(key=lambda x: x['risk_reward_ratio'], reverse=True)
            
            # If not enough stocks meet the criteria, add best confidence stocks
            if len(filtered_opportunities) < max_stocks:
                remaining = [stock for stock in opportunities if stock not in filtered_opportunities]
                remaining.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Add note to these stocks that they don't meet R:R criteria
                for stock in remaining[:max_stocks - len(filtered_opportunities)]:
                    stock['below_rr_threshold'] = True
                    
                filtered_opportunities.extend(remaining[:max_stocks - len(filtered_opportunities)])
            
            return filtered_opportunities[:max_stocks]
        else:
            # Default: sort by confidence
            opportunities.sort(key=lambda x: x['confidence'], reverse=True)
            return opportunities[:max_stocks]
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        # Only allow localhost origins for security
        origin = self.headers.get('Origin', '')
        if origin and ('localhost' in origin or '127.0.0.1' in origin):
            self.send_header('Access-Control-Allow-Origin', origin)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        # Only allow localhost origins for security
        origin = self.headers.get('Origin', '')
        if origin and ('localhost' in origin or '127.0.0.1' in origin):
            self.send_header('Access-Control-Allow-Origin', origin)
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

if __name__ == '__main__':
    PORT = 8000
    print(f"Starting server on http://localhost:{PORT}")
    print("Open your browser and navigate to the URL above")
    
    httpd = HTTPServer(('localhost', PORT), StockAnalyzerHandler)
    httpd.serve_forever()