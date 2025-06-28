"""European stock search with fuzzy matching support."""

from typing import Optional, List, Dict, Tuple
from difflib import get_close_matches, SequenceMatcher
import re

def fuzzy_search_european_stocks(company_name: str, name_to_ticker: Dict[str, str], 
                                threshold: float = 0.6) -> Optional[str]:
    """
    Implement fuzzy string matching for European company names.
    
    Args:
        company_name: User input company name
        name_to_ticker: Dictionary mapping company names to ticker symbols
        threshold: Similarity threshold (0-1, default 0.6)
        
    Returns:
        Best matching ticker symbol or None
    """
    if not company_name:
        return None
        
    # Clean input
    search_term = company_name.lower().strip()
    
    # Direct match first
    if search_term in name_to_ticker:
        return name_to_ticker[search_term]
    
    # Try fuzzy matching
    company_names = list(name_to_ticker.keys())
    matches = get_close_matches(search_term, company_names, n=1, cutoff=threshold)
    
    if matches:
        return name_to_ticker[matches[0]]
    
    # Try partial matching with higher threshold
    best_match = None
    best_score = 0
    
    for name in company_names:
        # Check if search term is contained in company name
        if search_term in name:
            score = len(search_term) / len(name)
            if score > best_score and score > 0.3:
                best_score = score
                best_match = name
        
        # Check if company name is contained in search term
        elif name in search_term:
            score = len(name) / len(search_term)
            if score > best_score and score > 0.5:
                best_score = score
                best_match = name
        
        # Advanced token-based matching
        else:
            search_tokens = set(search_term.split())
            name_tokens = set(name.split())
            
            # Check token overlap
            common_tokens = search_tokens & name_tokens
            if common_tokens:
                score = len(common_tokens) / max(len(search_tokens), len(name_tokens))
                if score > best_score and score > 0.5:
                    best_score = score
                    best_match = name
    
    if best_match:
        return name_to_ticker[best_match]
    
    return None


def get_alternative_tickers(company_name: str, name_to_ticker: Dict[str, str]) -> List[str]:
    """
    Return multiple ticker options for the same company.
    Example: BioNTech -> ['BNTX', '22UA.DE']
    
    Args:
        company_name: Company name to search
        name_to_ticker: Dictionary mapping company names to ticker symbols
        
    Returns:
        List of alternative ticker symbols
    """
    alternatives = []
    search_term = company_name.lower().strip()
    
    # Find all entries that match or contain the search term
    for name, ticker in name_to_ticker.items():
        if search_term in name or name in search_term:
            if ticker not in alternatives:
                alternatives.append(ticker)
    
    # Special cases for companies with multiple listings
    multi_listing_mappings = {
        'biontech': ['BNTX', '22UA.DE'],
        'astrazeneca': ['AZN.L', 'AZN.ST', 'AZN'],
        'nordea': ['NDA-SE.ST', 'NDA-FI.HE'],
        'stellantis': ['STLA.PA', 'STLA.MI'],
        'unilever': ['UNA.AS', 'ULVR.L'],
        'abb': ['ABB.SW', 'ABB.ST'],
        'shell': ['SHEL.AS', 'SHEL.L', 'SHEL'],
        'spotify': ['SPOT', 'SPOT.ST'],
        'adyen': ['ADYEN.AS', 'ADYEY'],
        'prosus': ['PRX.AS', 'PROSY'],
    }
    
    # Check for known multi-listing companies
    for key, tickers in multi_listing_mappings.items():
        if key in search_term or search_term in key:
            for ticker in tickers:
                if ticker not in alternatives:
                    alternatives.append(ticker)
    
    return alternatives


def normalize_company_name(name: str) -> str:
    """
    Normalize company name for better matching.
    
    Args:
        name: Company name to normalize
        
    Returns:
        Normalized company name
    """
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove common suffixes and legal forms
    suffixes_to_remove = [
        ' se', ' sa', ' ag', ' nv', ' plc', ' ltd', ' limited', ' inc', ' corp',
        ' corporation', ' company', ' group', ' holdings', ' holding', ' spa',
        ' gmbh', ' kg', ' kgaa', ' as', ' asa', ' ab', ' oyj', ' pte'
    ]
    
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    # Remove special characters and extra spaces
    normalized = re.sub(r'[^\w\s-]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def get_exchange_suffix(ticker: str) -> str:
    """
    Extract exchange suffix from ticker symbol.
    
    Args:
        ticker: Ticker symbol
        
    Returns:
        Exchange suffix or empty string
    """
    if '.' in ticker:
        return ticker.split('.')[-1]
    return ''


def get_country_from_exchange(exchange: str) -> str:
    """
    Map exchange suffix to country.
    
    Args:
        exchange: Exchange suffix
        
    Returns:
        Country name
    """
    exchange_to_country = {
        'DE': 'Germany',
        'PA': 'France',
        'AS': 'Netherlands',
        'SW': 'Switzerland',
        'MI': 'Italy',
        'MC': 'Spain',
        'L': 'United Kingdom',
        'BR': 'Belgium',
        'ST': 'Sweden',
        'CO': 'Denmark',
        'OL': 'Norway',
        'HE': 'Finland',
        'VI': 'Austria',
        'I': 'Ireland',
        'LS': 'Portugal',
        'AT': 'Greece',
        'WA': 'Poland',
        'PR': 'Czech Republic',
        'BD': 'Hungary'
    }
    
    return exchange_to_country.get(exchange, 'Unknown')


def search_by_country(country: str, name_to_ticker: Dict[str, str]) -> List[Tuple[str, str]]:
    """
    Get all companies from a specific country.
    
    Args:
        country: Country name
        name_to_ticker: Dictionary mapping company names to ticker symbols
        
    Returns:
        List of (company_name, ticker) tuples
    """
    country = country.lower()
    results = []
    
    for name, ticker in name_to_ticker.items():
        exchange = get_exchange_suffix(ticker)
        ticker_country = get_country_from_exchange(exchange).lower()
        
        if ticker_country == country:
            results.append((name, ticker))
    
    # Sort by company name
    results.sort(key=lambda x: x[0])
    
    return results