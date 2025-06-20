#!/usr/bin/env python3
"""
Results Database Module
Lightweight SQLite database for logging predictions and tracking accuracy.
Keeps under 1GB storage limit while providing valuable performance insights.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path

class ResultsDatabase:
    """
    Lightweight SQLite database for tracking prediction accuracy and performance.
    
    Features:
    - Prediction logging with timestamps
    - Accuracy tracking over time
    - Performance analytics by sector/market conditions
    - Storage optimization (automatic cleanup of old data)
    """
    
    def __init__(self, db_path: str = "stock_forecaster_results.db"):
        self.db_path = db_path
        self.max_records = 50000  # Limit to ~50k records (~50MB)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ticker TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    price_at_prediction REAL NOT NULL,
                    technical_score REAL,
                    momentum_score REAL,
                    volume_ratio REAL,
                    volatility_spike BOOLEAN,
                    multi_timeframe_score REAL,
                    confluence_score REAL,
                    market_regime TEXT,
                    sector TEXT,
                    reasoning TEXT,
                    prediction_source TEXT DEFAULT 'main_analyzer'
                )
            """)
            
            # Results table (for tracking actual outcomes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_id INTEGER,
                    check_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    days_after INTEGER NOT NULL,
                    price_after_1d REAL,
                    price_after_3d REAL,
                    price_after_7d REAL,
                    return_1d REAL,
                    return_3d REAL,
                    return_7d REAL,
                    direction_correct_1d BOOLEAN,
                    direction_correct_3d BOOLEAN,
                    direction_correct_7d BOOLEAN,
                    max_drawdown REAL,
                    max_gain REAL,
                    FOREIGN KEY (prediction_id) REFERENCES predictions (id)
                )
            """)
            
            # Performance analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_predictions INTEGER,
                    accuracy_1d REAL,
                    accuracy_3d REAL,
                    accuracy_7d REAL,
                    avg_return_1d REAL,
                    avg_return_3d REAL,
                    avg_return_7d REAL,
                    buy_signals INTEGER,
                    buy_accuracy REAL,
                    sell_signals INTEGER,
                    sell_accuracy REAL,
                    hold_signals INTEGER,
                    hold_accuracy REAL,
                    risky_buy_signals INTEGER,
                    risky_buy_accuracy REAL
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_ticker ON predictions(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_rating ON predictions(rating)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prediction_id ON prediction_results(prediction_id)")
            
            conn.commit()
    
    def log_prediction(self, prediction_data: Dict) -> int:
        """
        Log a new prediction to the database.
        
        Args:
            prediction_data: Dictionary containing prediction details
            
        Returns:
            prediction_id: ID of the inserted prediction
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Extract data with defaults
            ticker = prediction_data.get('ticker', '')
            rating = prediction_data.get('rating', 'HOLD')
            confidence = prediction_data.get('confidence', 0.5)
            price = prediction_data.get('current_price', 0.0)
            technical_score = prediction_data.get('technical_score', None)
            momentum_score = prediction_data.get('momentum_score', None)
            volume_ratio = prediction_data.get('volume_ratio', None)
            volatility_spike = prediction_data.get('volatility_spike', False)
            multi_tf_score = prediction_data.get('multi_timeframe_score', None)
            confluence_score = prediction_data.get('confluence_score', None)
            market_regime = prediction_data.get('market_regime', None)
            sector = prediction_data.get('sector', None)
            reasoning = json.dumps(prediction_data.get('reasoning', []))
            source = prediction_data.get('source', 'main_analyzer')
            
            cursor.execute("""
                INSERT INTO predictions (
                    ticker, rating, confidence, price_at_prediction,
                    technical_score, momentum_score, volume_ratio, volatility_spike,
                    multi_timeframe_score, confluence_score, market_regime, sector,
                    reasoning, prediction_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker, rating, confidence, price,
                technical_score, momentum_score, volume_ratio, volatility_spike,
                multi_tf_score, confluence_score, market_regime, sector,
                reasoning, source
            ))
            
            prediction_id = cursor.lastrowid
            conn.commit()
            
            # Clean up old records if we're approaching the limit
            self._cleanup_old_records()
            
            return prediction_id
    
    def update_prediction_result(self, prediction_id: int, days_after: int, 
                               current_price: float) -> bool:
        """
        Update prediction result with actual market outcome.
        
        Args:
            prediction_id: ID of the original prediction
            days_after: Number of days after prediction (1, 3, or 7)
            current_price: Current stock price
            
        Returns:
            bool: Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get original prediction
                cursor.execute("""
                    SELECT rating, price_at_prediction 
                    FROM predictions 
                    WHERE id = ?
                """, (prediction_id,))
                
                result = cursor.fetchone()
                if not result:
                    return False
                
                rating, original_price = result
                
                # Calculate return
                return_pct = (current_price - original_price) / original_price * 100
                
                # Check if direction was correct
                direction_correct = self._is_direction_correct(rating, return_pct)
                
                # Check if result record exists
                cursor.execute("""
                    SELECT id FROM prediction_results 
                    WHERE prediction_id = ? AND days_after = ?
                """, (prediction_id, days_after))
                
                if cursor.fetchone():
                    # Update existing record
                    if days_after == 1:
                        cursor.execute("""
                            UPDATE prediction_results 
                            SET price_after_1d = ?, return_1d = ?, direction_correct_1d = ?
                            WHERE prediction_id = ? AND days_after = ?
                        """, (current_price, return_pct, direction_correct, prediction_id, days_after))
                    elif days_after == 3:
                        cursor.execute("""
                            UPDATE prediction_results 
                            SET price_after_3d = ?, return_3d = ?, direction_correct_3d = ?
                            WHERE prediction_id = ? AND days_after = ?
                        """, (current_price, return_pct, direction_correct, prediction_id, days_after))
                    elif days_after == 7:
                        cursor.execute("""
                            UPDATE prediction_results 
                            SET price_after_7d = ?, return_7d = ?, direction_correct_7d = ?
                            WHERE prediction_id = ? AND days_after = ?
                        """, (current_price, return_pct, direction_correct, prediction_id, days_after))
                else:
                    # Insert new result record
                    cursor.execute("""
                        INSERT INTO prediction_results (
                            prediction_id, days_after, price_after_1d, price_after_3d, price_after_7d,
                            return_1d, return_3d, return_7d, 
                            direction_correct_1d, direction_correct_3d, direction_correct_7d
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prediction_id, days_after,
                        current_price if days_after == 1 else None,
                        current_price if days_after == 3 else None,
                        current_price if days_after == 7 else None,
                        return_pct if days_after == 1 else None,
                        return_pct if days_after == 3 else None,
                        return_pct if days_after == 7 else None,
                        direction_correct if days_after == 1 else None,
                        direction_correct if days_after == 3 else None,
                        direction_correct if days_after == 7 else None
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating prediction result: {str(e)}")
            return False
    
    def _is_direction_correct(self, rating: str, return_pct: float) -> bool:
        """Check if prediction direction was correct."""
        if rating == 'BUY' and return_pct > 0:
            return True
        elif rating == 'RISKY_BUY' and return_pct > 0:
            return True
        elif rating == 'SELL' and return_pct < 0:
            return True
        elif rating == 'HOLD' and abs(return_pct) < 2.0:
            return True
        return False
    
    def get_accuracy_stats(self, days: int = 30) -> Dict:
        """
        Get accuracy statistics for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with accuracy metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Overall accuracy
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_predictions,
                    AVG(CASE WHEN pr.direction_correct_1d = 1 THEN 1.0 ELSE 0.0 END) as accuracy_1d,
                    AVG(CASE WHEN pr.direction_correct_3d = 1 THEN 1.0 ELSE 0.0 END) as accuracy_3d,
                    AVG(CASE WHEN pr.direction_correct_7d = 1 THEN 1.0 ELSE 0.0 END) as accuracy_7d,
                    AVG(pr.return_1d) as avg_return_1d,
                    AVG(pr.return_3d) as avg_return_3d,
                    AVG(pr.return_7d) as avg_return_7d
                FROM predictions p
                LEFT JOIN prediction_results pr ON p.id = pr.prediction_id
                WHERE p.timestamp >= ?
            """, (cutoff_date,))
            
            overall_stats = cursor.fetchone()
            
            # Rating-specific accuracy
            cursor.execute("""
                SELECT 
                    p.rating,
                    COUNT(*) as count,
                    AVG(CASE WHEN pr.direction_correct_1d = 1 THEN 1.0 ELSE 0.0 END) as accuracy_1d,
                    AVG(pr.return_1d) as avg_return_1d
                FROM predictions p
                LEFT JOIN prediction_results pr ON p.id = pr.prediction_id
                WHERE p.timestamp >= ?
                GROUP BY p.rating
            """, (cutoff_date,))
            
            rating_stats = cursor.fetchall()
            
            return {
                'overall': {
                    'total_predictions': overall_stats[0] or 0,
                    'accuracy_1d': overall_stats[1] or 0,
                    'accuracy_3d': overall_stats[2] or 0,
                    'accuracy_7d': overall_stats[3] or 0,
                    'avg_return_1d': overall_stats[4] or 0,
                    'avg_return_3d': overall_stats[5] or 0,
                    'avg_return_7d': overall_stats[6] or 0
                },
                'by_rating': {
                    row[0]: {
                        'count': row[1],
                        'accuracy_1d': row[2] or 0,
                        'avg_return_1d': row[3] or 0
                    } for row in rating_stats
                },
                'period_days': days,
                'last_updated': datetime.now().isoformat()
            }
    
    def get_performance_trends(self, weeks: int = 8) -> Dict:
        """Get performance trends over time."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Weekly performance
            cursor.execute("""
                SELECT 
                    DATE(p.timestamp, 'weekday 0', '-6 days') as week_start,
                    COUNT(*) as predictions,
                    AVG(CASE WHEN pr.direction_correct_1d = 1 THEN 1.0 ELSE 0.0 END) as accuracy,
                    AVG(pr.return_1d) as avg_return
                FROM predictions p
                LEFT JOIN prediction_results pr ON p.id = pr.prediction_id
                WHERE p.timestamp >= DATE('now', '-{} weeks')
                GROUP BY DATE(p.timestamp, 'weekday 0', '-6 days')
                ORDER BY week_start
            """.format(weeks))
            
            trends = cursor.fetchall()
            
            return {
                'weekly_trends': [
                    {
                        'week': row[0],
                        'predictions': row[1],
                        'accuracy': row[2] or 0,
                        'avg_return': row[3] or 0
                    } for row in trends
                ]
            }
    
    def get_top_performing_stocks(self, limit: int = 10) -> List[Dict]:
        """Get stocks with best prediction accuracy."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.ticker,
                    COUNT(*) as prediction_count,
                    AVG(CASE WHEN pr.direction_correct_1d = 1 THEN 1.0 ELSE 0.0 END) as accuracy,
                    AVG(pr.return_1d) as avg_return
                FROM predictions p
                LEFT JOIN prediction_results pr ON p.id = pr.prediction_id
                WHERE pr.direction_correct_1d IS NOT NULL
                GROUP BY p.ticker
                HAVING COUNT(*) >= 3  -- At least 3 predictions
                ORDER BY accuracy DESC, avg_return DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            
            return [
                {
                    'ticker': row[0],
                    'prediction_count': row[1],
                    'accuracy': row[2] or 0,
                    'avg_return': row[3] or 0
                } for row in results
            ]
    
    def _cleanup_old_records(self):
        """Remove old records to keep database size under control."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check current record count
            cursor.execute("SELECT COUNT(*) FROM predictions")
            count = cursor.fetchone()[0]
            
            if count > self.max_records:
                # Delete oldest 10% of records
                delete_count = int(count * 0.1)
                
                cursor.execute("""
                    DELETE FROM predictions 
                    WHERE id IN (
                        SELECT id FROM predictions 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                """, (delete_count,))
                
                # Clean up orphaned results
                cursor.execute("""
                    DELETE FROM prediction_results 
                    WHERE prediction_id NOT IN (SELECT id FROM predictions)
                """)
                
                conn.commit()
                print(f"Cleaned up {delete_count} old prediction records")
    
    def get_database_stats(self) -> Dict:
        """Get database size and record count statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get record counts
            cursor.execute("SELECT COUNT(*) FROM predictions")
            prediction_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM prediction_results")
            result_count = cursor.fetchone()[0]
            
            # Get database file size
            try:
                file_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            except:
                file_size = 0
            
            return {
                'prediction_records': prediction_count,
                'result_records': result_count,
                'file_size_mb': round(file_size, 2),
                'max_records': self.max_records,
                'storage_usage_pct': round((prediction_count / self.max_records) * 100, 1)
            }


# Global database instance
_db_instance = None

def get_database() -> ResultsDatabase:
    """Get global database instance (singleton pattern)."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ResultsDatabase()
    return _db_instance

def log_prediction(prediction_data: Dict) -> int:
    """Convenience function to log a prediction."""
    return get_database().log_prediction(prediction_data)

def update_result(prediction_id: int, days_after: int, current_price: float) -> bool:
    """Convenience function to update prediction result."""
    return get_database().update_prediction_result(prediction_id, days_after, current_price)

def get_recent_accuracy(days: int = 30) -> Dict:
    """Convenience function to get recent accuracy stats."""
    return get_database().get_accuracy_stats(days)