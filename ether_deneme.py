import json

from web3 import Web3
from web3.middleware import geth_poa_middleware

# Alchemy ile bağlantı kur
w3 = Web3(Web3.WebsocketProvider('wss://polygon-mumbai.g.alchemy.com/v2/jB5HZcHV7k10Go5aPc-mr5rztjzdXITZ'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Kontratın ABI ve adresini tanımla
with open('./nftabi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract_address = '0x9D51bBaB56C01e90DbaCCBD99ca97B0CE2155CDf'

# Kontratı oluştur
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Event filtresi oluştur
event_filter = contract.events.charged.create_filter(fromBlock='latest')

# Eventleri dinle
while True:
    for event in event_filter.get_new_entries():
        user_address = event.args.userAddress
        token_id = event.args.tokenId
        charge = event.args.charge

        print(f'User Address: {user_address}')
        print(f'Token ID: {token_id}')
        print(f'Charge: {charge}')

        # Firebase function'ınızı burada tetikleyebilirsiniz
