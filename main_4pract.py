from web3 import Web3
import re
from getpass import getpass
from web3.middleware import geth_poa_middleware 
from contract_info import abi, contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract_address, abi=abi)
account = ""

def check(password):
    return (len(password) >= 12 and
            re.search(r"[A-Z]", password) and
            re.search(r"[a-z]", password) and
            re.search(r"[0-9]", password) and
            re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password) and
            not re.search(r"password123|qwerty123", password, re.IGNORECASE))

def register():
    try:
        account_created = False
        password = getpass("Введите пароль: ")
        while not account_created:
            if check(password):
                # Создание нового аккаунта
                account = w3.geth.personal.new_account(password)
                
                # Разблокировка основного аккаунта для отправки транзакции
                sender_account = "0xCf6DB0F2f5AD330b726864C79ccE46c355B92f75"
                sender_password = getpass("Введите пароль для отправителя: ")  # Введите пароль для аккаунта отправителя
                w3.geth.personal.unlock_account(sender_account, sender_password)

                # Отправка транзакции с начальным балансом
                tx_hash = w3.eth.send_transaction({
                    "to": account, 
                    "from": sender_account, 
                    "value": w3.to_wei(1, 'ether')  # Используем правильный метод преобразования
                })

                # Ожидание получения квитанции о транзакции
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                print(f"Публичный ключ: {account}")
                print(f"Квитанция о транзакции: {tx_receipt}")
                account_created = True
                break
            else:
                print("Пароль не надежный")
                password = getpass("Введите пароль: ")
    except Exception as e:
        print("Ошибка в регистрации: ", e)
        main()

#1
def authorize():
    try:
        global account
        publicKey = input("Введите публичный ключ: ")
        password = input("Введите пароль: ")
        w3.geth.personal.unlock_account(publicKey, password)
        account = publicKey
        print("Авторизация прошла успешна!\n")
        return True
    except Exception as e:
        print("Ошибка в авторизации. Проверьте публичный ключ и пароль." , e)
        return False

def createEstate():
    try:
        address = input("Введите адрес: ")
        tx = contract.functions.createEstate(address).transact({
            'from': account
        })
        print("Недвижимость успешно создана")

    except Exception as e:
        print("Ошибка создания недвижимости", e)

def createAD():
    try:
        price = int(input("Введите цену: "))
        idEstate = int(input("Введите номер недвижимости: "))

        contract.functions.createAd(price, idEstate).transact({
            'from': account
        })
        print("Успешное создание объявления")
    except Exception as e:
        print("Ошибка добавления недвижимости: ", e)

