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
        
        # Extract high/low for institutional indicators
        highs = hist['High'].tolist() if 'High' in hist.columns else prices
        lows = hist['Low'].tolist() if 'Low' in hist.columns else prices
        
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
            pe_ratio=info.get('trailingPE'),
            highs=highs,
            lows=lows
        )
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None

def validate_ticker(ticker: str) -> bool:
    """Check if ticker is valid and has data available."""
    try:
        # Input sanitization
        if not ticker or not isinstance(ticker, str):
            return False
        
        # Remove any whitespace
        ticker = ticker.strip()
        
        # Check length (tickers are typically 1-5 chars, with exchange suffix max 10)
        if len(ticker) == 0 or len(ticker) > 10:
            return False
        
        # Allow only alphanumeric, dots, and hyphens (for tickers like BRK-B, RHM.DE)
        import re
        if not re.match(r'^[A-Za-z0-9.\-]+$', ticker):
            return False
        
        # Prevent common injection patterns
        forbidden_patterns = ['..', '--', '\\', '/', '<', '>', '|', '&', ';', '$', '`', '"', "'", '\n', '\r', '\0']
        for pattern in forbidden_patterns:
            if pattern in ticker:
                return False
        
        # Check with yfinance
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
            'prudential': 'PRU.L',
            
            # Belgium Companies
            'anheuser-busch': 'ABI.BR',
            'anheuser busch inbev': 'ABI.BR',
            'ab inbev': 'ABI.BR',
            'kbc group': 'KBC.BR',
            'kbc': 'KBC.BR',
            'solvay': 'SOLB.BR',
            'ucb': 'UCB.BR',
            'ageas': 'AGS.BR',
            'proximus': 'PROX.BR',
            'colruyt': 'COLR.BR',
            'sofina': 'SOF.BR',
            'ackermans': 'ACKB.BR',
            'gbl': 'GBLB.BR',
            
            # More German Companies
            'biontech': 'BNTX',  # NASDAQ listing
            'biontech se': '22UA.DE',  # German listing
            'deutsche post': 'DPW.DE',
            'fresenius': 'FRE.DE',
            'merck kgaa': 'MRK.DE',
            'deutsche telekom': 'DTE.DE',
            'e.on': 'EOAN.DE',
            'rwe': 'RWE.DE',
            'thyssenkrupp': 'TKA.DE',
            'beiersdorf': 'BEI.DE',
            'porsche': 'P911.DE',
            'zalando': 'ZAL.DE',
            'hellofresh': 'HFG.DE',
            'delivery hero': 'DHER.DE',
            'wirecard': 'WDI.DE',
            'commerzbank': 'CBK.DE',
            'metro': 'B4B.DE',
            'hugo boss': 'BOSS.DE',
            'puma': 'PUM.DE',
            
            # More Dutch Companies
            'ahold delhaize': 'AD.AS',
            'wolters kluwer': 'WKL.AS',
            'kpn': 'KPN.AS',
            'aegon': 'AGN.AS',
            'nn group': 'NN.AS',
            'just eat takeaway': 'TKWY.AS',
            'randstad': 'RAND.AS',
            'imcd': 'IMCD.AS',
            'signify': 'LIGHT.AS',
            'arcadis': 'ARCAD.AS',
            'corbion': 'CRBN.AS',
            'fugro': 'FUR.AS',
            
            # More French Companies
            'atos': 'ATO.PA',
            'societe generale': 'GLE.PA',
            'credit agricole': 'ACA.PA',
            'essilor': 'EL.PA',
            'essilorluxottica': 'EL.PA',
            'saint-gobain': 'SGO.PA',
            'renault': 'RNO.PA',
            'carrefour': 'CA.PA',
            'vivendi': 'VIV.PA',
            'thales': 'HO.PA',
            'veolia': 'VIE.PA',
            'air liquide': 'AI.PA',
            'legrand': 'LR.PA',
            'dassault systemes': 'DSY.PA',
            'engie': 'ENGI.PA',
            'edenred': 'EDEN.PA',
            'sodexo': 'SW.PA',
            'publicis': 'PUB.PA',
            'teleperformance': 'TEP.PA',
            
            # More Swiss Companies
            'swatch': 'UHR.SW',
            'holcim': 'HOLN.SW',
            'lafargeholcim': 'HOLN.SW',
            'julius baer': 'BAER.SW',
            'partners group': 'PGHN.SW',
            'schindler': 'SCHN.SW',
            'sika': 'SIKA.SW',
            'geberit': 'GEBN.SW',
            'kuehne nagel': 'KNIN.SW',
            'baloise': 'BALN.SW',
            'temenos': 'TEMN.SW',
            'logitech': 'LOGN.SW',
            'sonova': 'SOON.SW',
            'straumann': 'STMN.SW',
            
            # More Italian Companies
            'fiat chrysler': 'STLA.MI',
            'fca': 'STLA.MI',
            'pirelli': 'PIRC.MI',
            'luxottica': 'LUX.MI',
            'atlantia': 'ATL.MI',
            'poste italiane': 'PST.MI',
            'terna': 'TRN.MI',
            'snam': 'SRG.MI',
            'mediobanca': 'MB.MI',
            'banco bpm': 'BAMI.MI',
            'banca mediolanum': 'BMED.MI',
            'campari': 'CPR.MI',
            'diasorin': 'DIA.MI',
            'amplifon': 'AMP.MI',
            'recordati': 'REC.MI',
            
            # More Spanish Companies
            'caixabank': 'CABK.MC',
            'amadeus': 'AMS.MC',
            'siemens gamesa': 'SGRE.MC',
            'acciona': 'ANA.MC',
            'acs': 'ACS.MC',
            'grifols': 'GRF.MC',
            'mapfre': 'MAP.MC',
            'red electrica': 'REE.MC',
            'enagas': 'ENG.MC',
            'bankinter': 'BKT.MC',
            'indra': 'IDR.MC',
            'cellnex': 'CLNX.MC',
            'merlin properties': 'MRL.MC',
            'inmobiliaria colonial': 'COL.MC',
            
            # Nordic Companies - Sweden
            'ericsson': 'ERIC-B.ST',
            'volvo': 'VOLV-B.ST',
            'hennes & mauritz': 'HM-B.ST',
            'h&m': 'HM-B.ST',
            'atlas copco': 'ATCO-A.ST',
            'sandvik': 'SAND.ST',
            'investor': 'INVE-B.ST',
            'nordea': 'NDA-SE.ST',
            'swedbank': 'SWED-A.ST',
            'seb': 'SEB-A.ST',
            'skf': 'SKF-B.ST',
            'telia': 'TELIA.ST',
            'hexagon': 'HEXA-B.ST',
            'essity': 'ESSITY-B.ST',
            'abb': 'ABB.ST',
            'astrazeneca': 'AZN.ST',
            'spotify': 'SPOT.ST',
            'evolution': 'EVO.ST',
            'swedish match': 'SWMA.ST',
            'electrolux': 'ELUX-B.ST',
            
            # Nordic Companies - Denmark
            'novo nordisk': 'NOVO-B.CO',
            'danske bank': 'DANSKE.CO',
            'carlsberg': 'CARL-B.CO',
            'orsted': 'ORSTED.CO',
            'vestas': 'VWS.CO',
            'pandora': 'PNDORA.CO',
            'dsv': 'DSV.CO',
            'coloplast': 'COLO-B.CO',
            'demant': 'DEMANT.CO',
            'gn store nord': 'GN.CO',
            'chr hansen': 'CHR.CO',
            'ambu': 'AMBU-B.CO',
            'tryg': 'TRYG.CO',
            'novozymes': 'NZYM-B.CO',
            
            # Nordic Companies - Norway
            'equinor': 'EQNR.OL',
            'dnb': 'DNB.OL',
            'telenor': 'TEL.OL',
            'norsk hydro': 'NHY.OL',
            'yara': 'YAR.OL',
            'gjensidige': 'GJF.OL',
            'orkla': 'ORK.OL',
            'schibsted': 'SCHA.OL',
            'aker': 'AKER.OL',
            'storebrand': 'STB.OL',
            'salmar': 'SALM.OL',
            'mowi': 'MOWI.OL',
            
            # Nordic Companies - Finland
            'nokia': 'NOKIA.HE',
            'nordea': 'NDA-FI.HE',
            'sampo': 'SAMPO.HE',
            'kone': 'KNEBV.HE',
            'neste': 'NESTE.HE',
            'upm': 'UPM.HE',
            'stora enso': 'STERV.HE',
            'wartsila': 'WRT1V.HE',
            'metso': 'METSO.HE',
            'elisa': 'ELISA.HE',
            'fortum': 'FORTUM.HE',
            'orion': 'ORNBV.HE',
            
            # Austrian Companies
            'omv': 'OMV.VI',
            'erste group': 'EBS.VI',
            'voestalpine': 'VOE.VI',
            'verbund': 'VER.VI',
            'andritz': 'ANDR.VI',
            'wienerberger': 'WIE.VI',
            'raiffeisen': 'RBI.VI',
            'vienna insurance': 'VIG.VI',
            
            # Irish Companies
            'ryanair': 'RYA.I',
            'crh': 'CRH.I',
            'kerry group': 'KYG.I',
            'smurfit kappa': 'SKG.I',
            'aib': 'AIBG.I',
            'bank of ireland': 'BIRG.I',
            'paddy power': 'PPB.I',
            'flutter': 'FLTR.I',
            
            # Portuguese Companies
            'edp': 'EDP.LS',
            'galp': 'GALP.LS',
            'jeronimo martins': 'JMT.LS',
            'bcp': 'BCP.LS',
            'nos': 'NOS.LS',
            'navigator': 'NVG.LS',
            
            # Greek Companies
            'national bank greece': 'ETE.AT',
            'alpha bank': 'ALPHA.AT',
            'opap': 'OPAP.AT',
            'ote': 'HTO.AT',
            'motor oil': 'MOH.AT',
            'titan cement': 'TITK.AT',
            
            # Polish Companies
            'pkn orlen': 'PKN.WA',
            'pko bank': 'PKO.WA',
            'pzu': 'PZU.WA',
            'kghm': 'KGH.WA',
            'cd projekt': 'CDR.WA',
            'dino polska': 'DNP.WA',
            'allegro': 'ALE.WA',
            
            # Czech Companies
            'cez': 'CEZ.PR',
            'komercni banka': 'KOMB.PR',
            'moneta': 'MONET.PR',
            'avast': 'AVST.PR',
            
            # Hungarian Companies
            'otp bank': 'OTP.BD',
            'mol': 'MOL.BD',
            'richter': 'RICHT.BD',
            'mtelekom': 'MTEL.BD'
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
        
        # Try fuzzy search as fallback
        try:
            from .european_stock_search import fuzzy_search_european_stocks
            fuzzy_result = fuzzy_search_european_stocks(company_name, name_to_ticker)
            if fuzzy_result:
                return fuzzy_result
        except Exception as e:
            print(f"Fuzzy search failed: {e}")
        
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
        'SHOP', 'ROKU', 'TWLO', 'OKTA', 'DDOG', 'NET', 'FSLY',
        'ESTC', 'MDB', 'WDAY', 'VEEV', 'ZS', 'PANW', 'SMCI', 'AVGO',
        
        # Energy & commodities (volatile, news-sensitive)
        'XOM', 'CVX', 'SLB', 'HAL', 'OXY', 'DVN', 'EOG', 'COP', 'EPD',
        
        # Meme stocks & social media driven
        'GME', 'AMC', 'BB', 'NOK', 'CLOV', 'SPCE', 'TLRY', 'BBBY', 'APE',
        
        # Chinese stocks (high volatility, accessible in Germany)
        'BABA', 'BIDU', 'JD', 'PDD', 'BILI', 'DIDI', 'NIO', 'XPEV', 'LI',
        
        # European high-beta stocks (directly accessible)
        'ASML.AS', 'SAP.DE', 'RHM.DE', 'TSLA', 'SPOT', 'ADYEN.AS',
        'BNTX', 'QCOM', 'ARM', 'TM', 'SONY', 'BABA', 'TSM'
    ]

