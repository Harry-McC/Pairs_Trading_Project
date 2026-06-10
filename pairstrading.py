# Pairs Trading Strategy: Gold vs US Dollar Index
# Author: Harry McCarthy
# Description: This project tests whether gold & the dollar index have a
# mean-reverting relationship, and backtests a simple trading strategy that
# exploits temporary divergences between them.

# PART 1: IMPORTING LIBRARIES
import yfinance as yf
     #downloads real market data from Yahoo Finance
import pandas as pd
     #handles data im table (Date Frame) format
import numpy as np
     #perfrom fast mathematical & statistical calculations on numerical data
import matplotlib.pyplot as plt
     #creat charts & graphs for financial analysis
import seaborn as sns
     #create more attractive & advanced statistical visualisations
from statsmodels.tsa.stattools import adfuller
     #the ADF stationarity test
from statsmodels.tsa.stattools import coint
     #the Engle Granger Cointegration test
sns.set(style="whitegrid")
     #set a clean visual style for all charts
print("All libraries imported successfully")


# PART 2: DOWNLOAD RELEVANT MARKET DATA
print("/nDownloading market data...")
gold_data = yf.download('GC=F', start='2023-01-01', end='2026-06-08', auto_adjust=True)
dollar_data = yf.download('DX-Y.NYB', start='2023-01-01', end='2026-06-08', auto_adjust=True)
     #download gold price & dollar index data
gold = gold_data['Close'].squeeze()
dollar = dollar_data['Close'].squeeze()
     #extract just the closing data from each dataset. 'Close' is just
     #the price at the end of each trading day
df = pd.DataFrame({'Gold':gold, 'Dollar':dollar}).dropna()
     #combine both into one table & remove any days where data is missing

print(f"Data download: {len(df)} trading days loaded")
print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
print(f"Gold price range: ${df['Gold'].min():.0f} - ${df['Gold'].max():.0f}")
print(f"Dollar index range:{df['Dollar'].min():.1f} - {df['Dollar'].max():.1f}")


#PART 3: NORMALISE BOTH SERIES
#Gold & the US Dollar index trade at very different price levels.
#Comparing the raw prices directly would be misleading so we need to normalise the data to compare.
#We make them both start at 100 to see relative performance.
#Formula: (today price / first price) * 100
df['Gold_norm'] = (df['Gold'] / df['Gold'].iloc[0]) * 100
df['Dollar_norm'] = (df['Dollar'] / df['Dollar'].iloc[0]) * 100
print("\n✓ Both series normalised to base 100")


#PART 4: PLOTTING THE NORMALISED SERIES
#This gives the first visual check, we should see gold & the dollar moving roughly in opposite
#directions. This represents their well-known inverse relationship.
plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Gold_norm'], label='Gold', color='goldenrod', linewidth=1.5)
plt.plot(df.index, df['Dollar_norm'], label='Dollar', color='steelblue', linewidth=1.5)
plt.axhline(100, color='grey', linestyle='--', linewidth=0.8, alpha=0.5)
plt.title('Gold vs Dollar Index - Normalised to 100', fontsize=14, fontweight='bold')
plt.ylabel('Indexed Price (Base=100)')
plt.xlabel('Date')
plt.legend()
plt.tight_layout()
plt.savefig('plot1_normalised_prices.png', dpi=150)
plt.show()
print("✓ Chart 1 saved: plot1_normalised_prices.png")


#PART 5: CALCULATE THE SPREAD
#The spread is the difference between the 2 normalised series.
#When gold is expensive relative to the dollar, the spread is high.
#When gold is cheap relative to the dollar, the spread is low.
#The key assumption: this spread should mean-revert, return to average.
df['Spread'] = df['Gold_norm'] - df['Dollar_norm']

print(f"\n✓  Spread calculated")
print(f"✓  Spread mean:  {df['Spread'].mean():.2f}")
print(f"✓  Spread std:  {df['Spread'].std():.2f}")
print(f"✓  Spread range:  {df['Spread'].min():.2f} to {df['Spread'].max():.2f}")


#PART 6: ADF STATIONARITY TEST & THE ENGLE-GRANGER COINTEGRATION TEST
#Need to statistically prove that the spread is mean-reverting (stationary). If it is not,
#the whole strategy is built on a false assumption.
#The ADF test checks this formally:
#   H0: series is non-stationary (has a unit root)
#Want to reject the null, meaning p-value < 0.05
#A p-value < 0.05 means we're >95% confident that the spread is stationary.
print("\n--- ADF STATIONARITY TEST ON THE SPREAD ---")

