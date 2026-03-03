"""Debug parser to identify missing fields"""

from bdfinance import BDStockClient
import pandas as pd


def draw_candlestick_chart(df: pd.DataFrame) -> None:
    """Draw candlestick chart using matplotlib"""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc

    # Convert date to matplotlib format
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date"] = df["Date"].map(mdates.date2num)

    # Prepare data for candlestick chart
    ohlc_data = df[["Date", "Open", "High", "Low", "Close"]].values

    # Create figure and axis
    fig, ax = plt.subplots()

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data, width=0.6, colorup="green", colordown="red")

    # Format x-axis with dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    plt.title("Candlestick Chart")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid()
    plt.tight_layout()
    plt.show()

async def main() -> None:
    async with BDStockClient() as client:
        tk = client.ticker("GP")
        await tk.validate_symbol()
        df = await tk.history(period="5y")
    
        
        


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
