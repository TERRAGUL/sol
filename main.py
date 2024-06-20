from web3 import Web3
from web3.middleware import geth_poa_middleware 
from contract_info import abi, contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def main():
    if w3.is_connected():
        print("Соединение с узлом Ethereum установлено.")
        
        # Проверка баланса для каждого аккаунта
        accounts = [
            '0xCf6DB0F2f5AD330b726864C79ccE46c355B92f75',
            '0xDC1b8d76f463085D79E0969bC1AB11333004D723',
            '0x0eE6bD2e28a2970FBA7e934921B8270f73b6b43e',
            '0x1B607672E4B8b7A64103766662618F1EcA611e60',
            '0x41cB26a20D9c9828fa11962c7e41f2Ccc641bC48'
        ]

        for account in accounts:
            balance = w3.eth.get_balance(account)
            print(f"Баланс аккаунта {account}: {w3.from_wei(balance, 'ether')} ETH")
    else:
        print("Не удалось установить соединение с узлом Ethereum.")

if __name__ == '__main__':
    main()