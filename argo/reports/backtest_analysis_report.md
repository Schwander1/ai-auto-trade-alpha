
# Backtest Results Analysis Report
Generated: 2025-11-15 05:17:48

## Executive Summary

**Total Backtests:** 60
**Total Symbols:** 12
**Total Configurations:** 5
**Total Trades:** 38,880

### Average Performance
- **Win Rate:** 47.73%
- **Total Return:** 21.01%
- **Sharpe Ratio:** 1.06
- **Max Drawdown:** -25.55%

### Best Configuration
- **Config:** all_optimizations
- **Win Rate:** 47.73%
- **Total Return:** 21.01%
- **Sharpe Ratio:** 1.06
- **Total Trades:** 7,776

### Best Symbol
- **Symbol:** AMD
- **Win Rate:** 49.94%
- **Total Return:** 33.22%
- **Sharpe Ratio:** 1.16
- **Total Trades:** 4,105

## Configuration Comparison

                    win_rate                     total_return                    sharpe_ratio                   max_drawdown                     total_trades       
                        mean   std    min    max         mean   std   min    max         mean   std   min   max         mean   std    min    max          sum   mean
config                                                                                                                                                              
all_optimizations      47.73  2.27  43.96  50.55        21.01  11.8 -8.93  33.46         1.06  0.12  0.69  1.16       -25.55  2.18 -29.86 -22.89         7776  648.0
baseline               47.73  2.27  43.96  50.55        21.01  11.8 -8.93  33.46         1.06  0.12  0.69  1.16       -25.55  2.18 -29.86 -22.89         7776  648.0
confidence_88          47.73  2.27  43.96  50.55        21.01  11.8 -8.93  33.46         1.06  0.12  0.69  1.16       -25.55  2.18 -29.86 -22.89         7776  648.0
regime_weights         47.73  2.27  43.96  50.55        21.01  11.8 -8.93  33.46         1.06  0.12  0.69  1.16       -25.55  2.18 -29.86 -22.89         7776  648.0
weight_optimization    47.73  2.27  43.96  50.55        21.01  11.8 -8.93  33.46         1.06  0.12  0.69  1.16       -25.55  2.18 -29.86 -22.89         7776  648.0

## Symbol Comparison

        win_rate                    total_return                    sharpe_ratio                  max_drawdown                    total_trades       
            mean  std    min    max         mean  std    min    max         mean  std   min   max         mean  std    min    max          sum   mean
symbol                                                                                                                                               
AAPL       49.32  0.0  49.32  49.32        16.51  0.0  16.51  16.51         1.08  0.0  1.08  1.08       -24.41  0.0 -24.41 -24.41         3700  740.0
AMD        49.94  0.0  49.94  49.94        33.22  0.0  33.22  33.22         1.16  0.0  1.16  1.16       -29.86  0.0 -29.86 -29.86         4105  821.0
AMZN       43.96  0.0  43.96  43.96        33.46  0.0  33.46  33.46         1.09  0.0  1.09  1.09       -23.72  0.0 -23.72 -23.72         3685  737.0
BTC-USD    45.57  0.0  45.57  45.57        22.69  0.0  22.69  22.69         0.69  0.0  0.69  0.69       -23.74  0.0 -23.74 -23.74         1635  327.0
ETH-USD    50.55  0.0  50.55  50.55         7.99  0.0   7.99   7.99         1.05  0.0  1.05  1.05       -28.34  0.0 -28.34 -28.34         2285  457.0
GOOGL      48.28  0.0  48.28  48.28        22.55  0.0  22.55  22.55         1.09  0.0  1.09  1.09       -24.89  0.0 -24.89 -24.89         3635  727.0
META       45.63  0.0  45.63  45.63        -8.93  0.0  -8.93  -8.93         1.09  0.0  1.09  1.09       -26.75  0.0 -26.75 -26.75         2520  504.0
MSFT       44.84  0.0  44.84  44.84        28.37  0.0  28.37  28.37         1.09  0.0  1.09  1.09       -23.59  0.0 -23.59 -23.59         3680  736.0
NVDA       46.97  0.0  46.97  46.97        22.81  0.0  22.81  22.81         1.10  0.0  1.10  1.10       -27.52  0.0 -27.52 -27.52         3790  758.0
QQQ        49.33  0.0  49.33  49.33        27.26  0.0  27.26  27.26         1.04  0.0  1.04  1.04       -24.59  0.0 -24.59 -24.59         3365  673.0
SPY        50.22  0.0  50.22  50.22        19.19  0.0  19.19  19.19         1.09  0.0  1.09  1.09       -22.89  0.0 -22.89 -22.89         3435  687.0
TSLA       48.11  0.0  48.11  48.11        27.04  0.0  27.04  27.04         1.13  0.0  1.13  1.13       -26.31  0.0 -26.31 -26.31         3045  609.0

## Detailed Results

### Top 10 Performers (by Sharpe Ratio)
symbol              config  win_rate  total_return  sharpe_ratio  total_trades
   AMD            baseline 49.939099     33.219601      1.164691           821
   AMD weight_optimization 49.939099     33.219601      1.164691           821
   AMD      regime_weights 49.939099     33.219601      1.164691           821
   AMD       confidence_88 49.939099     33.219601      1.164691           821
   AMD   all_optimizations 49.939099     33.219601      1.164691           821
  TSLA            baseline 48.111658     27.035013      1.133391           609
  TSLA weight_optimization 48.111658     27.035013      1.133391           609
  TSLA      regime_weights 48.111658     27.035013      1.133391           609
  TSLA       confidence_88 48.111658     27.035013      1.133391           609
  TSLA   all_optimizations 48.111658     27.035013      1.133391           609

### Bottom 10 Performers (by Sharpe Ratio)
 symbol              config  win_rate  total_return  sharpe_ratio  total_trades
BTC-USD            baseline 45.565749     22.689372      0.688864           327
BTC-USD weight_optimization 45.565749     22.689372      0.688864           327
BTC-USD      regime_weights 45.565749     22.689372      0.688864           327
BTC-USD       confidence_88 45.565749     22.689372      0.688864           327
BTC-USD   all_optimizations 45.565749     22.689372      0.688864           327
    QQQ            baseline 49.331352     27.262911      1.038261           673
    QQQ weight_optimization 49.331352     27.262911      1.038261           673
    QQQ      regime_weights 49.331352     27.262911      1.038261           673
    QQQ       confidence_88 49.331352     27.262911      1.038261           673
    QQQ   all_optimizations 49.331352     27.262911      1.038261           673

### Most Active (by Trade Count)
symbol              config  win_rate  total_return  sharpe_ratio  total_trades
   AMD            baseline 49.939099     33.219601      1.164691           821
   AMD weight_optimization 49.939099     33.219601      1.164691           821
   AMD      regime_weights 49.939099     33.219601      1.164691           821
   AMD       confidence_88 49.939099     33.219601      1.164691           821
   AMD   all_optimizations 49.939099     33.219601      1.164691           821
  NVDA            baseline 46.965699     22.814648      1.099866           758
  NVDA weight_optimization 46.965699     22.814648      1.099866           758
  NVDA      regime_weights 46.965699     22.814648      1.099866           758
  NVDA       confidence_88 46.965699     22.814648      1.099866           758
  NVDA   all_optimizations 46.965699     22.814648      1.099866           758