adf_result = adfuller(df['Spread'].dropna())

adf_statistic = adf_result[0]   #test statistic
p_value = adf_result[1]   #p-value
critical_values = adf_result[4]   #critical value at the 1%, 5%, 10%
# [0]=test statistic; [1]=p-value; [2]=lags used; [3]=n observations; [4]=critical values ...

print(f"   ADF Statistic: {adf_statistic:.4f}")
print(f"   P-value: {p_value:.4f}")
print(f"   Critical Values:")
for level, value in critical_values.items():
    print(f"   {level}: {value:.4f}")

#Interpret the results clearly:
if p_value < 0.05:
    print(f"\n✓ RESULT: p-value ({p_value:.4f}) < 0.05")
    print(" We reject the null hypothesis.")
    print(" The spread is STATIONARY - mean reversion confirmed.")
    print(" Our pairs trading strategy is statistically valid.")
else:
    print(f"\nx RESULT: p-value ({p_value:.4f}) > 0.05")
    print(" We FAIL TO REJECT the null hypothesis.")
    print(" The spread may NOT be stationary over this period.")
    print(" Consider adjusting the date range or asset selection.")

print("\n--- ENGLE_GRANGER COINTEGRATION TEST ---")

score, p_value_coint, crit_values_coint = coint(df['Gold'], df['Dollar'])

print(f"   Cointegration Test Statistic: {score:>4f}")
print(f"   P-value: {p_value_coint:.4f}")
print(f"   Critical Values (1%, 5%, 10%): {crit_values_coint}")

if p_value_coint < 0.05:
    print(f"\n✓ RESULT: p-value ({p_value_coint:.4f}) < 0.05")
    print(" We REJECT the null hypothesis.")
    print(" Gold and the Dollar ARE cointegrated.")
    print(" A long-run equilibrium relationship exists.")
    print(" Pairs trading strategy is statistically valid despite the ADF result.")
else:
    print(f"\nx RESULT: p-value ({p_value_coint:.4f}) > 0.05")
    print(" We FAIL TO REJECT the null hypothesis.")
    print(" Gold and the Dollar are NOT cointegrated over this period.")
    print(" Pairs trading is NOT valid if ADF test also failed, if ADF passed, proceed cautiously or re-evaluate.")


#PART 7: CALCULATE THE ROLLING Z-SCORE
#The z-score tells us how far the spread is from its recent average, measured in standard deviations.
#Formula = (current spread - rolling mean) / rolling standard deviation
#We use a 60-day rolling window, meaning we compare today's spread to the last 60 days,
#not the entire history. This keeps the model adaptive.
#Interpretation:
#z > +2 --> spread is unusually wide (gold is expensive vs the dollar)
#z < -2 --> spread is unusually narrow (gold is cheap vs the dollar)
#z ~ 0 --> spread is at its normal level

WINDOW = 60

df['Spread_mean'] = df['Spread'].rolling(window=WINDOW).mean()
df['Spread_std'] = df['Spread'].rolling(window=WINDOW).std()
df['Z_score'] = (df['Spread'] - df['Spread_mean']) / df['Spread_std']

print(f"\n✓ Z-score calculated (rolling {WINDOW}-day window)")


#PART 8: PLOT THE Z-SCORE
#Visualise where the spread is extreme vs normal.
#The red dashed lines at +-2 are our entry thresholds.

plt.figure(figsize=(12, 4))
plt.plot(df.index, df['Z_score'], color='purple', linewidth=1, label='Z-score')
plt.axhline(2, color='red', linestyle='--', linewidth=1.2, label='Entry threshold (+2)')
plt.axhline(-2, color='green', linestyle='--', linewidth=1.2, label='Entry threshold (+2)')
plt.axhline(0.5, color='orange', linestyle=':', linewidth=0.8, label='Exit threshold (+-0.5)')
plt.axhline(-0.5, color='orange', linestyle=':', linewidth=0.8)
plt.axhline(0, color='grey', linestyle='-', linewidth=0.8, alpha=0.5)
plt.fill_between(df.index, df['Z_score'], 2,
                 where=(df['Z_score'] < -2), alpha=0.2, color='green')
plt.title('Z-score of Gold/Dollar Spread - Entry & Exit Signals', fontsize=14, fontweight='bold')
plt.ylabel('Z-score (standard deviations from mean)')
plt.xlabel('Date')
plt.legend(loc='upper right', fontsize=8)
plt.tight_layout()
plt.savefig('plot2_zscore.png', dpi=150)
plt.show()
print("✓ Chart 2 saved: plot2_zscore.png")


