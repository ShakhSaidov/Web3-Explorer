import requests
import json

url = "https://eth-mainnet.g.alchemy.com/v2/RFZwgvbVeEzxo2bZwX4sR6AG1p0TTaso"

#block on Dec 31 23:55:50 UTC
count = "0x64"

#BUY TXN LIST
def getBuys(address):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "category": ["erc20"],
                "withMetadata": True,
                "excludeZeroValue": True,
                "maxCount": count,
                "toAddress": address,
                "order": "desc"
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response = response.text
    responseJSON = json.loads(response)
    return responseJSON["result"]["transfers"]


#SELL TXN LIST
def getSells(address):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "category": ["erc20"],
                "withMetadata": True,
                "excludeZeroValue": True,
                "maxCount": count,
                "fromAddress": address,
                "order": "desc"
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response = response.text
    responseJSON = json.loads(response)
    return responseJSON["result"]["transfers"]