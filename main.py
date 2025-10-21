"""Debug parser to identify missing fields"""

from bdfinance import BDStockClient


async def main() -> None:
    async with BDStockClient() as client:
        tk = client.ticker("ACIFORMULA")
        info = await tk.info()

        df = await tk.history(period="7d")
        print(info)
        print(df)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
