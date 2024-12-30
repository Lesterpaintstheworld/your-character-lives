"""Data visualization module for performance and memory insights"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional

from config import Config

class PerformanceVisualizer:
    def __init__(self, config: Config):
        self.config = config
        plt.style.use(config.DEFAULT_PLOT_STYLE)
        self.default_figsize = config.CHART_FIGSIZE
        
    def plot_memory_usage(self, data: List[Dict], save: bool = True) -> Optional[str]:
        """Plot memory usage over time"""
        plt.figure(figsize=self.default_figsize)
        df = pd.DataFrame(data)
        
        sns.lineplot(data=df, x='timestamp', y='memory_usage', marker='o')
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time')
        plt.ylabel('Memory Usage (MB)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save:
            filename = f'memory_usage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join(self.config.VISUALIZATION_OUTPUT_DIR, filename)
            plt.savefig(filepath, dpi=self.config.CHART_DPI)
            plt.close()
            return filepath
        plt.show()
        return None

    def plot_query_performance(self, data: List[Dict], save: bool = True) -> Optional[str]:
        """Compare query times for different memory sizes"""
        plt.figure(figsize=self.default_figsize)
        df = pd.DataFrame(data)
        
        sns.boxplot(data=df, x='memory_size', y='query_time')
        plt.title('Query Performance by Memory Size')
        plt.xlabel('Memory Size (MB)')
        plt.ylabel('Query Time (ms)')
        plt.tight_layout()
        
        if save:
            filename = f'query_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join(self.config.VISUALIZATION_OUTPUT_DIR, filename)
            plt.savefig(filepath, dpi=self.config.CHART_DPI)
            plt.close()
            return filepath
        plt.show()
        return None

    def plot_algorithm_comparison(self, data: List[Dict], save: bool = True) -> Optional[str]:
        """Compare performance of different optimization algorithms"""
        plt.figure(figsize=self.default_figsize)
        df = pd.DataFrame(data)
        
        sns.barplot(data=df, x='algorithm', y='execution_time')
        plt.title('Algorithm Performance Comparison')
        plt.xlabel('Algorithm')
        plt.ylabel('Execution Time (ms)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save:
            filename = f'algorithm_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join(self.config.VISUALIZATION_OUTPUT_DIR, filename)
            plt.savefig(filepath, dpi=self.config.CHART_DPI)
            plt.close()
            return filepath
        plt.show()
        return None

    def plot_config_impact(self, data: List[Dict], save: bool = True) -> Optional[str]:
        """Visualize impact of different configurations on performance"""
        plt.figure(figsize=self.default_figsize)
        df = pd.DataFrame(data)
        
        sns.heatmap(df.pivot("config_param", "value", "performance_score"), 
                   annot=True, cmap='YlOrRd', fmt='.2f')
        plt.title('Configuration Impact on Performance')
        plt.tight_layout()
        
        if save:
            filename = f'config_impact_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join(self.config.VISUALIZATION_OUTPUT_DIR, filename)
            plt.savefig(filepath, dpi=self.config.CHART_DPI)
            plt.close()
            return filepath
        plt.show()
        return None
