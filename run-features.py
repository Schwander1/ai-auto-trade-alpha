import pandas as pd
import numpy as np
import clickhouse_connect
from sklearn.preprocessing import StandardScaler

client = clickhouse_connect.get_client(host='localhost', port=8123, username='default', password='password123')
all_data = []

for symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']:
    print(f'Processing {symbol}...')
query = f"SELECT timestamp, open, high, low, close, volume FROM trading_db.market_data WHERE symbol = '{symbol}' ORDER BY timestamp"
result = client.query(query)

if result.result_rows:
    df = pd.DataFrame(result.result_rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    close = df['close'].values.astype(float)

    df['rsi'] = pd.Series(close).rolling(14).mean()
    df['macd'] = pd.Series(close).ewm(span=12).mean() - pd.Series(close).ewm(span=26).mean()
    df['atr'] = pd.Series(df['high'] - df['low']).rolling(14).mean()
    df['sma_20'] = pd.Series(close).rolling(20).mean()
    df['sma_50'] = pd.Series(close).rolling(50).mean()
    df['bb_upper'] = pd.Series(close).rolling(20).mean() + 2 * pd.Series(close).rolling(20).std()
    df['bb_lower'] = pd.Series(close).rolling(20).mean() - 2 * pd.Series(close).rolling(20).std()
    df['obv'] = pd.Series(df['volume']).cumsum()
    df['ad_line'] = 0
    df['cci'] = 0
    df['target'] = (df['close'] > df['open']).astype(int)

    all_data.append(df)
    print(f'  ✓ {len(df)} rows')
client.close()

if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    scaler = StandardScaler()
    feature_cols = ['rsi', 'macd', 'atr', 'sma_20', 'sma_50', 'bb_upper', 'bb_lower', 'obv', 'ad_line', 'cci']
    combined[feature_cols] = scaler.fit_transform(combined[feature_cols].fillna(0))
    combined.to_csv('datapipeline/features/features_output.csv', index=False)
    print(f'\n✓ SUCCESS! {len(combined)} rows saved')
else:
    print('❌ No data')
