import numpy as np
import pandas as pd
from datetime import datetime
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from StocksAssistant.share import Share


class SmaCross(Strategy):
    n1 = None
    n2 = None

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


class SmaCross_05_10(SmaCross):
    n1 = 5
    n2 = 10


class SmaCross_05_20(SmaCross):
    n1 = 5
    n2 = 20


class SmaCross_10_20(SmaCross):
    n1 = 10
    n2 = 20


class Indicator(Strategy):
    def init(self):
        self.close = self.data.Close

    def next(self):
        if self.close < 100:
            self.buy()
        elif self.close > 100:
            self.sell()


class StrategyTester(object):
    strategy_pool = [
        SmaCross_05_10,
        SmaCross_05_20,
        SmaCross_10_20,
    ]

    def __call__(self, share: Share, duration: int):
        # get last trade date
        lastTradeDate = share.lastTradeDate
        # get all results
        df = StrategyTester.runAll(share, duration)
        # # get best strategy
        # df_best = StrategyTester.getBest(df)
        # print(df_best[["Code", "Strategy", "Return [%]"]])
        # get action
        df_action = StrategyTester.getAction(df, lastTradeDate)
        print(df_action[["Code", "Action"]])

    @staticmethod
    def run(code: str, data: pd.DataFrame, strategy: Strategy, cash: float = 10000.0, commission: float = 0.000):
        test = Backtest(
            data=data,
            strategy=strategy,
            cash=cash,
            commission=commission,
            exclusive_orders=True,
            trade_on_close=True,
        )
        result = test.run()
        result = pd.DataFrame(result).T
        result.insert(0, 'Code', code)
        result.insert(1, 'Strategy', strategy.__name__)
        return result

    @staticmethod
    def runAll(share: Share, duration: int):
        # initialize results
        df = pd.DataFrame([])
        # load data
        data_grp = share.loadPrice()
        # strategies
        for strategy in StrategyTester.strategy_pool:
            for code, data in data_grp:
                # set data
                data["Date"] = pd.to_datetime(data["Date"])
                data = data.set_index("Date")
                data = data.iloc[-duration:]
                # run strategy
                result = StrategyTester.run(
                    code=code,
                    data=data,
                    strategy=strategy,
                    cash=share.cash,
                    commission=share.commission,
                )
                df = pd.concat([df, result])
        # sort by return
        df["Return [%]"] = df["Return [%]"].astype(float)
        df = df.sort_values(by=["Return [%]"])
        # sort by code
        df = df.drop_duplicates(subset=["Code"])
        df = df.sort_values(by=["Code", "Strategy"])
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def getBest(df: pd.DataFrame):
        # best 3 strategy
        df_best = df.nlargest(3, ["Return [%]"])
        df_best = df_best.reset_index(drop=True)
        return df_best

    @staticmethod
    def getAction(df: pd.DataFrame, lastTradeDate: datetime.date):
        df["Action"] = "None"
        for index, row in df.iterrows():
            try:
                size, entry_time = row["_trades"].iloc[-1][["Size",
                                                            "EntryTime"]].values
                entry_time = datetime.date(entry_time)
                days = (lastTradeDate - entry_time).days
                if row["Return [%]"] > 5 and days < 2:
                    if size > 0:
                        df.loc[index, "Action"] = "buy"
                    else:
                        df.loc[index, "Action"] = "sale"
            except:
                pass
        df_action = df.loc[df["Action"] != "None"]
        return df_action
