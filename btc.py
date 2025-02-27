import requests
import time
import numpy as np

from logger_custom import get_module_logger_btc


logger = get_module_logger_btc(__name__)

def get_btc_eur_price():
    try:
        response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        data = response.json()
        res = float(data["bpi"]["EUR"]["rate"].replace(",", ""))
        return res
    except Exception as e:
        print('# Error in get_btc_eur_price: '+str(e))
        return 0


def get_btc_eur_price_mock():
    # Set the desired mean and variance
    desired_mean = 27000
    desired_variance = 100

    # Calculate the standard deviation (square root of variance)
    desired_std_dev = np.sqrt(desired_variance)

    # Generate a single random number with the desired mean and variance
    random_number = np.random.normal(loc=desired_mean, scale=desired_std_dev, size=1)

    # Print the generated random number
    return random_number[0] #print(f"Generated Random Number: {random_number[0]:.2f}")



def raise_count(last_10_items):
    count = 0
    for i in range(1, len(last_10_items)):
        if last_10_items[i] > last_10_items[i - 1]:
            count += 1
    return count

def fall_count(last_10_items):
    count = 0
    for i in range(1, len(last_10_items)):
        if last_10_items[i] < last_10_items[i - 1]:
            count += 1
    return count

def main(fetch_period, budget_eur, backward_samples, percentage_fall_raise):
    btc_coins = 0  # Initial BTC holdings
    price_history = []
    
    while True:
        price = get_btc_eur_price()
        if price == 0:
            price = price_history[-1]
        price_history.append(price)
        print('Current price - BTC/EUR: '+str(price))
        logger.debug('# Current price - BTC/EUR: '+str(price))

        
        if len(price_history) > backward_samples:
            price_history.pop(0)            
            criteria = int(percentage_fall_raise * backward_samples / 100)
            #print(criteria)
            
            #print('#### price_history[-backward_samples:]: '+str(raise_count(price_history[-backward_samples:])))
            
            if raise_count(price_history[-backward_samples:]) >= criteria and budget_eur > 0:
                buy_amount_eur = 0.05 * budget_eur
                buy_amount_btc = buy_amount_eur / price
                budget_eur -= buy_amount_eur
                btc_coins += buy_amount_btc
                print(f"######## Buy: {buy_amount_btc} BTC at {price} EUR")
                #print(f"Budget: {budget_eur} EUR")
                #print(f"BTC coins: {btc_coins}")
                print('assets in EUR: '+str(budget_eur + btc_coins * price))
                print('assets in BTC: '+str(budget_eur / price + btc_coins))
            elif fall_count(price_history[-backward_samples:]) >= criteria and btc_coins > 0:
                sell_amount_btc = 0.05 * btc_coins
                sell_amount_eur = sell_amount_btc * price
                budget_eur += sell_amount_eur
                btc_coins -= sell_amount_btc
                print(f"######## Sell: {sell_amount_btc} BTC at {price} EUR")
                # print(f"Budget: {budget_eur} EUR")
                # print(f"BTC coins: {btc_coins}")
                print('assets in EUR: '+str(budget_eur + btc_coins * price))
                print('assets in BTC: '+str(budget_eur / price + btc_coins))

            else:
                #print('raise_count(price_history[-backward_samples:0]) is: '+str(raise_count(price_history[-backward_samples:])))
                #print('fall_count(price_history[-backward_samples:0]) is: '+str(fall_count(price_history[-backward_samples:])))
                pass
                
        time.sleep(fetch_period)
    
    # The code will run indefinitely, you can set a condition to stop it if needed.

if __name__ == "__main__":
    #spread_factor = 1.0  
    fetch_period = 60  # Example period of fetching the price in seconds
    budget_eur = 1000  # Example initial budget in Euro
    backward_samples = 10  # Example number of samples to look back
    percentage_fall_raise = 65
    main(fetch_period, budget_eur, backward_samples, percentage_fall_raise)
    
    #my_list = [1,2,3,4,50,51,30,20,10,9]
    
    #print(raise_count(my_list))
