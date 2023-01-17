import os
import time
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
from yahoo_fin import stock_info as si
import mplfinance as mpf
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor
from StocksAssistant.utils import parseArgs

args = parseArgs()


class Share(object):
    columns_share = ["Code", "Date", "GICS"]
    columns_price = ["Code", "Date", "Open", "High", "Low", "Close", "Volume"]

    def updateCodes():
        raise NotImplementedError

    def updatePrice(self):
        # initialize data
        df = self.loadPrice()
        # update price
        codes = self.codes
        for i, code in enumerate(codes):
            df_append = Share.getPrice(self.region, code, -1)
            df = pd.concat([df, df_append])
        # export
        self.savePrice(df)

    def loadPrice(self, enable_group: bool = False, timeperiod: int = -1):
        if os.path.exists(self.fname_price):
            df = pd.read_parquet(self.fname_price)
            if list(df.columns) != Share.columns_price:
                raise BaseException(
                    f"Please check current data: {self.fname_price}"
                )
            df.columns = Share.columns_price
        else:
            print(f"Data not exist: {self.fname_price}")
            df = pd.DataFrame(columns=Share.columns_price)
            df = df.replace(np.inf, np.nan)
            df = df.interpolate(
                method='linear', limit_direction='forward', axis=0)
            df = df.dropna()
        df = df.replace(np.inf, np.nan)
        df = df.interpolate(
            method='linear', limit_direction='forward', axis=0)
        df = df.dropna()
        # group
        grp = df.groupby("Code", group_keys=False)
        if timeperiod > 0:
            grp = grp.apply(lambda x: x.iloc[-timeperiod:])
            grp = grp.groupby("Code", group_keys=False)
        return grp
    
    @staticmethod
    def code_yf(region: str, code: str):
        if region.lower() == "us":
            return code
        if region.lower() == "tw":
            return code + ".TW"
        raise ValueError(
            f"No region: {region}"
        )

    @staticmethod
    def getPrice(region: str, code: str, days: int = -1) -> pd.DataFrame:
        df = pd.DataFrame(columns=Share.columns_price)
        # set period
        if days == 0:
            print("Skip price(%s): %-6s" % (region, code))
            return df
        if days < 0:
            period = "99y"
        else:
            period = f"{days}d"
        # get hist
        if not any([c in code for c in [".", "$"]]):
            hist = yf.Ticker(Share.code_yf(region, code))
            hist = pd.DataFrame(hist.history(period=period))
            hist = hist.reset_index()
            hist.insert(loc=0, column="Code", value=code)
            hist["Date"] = pd.to_datetime(
                hist["Date"]).apply(lambda x: x.date())
            hist = hist[["Code", "Date", "Open",
                         "High", "Low", "Close", "Volume"]]
            hist.columns = Share.columns_price
            df = pd.concat([df, hist])
            time.sleep(0.8)
            print("Get price(%s): %-6s,\t%s" % (region, code, period))
        return df

    @property
    def lastTradeDate(self):
        df_curr = Share.getPrice(self.region, self.main_stock, 1)
        return df_curr.iloc[-1]["Date"]
    
    @property
    def codes(self):
        raise NotImplementedError

    def saveCodes(self, df: pd.DataFrame):
        df = df.dropna(subset=["Code"])
        df = df.drop_duplicates(subset=["Code"])
        df = df.sort_values(by=["Code"])
        df = df.reset_index(drop=True)
        # export
        df.to_parquet(self.fname_codes, compression="gzip")
        print(f"Codes updated: {self.region}, {self.fname_codes}")

    def savePrice(self, df: pd.DataFrame):
        df = df.drop_duplicates(subset=["Code", "Date"])
        df = df.sort_values(by=["Code", "Date"])
        df = df.reset_index(drop=True)
        # export
        df.to_parquet(self.fname_price, compression="gzip")
        print(f"Price updated: {self.region}, {self.fname_price}")

    @staticmethod
    def plotChart(region: str, code: str, days: int = 180):
        # get data
        df = Share.getPrice(region, code, days)
        df = df.set_index("Date")
        df.index = pd.DatetimeIndex(df.index)
        # set kwargs
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        savefig = dict(fname="chart.jpg", dpi=300, pad_inches=0.25)
        kwargs = dict(
            data=df,
            type="candle",
            mav=(5, 20, 60),
            volume=True,
            figratio=(10, 8),
            figscale=0.75,
            title=code,
            style=style,
            returnfig=True,
            savefig=savefig,
        )
        # plot
        return mpf.plot(**kwargs)


