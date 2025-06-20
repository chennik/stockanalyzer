import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from .models import StockData

def fetch_stock_data(ticker: str, period: str = "3mo", interval: str = "1d") -> Optional[StockData]:
    """Fetch stock data from yfinance API."""
    try:
        stock = yf.Ticker(ticker.upper())
        
        # Get historical data
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            return None
        
        # Get current info
        info = stock.info
        
        # Extract data
        prices = hist['Close'].tolist()
        volumes = hist['Volume'].tolist()
        dates = [d.to_pydatetime() for d in hist.index]
        
        current_price = prices[-1] if prices else 0
        prev_close = prices[-2] if len(prices) > 1 else current_price
        daily_change = current_price - prev_close
        daily_change_percent = (daily_change / prev_close * 100) if prev_close > 0 else 0
        
        return StockData(
            ticker=ticker.upper(),
            prices=prices,
            volumes=volumes,
            dates=dates,
            current_price=current_price,
            daily_change=daily_change,
            daily_change_percent=daily_change_percent,
            market_cap=info.get('marketCap'),
            pe_ratio=info.get('trailingPE')
        )
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None

def validate_ticker(ticker: str) -> bool:
    """Check if ticker is valid and has data available."""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period="1d")
        return not hist.empty
    except:
        return False

def search_ticker_by_name(company_name: str) -> Optional[str]:
    """Search for ticker symbol by company name."""
    try:
        # Common mappings for popular companies
        name_to_ticker = {
            # US Companies
            'microsoft': 'MSFT',
            'apple': 'AAPL',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'berkshire': 'BRK-B',
            'jpmorgan': 'JPM',
            'johnson': 'JNJ',
            'visa': 'V',
            'walmart': 'WMT',
            'mastercard': 'MA',
            'disney': 'DIS',
            'netflix': 'NFLX',
            'intel': 'INTC',
            'cisco': 'CSCO',
            'oracle': 'ORCL',
            'salesforce': 'CRM',
            'adobe': 'ADBE',
            'paypal': 'PYPL',
            'exxon': 'XOM',
            'chevron': 'CVX',
            'pfizer': 'PFE',
            'coca-cola': 'KO',
            'pepsi': 'PEP',
            'boeing': 'BA',
            'mcdonald': 'MCD',
            'nike': 'NKE',
            'verizon': 'VZ',
            'at&t': 'T',
            'home depot': 'HD',
            'procter': 'PG',
            'bank of america': 'BAC',
            'wells fargo': 'WFC',
            'goldman': 'GS',
            'morgan stanley': 'MS',
            'general electric': 'GE',
            'ford': 'F',
            'general motors': 'GM',
            'starbucks': 'SBUX',
            'costco': 'COST',
            'target': 'TGT',
            'cvs': 'CVS',
            'walgreens': 'WBA',
            'uber': 'UBER',
            'airbnb': 'ABNB',
            'spotify': 'SPOT',
            'square': 'SQ',
            'block': 'SQ',
            'zoom': 'ZM',
            'docusign': 'DOCU',
            'snowflake': 'SNOW',
            'palantir': 'PLTR',
            'coinbase': 'COIN',
            
            # German Companies
            'rheinmetall': 'RHM.DE',
            'sap': 'SAP.DE',
            'siemens': 'SIE.DE',
            'volkswagen': 'VOW3.DE',
            'bmw': 'BMW.DE',
            'mercedes': 'MBG.DE',
            'mercedes-benz': 'MBG.DE',
            'daimler': 'MBG.DE',
            'adidas': 'ADS.DE',
            'bayer': 'BAYN.DE',
            'basf': 'BAS.DE',
            'deutsche bank': 'DBK.DE',
            'allianz': 'ALV.DE',
            'lufthansa': 'LHA.DE',
            'munich re': 'MUV2.DE',
            'continental': 'CON.DE',
            'henkel': 'HEN3.DE',
            'infineon': 'IFX.DE',
            
            # Dutch Companies
            'asml': 'ASML.AS',
            'shell': 'SHEL.AS',
            'unilever': 'UNA.AS',
            'philips': 'PHIA.AS',
            'ing': 'INGA.AS',
            'abn amro': 'ABN.AS',
            'heineken': 'HEIA.AS',
            'prosus': 'PRX.AS',
            'akzo nobel': 'AKZA.AS',
            'dsm': 'DSM.AS',
            
            # French Companies
            'lvmh': 'MC.PA',
            'loreal': 'OR.PA',
            'l\'oreal': 'OR.PA',
            'airbus': 'AIR.PA',
            'total': 'TTE.PA',
            'totalenergies': 'TTE.PA',
            'sanofi': 'SAN.PA',
            'bnp paribas': 'BNP.PA',
            'kering': 'KER.PA',
            'schneider electric': 'SU.PA',
            'vinci': 'DG.PA',
            'orange': 'ORA.PA',
            'danone': 'BN.PA',
            'michelin': 'ML.PA',
            'peugeot': 'UG.PA',
            'stellantis': 'STLA.PA',
            'capgemini': 'CAP.PA',
            'hermes': 'RMS.PA',
            
            # Swiss Companies
            'nestle': 'NESN.SW',
            'nestlé': 'NESN.SW',
            'roche': 'ROG.SW',
            'novartis': 'NOVN.SW',
            'ubs': 'UBSG.SW',
            'zurich': 'ZURN.SW',
            'abb': 'ABBN.SW',
            'swiss re': 'SREN.SW',
            'credit suisse': 'CSGN.SW',
            'richemont': 'CFR.SW',
            'lonza': 'LONN.SW',
            'givaudan': 'GIVN.SW',
            
            # Italian Companies
            'ferrari': 'RACE.MI',
            'eni': 'ENI.MI',
            'intesa sanpaolo': 'ISP.MI',
            'unicredit': 'UCG.MI',
            'generali': 'G.MI',
            'stellantis': 'STLA.MI',
            'enel': 'ENEL.MI',
            'telecom italia': 'TIT.MI',
            'prysmian': 'PRY.MI',
            'moncler': 'MONC.MI',
            
            # Spanish Companies
            'santander': 'SAN.MC',
            'bbva': 'BBVA.MC',
            'iberdrola': 'IBE.MC',
            'telefonica': 'TEF.MC',
            'repsol': 'REP.MC',
            'inditex': 'ITX.MC',
            'zara': 'ITX.MC',
            'ferrovial': 'FER.MC',
            'endesa': 'ELE.MC',
            'naturgy': 'NTGY.MC',
            
            # UK Companies
            'bp': 'BP.L',
            'astrazeneca': 'AZN.L',
            'vodafone': 'VOD.L',
            'bt': 'BT-A.L',
            'rolls royce': 'RR.L',
            'rolls-royce': 'RR.L',
            'rio tinto': 'RIO.L',
            'tesco': 'TSCO.L',
            'lloyds': 'LLOY.L',
            'barclays': 'BARC.L',
            'hsbc': 'HSBA.L',
            'gsk': 'GSK.L',
            'glaxosmithkline': 'GSK.L',
            'unilever': 'ULVR.L',
            'british american tobacco': 'BATS.L',
            'diageo': 'DGE.L',
            'aviva': 'AV.L',
            'prudential': 'PRU.L'
        }
        
        # Convert to lowercase for matching
        search_term = company_name.lower().strip()
        
        # Direct match
        if search_term in name_to_ticker:
            return name_to_ticker[search_term]
        
        # Partial match - check if search term starts with company name or vice versa
        for name, ticker in name_to_ticker.items():
            if search_term.startswith(name.lower()) or name.lower().startswith(search_term):
                return ticker
        
        # If no match found, try using the input as ticker
        if validate_ticker(company_name):
            return company_name.upper()
        
        return None
        
    except Exception as e:
        print(f"Error searching for company: {str(e)}")
        return None

