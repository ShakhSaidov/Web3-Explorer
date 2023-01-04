import requests
import json
import time
graphqlLink = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
usdc = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
usdt = "0xdac17f958d2ee523a2206206994597c13d831ec7"

def getEthPrice():
    query = """
            query{
                pair(id: "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc") {
                    token0Price
                }
            }
        """
    json_data = sendRequest(query, None)
    return float(json_data["data"]["pair"]["token0Price"])

def checkIfProblemToken(pair):
    query = """
            query($input: String!){
                pairs(where: {id: $input}) {
                    token0 {
                        id
                    }
                    token1 {
                        id
                    }
                }
            }
        """
    variables = {"input": pair}

    json_data = sendRequest(query, variables)
    json_data = json_data["data"]["pairs"]
    
    #something wrong, like router contract, null address, or smth
    if(len(json_data) == 0):
        return True

    json_data = json_data[0]
    if(json_data["token0"]["id"] == usdc or json_data["token1"]["id"] == usdc
    or json_data["token0"]["id"] == usdt or json_data["token1"]["id"] == usdt):
        return True
    
    return False

# sending graphql request
def sendRequest(query, variables):
    resp = requests.post(graphqlLink, json={
                         'query': query, 'variables': variables})
    json_data = json.loads(resp.text)

    # retry one more time
    if (json_data.__contains__("errors")):
        time.sleep(1)
        resp = requests.post(graphqlLink, json={
                             'query': query, 'variables': variables})
        json_data = json.loads(resp.text)

    return json_data

# calculate ath of token within hour (if token is token0)
def calculateMaxInHour0(pair, timestamp, initial):
    variables = {"input": pair, "time1": str(timestamp), "time2": str(timestamp + 3600)}
    query = """
            query($input: String!, $time1: String!, $time2: String!){
                swaps(
                    where: {
                        pair_: {id: $input}, 
                        timestamp_lte: $time2, 
                        timestamp_gt: $time1
                    }
                    orderBy: timestamp
                    first: 1000
                ) {
                    amount1In
                    amount0Out
                    amount1Out
                    amount0In
                    timestamp
                }
            }
        """
    json_data = sendRequest(query, variables)
    json_data = json_data["data"]["swaps"]
    
    prices = []
    mevTimestamps = []
    #mevbot check
    for i in json_data:
        if(float(i["amount1In"]) >= 2 or float(i["amount1Out"]) >= 2):
            mevTimestamps.append(i["timestamp"])
    json_data = [i for i in json_data if not (i["timestamp"] in mevTimestamps)]

    #no profit
    if(len(json_data) == 0):
        return initial
    
    #print(f"{pair} ||| {timestamp}\n")
    #print(json_data)

    #getting all prices within hour
    for eachData in json_data:
        #if buy
        ethSpent = float(eachData["amount1In"])
        tokensGot = float(eachData["amount0Out"])
        #if sell
        tokensSold = float(eachData["amount0In"])
        ethReceived = float(eachData["amount1Out"])
        
        #mevbot maybe
        if(ethSpent < 0.00006 and tokensGot < 1 and ethReceived == 0 and tokensSold == 0):
            continue
        if(ethReceived < 0.00006 and tokensSold < 1 and ethSpent == 0 and tokensGot == 0):
            continue
        
        #weird case
        if((ethSpent == tokensGot and tokensSold == ethReceived)):
            continue

        price = (ethSpent / tokensGot) if ethReceived == 0.0 else (ethReceived / tokensSold)

        #print(f"EthSpent: {ethSpent} ||| TokensGot: {tokensGot:.10f} ||| EthReceived: {ethReceived} ||| TokensSold: {tokensSold:.10f} ||| Price: {price:.10f}\n")
        prices.append(price)

    #subgraph is acting weird
    if(len(prices) == 0):
        return 1000000
        
    return max(prices)

# calculate ath of token within hour (if token is token1)
def calculateMaxInHour1(pair, timestamp, initial):
    variables = {"input": pair, "time1": str(timestamp), "time2": str(timestamp + 3600)}
    query = """
            query($input: String!, $time1: String!, $time2: String!){
                swaps(
                    where: {
                        pair_: {id: $input}, 
                        timestamp_lte: $time2, 
                        timestamp_gt: $time1
                    }
                    orderBy: timestamp
                    first: 1000
                ) {
                    amount0In
                    amount1Out
                    amount1In
                    amount0Out
                    timestamp
                }
            }
        """

    json_data = sendRequest(query, variables)
    json_data = json_data["data"]["swaps"]
    prices = []

    mevTimestamps = []
    #mevbot check
    for i in json_data:
        if(float(i["amount0In"]) >= 2 or float(i["amount0Out"]) >= 2):
            mevTimestamps.append(i["timestamp"])
    json_data = [i for i in json_data if not (i["timestamp"] in mevTimestamps)]

    #no profit
    if(len(json_data) == 0):
        return initial

    #getting all prices within hour
    for eachData in json_data:
        #if buy
        ethSpent = float(eachData["amount0In"])
        tokensGot = float(eachData["amount1Out"])
        #if sell
        tokensSold = float(eachData["amount1In"])
        ethReceived = float(eachData["amount0Out"])

        #mevbot maybe
        if(ethSpent < 0.00006 and tokensGot < 1 and ethReceived == 0 and tokensSold == 0):
            continue
        if(ethReceived < 0.00006 and tokensSold < 1 and ethSpent == 0 and tokensGot == 0):
            continue

        #weird case
        if(ethSpent == tokensGot and tokensSold == ethReceived):
            continue

        price = (ethSpent / tokensGot) if ethReceived == 0.0 else (ethReceived / tokensSold)

        #print(f"EthSpent: {ethSpent} ||| TokensGot: {tokensGot} ||| Price: {price}\n")
        prices.append(price)

    #subgraph acting weird
    if(len(prices) == 0):
        return 1000000

    return max(prices)