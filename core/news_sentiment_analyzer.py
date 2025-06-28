"""
News Sentiment Analyzer for Stock Forecasting

Analyzes news sentiment and detects potential manipulation patterns using free data sources.
Uses TextBlob for sentiment analysis and various free news APIs.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import time
import json
import re
from urllib.parse import quote_plus

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not available. News sentiment analysis will be limited.")

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("Warning: feedparser not available. RSS feeds will not be accessible.")


@dataclass
class NewsArticle:
    """Represents a news article with sentiment analysis."""
    title: str
    description: str
    published_date: datetime
    source: str
    url: str
    sentiment_score: float  # -1.0 (negative) to 1.0 (positive)
    sentiment_magnitude: float  # 0.0 to 1.0 (strength of sentiment)


@dataclass
class NewsSentimentResult:
    """Results from news sentiment analysis."""
    sentiment_score: float  # Overall sentiment (-1.0 to 1.0)
    manipulation_risk: float  # 0.0 to 1.0
    news_volume: int  # Number of articles analyzed
    sentiment_trend: str  # 'INCREASING', 'DECREASING', 'STABLE'
    price_correlation: float  # -1.0 to 1.0
    pump_dump_probability: float  # 0.0 to 1.0
    articles: List[NewsArticle]
    analysis_summary: List[str]


class NewsSentimentForecaster:
    """
    Analyzes news sentiment and detects potential manipulation patterns.
    """
    
    def __init__(self):
        self.news_sources = {
            'yahoo_finance_rss': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US',
            'google_news': 'https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en',
        }
        self.max_articles_per_source = 20
        self.sentiment_cache = {}  # Simple cache to avoid re-analyzing same articles
    
    def analyze_news_sentiment_forecast(self, ticker: str, days_lookback: int = 30) -> NewsSentimentResult:
        """
        Main news sentiment analysis function.
        
        Args:
            ticker: Stock ticker symbol
            days_lookback: Number of days to look back for news
            
        Returns:
            NewsSentimentResult with comprehensive sentiment analysis
        """
        try:
            # Collect news articles from all sources
            all_articles = []
            
            # Yahoo Finance RSS
            yahoo_articles = self.fetch_yahoo_finance_news(ticker)
            all_articles.extend(yahoo_articles)
            
            # Google News RSS
            google_articles = self.fetch_google_news_mentions(ticker)
            all_articles.extend(google_articles)
            
            # Filter articles by date
            cutoff_date = datetime.now() - timedelta(days=days_lookback)
            recent_articles = [a for a in all_articles if a.published_date >= cutoff_date]
            
            if not recent_articles:
                return self._create_neutral_result("No recent news articles found")
            
            # Calculate overall sentiment metrics
            sentiment_scores = [a.sentiment_score for a in recent_articles]
            overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Analyze sentiment trend
            sentiment_trend = self._analyze_sentiment_trend(recent_articles)
            
            # Detect manipulation patterns
            manipulation_risk = self._detect_manipulation_patterns(recent_articles, ticker)
            
            # Calculate pump and dump probability
            pump_dump_prob = self._calculate_pump_dump_probability(recent_articles, manipulation_risk)
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(
                recent_articles, overall_sentiment, manipulation_risk, sentiment_trend
            )
            
            return NewsSentimentResult(
                sentiment_score=overall_sentiment,
                manipulation_risk=manipulation_risk,
                news_volume=len(recent_articles),
                sentiment_trend=sentiment_trend,
                price_correlation=0.0,  # Would need price data to calculate
                pump_dump_probability=pump_dump_prob,
                articles=recent_articles,
                analysis_summary=analysis_summary
            )
            
        except Exception as e:
            print(f"Error in news sentiment analysis for {ticker}: {e}")
            return self._create_neutral_result(f"Analysis failed: {str(e)}")
    
    def fetch_yahoo_finance_news(self, ticker: str) -> List[NewsArticle]:
        """
        Fetch news from Yahoo Finance RSS feeds.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of NewsArticle objects
        """
        if not FEEDPARSER_AVAILABLE:
            return []
        
        articles = []
        try:
            url = self.news_sources['yahoo_finance_rss'].format(ticker=ticker)
            
            # Add user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    # Parse publication date
                    pub_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    # Extract title and description
                    title = entry.get('title', '')
                    description = entry.get('summary', '')
                    
                    # Analyze sentiment
                    sentiment_score, magnitude = self.analyze_sentiment_textblob(title + ' ' + description)
                    
                    article = NewsArticle(
                        title=title,
                        description=description,
                        published_date=pub_date,
                        source='Yahoo Finance',
                        url=entry.get('link', ''),
                        sentiment_score=sentiment_score,
                        sentiment_magnitude=magnitude
                    )
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Error processing Yahoo Finance article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Yahoo Finance news for {ticker}: {e}")
        
        return articles
    
    def fetch_google_news_mentions(self, ticker: str) -> List[NewsArticle]:
        """
        Fetch news from Google News RSS.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of NewsArticle objects
        """
        if not FEEDPARSER_AVAILABLE:
            return []
        
        articles = []
        try:
            # Create search query
            search_query = f"{ticker} stock"
            url = self.news_sources['google_news'].format(ticker=quote_plus(search_query))
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    # Parse publication date
                    pub_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    # Extract title and description
                    title = entry.get('title', '')
                    description = entry.get('summary', '')
                    
                    # Only include if ticker is mentioned
                    if ticker.upper() not in (title + ' ' + description).upper():
                        continue
                    
                    # Analyze sentiment
                    sentiment_score, magnitude = self.analyze_sentiment_textblob(title + ' ' + description)
                    
                    article = NewsArticle(
                        title=title,
                        description=description,
                        published_date=pub_date,
                        source='Google News',
                        url=entry.get('link', ''),
                        sentiment_score=sentiment_score,
                        sentiment_magnitude=magnitude
                    )
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Error processing Google News article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching Google News for {ticker}: {e}")
        
        return articles
    
    def analyze_sentiment_textblob(self, text: str) -> Tuple[float, float]:
        """
        Use TextBlob for free sentiment analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, magnitude)
        """
        if not TEXTBLOB_AVAILABLE or not text:
            return 0.0, 0.0
        
        try:
            blob = TextBlob(text)
            
            # TextBlob returns polarity (-1 to 1) and subjectivity (0 to 1)
            sentiment_score = blob.sentiment.polarity
            magnitude = abs(sentiment_score) * blob.sentiment.subjectivity
            
            return sentiment_score, magnitude
            
        except Exception as e:
            print(f"Error in TextBlob sentiment analysis: {e}")
            return 0.0, 0.0
    
    def _detect_manipulation_patterns(self, articles: List[NewsArticle], ticker: str) -> float:
        """
        Detect pump and dump patterns in news sentiment.
        
        Args:
            articles: List of news articles
            ticker: Stock ticker
            
        Returns:
            Manipulation risk score (0.0 to 1.0)
        """
        if len(articles) < 3:
            return 0.0
        
        risk_factors = []
        risk_score = 0.0
        
        # Check for unusual news volume spikes (more realistic thresholds)
        recent_24h = [a for a in articles if (datetime.now() - a.published_date).days < 1]
        normal_daily_volume = max(3, len(articles) / 7)  # Estimate normal daily volume
        if len(recent_24h) > normal_daily_volume * 2:
            risk_score += 0.2
            risk_factors.append(f"News volume spike: {len(recent_24h)} articles in 24h")
        
        # Check for extreme positive sentiment (lowered thresholds)
        very_positive = [a for a in articles if a.sentiment_score > 0.5]
        positive_ratio = len(very_positive) / len(articles)
        if positive_ratio > 0.75:
            risk_score += 0.3
            risk_factors.append(f"Excessive positive sentiment: {positive_ratio:.0%} very positive")
        elif positive_ratio > 0.6:
            risk_score += 0.15
            risk_factors.append(f"High positive sentiment: {positive_ratio:.0%} very positive")
        
        # Check for repetitive headlines (more sensitive detection)
        titles = [a.title.lower() for a in articles]
        unique_titles = set(titles)
        uniqueness_ratio = len(unique_titles) / len(titles)
        if uniqueness_ratio < 0.6:
            risk_score += 0.3
            risk_factors.append(f"Repetitive headlines: {uniqueness_ratio:.0%} unique")
        elif uniqueness_ratio < 0.8:
            risk_score += 0.15
            risk_factors.append(f"Some repetitive headlines: {uniqueness_ratio:.0%} unique")
        
        # Enhanced promotional language detection
        promotional_keywords = [
            'rocket', 'moon', 'diamond hands', 'to the moon', 'massive gains',
            'guaranteed', 'hot stock', 'next big thing', 'explosive growth',
            'breakout', 'surge', 'skyrocket', 'bullish', 'bearish', 'rally'
        ]
        
        promotional_count = 0
        total_keywords = 0
        for article in articles:
            text = (article.title + ' ' + article.description).lower()
            article_keywords = sum(1 for keyword in promotional_keywords if keyword in text)
            if article_keywords > 0:
                promotional_count += 1
            total_keywords += article_keywords
        
        promo_ratio = promotional_count / len(articles)
        if promo_ratio > 0.4:
            risk_score += 0.25
            risk_factors.append(f"High promotional language: {promo_ratio:.0%} of articles")
        elif promo_ratio > 0.2:
            risk_score += 0.1
            risk_factors.append(f"Some promotional language: {promo_ratio:.0%} of articles")
        
        # Add sentiment volatility check
        if len(articles) >= 5:
            sentiment_scores = [a.sentiment_score for a in articles]
            sentiment_std = (sum((x - sum(sentiment_scores)/len(sentiment_scores))**2 for x in sentiment_scores) / len(sentiment_scores))**0.5
            if sentiment_std > 0.6:
                risk_score += 0.15
                risk_factors.append(f"High sentiment volatility: {sentiment_std:.2f}")
        
        # Add time clustering check (multiple articles in short timespan)
        if len(articles) >= 5:
            time_diffs = []
            sorted_articles = sorted(articles, key=lambda x: x.published_date)
            for i in range(1, len(sorted_articles)):
                diff_hours = (sorted_articles[i].published_date - sorted_articles[i-1].published_date).total_seconds() / 3600
                time_diffs.append(diff_hours)
            
            avg_time_diff = sum(time_diffs) / len(time_diffs)
            if avg_time_diff < 2:  # Articles less than 2 hours apart on average
                risk_score += 0.2
                risk_factors.append(f"Time clustering: articles {avg_time_diff:.1f}h apart avg")
        
        return min(1.0, risk_score)
    
    def _calculate_pump_dump_probability(self, articles: List[NewsArticle], manipulation_risk: float) -> float:
        """
        Calculate probability of pump and dump scheme with improved sensitivity.
        
        Args:
            articles: List of news articles
            manipulation_risk: Pre-calculated manipulation risk
            
        Returns:
            Pump and dump probability (0.0 to 1.0)
        """
        if len(articles) < 3:
            return 0.0
        
        pump_score = 0.0
        
        # Base score from manipulation risk
        pump_score += manipulation_risk * 0.4
        
        # Sudden spike in positive news (more realistic thresholds)
        positive_articles = [a for a in articles if a.sentiment_score > 0.3]
        positive_ratio = len(positive_articles) / len(articles)
        if positive_ratio > 0.7:
            pump_score += 0.3
        elif positive_ratio > 0.6:
            pump_score += 0.15
        
        # Very high positive sentiment
        very_positive = [a for a in articles if a.sentiment_score > 0.6]
        if len(very_positive) / len(articles) > 0.5:
            pump_score += 0.2
        
        # Lack of substantial news content (more lenient)
        if articles:
            avg_description_length = sum(len(a.description) for a in articles) / len(articles)
            if avg_description_length < 150:
                pump_score += 0.2
            elif avg_description_length < 100:
                pump_score += 0.3
        
        # Recent concentration of articles
        recent_12h = [a for a in articles if (datetime.now() - a.published_date).total_seconds() < 43200]
        if len(recent_12h) / len(articles) > 0.6:
            pump_score += 0.15
        
        # Sentiment uniformity (all articles similar sentiment - suspicious)
        if len(articles) >= 3:
            sentiment_scores = [a.sentiment_score for a in articles]
            sentiment_range = max(sentiment_scores) - min(sentiment_scores)
            if sentiment_range < 0.3:  # Very similar sentiments
                pump_score += 0.15
        
        # Keywords associated with pump schemes
        pump_keywords = ['surge', 'spike', 'breakout', 'rally', 'soar', 'explode', 'rocket']
        keyword_count = 0
        for article in articles:
            text = (article.title + ' ' + article.description).lower()
            keyword_count += sum(1 for keyword in pump_keywords if keyword in text)
        
        if keyword_count / len(articles) > 0.5:
            pump_score += 0.2
        
        return min(1.0, pump_score)
    
    def _analyze_sentiment_trend(self, articles: List[NewsArticle]) -> str:
        """
        Analyze sentiment trend over time.
        
        Args:
            articles: List of news articles sorted by date
            
        Returns:
            Trend direction: 'INCREASING', 'DECREASING', 'STABLE'
        """
        if len(articles) < 5:
            return 'STABLE'
        
        # Sort articles by date
        sorted_articles = sorted(articles, key=lambda x: x.published_date)
        
        # Split into first half and second half
        midpoint = len(sorted_articles) // 2
        first_half = sorted_articles[:midpoint]
        second_half = sorted_articles[midpoint:]
        
        # Calculate average sentiment for each half
        first_avg = sum(a.sentiment_score for a in first_half) / len(first_half)
        second_avg = sum(a.sentiment_score for a in second_half) / len(second_half)
        
        # Determine trend
        difference = second_avg - first_avg
        
        if difference > 0.1:
            return 'INCREASING'
        elif difference < -0.1:
            return 'DECREASING'
        else:
            return 'STABLE'
    
    def _generate_analysis_summary(self, articles: List[NewsArticle], sentiment: float, 
                                 manipulation_risk: float, trend: str) -> List[str]:
        """
        Generate human-readable analysis summary.
        
        Args:
            articles: News articles
            sentiment: Overall sentiment score
            manipulation_risk: Manipulation risk score
            trend: Sentiment trend
            
        Returns:
            List of summary statements
        """
        summary = []
        
        # Overall sentiment interpretation
        if sentiment > 0.3:
            summary.append(f"Overall news sentiment is POSITIVE ({sentiment:.2f})")
        elif sentiment < -0.3:
            summary.append(f"Overall news sentiment is NEGATIVE ({sentiment:.2f})")
        else:
            summary.append(f"Overall news sentiment is NEUTRAL ({sentiment:.2f})")
        
        # News volume assessment
        if len(articles) > 15:
            summary.append(f"High news volume ({len(articles)} articles) indicates elevated interest")
        elif len(articles) < 5:
            summary.append(f"Low news volume ({len(articles)} articles) suggests limited attention")
        
        # Sentiment trend
        summary.append(f"Sentiment trend is {trend}")
        
        # Manipulation warning
        if manipulation_risk > 0.6:
            summary.append(f"HIGH manipulation risk detected ({manipulation_risk:.1%})")
        elif manipulation_risk > 0.3:
            summary.append(f"Moderate manipulation risk ({manipulation_risk:.1%})")
        
        # Most common sentiment
        positive_count = len([a for a in articles if a.sentiment_score > 0.1])
        negative_count = len([a for a in articles if a.sentiment_score < -0.1])
        
        if positive_count > negative_count * 2:
            summary.append("Predominantly positive news coverage")
        elif negative_count > positive_count * 2:
            summary.append("Predominantly negative news coverage")
        
        return summary
    
    def _create_neutral_result(self, reason: str) -> NewsSentimentResult:
        """Create a neutral result when analysis fails or no data available."""
        return NewsSentimentResult(
            sentiment_score=0.0,
            manipulation_risk=0.0,
            news_volume=0,
            sentiment_trend='STABLE',
            price_correlation=0.0,
            pump_dump_probability=0.0,
            articles=[],
            analysis_summary=[reason]
        )