class ShareUS(Share):
    region = "US"
    main_stock = "^IXIC"
    ext_code_list = ["SPOT"]
    fname_codes = os.path.join(args.data_path, "codes_us.parquet.gzip")
    fname_price = os.path.join(args.data_path, "price_us.parquet.gzip")
    commission = 0.000

    def __init__(self, cash: float) -> None:
        super().__init__()
        ShareUS.cash = cash

    def updateCodes(self):
        # get data
        sp500 = si.tickers_sp500(include_company_data=True)
        nasdaq = si.tickers_nasdaq(include_company_data=True)
        dow = si.tickers_dow(include_company_data=True)
        others = si.tickers_other(include_company_data=True)
        # set columns
        sp500 = sp500[["Symbol", "Security", "GICS Sector"]]
        dow = dow[["Symbol", "Company", "Industry"]]
        nasdaq = nasdaq[["Symbol", "Security Name", "Market Category"]]
        others = others[["NASDAQ Symbol", "Security Name"]]
        others["GICS"] = None
        sp500.columns = Share.columns_share
        nasdaq.columns = Share.columns_share
        dow.columns = Share.columns_share
        others.columns = Share.columns_share
        # concat data
        # df = pd.concat([sp500, dow, nasdaq, others])
        df = pd.concat([sp500, dow])
        # export
        self.saveCodes(df)

    @property
    def codes(self):
        df = pd.read_parquet(self.fname_codes)
        return sorted(list(df["Code"]))


class ShareTW(Share):
    region = "TW"
    main_stock = "0050"
    ext_code_list = ["00878"]
    fname_codes = os.path.join(args.data_path, "codes_tw.parquet.gzip")
    fname_price = os.path.join(args.data_path, "price_tw.parquet.gzip")
    commission = 0.003

    def __init__(self, cash: float) -> None:
        super().__init__()
        ShareTW.cash = cash

    def updateCodes(self):
        # get data
        url = "https://isin.twse.com.tw/isin/e_C_public.jsp?strMode=2"
        df = pd.read_html(url, encoding='big5')[0]
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        # add type
        df["Type"] = None
        stock_types = df[df["ISIN Code"] == df["Market"]]
        stock_types = stock_types.reset_index()
        stock_types = stock_types[["index", "Market"]]
        stock_types.columns = ["index", "Type"]
        stock_types["index_next"] = stock_types["index"].shift(
            periods=-1, fill_value=df.index[-1])
        for index, row in stock_types.iterrows():
            index = int(row["index"])
            index_next = int(row["index_next"])
            df["Type"][index:index_next] = row["Type"]
        for index in stock_types["index"]:
            df = df[df.index != index]
        df = df.reset_index(drop=True)
        # split code and name
        df_temp = pd.DataFrame([])
        df_temp[["Code", "Name"]] = df["Security Code & Security Name"].str.split(
            "　", 1, expand=True)
        df.insert(0, 'Code', df_temp["Code"])
        df.insert(1, 'Name', df_temp["Name"])
        df = df.drop(["Security Code & Security Name"], axis=1)
        del df_temp
        # set columns
        df = df[["Code", "Name", "Industrial Group"]]
        df.columns = Share.columns_share
        # export
        self.saveCodes(df)

    @property
    def codes(self):
        df = pd.read_parquet(self.fname_codes)
        codes = sorted([code for code in list(df["Code"]) if len(code) < 5])
        codes.extend(self.ext_code_list)
        return codes
