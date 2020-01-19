from pandas_datareader import data  # You will need to run "pip install pandas_datareader"
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import holidays   # You will need to run "pip install holidays"
import datetime 
import numpy as np
from dateutil.relativedelta import relativedelta

ONE_DAY = datetime.timedelta(days=1)
HOLIDAYS_US = holidays.US()

def previous_business_day(specific_date):
    previous_day = specific_date
    while previous_day.weekday() in holidays.WEEKEND or previous_day in HOLIDAYS_US:
        previous_day -= ONE_DAY
    return previous_day

def next_business_day(specific_date):
    next_day = specific_date
    while next_day.weekday() in holidays.WEEKEND or next_day in HOLIDAYS_US:
        next_day += ONE_DAY
    return next_day

def get_historical_data(share, start_date='2019-01-02', end_date='2019-12-31', source='yahoo'):
    try:
        panel_data = data.DataReader(share, source, start_date, end_date)
    except:
        panel_data = pd.DataFrame()
    return panel_data

def compute_average_annual_return(share, start_date='2019-01-02', end_date='2019-12-31', source='yahoo'):
    panel_data = get_historical_data(share, start_date, end_date, source)
    if panel_data.empty:
        return None, None, None, None, None
    
    adj_close = panel_data['Adj Close']
    
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    while start_date.strftime('%Y-%m-%d') not in adj_close.index: 
        start_date = next_business_day(start_date)
    
    while end_date.strftime('%Y-%m-%d') not in adj_close.index: 
        end_date = previous_business_day(end_date)
    
    delta = end_date - start_date
    years = delta.days / 365
    
    start_price = adj_close.loc[start_date.strftime('%Y-%m-%d')]
    end_price = adj_close.loc[end_date.strftime('%Y-%m-%d')]
    
    return_value = (end_price/start_price)**(1/years) - 1
    return round(return_value, 4), start_date, end_date, delta, years

def compute_daily_return_std_per_year(share, start_date='2019-01-02', end_date='2019-12-31', source='yahoo'):
    panel_data = get_historical_data(share, start_date, end_date, source)
    if panel_data.empty:
        return None

    last_day_price = None
    daily_returns = []
    for index, row in panel_data.iterrows():
        if last_day_price:
            daily_returns.append(row['Adj Close']/last_day_price - 1)
        last_day_price = row['Adj Close']
    return round(np.std(daily_returns)*np.sqrt(252), 4)

def compute_sharpe(share, start_date='2019-01-02', end_date='2019-12-31', source='yahoo'):
    avg, _, _, _, _ = compute_average_annual_return(share, start_date, end_date, source)
    std = compute_daily_return_std_per_year(share, start_date, end_date, source)
    if not avg or not std:
        return
    return round(avg/std, 4)

def plot_stock_price(stock, start_date='2019-01-02', end_date='2019-12-31', source='yahoo'):
    plt.figure(figsize=(16,6))
    daa = get_historical_data(stock, start_date=start_date, end_date=end_date, source=source)
    #sharpe_ratio = compute_sharpe(stock)
    plt.plot(daa['Adj Close'])
    plt.grid(color='g', linestyle='-.', linewidth=0.5)
    plt.legend([stock])
    plt.savefig('../results/{}_{}_{}.png'.format(stock, start_date, end_date))
    adj_close = daa['Adj Close']

    start_date_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d')
 
    while start_date_datetime.strftime('%Y-%m-%d') not in adj_close.index:
        start_date_datetime = next_business_day(start_date_datetime)
   
    while end_date_datetime.strftime('%Y-%m-%d') not in adj_close.index:
        end_date_datetime = previous_business_day(end_date_datetime)

    delta = end_date_datetime - start_date_datetime 
    duration = delta.days/365
    end_price = daa.loc[end_date_datetime.strftime('%Y-%m-%d')]['Adj Close']
    start_price = daa.loc[start_date_datetime.strftime('%Y-%m-%d')]['Adj Close']
    annual_ret = (end_price/start_price)**(1/duration)-1
    return round(annual_ret, 4)

