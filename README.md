Gold vs US Dollar Index: Pairs Trading Strategy  
Python - pandas - statsmodels - yfinance - matplotlib 

### Overview   
A market neutral pairs trading strategy exploiting the inverse relationship between gold futures (GC=F) and the US Index (DX-Y.NYB).  
Built independently as a finance project, applying statistical testing, signal generation and backtesting across 860 trading days (Jan 2023 - Jun 2026).  
However, ADF and Engle-Granger tests identified a structural breakdown in the gold/dollar inverse relationship. 

### Methodology  
**Data Collection**: Daily closing prices downloaded via yfinance from Jan 2023 - Jun 2026.  
**Normalisation**: Both series indexed to 100 to enable direct comparison.  
**Stationarity Testing**: ADF test applied to spread (p = 0.97, hence non-stationary).  
**Cointegration Testing**: Engle-Granger test on raw series (p = 0.78, hence not cointegrated).  
**Z-score Signals**: 60 day rolling window, +-2 entry threshold, +-0.5 exit threshold.   
**Pairs Trade Construction**: Simultaneous long/short positions across both assets.  
**Backtesting**: Daily returns calculated using prior-day signals to avoid look-ahead bias.  

### Results  
| Metric | Value |
|---|---|
| Strategy Return | −30.8% |
| Buy & Hold Gold (Benchmark) | +135.8% |
| Annualised Sharpe Ratio | −0.98 |
| Maximum Drawdown | −37.42% |
| Win Rate | 45.3% |  

### Key Finding
Both the ADF and Engle-Granger tests identified a structural breakdown in the 
gold/dollar relationship over the sample period. Gold decoupled from its 
traditional inverse relationship with the dollar, driven by sustained central 
bank accumulation and geopolitical safe-haven demand. The strategy's negative 
returns directly confirmed this — mean reversion strategies systematically fail 
during structural regime changes, a limitation the statistical testing identified 
before the backtest results confirmed it.

### Charts
- **Figure 1** — Gold vs Dollar Index normalised to 100
- **Figure 2** — Rolling z-score with entry and exit thresholds
- **Figure 3** — Strategy vs Buy & Hold Gold cumulative returns
- **Figure 4** — Spread with long/short trade regions highlighted

<img width="1800" height="750" alt="image" src="https://github.com/user-attachments/assets/e9f8fae3-594b-4821-92ba-114278988cf1" />
<img width="1800" height="600" alt="image" src="https://github.com/user-attachments/assets/fe97ecd0-6d8d-4ba9-aaa7-79a841eb2cb4" />
<img width="1800" height="750" alt="image" src="https://github.com/user-attachments/assets/a3da97bf-eb13-4def-bc12-5cc45c280808" />
<img width="1800" height="600" alt="image" src="https://github.com/user-attachments/assets/65f63b23-f2af-4351-9a26-60e759a9a660" />

### Author  
Harry McCarthy | BSc Economics & Finance, University of Bristol 
