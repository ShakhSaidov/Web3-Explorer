import requests
import json
from csv import writer
import pandas as pd
import time
import graphql

with open("rowNum.txt", "r") as f:
    rowNum = int(f.read())

count = rowNum + 1

#change file here
addressLists = pd.read_csv("wallets_PREPARED.csv")

for i, row in addressLists[rowNum:].iterrows():
    address = row["Address"]
    # making request
    # First blocknumber after 09.01.2022 00:00:00 - 15450668

    startblock = 16075660
    endblock = 99999999
    #tobepasted
    # https://api.etherscan.io/api?module=account&action=tokentx&address={address}&startblock=15649626&sort=asc&apikey=7YRRHUFSDSM5BXCIM8FY3NPJ192WYKRC1G

    #url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={address}&startblock={startblock}&endblock={endblock}&sort=asc&apikey=7YRRHUFSDSM5BXCIM8FY3NPJ192WYKRC1G"
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={address}&startblock={startblock}&sort=asc&apikey=7YRRHUFSDSM5BXCIM8FY3NPJ192WYKRC1G"

    resp0 = requests.get(url)
    jsonData = json.loads(resp0.text)
    data = jsonData["result"]

    # removing duplicates
    uniqueData = []
    for txn in data:
        if all(unique_txn["hash"] != txn["hash"] for unique_txn in uniqueData):
            uniqueData.append(txn)

    totalBought = 0
    totalSold = 0

    #if(len(uniqueData) > 500):
    #    continue

    totalTokens = {}
    # looping through wallet's transactions
    for txn in uniqueData:
        bought = False
        sold = False

        if (txn['to'] == address):
            bought = True
        elif (txn['from'] == address):
            sold = True

        contract = txn['contractAddress']
        txnID = txn['hash']

        #usdc or usdt coin itself
        if(contract == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48" or contract == "0xdac17f958d2ee523a2206206994597c13d831ec7"):
            continue

        variables = {"input": txnID}
        query = """
            query($input: String!){
                transaction(
                    id: $input
                    ) {
                        swaps(orderBy: amountUSD, orderDirection: desc) {
                            amount0In
                            amount1In
      						amount1Out
      						amount0Out
                        }
                    }
            }
        """

        json_data = graphql.sendRequest(query, variables)
        if ((json_data.__contains__("errors")) or (json_data["data"]["transaction"] is None) or (len(json_data["data"]["transaction"]["swaps"])) == 0):
            continue

        #if usdc pair, just skip (for now at least)
        #if(bought and graphql.checkIfProblemToken(txn['from'])):
        #    continue

        #if usdc pair, just skip (for now at least)
        #if(sold and graphql.checkIfProblemToken(txn['to'])):
        #    continue

        json_data = json_data["data"]["transaction"]["swaps"][0]

        generalAmount = 0
        amount1In = float(json_data["amount1In"])
        amount0In = float(json_data["amount0In"])
        amount1Out = float(json_data["amount1Out"])
        amount0Out = float(json_data["amount0Out"])

        #BUY
        if (bought):
            if (amount1Out == 0.0):
                if contract in totalTokens:
                    totalTokens[contract] -= float(amount1In)
                else:
                    totalTokens[contract] = 0 - float(amount1In)
                generalAmount = float(amount1In)

                if(generalAmount > 100): generalAmount /= graphql.getEthPrice()
                totalBought += generalAmount

            else:
                if contract in totalTokens:
                    totalTokens[contract] -= float(amount0In)
                else:
                    totalTokens[contract] = 0 - float(amount0In)
                generalAmount = float(amount0In)

                if(generalAmount > 100): generalAmount /= graphql.getEthPrice()
                totalBought += generalAmount

        #SELL
        elif (sold):
            if (amount1In == 0.0):
                if contract in totalTokens:
                    totalTokens[contract] += float(amount1Out)
                else:
                    totalTokens[contract] = 0 + float(amount1Out)
                generalAmount = float(amount1Out)

                if(generalAmount > 100): generalAmount /= graphql.getEthPrice()
                totalSold += generalAmount
                
            else:
                if contract in totalTokens:
                    totalTokens[contract] -= float(amount0Out)
                else:
                    totalTokens[contract] = 0 - float(amount0Out)
                generalAmount = float(amount0Out)
                
                if(generalAmount > 100): generalAmount /= graphql.getEthPrice()
                totalSold += generalAmount

        #print(f"""
        #    ADDRESS --- {address}
        #    TO --- {txn['to']} ||| FROM --- {txn['from']}
        #    BUY --- {bought} ||| SELL --- {sold}
        #    TXNHASH --- {txnID}
        #    AMOUNT --- {generalAmount}
        #    \n
        #""")

    if totalBought == 0:
        continue

    avgGain = totalSold * 100 / totalBought - 100

    totalProfits = 0
    totalLosses = 0
    for key in totalTokens:
        if (totalTokens[key] <= 0):
            totalLosses += 1
        else:
            totalProfits += 1

    netProfits = totalProfits * 100 / len(totalTokens)

    textLine = f"{address}, {totalBought}, {totalSold}, {len(totalTokens)}, {totalProfits}, {totalLosses}, {avgGain}, {netProfits}\n"
    with open('wallets_selected_RESULTS_WITH_SELLS.csv', 'a') as fd:
        fd.write(textLine)

    count += 1

    with open("rowNum.txt", "w") as f:
        f.write(str(count-1))
