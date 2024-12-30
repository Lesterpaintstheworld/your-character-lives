"""Data processing module for visualization preparation"""

from typing import List, Dict
import pandas as pd
from datetime import datetime, timedelta
import psutil
import time

class PerformanceDataProcessor:
    def __init__(self):
        self.memory_data = []
        self.query_data = []
        self.algorithm_data = []
        self.config_data = []

    def collect_memory_data(self, duration_seconds: int = 60, interval: int = 1) -> List[Dict]:
        """Collect memory usage data over time"""
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            self.memory_data.append({
                'timestamp': datetime.now(),
                'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
            })
            time.sleep(interval)
        return self.memory_data

    def process_query_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Process raw query performance data"""
        df = pd.DataFrame(raw_data)
        # Group by memory size and calculate statistics
        processed_data = df.groupby('memory_size').agg({
            'query_time': ['mean', 'std', 'min', 'max']
        }).reset_index()
        return processed_data.to_dict('records')

    def process_algorithm_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Process algorithm comparison data"""
        df = pd.DataFrame(raw_data)
        # Calculate average execution time for each algorithm
        processed_data = df.groupby('algorithm')['execution_time'].mean().reset_index()
        return processed_data.to_dict('records')

    def process_config_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Process configuration impact data"""
        df = pd.DataFrame(raw_data)
        # Pivot and normalize data for heatmap
        processed_data = df.pivot_table(
            index='config_param',
            columns='value',
            values='performance_score',
            aggfunc='mean'
        ).reset_index()
        return processed_data.to_dict('records')