#PART 9: GENERATE TRADING SIGNALS
#Based on the z-score, we generate 3 possible signals:
#signal = -1 (short gold)
     #z-score > +2, spread is too wide, gold overpriced vs dollar
     #bet that gold falls back toward the average
#signal = +1 (long gold)
     #z-score < -2, spread is too narrow, gold underpriced vs dollar
     #bet that gold rises back toward average
#signal = 0 (no position)
     #z-score between -0.5 and +0.5, spread has normalised, exit trade

# Note: we use .loc[] to set values directly on the original dataframe.
# This is the correct pandas pattern and avoids the SettingWithCopyWarning
# that occurs if you try to edit a filtered slice of a dataframe directly.

ENTRY_THRESHOLD = 2.0   #enter trade when z-score crosses +-2
EXIT_THRESHOLD = 0.5   #exit trade when z-score returns within +-0.5
df['Signal'] = 0   #start with no position everywhere

df.loc[df['Z_score'] > ENTRY_THRESHOLD, 'Signal'] = -1
#where z-score is above +2, short gold, we expect it to fall back

df.loc[df['Z_score'] < -ENTRY_THRESHOLD, 'Signal'] = 1
#when z-score is below -2, long gold, we expect it to rise back

df.loc[df['Z_score'].abs() < EXIT_THRESHOLD, 'Signal'] = 0
#when z-score has normalised, no position, exit any open trades

#forward fill signals, once we enter a trade, stay in it until exit signal, (otherwise position would
#disappear every day between entry and exit)
df['Signal'] = df['Signal'].replace(0, np.nan).ffill().fillna(0)

#re-apply the exit: force signal to 0 when z-score is back to normal
df.loc[df['Z_score'].abs() < EXIT_THRESHOLD, 'Signal'] = 0

n_long = (df['Signal'] == 1).sum()
n_short = (df['Signal'] == -1).sum()
n_flat = (df['Signal'] == 0).sum()
print(f"\n✓ Signal generated:")
print(f"   Long (buy gold): {n_long} days")
print(f"   Short (sell gold): {n_short} days")
print(f"   Flat (no trade): {n_flat} days")


#PART 10: BACKTEST - TRUE PAIRS TRADE
#Trade both assets simultaneously:
#   Gold position: follows the signal (long or short)
#   Dollar position: opposite of gold
#This makes the strategy market neutral, we profit from the relationship between the
#2 assets normalising, not from either asset's direction.

df['Gold_return'] = df['Gold'].pct_change()
df['Dollar_return'] = df['Dollar'].pct_change()

df['Gold_leg'] = df['Signal'].shift(1) * df['Gold_return']
df['Dollar_leg'] = -df['Signal'].shift(1) * df['Dollar_return']

df['Strategy_return'] = (df['Gold_leg'] + df['Dollar_leg']) / 2
#Combined pairs trade return = average of both legs
#Divide by 2 as we're splitting capital across 2 positions

df['Return_of_holding_gold'] = df['Gold_return']    #for comparison, just buying & holding gold
df['Return_of_holding_dollar'] = df['Dollar_return']    #for comparison, just buying & holding dollar

df = df.dropna(subset=['Strategy_return', 'Gold_return'])
#removes Nan (not a number) from pct_change & shift datesets

print()
print(f"✓ Pairs trade backtest complete: {len(df)} trading days simulated")
print(f"   Gold leg trades: {(df['Gold_leg'] != 0).sum()} active days")
print(f"   Dollar leg trades: {(df['Dollar_leg'] != 0).sum()} active days")


#PART 11: PERFORMANCE METRICS
# 3 standard metrics used on trading desks:
   # 1. TOTAL RETURN - overall profit (or loss) across the full period
   # 2. SHARPE RATIO - return per unit of risk taken
   #    formula: (mean daily return / std of daily return) * sqrt(252)
   #    sqrt(252) converts daily to annual (252 trading days per year)
   #    above 1.0 = good and above 2.0 = excellent
   # 3. MAX DRAWDOWN - worst peak to trough loss during the period
   #    e.g. -12% means the strategy fell 12% from its highest point before recovering.
   #    measures downside risk.

# Cumulative returns (compounded)
df['Cumulative_strategy'] = (1 + df['Strategy_return']).cumprod()
df['Cumulative_gold'] = (1 + df['Return_of_holding_gold']).cumprod()
df['Cumulative_dollar'] = (1 + df['Return_of_holding_dollar']).cumprod()

