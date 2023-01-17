def run():
    from StocksAssistant.utils import installPkgs
    # install package
    installPkgs(["yfinance", "yahoo-fin", "mplfinance", "backtesting", "TA-Lib"])
    # import package
    from StocksAssistant.utils import parseArgs, setDataPath
    from StocksAssistant.market import Market
    # args
    args = parseArgs()
    # set path
    setDataPath(args.data_path)
    # run
    if args.codes:
        Market.updateCodes()
    if args.price:
        Market.updatePrice()
    if args.alert:
        Market.updateAlert()
    if args.strategy:
        Market.updateStrategy()
    if args.chart:
        Market.plotChart()


if __name__ == "__main__":
    run()
