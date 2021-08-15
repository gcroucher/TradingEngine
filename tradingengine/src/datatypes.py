from collections import deque
import io
import json
import copy

from json import JSONEncoder

from enum import Enum

class OrderStatus(Enum):
    PENDING = 0
    ACTIVE = 1
    AMENDED = 2
    COMPLETED = 3 #unused atm
    CANCELLED = 4


class DequeEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, deque):
            return list(object)
        return JSONEncoder.default(self, object)

class Order(dict):
    """Order class extends dict"""
    def __init__(self, instrument, isbid, volume, price, username, order_id=0, order_status=OrderStatus.PENDING.value):
        dict.__init__(self, order_id = 0,
                    instrument = instrument,
                    isbid = isbid,
                    volume = volume,
                    price = price,
                    username = username,
                    order_status = order_status)

    def __str__(self):
        return f"{self.print_side()} {self['volume']} @ {self['price']} from {self['username']}"
    
    def print_side(self):
        return "Buy" if self['isbid'] else "Sell"

class Trade(dict):
    """Trade class extends dict"""
    def __init__(self, trade_id, instrument, aggressor_order, sitting_order, traded_volume, traded_price):
        dict.__init__(self, trade_id = trade_id,
                    instrument = instrument,
                    aggressor_order = aggressor_order,
                    sitting_order = sitting_order,
                    traded_volume = traded_volume,
                    traded_price = traded_price)
    #TODO some sweet printing functions for trades