def get_top_stocks_for_scanning() -> List[str]:
    """Get stocks optimized for short-term trading opportunities accessible in Germany."""
    return [
        # High-volatility momentum stocks (short-term opportunities)
        'TSLA', 'NVDA', 'AMD', 'PLTR', 'RIOT', 'MARA', 'COIN', 'RBLX',
        'SOFI', 'LCID', 'RIVN', 'CRWD', 'SNOW', 'ZM', 'DOCU', 'PTON',
        
        # Biotech & small pharma (high volatility, news-driven)
        'MRNA', 'BNTX', 'GILD', 'REGN', 'VRTX', 'BIIB', 'ILMN', 'AMGN',
        
        # Tech growth stocks (momentum-driven)
        'SHOP', 'SQ', 'ROKU', 'TWLO', 'OKTA', 'DDOG', 'NET', 'FSLY',
        'ESTC', 'MDB', 'SPLK', 'WDAY', 'VEEV', 'ZS', 'PANW',
        
        # Energy & commodities (volatile, news-sensitive)
        'XOM', 'CVX', 'SLB', 'HAL', 'OXY', 'DVN', 'EOG', 'PXD',
        
        # Meme stocks & social media driven
        'GME', 'AMC', 'BB', 'NOK', 'WISH', 'CLOV', 'SPCE', 'TLRY',
        
        # Chinese stocks (high volatility, accessible in Germany)
        'BABA', 'BIDU', 'JD', 'PDD', 'BILI', 'DIDI', 'NIO', 'XPEV', 'LI',
        
        # European high-beta stocks (directly accessible)
        'ASML.AS', 'SAP.DE', 'RHM.DE', 'TSLA', 'SPOT', 'ADYEN.AS',
        'BNTX', 'QCOM', 'ARM', 'TM', 'SONY', 'BABA', 'TSM'
    ]