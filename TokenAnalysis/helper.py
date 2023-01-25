from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import json


def isContract(address):
    alchemyURL = "https://eth-mainnet.g.alchemy.com/v2/RFZwgvbVeEzxo2bZwX4sR6AG1p0TTaso"

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

    if response == "0x":
        return False
    else:
        return True


def getBalance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey=7YRRHUFSDSM5BXCIM8FY3NPJ192WYKRC1G"

    response = requests.get(url)
    jsonData = json.loads(response.text)
    return jsonData["result"]


def getTokenBalance(address):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    chrome_options.add_argument('headless')
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(f"https://etherscan.io/address/{address}")
    element = driver.find_element(By.ID, "availableBalanceDropdown")
    text = element.text
    driver.close()

    tokenBalance = text[2:].split()
    tokenBalance = tokenBalance[0]
    return tokenBalance
