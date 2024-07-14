import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize
from fredapi import Fred
import matplotlib.pyplot as plt
import prettytable as pt

def get_user_input():
    print("Enter the stock tickers (comma-separated):")
    tickers = [ticker.strip() for ticker in input().split(',')]

    try:
        years = int(input("Enter the number of years for historical data: "))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return get_user_input()

    return tickers, years

def standard_deviation(weights, cov_matrix):
    variance = weights.T @ cov_matrix @ weights
    return np.sqrt(variance)

def expected_returns(weights, log_returns):
    return np.sum(log_returns.mean() * weights) * 252

def sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    return (expected_returns(weights, log_returns) - risk_free_rate) / standard_deviation(weights, cov_matrix)

def neg_sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    return -sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)

def calculate_metrics(weights, log_returns, cov_matrix, risk_free_rate):
    portfolio_return = expected_returns(weights, log_returns)
    portfolio_volatility = standard_deviation(weights, cov_matrix)
    portfolio_sharpe_ratio = sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)
    return portfolio_return, portfolio_volatility, portfolio_sharpe_ratio

def display_table(headers, data, title):
    table = pt.PrettyTable()
    table.field_names = headers
    for row in data:
        table.add_row(row)
    print(f'\n{title}:')
    print(table)

def main():
    # Get user input for tickers and number of years
    tickers, years = get_user_input()

    # Sort tickers alphabetically
    tickers.sort()

    # Set start and end dates for historical data
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)

    # Download historical data for selected tickers
    adj_close_df = pd.DataFrame({ticker: yf.download(ticker, start=start_date, end=end_date)['Adj Close'] for ticker in tickers})

    # Calculate log-returns
    log_returns = np.log(adj_close_df / adj_close_df.shift(1)).dropna()

    # Calculate covariance matrix
    cov_matrix = log_returns.cov() * 252

    # Get the risk-free rate from the U.S. Treasury yield
    fred = Fred(api_key='GET YOUR OWN')
    ten_year_treasury_rate = fred.get_series_latest_release('GS10') / 100
    risk_free_rate = ten_year_treasury_rate.iloc[-1]

    # Set constraints and bounds for portfolio optimization
    constraints = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    bounds = [(0, 0.5) for _ in range(len(tickers))]

    # Set initial weights for optimization
    initial_weights = np.array([1 / len(tickers)] * len(tickers))

    # Optimize portfolio weights to maximize Sharpe ratio
    optimized_results = minimize(neg_sharpe_ratio, initial_weights, args=(log_returns, cov_matrix, risk_free_rate),
                                 method='SLSQP', constraints=constraints, bounds=bounds)
    threshold = 1e-2
    optimal_weights = np.where(optimized_results.x < threshold,0,optimized_results.x)
    
    # Display optimal portfolio weights
    headers_weights = ['Ticker', 'Optimal Weight (%)']
    data_weights = list(zip(tickers, optimal_weights*100))
    display_table(headers_weights, data_weights, 'Optimal Weights')

    # Calculate and display portfolio performance metrics
    optimal_portfolio_return, optimal_portfolio_volatility, optimal_sharpe_ratio = calculate_metrics(
        optimal_weights, log_returns, cov_matrix, risk_free_rate
    )

    headers_metrics = ['Metric', 'Value']
    data_metrics = [
        ('Expected Annual Return', f'{optimal_portfolio_return:.4f}'),
        ('Expected Volatility', f'{optimal_portfolio_volatility:.4f}'),
        ('Sharpe Ratio', f'{optimal_sharpe_ratio:.4f}')
    ]
    display_table(headers_metrics, data_metrics, 'Portfolio Performance Metrics')

    # Get user input for investment amount
    try:
        invest_amount = float(input('Enter the amount of money you want to invest: '))
    except ValueError:
        print('Invalid input, please try again.')
        return
    
    # Calculate the amount to invest in each stock based on optimal weights
    threshold = 1e-2

    # Calculate the amount to invest in each stock based on optimal weights
    investment_allocation = np.where(optimal_weights * invest_amount < threshold, 0, optimal_weights * invest_amount)

    # Display the amount to invest in each stock
    headers_allocation = ['Ticker', 'Investment Allocation($)']
    data_allocation = list(zip(tickers, investment_allocation))
    display_table(headers_allocation, data_allocation, 'Investment Allocation')

    # Calculate the number of shares to buy for each stock based on the last available non-NaN closing price
    shares_to_buy = np.where(investment_allocation / adj_close_df.ffill().iloc[-1].values < threshold, 0, investment_allocation / adj_close_df.ffill().iloc[-1].values)

    # Display the number of shares to buy for each stock
    headers_shares = ['Ticker', 'Shares to Buy']
    data_shares = list(zip(tickers, shares_to_buy))
    display_table(headers_shares, data_shares, 'Number of Shares to Buy')

    # Calculate and display the remaining cash after the investment
    remaining_cash = invest_amount - np.sum(investment_allocation)
    print(f'Remaining Cash: {remaining_cash:.2f}')

    # Plot optimal portfolio allocations as a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(tickers, optimal_weights*100)
    plt.xlabel('Assets')
    plt.ylabel('Optimal Weights (%)')
    plt.title('Optimal Portfolio Allocations')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
