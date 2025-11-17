#!/usr/bin/env python3
"""
Create Visualization Dashboard
Interactive dashboard for backtest results analysis
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def create_html_dashboard(results_file: str, output_file: str):
    """Create interactive HTML dashboard with charts"""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        PLOTLY_AVAILABLE = True
    except ImportError:
        PLOTLY_AVAILABLE = False
        logger.warning("Plotly not available - creating basic HTML report")
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Prepare data
    all_results = []
    for config_name, results in data.items():
        for r in results:
            if 'error' not in r:
                r['config'] = config_name
                all_results.append(r)
    
    if not all_results:
        logger.warning("No results to visualize")
        return
    
    df = pd.DataFrame(all_results)
    
    # Create HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Backtest Results Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f0f0f0; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .metric-label {{ font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <h1>📊 Backtest Results Dashboard</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Summary Statistics</h2>
    <div class="metric">
        <div class="metric-value">{len(all_results)}</div>
        <div class="metric-label">Total Backtests</div>
    </div>
    <div class="metric">
        <div class="metric-value">{df['total_trades'].sum() if 'total_trades' in df.columns else 0}</div>
        <div class="metric-label">Total Trades</div>
    </div>
    <div class="metric">
        <div class="metric-value">{df['win_rate'].mean():.2f}%</div>
        <div class="metric-label">Avg Win Rate</div>
    </div>
    <div class="metric">
        <div class="metric-value">{df['total_return'].mean():.2f}%</div>
        <div class="metric-label">Avg Return</div>
    </div>
    
    <h2>Performance by Configuration</h2>
    <div id="config-chart"></div>
    
    <h2>Performance by Symbol</h2>
    <div id="symbol-chart"></div>
    
    <script>
        // Configuration comparison
        var configData = {{
            x: {list(df.groupby('config')['win_rate'].mean().index) if 'win_rate' in df.columns else []},
            y: {list(df.groupby('config')['win_rate'].mean().values) if 'win_rate' in df.columns else []},
            type: 'bar',
            name: 'Win Rate %'
        }};
        
        var configLayout = {{
            title: 'Average Win Rate by Configuration',
            xaxis: {{ title: 'Configuration' }},
            yaxis: {{ title: 'Win Rate %' }}
        }};
        
        Plotly.newPlot('config-chart', [configData], configLayout);
        
        // Symbol comparison
        var symbolData = {{
            x: {list(df.groupby('symbol')['total_return'].mean().index) if 'total_return' in df.columns else []},
            y: {list(df.groupby('symbol')['total_return'].mean().values) if 'total_return' in df.columns else []},
            type: 'bar',
            name: 'Total Return %'
        }};
        
        var symbolLayout = {{
            title: 'Average Return by Symbol',
            xaxis: {{ title: 'Symbol' }},
            yaxis: {{ title: 'Total Return %' }}
        }};
        
        Plotly.newPlot('symbol-chart', [symbolData], symbolLayout);
    </script>
</body>
</html>
    """
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"✅ Dashboard created: {output_file}")

if __name__ == "__main__":
    results_file = "argo/reports/comprehensive_backtest_results.json"
    output_file = "argo/reports/dashboard.html"
    
    create_html_dashboard(results_file, output_file)

