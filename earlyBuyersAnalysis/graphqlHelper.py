import requests
import json
import time
graphqlLink = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

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


def getData(txn):
    #print(txn)

    query = """
            query($input: String!){
                transaction(
                    id: $input
                ) {
                    swaps(orderBy: amountUSD, orderDirection: desc) {
                        amountUSD
                        pair {
                            token0 {
                                symbol
                            }
                            token1 {
                                symbol
                            }
                        }
                    }
                }
            }
        """
    variables = {"input": txn}

    json_data = sendRequest(query, variables)

    #print("FIRST: ", json_data)

    json_data = json_data["data"]["transaction"]
    # null response, probably a transfer between accounts
    if (json_data is None):
        return -1
    
    #print("SECOND: ", json_data)

    json_data = json_data["swaps"]
    if (json_data is None or json_data == []):
        return -1

    #print("THIRD: ", json_data)


    #print("THIS IS JSON_DATA CURRENTLY", json_data)

    #IF IT IS A STABLECOIN TRANSFER
    if (
            len(json_data) == 1 and 
            (   json_data[0]["pair"]["token0"]["symbol"] == "USDT" or
                json_data[0]["pair"]["token1"]["symbol"] == "USDT" or
                json_data[0]["pair"]["token0"]["symbol"] == "USDC" or
                json_data[0]["pair"]["token1"]["symbol"] == "USDC" or
                json_data[0]["pair"]["token0"]["symbol"] == "BUSD" or
                json_data[0]["pair"]["token1"]["symbol"] == "BUSD" or
                json_data[0]["pair"]["token0"]["symbol"] == "DAI" or
                json_data[0]["pair"]["token1"]["symbol"] == "DAI"
            )
        ):
        return -2

    else:
        #print("RETURNING ", float(json_data[0]["amountUSD"]))
        return float(json_data[0]["amountUSD"])