# Total return
total_return = df['Cumulative_strategy'].iloc[-1] - 1
gold_return = df['Cumulative_gold'].iloc[-1] - 1
dollar_return = df['Cumulative_dollar'].iloc[-1] - 1


# Sharpe ratio (annualised)
sharpe = (df['Strategy_return'].mean() / df['Strategy_return'].std()) * np.sqrt(252)

# Maximum drawdown
rolling_max = df['Cumulative_strategy'].cummax()
drawdown = (df['Cumulative_strategy'] - rolling_max) / rolling_max
max_drawdown = drawdown.min()

# Win rate
active_days = df[df['Strategy_return'] != 0]
win_rate = (df['Strategy_return'] > 0).sum() / len(df[df['Strategy_return'] != 0]) * 100

print("\n" + "="*50)
print("      PAIRS TRADE PERFORMANCE SUMMARY")
print("="*50)
print(f"  Strategy (Pairs Trade):    {total_return:+.2%}")
print(f"  Benchmark (Buy&Hold Gold): {gold_return:+.2%}")
print(f"  Benchmark (Buy & Hold Dollar): {dollar_return:+.2%}")
print(f"  Annualised Sharpe Ratio:   {sharpe:.2f}")
print(f"  Maximum Drawdown:          {max_drawdown:.2%}")
print(f"  Win Rate:                  {win_rate:.1f}%")
print("="*50)


#PART 12: PLOT CUMULATIVE RETURNS COMPARISON
#Compare our pairs trade returns against simply buying & holding gold or the dollar.
#If our strategy line is above the gold or dollar line, we outperformed.
#If below, buying & holding the asset that is above would've been better.
#In this case, only compare to gold as the dollar basically flatlined.

plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Cumulative_strategy'], color='darkgreen', linewidth=2,
         label='Pairs Trading Strategy (Gold & Dollar)')
plt.plot(df.index, df['Cumulative_gold'], color='goldenrod', linewidth=1.5, linestyle='--',
         label='Buy & Hold Gold (Benchmark)')
plt.axhline(1, color='grey', linestyle='-', linewidth=0.8, alpha=0.5)
plt.title('Pairs Trade vs Buy & Hold Gold - Cumulative Returns', fontsize=14, fontweight='bold')
plt.ylabel('Growth of £1 invested')
plt.xlabel('Date')
plt.legend()

#Annotation box showing key stats directly on the chart.
textstr = f'Sharpe: {sharpe:.2f}\nMax DD: {max_drawdown:.1%}\nReturn: {total_return:+.1%}'
props = dict(boxstyle='round', facecolor='white', alpha=0.8)
plt.text(0.02, 0.95, textstr, transform=plt.gca().transAxes, fontsize=9,
         verticalalignment='top', bbox=props)

plt.tight_layout()
plt.savefig('plot3_cumulative_returns.png', dpi=150)
plt.show()
print("✓ Chart 3 saved: plot3_cumulative_returns.png")


#PART 13: PLOT — SPREAD WITH TRADE ENTRY AND EXIT REGIONS
# Shows the actual spread over time with shading wherever we were in a trade.
# Green shading = long gold / short dollar
# Red shading   = short gold / long dollar
# This lets you visually check whether the strategy entered and exited
# at sensible points relative to the spread's movement.

plt.figure(figsize=(12, 4))
plt.plot(df.index, df['Spread'], color='navy', linewidth=1,
         label='Spread (Gold - Dollar)', alpha=0.7)
plt.plot(df.index, df['Spread_mean'], color='grey', linewidth=1,
         linestyle='--', label='60-day rolling mean')

# Green shading — long gold, short dollar (z-score was too low)
plt.fill_between(df.index, df['Spread'], df['Spread_mean'],
                 where=(df['Signal'] == 1),
                 alpha=0.3, color='green',
                 label='Long gold / Short dollar')

# Red shading — short gold, long dollar (z-score was too high)
plt.fill_between(df.index, df['Spread'], df['Spread_mean'],
                 where=(df['Signal'] == -1),
                 alpha=0.3, color='red',
                 label='Short gold / Long dollar')

plt.title('Gold/Dollar Spread — Pairs Trade Entry & Exit Regions',
          fontsize=14, fontweight='bold')
plt.ylabel('Spread (normalised points)')
plt.xlabel('Date')
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig('plot4_spread_signals.png', dpi=150)
plt.show()
print("✓ Chart 4 saved: plot4_spread_signals.png")

print("\n✓ Project complete. All charts saved to your project folder.")
print("  Files: plot1_normalised_prices.png, plot2_zscore.png,")
print("         plot3_cumulative_returns.png, plot4_spread_signals.png")