import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page title
st.set_page_config(page_title="Interactive Stock Analysis Report", layout="wide")

# Title
st.title("Interactive Stock Analysis Report")

# Sidebar for user input
st.sidebar.header("Customize Your Report")

# Stock selection
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")

# Date range selection
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)
date_range = st.sidebar.date_input("Select Date Range", value=[start_date, end_date])

# Moving average parameters
ma_short = st.sidebar.number_input("Short-term Moving Average", min_value=1, max_value=100, value=20)
ma_long = st.sidebar.number_input("Long-term Moving Average", min_value=1, max_value=200, value=50)

# Fetch data
@st.cache_data
def get_stock_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end)

data = get_stock_data(ticker, date_range[0], date_range[1])

# Display raw data
st.header("Raw Data")
st.dataframe(data)

# Calculate moving averages
data[f'MA{ma_short}'] = data['Close'].rolling(window=ma_short).mean()
data[f'MA{ma_long}'] = data['Close'].rolling(window=ma_long).mean()

# Visualizations
st.header("Stock Price Analysis")

# Candlestick chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlesticks")])

# Add moving averages to the chart
fig.add_trace(go.Scatter(x=data.index, y=data[f'MA{ma_short}'], name=f'{ma_short}-day MA', line=dict(color='orange', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data[f'MA{ma_long}'], name=f'{ma_long}-day MA', line=dict(color='green', width=1)))

fig.update_layout(title=f"{ticker} Stock Price", xaxis_title="Date", yaxis_title="Price", height=600)
st.plotly_chart(fig, use_container_width=True)

# Summary statistics
st.header("Summary Statistics")
summary = data['Close'].describe()
st.write(summary)

# Code display
st.header("Python Code for Analysis")
code = '''
import yfinance as yf
import pandas as pd

# Fetch data
data = yf.download("{}", start="{}", end="{}")

# Calculate moving averages
data['MA{}'] = data['Close'].rolling(window={}).mean()
data['MA{}'] = data['Close'].rolling(window={}).mean()

# Summary statistics
summary = data['Close'].describe()
print(summary)
'''.format(ticker, date_range[0], date_range[1], ma_short, ma_short, ma_long, ma_long)

st.code(code, language='python')

# Conditional insights
st.header("Insights")
last_close = data['Close'].iloc[-1]
last_ma_short = data[f'MA{ma_short}'].iloc[-1]
last_ma_long = data[f'MA{ma_long}'].iloc[-1]

if last_close > last_ma_short > last_ma_long:
    st.write(f"The current stock price (${last_close:.2f}) is above both the {ma_short}-day moving average (${last_ma_short:.2f}) and the {ma_long}-day moving average (${last_ma_long:.2f}), suggesting a potential bullish trend.")
elif last_ma_short > last_close > last_ma_long:
    st.write(f"The current stock price (${last_close:.2f}) is between the {ma_short}-day moving average (${last_ma_short:.2f}) and the {ma_long}-day moving average (${last_ma_long:.2f}), suggesting a potential market indecision.")
else:
    st.write(f"The current stock price (${last_close:.2f}) is below both the {ma_short}-day moving average (${last_ma_short:.2f}) and the {ma_long}-day moving average (${last_ma_long:.2f}), suggesting a potential bearish trend.")

# Disclaimer
st.sidebar.markdown("---")
st.sidebar.caption("This report is for educational purposes only and should not be considered as financial advice.")