import asyncio
import json

import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Firebase Function webhook
webhook_url = "https://updatenftvalues-gtgyvdwnta-uc.a.run.app"


# Alchemy ile bağlantı kur
w3 = Web3(Web3.WebsocketProvider(
    'wss://polygon-mumbai.g.alchemy.com/v2/jB5HZcHV7k10Go5aPc-mr5rztjzdXITZ'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Kontratın ABI ve adresini tanımla
with open('./nftabi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract_address = '0x9D51bBaB56C01e90DbaCCBD99ca97B0CE2155CDf'
# eski: 0xd96a66344e80aE58Cacb6485df277bE0E7d66374

# Kontratı oluştur
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Event filtrelerini oluştur
filter_charged = contract.events.charged.create_filter(fromBlock='latest')
filter_nftMinted = contract.events.nftMinted.create_filter(fromBlock='latest')
filter_factorXChanged = contract.events.factorXChanged.create_filter(
    fromBlock='latest')
filter_levelUp = contract.events.levelUpEvent.create_filter(fromBlock = 'latest')
filter_decreaseCharge = contract.events.decreaseChargeEvent.create_filter(fromBlock='latest')
filter_nftTransfer = contract.events.Transfer.create_filter(fromBlock='latest')

# Eventleri dinle


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            # print(event)
            if 'charged' in event.event:
                # charged event'i için bir işlem gerçekleştir
                user_address = event.args.userAddress
                token_id = event.args.tokenId
                charge = event.args.charge
                print(
                    f'Charged Event - User Address: {user_address}, Token ID: {token_id}, Charge: {charge}')
                # Veritabanı güncellemesi yapabilirsiniz
                charged_data = {
                    "root": [
                        {
                            "event_name": "charged",
                            "charged_address": user_address,
                            "token_id": token_id,
                            "charge": charge
                        }

                    ]
                }
                response_charged = requests.post(
                    webhook_url, json=charged_data)
                # Yanıtı kontrol et
                if response_charged.status_code == 200:
                    print("Firebase function triggered successfully for Charged Event.")
                else:
                    print(
                        f"Firebase function ERROR in charged event: {response_charged.text}")

            elif 'factorXChanged' in event.event:  # factorXChanged event'i için bir işlem gerçekleştir
                # Özelliklerinizi burada belirtin
                user_address = event.args.userAddress
                token_id = event.args.tokenId
                new_factorX = event.args.newFactorX

                print(
                    f'factorXChanged Event - User Address: {user_address}, Token ID: {token_id}, FactorX: {new_factorX} \n')

                # Veritabanı güncellemesi yapabilirsiniz
                factorX_data = {
                    "root": [
                        {
                            "event_name": "factorXChanged",
                            "factorx_address": user_address,
                            "token_id": token_id,
                            "new_factorX": new_factorX
                        }
                    ]
                }
                response_factorX = requests.post(
                    webhook_url, json=factorX_data)
                # Yanıtı kontrol et
                if response_factorX.status_code == 200:
                    print(
                        "Firebase function triggered successfully for factorXChanged Event.")
                else:
                    print(
                        f"Firebase function ERROR in factorXChanged event: {response_factorX.text}")

            elif "decreaseChargeEvent" in event.event:
                # Özelliklerinizi burada belirtin
                user_address = event.args.userAddress
                token_id = event.args.tokenId
                new_decreased_charge = event.args.newDecreasedCharge

                print(
                    f'decreaseChargeEvent - User Address: {user_address}, Token ID: {token_id}, Charge: {new_decreased_charge}')

                # Veritabanı güncellemesi yapabilirsiniz
                decreased_charge_data = {
                    "root": [
                        {
                            "event_name": "decreaseChargeEvent",
                            "charged_address": user_address,
                            "token_id": token_id,
                            "charge": new_decreased_charge
                        }
                    ]
                }
                response_decreased_charge = requests.post(
                    webhook_url, json=decreased_charge_data)
                # Yanıtı kontrol et
                if response_decreased_charge.status_code == 200:
                    print(
                        "Firebase function triggered successfully for decreaseChargeEvent Event.")
                else:
                    print(
                        f"Firebase function ERROR in decreaseChargeEvent event: {response_decreased_charge.text}")
            
            elif "Transfer" in event.event:
                token_id = event.args.tokenId
                from_user = getattr(event.args, 'from')  # 'from' özelliğine dinamik erişim
                to_user = event.args.to
                            
                print(f"tokenid: {token_id} || from: {from_user} || to: {to_user}")


            elif "levelUpEvent" in event.event:
                # Özelliklerinizi burada belirtin
                token_id = event.args.tokenId
                new_level = event.args.newLevel

                print(
                    f'levelUpEvent - Token ID: {token_id}, Level: {new_level}')

                # Veritabanı güncellemesi yapabilirsiniz
                level_up_data = {
                    "root": [
                        {
                            "event_name": "levelUpEvent",
                            "token_id": token_id,
                            "new_level": new_level
                        }
                    ]
                }
                response_level_up = requests.post(
                    webhook_url, json=level_up_data)
                # Yanıtı kontrol et
                if response_level_up.status_code == 200:
                    print(
                        "Firebase function triggered successfully for levelUpEvent Event.")
                else:
                    print(
                        f"Firebase function ERROR in levelUpEvent event: {response_level_up.text}")
                    

        await asyncio.sleep(poll_interval)


# Eventleri dinleme looplarını oluştur
loop = asyncio.get_event_loop()
try:
    tasks = [
        loop.create_task(log_loop(filter_charged, 2)),
        loop.create_task(log_loop(filter_nftMinted, 2)),
        loop.create_task(log_loop(filter_factorXChanged, 2)),
        loop.create_task(log_loop(filter_levelUp, 2)),
        loop.create_task(log_loop(filter_decreaseCharge, 2)),
        loop.create_task(log_loop(filter_nftTransfer, 2))
        ]
    loop.run_until_complete(asyncio.wait(tasks))
except Exception as e:
    print("Error: ", e)
finally:
    for task in tasks:
        task.cancel()
    loop.close()
