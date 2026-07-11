import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("Asset Allocation Guide")

if "target_required_return" not in st.session_state:
    st.warning("Please complete the Wealth Goals page first.")

    if st.button("Return to Wealth Goals"):
        st.switch_page("Wealth_Goals.py")

    st.stop()

target_required_return = st.session_state["target_required_return"]

st.metric(
    "Target Required Annual Return",
    f"{target_required_return:.2f}%"
)

st.markdown("""
            Now you know how much annual return you need, we now look at allocations to achieve such returns.
            """)
st.subheader("Guide to use this section")
st.markdown("""
            1. Check the assets / markets that you want to invest in
            2. Rule of Thumb #1: You do not need to invest in as many market as possible, but keeping it simple enough that you can keep track of
            3. Rule of Thumb $2: The options below are general markets that are accessible to majority of investors, for advanced markets, please send your feedback to creator MUAHAHHAA
            4. Rule of Thumb #3: The outputs are based on historical returns, historical returns are not indicative of future returns
            """)
market_ticker_map = {"US Equities": "^SP500TR" ,
                     "Europe Equities": "VEUD.L" ,
                     "Japan Equities" : "IJPA.L" , 
                     "Asia Ex Japan Equities": "LYAEJ.SW" ,
                     "Global Bonds": "AGGU.L" ,
                     "Gold" : "IAU"}
selected_markets = st.multiselect("Select the markets you want to invest in: " , list(market_ticker_map.keys()))

#functions for asset prices
def download_asset_prices(tickers):
    data = yf.download(tickers, 
                       period = "max",
                       interval = "1d",
                       auto_adjust = True,
                       progress = False)
    if data.empty:
        return pd.DataFrame()
    close = data["Close"].copy()
    close = close.resample("W-FRI").last()
    close = close.dropna()
    return close

def random_portfolio(close , target_return_pct , num_portfolios = 5000):
    weekly_returns = close.pct_change().dropna()
    avg_returns = weekly_returns.mean() * 52
    cov_matrix = weekly_returns.cov() * 52
    tickers = avg_returns.index.tolist()
    portfolio_returns = []
    portfolio_risks = []
    portfolio_weights = []
    for i in range(num_portfolios):
        weights = np.random.random(len(selected_tickers))
        weights = weights / weights.sum()
        expected_return = np.dot(weights , avg_returns)
        expected_risk = np.sqrt(np.dot(weights.T , np.dot(cov_matrix , weights)))
        portfolio_returns.append(expected_return)
        portfolio_risks.append(expected_risk)
        portfolio_weights.append(weights)
    portfolio_df = pd.DataFrame({
        "Return":  portfolio_returns,
        "Risk": portfolio_risks
    })
    for i,ticker in enumerate(tickers):
        portfolio_df[f"{ticker} Weight"] = [w[i] for w in portfolio_weights]
    target_return = target_return_pct / 100
    feasible_portfolio = portfolio_df[portfolio_df["Return"] >= target_return]
    if feasible_portfolio.empty:
        return portfolio_df, None
    best_portfolio = feasible_portfolio.loc[feasible_portfolio["Risk"].idxmin()]
    return portfolio_df, best_portfolio

st.metric(
    "Target Required Annual Return",
    f"{target_required_return:.2f}%"
)

if len(selected_markets) < 2:
    st.warning("Please select at least 2 markets/assets to simulate a portfolio.")
else:
    selected_tickers = [market_ticker_map[market] for market in selected_markets]
    if st.button("Run Random Portfolio Simulation"):
        close = download_asset_prices(selected_tickers)
        first_data_date = close.index.min().strftime("%d %B %Y")
        last_data_date = close.index.max().strftime("%d %B %Y")
        portfolio_df , best_portfolio = random_portfolio(close, target_required_return, num_portfolios=5000)
        st.scatter_chart(portfolio_df,
                         x = "Risk", 
                         y = "Return",
                         x_label = "Expected Annual Risk",
                         y_label = "Expected Annual Returns",
                         width = "stretch")
        if best_portfolio is None:
            st.error("Based on the selected assets and historical data, none of the simulated portfolios achieve minimum returns")
        else:
            st.subheader("Lowest Risk Allocation That Meets Your Minimum Return")
            st.metric("Expected Annual Return: " , f"{best_portfolio["Return"]: .2%}")
            st.metric("Expected Annual Risk" , f"{best_portfolio["Risk"]: .2%}")
        allocation_data = []
        ticker_to_market_map = {ticker: market for market , ticker in market_ticker_map.items()}
        for ticker in selected_tickers:
            market_name = ticker_to_market_map[ticker]
            allocation_data.append({
                "Asset" : market_name,
                "Ticker" : ticker,
                "Allocation" : best_portfolio[f"{ticker} Weight"],
                "Allocation (%)" : best_portfolio[f"{ticker} Weight"] * 100
            })
        allocation_df = pd.DataFrame(allocation_data)
        st.dataframe(allocation_df [["Asset", "Ticker", "Allocation (%)"]], hide_index = True ,
                     column_config = {"Allocation (%)": st.column_config.NumberColumn("Allocation" , format = "%.1f%%")})
        allocation_chart =  allocation_df.set_index("Asset")[["Allocation (%)"]]
        st.bar_chart(allocation_chart,
                     y = "Allocation (%)",
                     y_label = "Allocation (%)",
                     width = "stretch")
        st.markdown(
            f"""
            Data: Historical Market Data retrieved from Yahoo Finance.
            
            Simulation uses weekly adjusted closing price data from {first_data_date} to {last_data_date}.
            
            The start date represents the earliest date with complete data available for all selected assets.
            
            Historical performance is not indicative of future performance.
            """
        )