def compute_avg_annual_return_between_2_periods(shares, start_date='2000-01-02', end_date='2019-12-31', source='yahoo'):
    shares_data = get_historical_data(shares, start_date=start_date, end_date=end_date, source=source)
    adj_close = shares_data['Adj Close']
    
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    while start_date.strftime('%Y-%m-%d') not in adj_close.index: 
        start_date = next_business_day(start_date)
    
    while end_date.strftime('%Y-%m-%d') not in adj_close.index: 
        end_date = previous_business_day(end_date)
    
    start_prices = adj_close.loc[start_date.strftime('%Y-%m-%d')]
    end_prices = adj_close.loc[end_date.strftime('%Y-%m-%d')]
    #print(end_prices, start_prices)
    return (end_prices/start_prices)**(1/(end_date.year - start_date.year)) - 1

def plot_us_gdp(start_date = '1900-01-01', end_date = '2020-01-01'):
    plt.figure(figsize=(16,6))
    gdp_data = get_historical_data('GDP', start_date = start_date, end_date = end_date, source = 'fred')
    plt.plot(gdp_data)
    plt.grid(color='g', linestyle='-.', linewidth=0.5)
    plt.legend(['US GDP'])
    plt.savefig('../results/us_gdp.png')

def plot_us_inflation(start_date='1940-01-01', end_date='2020-01-01', index ='CPILFESL'):
    CPI  = get_historical_data(index, start_date = start_date, end_date = end_date, source = 'fred')
    CPI['CPI_Diff_monthly'] = CPI[index].diff()
    CPI['CPI_Diff_yearly'] = CPI[index].diff(12)
    CPI['CPI_monthly_inflation_rate'] = (CPI['CPI_Diff_monthly']/CPI[index])*100
    CPI['CPI_yearly_inflation_rate_pp'] = (CPI['CPI_Diff_yearly']/CPI[index])*100
    plt.figure(figsize=(16,6))
    plt.plot(CPI['CPI_monthly_inflation_rate'])
    plt.plot(CPI['CPI_yearly_inflation_rate_pp'])
    plt.grid(color='g', linestyle='-.', linewidth=0.5)
    plt.legend(['US monthly inflation rate', 'US yearly point to point inflation rate'])
    plt.savefig('../results/us_inflation_data_{}.png'.format(index))
    return CPI

def plot_index(index, start_date = '2010-01-02', end_date = '2020-01-02', source = 'fred'):
    indx  = get_historical_data(index, start_date, end_date, source)
    plt.figure(figsize=(16,6))
    plt.plot(indx)
    plt.grid(color='g', linestyle='-.', linewidth=0.5)
    index_meaning = {'DGS30': '30-Year Treasury Constant Maturity Rate',
                     'DGS20': '20-Year Treasury Constant Maturity Rate',
                     'DGS10': '10-Year Treasury Constant Maturity Rate',
                     'DGS7': '7-Year Treasury Constant Maturity Rate',
                     'DGS5': '5-Year Treasury Constant Maturity Rate',
                     'DGS3': '3-Year Treasury Constant Maturity Rate',
                     'DGS2': '2-Year Treasury Constant Maturity Rate',
                     'DGS1': '1-Year Treasury Constant Maturity Rate',
                     'DGS6MO': '6-Month Treasury Constant Maturity Rate',
                     'DGS3MO': '3-Month Treasury Constant Maturity Rate',
                     'DGS1MO': '1-Month Treasury Constant Maturity Rate',
                     'FEDFUNDS': 'US Effective Federal Funds Rate',
                     'LIBOR': '3-Month London Interbank Offered Rate',
                     'NIKKEI225': 'Nikkei Stock Average, Nikkei 225',
                     'UNRATE': 'US Civilian Unemployment Rate',
                     'GFDEGDQ188S': 'Federal Debt: Total Public Debt as Percent of Gross Domestic Product',
                     'GDPC1': 'Real Gross Domestic Product percent change',
                     'A191RL1Q225SBEA': 'Real Gross Domestic Product dollars',
                     'CPIAUCSL': 'Consumer Price Index for All Urban Consumers: All Items',
                     'IRLTLT01JPM156N': 'Long-Term Government Bond Yields: 10-year: Japan'
                    }
    plt.legend([index_meaning[index]])
    plt.savefig('../results/index_{}_{}_{}.png'.format(index, start_date, end_date))

