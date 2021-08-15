from trader import Trader
import time

trader = Trader("phillyfusion", "NK225")
width = 4
tick = 5
volume = 5

#TODO 

# "HOTLOOP"
while True:
    response = trader.get_top_level()
    print(f"Top level of market is {response.json()}")
    
    #vwap will error if both bid and ask volumes are 0.. hmm
    vwap = round((response.json()['bid'] * response.json()['bid_volume'] + 
            response.json()['ask'] * response.json()['ask_volume']) / 
            (response.json()['bid_volume'] + response.json()['ask_volume']))
    print(f"Calculated VWAP: {vwap}")
    my_bid = tick * round((vwap - width)/tick)
    my_ask = tick * round((vwap + width)/tick)
    print(f"calculated bid: {my_bid} and ask: {my_ask}")
    
    # Time to improve the market
    if my_bid > response.json()['bid']:
        print(f"Inserting bid of {my_bid}")
        response = trader.place_order(1, volume, my_bid)
    if my_ask < response.json()['ask']:
        print(f"Inserting ask of {my_ask}")
        response = trader.place_order(0, volume, my_ask)

    print("Waiting..")
    time.sleep(5)