class OrderBook:
    """Orderbook class holds lists of orders per side per tick for a single Instrument
        - Receives new orders and executes the trades"""
    def __init__(self, instrument, start_order_id=0, max_price=100, min_price=0, tick_size=5, start_trade_id=0):
        self.instrument = instrument
        self.order_id = start_order_id
        self.max_price = max_price
        self.min_price = min_price
        self.tick_size = tick_size
        self.max_bid = 0
        self.min_ask = max_price + 1
        # This is the actual order book, a list of double-ended queues, which should contain order objects
        self.tick_levels = {k: deque() for k in range(self.min_price, self.max_price + 1, tick_size)}
        # This is the dict containing all orders, keyed by order_id.
        self.order_dict = {} 
        self.trade_id = start_trade_id
        # This is the dict containing all trades, keyed by trade_id
        self.trade_dict = {}

    def add_order_to_books(self, order):
        self.tick_levels[order['price']].append(order)
        self.order_dict[order['order_id']] = order
        order['order_status'] = OrderStatus.ACTIVE.value #AMENDED

    def get_order(self, order_id):
        return self.order_dict[order_id]

    def amend_volume(self, order_id, volume):
        order = self.order_dict[order_id]
        if volume > order['volume']:
            # if volume is increasing, push it to back of the level
            self.tick_levels[order['price']].remove(order)
            self.tick_levels[order['price']].append(order)

        order['volume'] = volume
        order['order_status'] = OrderStatus.AMENDED.value
        return order

    def amend_price(self, order_id, price):
        order = self.order_dict[order_id]
        # remove it from the old level
        self.tick_levels[order['price']].remove(order)
        # call insert 
        order['price'] = price
        order, trade_list = self.insert_order(order)
        order['order_status'] = OrderStatus.AMENDED.value
        return order, trade_list

    def delete_order(self, order_id):
        #TODO Find and remove from tick_levels!
        #self.tick_levels[order['price']].append(order)
        # find in order dict and set order status to CANCELLED
        print('in delete order, wtf yo')
        order = self.order_dict[order_id]
        print(f"{order}")
        # Got the order now remove it from that tick_levels level
        self.tick_levels[order['price']].remove(order)
        #for sit_order in self.tick_levels[order['price']]:
        #    if sit_order['order_id'] == order['order_id']:
        #TODO throws errosr if already deleted@

        order['order_status'] = OrderStatus.CANCELLED.value
        print(f"order deleted, status now: {OrderStatus(order['order_status'])}")
        return order

    def handle_trade(self, agg_order, sit_order, price, volume=0):
        self.trade_id += 1

        # figure out the volume:
        # We always trade for the volume of the least of the two orders.
        trade_volume = min(agg_order['volume'], sit_order['volume'])

        #make the trade
        print(f"Trading for vol {trade_volume}")
        new_trade = Trade(trade_id=self.trade_id, 
                        instrument=self.instrument, 
                        aggressor_order=copy.copy(agg_order), 
                        sitting_order=copy.copy(sit_order), 
                        traded_volume=trade_volume, 
                        traded_price=price)
        self.trade_dict[self.trade_id] = new_trade

        #decrement the volume of both orders
        agg_order['volume'] -= trade_volume
        sit_order['volume'] -= trade_volume

        #clear empty order from book
        if sit_order['volume'] == 0: 
            print(f"clearing the sitting order from book: {sit_order}")
            sit_order['order_status'] = OrderStatus.COMPLETED.value
            self.tick_levels[price].popleft() 

        #TODO - handle the sitting order update / push to user
        return new_trade

    def refresh_top_level(self):
        """ call this method when unsure that the top level prices are still correct, and it will update them
            Typically caused by trade-outs or amends or deletes
            We assume the self.min_ask and self.max_bid are the 'best case' and we only need to hunt backwards.
        """
        while not self.tick_levels[self.min_ask] and self.min_ask < self.max_price:  #i.e. there are no orders on that level
            self.min_ask += self.tick_size
        
        while not self.tick_levels[self.max_bid] and self.max_bid < self.min_price:  #i.e. there are no orders on that level
            self.max_bid -= self.tick_size

    def reply_top_level(self):
        """Returns the top level prices and total volume on that level"""
        self.refresh_top_level()
        bid_vol = ask_vol = 0
        # if one side doesnt exit, the top-level will be the max_price or min_price
        # and the vol will be 0. This makes this function 'work' fine.
        for bid_order in self.tick_levels[self.max_bid]:
            bid_vol += bid_order['volume']
        for ask_order in self.tick_levels[self.min_ask]:
            ask_vol += ask_order['volume']
        return (self.max_bid, bid_vol, self.min_ask, ask_vol)

    def reply_full_book(self):
        print("We are in reply_full_order_book, what do we return?")
        print(f"{self.to_json()}")
        return self.to_json()

    def insert_order(self, order):
        """ Inserts the passed order object into the order book"""
        if order['order_id'] == 0:
            self.order_id += 1
            order['order_id'] = self.order_id
        #TODO DO i even need this error checking here?
        if type(order['price']) != int:
            raise ValueError("Expected price to be int")
        if order['price'] % self.tick_size != 0:
            raise ValueError("Expected price to be steps of tick_size %f" % self.tick_size)

        curr_trade_list = [] #list of trades this insert caused

        if order['isbid']: 
            # Looks for sitting sell orders that cross with incoming order
            while order['price'] >= self.min_ask and order['volume'] > 0:
                level = self.tick_levels[self.min_ask]
                while level and order['volume'] > 0:
                    sell_order = level[0]
                    curr_trade_list.append(self.handle_trade(agg_order=order, sit_order=sell_order, price=self.min_ask))

                #If the level is now empty, increment to next tick and check outer loop
                if not level:
                    self.min_ask += self.tick_size

            # Once we are here then this can become a sitting order, if it still has untraded volume
            if order['volume'] > 0:
                self.add_order_to_books(order)
                if self.max_bid < order['price']:
                    self.max_bid = order['price']
            # Otherwise, its a completed order 
            else: 
                order['order_status'] = OrderStatus.COMPLETED.value

            return order, curr_trade_list

        else: # It's an Ask!
            # Looks for sitting buy orders that cross with incoming order
            while order['price'] <= self.max_bid and order['volume'] > 0:
                level = self.tick_levels[self.max_bid]
                while level and order['volume'] > 0:
                    buy_order = level[0]
                    curr_trade_list.append(self.handle_trade(agg_order=order, sit_order=buy_order, price=self.max_bid))

                #If the level is now empty, decrement to next tick and check outer loop
                if not level:
                    self.max_bid -= self.tick_size

            # Once we are here then this can become a sitting order, if it still has untraded volume
            if order['volume'] > 0:
                self.add_order_to_books(order)
                if self.min_ask > order['price']:
                    self.min_ask = order['price']
            # Otherwise, its a completed order 
            else: 
                order['order_status'] = OrderStatus.COMPLETED.value

            return order, curr_trade_list

    def to_json(self):
        return json.dumps(self.tick_levels, cls=DequeEncoder)

    def _render_level(self, level, maxlen=40):
        """
        Renders a single tick level for display
        """
        ret = ",".join(f"{order['volume']}:{order['username']}({order['order_id']})" for order in level)
        #TODO Understand the checking and formatting here for big levels
        if len(ret) > maxlen:
            ret = ",".join(str(order['volume']) for order in level )
        if len(ret) > maxlen:
            ret = f"{len(level)} orders (total size {sum(order['volume'] for order in level)}"
        return ret
    
    def render(self):
        """
        Renders a visual representation of the order book as a string
        mainly used for debugging
        TODO: Nothing, it works but assumes the book is NOT in cross
        """

        output = io.StringIO()
        output.write(("-"*110)+"\r\n")
        output.write("Buyers".center(55) + " | " + "Sellers".center(55) + "\r\n")
        output.write(("-"*110)+"\r\n")
        for tick in range(self.max_price, self.min_price-1, -1 * self.tick_size):
            level = self.tick_levels[tick]
            if level:
                if tick >= self.min_ask:
                    left_price = ""
                    left_orders = ""
                    right_price = str(tick)
                    right_orders = self._render_level(level)
                else:
                    left_price = str(tick)
                    left_orders = self._render_level(level)
                    right_price = ""
                    right_orders = ""
                output.write(left_orders.rjust(43))
                output.write(" |")
                output.write(left_price.rjust(10))
                output.write(" |")
                output.write(right_price.ljust(10))
                output.write("| ")
                output.write(right_orders.ljust(43))
                output.write("\r\n"+("-"*110)+"\r\n")
        return output.getvalue()