def changeEstate():
    try:
        idEstate = int(input("Введите номер недвижимости: "))
        isActive = True  # Здесь можно задать нужное значение активности недвижимости

        # Вызываем функцию updateEstateActive с двумя аргументами
        tx = contract.functions.updateEstateActive(idEstate, isActive).transact({
            'from': account
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)
        print("Недвижимость успешно обновлена")
    except Exception as e:
        print("Ошибка обновления недвижимости: ", e)

def changeAD():
    try:
        idAD = int(input("Введите номер объявления: "))
        newAdType = input("Введите новый статус объявления (true для открытого, false для закрытого): ").lower() == 'true'

        # Вызываем функцию updateAdType с двумя аргументами
        tx = contract.functions.updateAdType(idAD, newAdType).transact({
            'from': account
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)
        print("Успешное обновление объявления")
    except Exception as e:
        print("Ошибка обновления объявления: ", e)

def buyEstate():
    try:
        ad_id = int(input("Введите номер объявления: "))
        value = int(input("Введите цену недвижимости: "))
        
        # Вызываем функцию buyEstate с аргументом ad_id и отправляем ETH
        tx = contract.functions.buyEstate(ad_id).transact({
            'from': account,
            'value': value
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)
        print("Успешная покупка недвижимости")
    except Exception as e:
        print("Ошибка покупки недвижимости: ", e)


def withdraw():
    try:
        amount = int(input("Введите количество средств: "))       
        # Вызываем функцию withdraw без отправки эфира
        tx = contract.functions.withdraw(amount).transact({
            'from': account
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)
        print("Успешный вывод средств")
    except Exception as e:
        print("Ошибка вывода средств: ", e)

def pay():
    try:
        amount = float(input("Введите количество средств (в ETH): "))
        value_in_wei = w3.to_wei(amount, 'ether')
        tx = contract.functions.deposit().transact({
            'from': account,
            'value': value_in_wei
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx)
        print(f"Баланс успешно пополнен на {amount} ETH")
    except Exception as e:
        print("Ошибка: ", e)

def getEstates():
    try:
        # Получаем список всех недвижимостей
        estates = contract.functions.getAllEstates().call()
        
        # Получаем количество недвижимостей
        estates_length = len(estates)
        print(f"Всего недвижимости: {estates_length}")
        
        # Проходим по каждой недвижимости
        for i in range(estates_length):
            estate = estates[i]
            estate_id = estate[3]
            address_estate = estate[0]
            owner = estate[1]
            is_active = estate[2]
            print(f"ID: {estate_id}, Адрес: {address_estate}, Владелец: {owner}, Активность: {is_active}")
    except Exception as e:
        print("Ошибка получения информации о недвижимости: ", e)

def getAD():
    try:
        # Получаем список всех объявлений
        ads = contract.functions.getAllAds().call()
        
        # Получаем количество объявлений
        ads_length = len(ads)
        print(f"Всего объявлений: {ads_length}")
        
        # Проходим по каждому объявлению
        for i in range(ads_length):
            ad = ads[i]
            price = ad[0]
            estate_id = ad[1]
            owner = ad[2]
            buyer = ad[3]
            date_time = ad[4]
            ad_type = ad[5]
            print(f"ID объявления: {i}, Цена: {price}, ID недвижимости: {estate_id}, Владелец: {owner}, Покупатель: {buyer}, Дата и время: {date_time}, Тип объявления: {ad_type}")
    except Exception as e:
        print("Ошибка получения информации о текущих объявлениях: ", e)
        

def getBalance(account):
    try:
        balance = contract.functions.getBalance(account).call()
        print(f"Баланс аккаунта: {balance} Wei")
    except Exception as e:
        print("Ошибка получения баланса на контракте: ", e)
        
def getAccountBalance(account):
    try:
        balance = w3.eth.get_balance(account)
        print(f"Баланс на аккаунте {account}: {balance}")
    except Exception as e:
        print("Ошибка получения баланса на аккаунте: ", e)

def main():
    print("Выберите действие: \n1. Авторизация \n2. Регистрация \n3. Выход")
    choise0 = int(input())
    while choise0 != 3:
        if (choise0 == 1):
            if(authorize()):
                print("Выберите действие: \n1. Создание недвижимости \n2. Создание объявления \n3. Измененее статуса недвижимости \n4. Изменение статуса объявления \n5. Покупка недвижимости \n6. Вывод средств \n7. Получение информации \n8. Пополнить баланс")
                choise1 = int(input())
                while choise1 != 9:
                    match (choise1):
                        case 1:
                            createEstate()
                        case 2:
                            createAD()
                        case 3:
                            changeEstate()
                        case 4:
                            changeAD()
                        case 5:
                            buyEstate()
                        case 6:
                            withdraw()
                        case 7:
                            print("Выберите действие: \n1. Информация о доступных недвижимостях \n2. Информация о текущих объявлениях \n3. Информация о балансе на смарт-контракте \n4. Посмотреть баланс аккаунта")
                            choise2 = int(input())
                            match choise2:
                                case 1:
                                    getEstates()
                                case 2:
                                    getAD()
                                case 3:
                                    getBalance(account)
                                case 4:
                                    getAccountBalance(account)
                        case 8:
                            pay()
                        case 9:
                            exit(0)
                    print("Выберите действие: \n1. Создание недвижимости \n2. Создание объявления \n3. Измененее статуса недвижимости \n4. Изменение статуса объявления \n5. Покупка недвижимости \n6. Вывод средств \n7. Получение информации \n8. Пополнить баланс\n")
                    choise1 = int(input())
        elif  (choise0 == 2):
            register()

if __name__ == '__main__':
    main()