def get_top_stocks_for_scanning_with_europe() -> List[str]:
    """Get stocks including major European equities for comprehensive scanning."""
    us_stocks = get_top_stocks_for_scanning()
    
    # Add major European stocks
    european_stocks = [
        # German DAX stocks
        'SAP.DE', 'SIE.DE', 'ALV.DE', 'BMW.DE', 'BAS.DE', 'BAYN.DE',
        'ADS.DE', 'VNA.DE', 'DBK.DE', 'VOW3.DE', 'IFX.DE', 'HEN3.DE', 'MUV2.DE',
        'RHM.DE', 'DTE.DE', 'EON.DE',  # Added more active German stocks
        
        # French CAC 40
        'MC.PA', 'OR.PA', 'SAN.PA', 'TTE.PA', 'AIR.PA', 'BNP.PA', 'ACA.PA',
        'SU.PA', 'CS.PA', 'EL.PA', 'DG.PA', 'RI.PA', 'KER.PA',
        
        # Dutch AEX
        'ASML.AS', 'SHELL.AS', 'UNA.AS', 'HEIA.AS', 'INGA.AS', 'ADYEN.AS',
        'WKL.AS', 'PHIA.AS', 'ABN.AS', 'KPN.AS',
        
        # UK FTSE (accessible via European exchanges)
        'SHEL.L', 'AZN.L', 'HSBA.L', 'BP.L', 'GSK.L', 'DGE.L', 'RIO.L',
        'ULVR.L', 'NG.L', 'LLOY.L', 'BARC.L', 'STAN.L',
        
        # Swiss SMI
        'NESN.SW', 'ROG.SW', 'NOVN.SW', 'UBS.SW', 'CSGN.SW', 'SREN.SW',
        'GEBN.SW', 'GIVN.SW', 'ABBN.SW', 'LONN.SW',
        
        # Italian FTSE MIB
        'ISP.MI', 'UCG.MI', 'ENEL.MI', 'ENI.MI', 'RACE.MI', 'STM.MI',
        'G.MI', 'LDO.MI', 'MONC.MI',
        
        # Spanish IBEX
        'ITX.MC', 'SAN.MC', 'TEF.MC', 'IBE.MC', 'BBVA.MC', 'AMA.MC',
        'REP.MC', 'FER.MC', 'GRF.MC'
    ]
    
    # Combine and return unique stocks
    all_stocks = list(set(us_stocks + european_stocks))
    return all_stocks[:100]  # Limit to 100 for performance