from StocksAssistant.share import Share, ShareUS, ShareTW
from StocksAssistant.strategy import StrategyTester

class Market(object):
    # share
    share = Share()
    share_us = ShareUS(cash=1000.0)
    share_tw = ShareTW(cash=30000.0)
    # strategy
    duration = 60
    strategyTester = StrategyTester()

    def setParams(duration: int, cash_us, float, cash_tw: float):
        Market.duration = duration
        Market.ShareUS.cash = cash_us
        Market.ShareTW.cash = cash_tw
    
    def updateCodes():
        Market.share_us.updateCodes()
        Market.share_tw.updateCodes()
    
    def updatePrice():
        Market.share_us.updatePrice()
        Market.share_tw.updatePrice()
    
    def updateStrategy():
        Market.strategyTester(Market.share_us, Market.duration)
        Market.strategyTester(Market.share_tw, Market.duration)
    
    def plotChart():
        Market.share.plotChart("tw", "0050")