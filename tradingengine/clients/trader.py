import requests

class Trader:

    def __init__(self, username, feedcode="NK225", base_url="http://0.0.0.0:5000"):
        self.money = 0.0
        self.position = 0
        self.order_store = {} # dict of order with orderID as key
        self.tradelist = [] # list of trades done
        self.feedcode = feedcode
        self.username = username
        self.base_url = base_url

    def on_trade(self, price, quantity):
        self.position += quantity
        self.money -= (quantity * price)
        print(f"   we now have position {self.position} and money {self.money}")

    def get_pnl(self, current_price):
        return(self.money + self.position * current_price)

    def get_top_level(self):
        response = requests.get(self.base_url + "/toplevel/" + self.feedcode)
        return response

    def place_order(self, isbid, volume, price):
        response = requests.post(self.base_url + "/insertorder", data=dict(instrument=self.feedcode, isbid=isbid, volume=volume, price=price, username=self.username))
        if response.status_code == requests.codes.ok:
            order = response.json()['order_details']
            print(f"successfully inserted! - orderID = {order['order_id']}")
            self.order_store[order['order_id']] = order
            if response.json()["trade_list"]:
                print("Handling trade feed message(s)...")
                for trade in response.json()["trade_list"]:
                    self.tradelist.append(trade)
                    price = trade['traded_price']
                    quantity = 1 if isbid else -1  #set sign first
                    quantity = quantity * trade['traded_volume']
                    self.on_trade(price, quantity)
                    print(f"   Traded {quantity} @ {price} with {trade['sitting_order']['username']}")
                print(f'PNL is now: {self.get_pnl(price)}')  # uses the price from the last trade in list
        else:
            print(f"Failure in the request: {response.status_code}")
        return response


        

