#result: address, holdings, previousTradeTimestamp, boughtTotal, holdingCurrently

import pandas as pd

#GLOBAL VARIABLES
uniswapV2Router = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
uniswapV3Router = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
weiDivisible = 1000000000000000000

#getting count
with open("mainCOUNT.txt", "r") as f:
    rowNum = int(f.read())
count = rowNum + 1

walletsList = pd.read_csv("wallets.csv")
walletsList = walletsList.drop_duplicates()

for i, row in walletsList[rowNum:].iterrows():
    