def plot_yield_curve(specific_date):
    next_date = next_business_day(datetime.datetime.strptime(specific_date, '%Y-%m-%d'))
    specific_date = next_date.strftime('%Y-%m-%d')
    syms = ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30']
    yc = data.DataReader(syms, 'fred', specific_date, specific_date)
    names = dict(zip(syms, ['1m', '3m', '6m', '1yr', '2yr', '3yr', '5yr', '7yr', '10yr', '20yr', '30yr']))
    yc = yc.rename(columns=names)
    plt.figure(figsize=(16,6))
    #plt.plot([1, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360], yc.loc[specific_date])
    plt.plot(yc.loc[specific_date])
    plt.grid(color='g', linestyle='-.', linewidth=0.5)
    plt.legend(['US Yield Curve on {}'.format(specific_date)])
    plt.savefig('../results/yield_curve_{}.png'.format(specific_date))
    return yc.loc[specific_date]

def compute_stats(symb):
    ticker = data.get_quote_yahoo(symb)
    ticker['c1_marketCap_bn_calc'] = ticker['price'] * ticker['sharesOutstanding'] / 1e9
    ticker['c2_marketCap_bn_orig'] = ticker['marketCap'] / 1e9
    ticker['c3_price_calc'] = ticker['epsForward'] * ticker['trailingPE']
    ticker['c4_earnings_bn_calc'] = ticker['epsForward'] * ticker['sharesOutstanding'] / 1e9
    ticker['c5_25_times_PE_limit'] = 25 * ticker['trailingPE'] # A higher price than this value is risky
    return ticker

def compare_dollar_cost_averaging_return(symb, window_length=30, start_date='2000-01-02', end_date='2019-12-31'):
    #window_length is in days
    #Option 1 --> Dollar cost averaging --> buy shares number of shares
    #Option 2 --> Save up all monthly contributions --> buy end_shares at the end

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    curr_date = next_business_day(start_date)
    shares, counts = 0, 0

    while curr_date < datetime.datetime.strptime(end_date, '%Y-%m-%d'):
        counts += 1
        curr_date += datetime.timedelta(days=window_length)
        curr_date = next_business_day(curr_date)
        try:
            date_df = data.DataReader(symb, 'yahoo', curr_date, curr_date)
        except:
            date_df = pd.DataFrame()
            break

        adj_close = date_df['Adj Close']

        date_price = adj_close.loc[curr_date.strftime('%Y-%m-%d')]

        shares += 1/date_price

    end_biz = previous_business_day(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
    end_df = data.DataReader(symb, 'yahoo', end_biz, end_biz)
    print(end_df)
    if end_df.empty:
            return None

    end_adj_close = end_df['Adj Close']
    end_price = end_adj_close.loc[end_biz.strftime('%Y-%m-%d')]

    end_shares = counts/end_price

    return shares/end_shares - 1

def plot_housing_index(city, state):
    housing_data = pd.read_csv("../resources/City_Zhvi_SingleFamilyResidence.csv", encoding = "ISO-8859-1")
    housing_data = housing_data.loc[housing_data['State'] == state]
    housing_data = housing_data.loc[housing_data['RegionName'] == city]

    ONE_MONTH = relativedelta(months=+1)
    start_date = datetime.datetime.strptime('1996-04', '%Y-%m')
    available_data_date = []
    available_data_price = []
    curr_date = start_date

    while curr_date.year < 2020:
        available_data_date.append(curr_date)
        available_data_price.extend(housing_data[curr_date.strftime('%Y-%m')].tolist())
        curr_date += ONE_MONTH

    plt.figure(figsize=(16,6))
    plt.plot(available_data_date, available_data_price)
    plt.grid(color='g', linestyle='-.', linewidth=0.5)
    plt.legend(['{},{} Single Family Housing Price'.format(city, state)])
    plt.savefig('../results/housing_prices_{}_{}.png'.format(city, state))

    delta = available_data_date[-1] - available_data_date[0]
    duration = delta.days/365

    avg_annual_return_on_property = (available_data_price[-1]/available_data_price[0])**(1/duration)-1
    return available_data_price, available_data_date, round(avg_annual_return_on_property, 4)
