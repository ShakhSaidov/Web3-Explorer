import requests

alchemyURL = "https://eth-mainnet.g.alchemy.com/v2/RFZwgvbVeEzxo2bZwX4sR6AG1p0TTaso"

def isContract(address):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "params": [address, "latest"],
        "method": "eth_getCode"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(alchemyURL, json=payload, headers=headers)
    response = response.json()
    response = response['result']

    if response == "0x": return False
    else: return True