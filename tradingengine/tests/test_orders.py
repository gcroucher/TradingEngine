from tradingengine.src.datatypes import Order, OrderBook, Trade, OrderStatus    # The code to test
import json

def test_create_order():
    # a newly created order has 0 OID and 0 status, because those are edited by the order_book
    assert Order(instrument="NK225", isbid=True, volume=5, price=55, username="gracro") == {'instrument': 'NK225', 'isbid': True, 'order_id': 0, 'order_status': 0, 'price': 55, 'username': 'gracro', 'volume': 5}

def test_create_trade():
    # Not creating full order objects, just passing strings.
    assert Trade(trade_id=0, instrument="NK225", aggressor_order="Test Agg Order", sitting_order="Test Sit Order", traded_volume=5, traded_price=55)  == {'aggressor_order': 'Test Agg Order', 'instrument': 'NK225', 'sitting_order': 'Test Sit Order', 'trade_id': 0, 'traded_price': 55, 'traded_volume': 5}

def test_create_order_book():
    assert json.loads(OrderBook("NK225").to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [], "55": [], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_order_book():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert trade_list == []
    order, trade_list = order_book.insert_order(Order("NK225", False, 5, 60, "gracro"))
    assert trade_list == []
    assert json.loads(order_book.to_json())['50'] == [{'order_id': 1, 'instrument': 'NK225', 'isbid': True, 'volume': 5, 'price': 50, 'username': 'gracro', 'order_status': 1}]
    assert json.loads(order_book.to_json())['60'] == [{'order_id': 2, 'instrument': 'NK225', 'isbid': False, 'volume': 5, 'price': 60, 'username': 'gracro', 'order_status': 1}]
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [{'order_id': 1, 'instrument': 'NK225', 'isbid': True, 'volume': 5, 'price': 50, 'username': 'gracro', 'order_status': 1}], "55": [], "60": [{'order_id': 2, 'instrument': 'NK225', 'isbid': False, 'volume': 5, 'price': 60, 'username': 'gracro', 'order_status': 1}], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_delete():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert trade_list == []
    order = order_book.delete_order(1)
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [], "55": [], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_amend_volume_up():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    #insert a second order on same level
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 2, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    order = order_book.amend_volume(1,10)
    #status change, volume change expected
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 50, 'username': 'gracro', 'volume': 10}
    #move to back of the level expected
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [{'instrument': 'NK225', 'isbid': True, 'order_id': 2, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}, {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 50, 'username': 'gracro', 'volume': 10}], "55": [], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_amend_volume_down():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    #insert a second order on same level
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 2, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    order = order_book.amend_volume(1,2)
    #status change, volume change expected
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 50, 'username': 'gracro', 'volume': 2}
    #move to back of the level expected
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [{'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 50, 'username': 'gracro', 'volume': 2}, {'instrument': 'NK225', 'isbid': True, 'order_id': 2, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}], "55": [], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_amend_price_up():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    order, trade_list = order_book.amend_price(1,55)
    assert trade_list == []
    #status change, volume change expected
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 55, 'username': 'gracro', 'volume': 5}
    #move to back of the level expected
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [], "55": [{'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 55, 'username': 'gracro', 'volume': 5}], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_amend_price_down():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    order, trade_list = order_book.amend_price(1,45)
    assert trade_list == []
    #status change, volume change expected
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 45, 'username': 'gracro', 'volume': 5}
    #move to back of the level expected
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [{'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 45, 'username': 'gracro', 'volume': 5}], "50": [], "55": [], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

def test_insert_amend_price_to_cross():
    order_book = OrderBook("NK225")
    order, trade_list = order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    #insert a second order to cross with
    order, trade_list = order_book.insert_order(Order("NK225", False, 10, 55, "gracro"))
    assert order == {'instrument': 'NK225', 'isbid': False, 'order_id': 2, 'order_status': 1, 'price': 55, 'username': 'gracro', 'volume': 10}
    
    order, trade_list = order_book.amend_price(1,55)
    assert trade_list == [{'trade_id': 1, 'instrument': 'NK225', 'aggressor_order': {'order_id': 1, 'instrument': 'NK225', 'isbid': True, 'volume': 5, 'price': 55, 'username': 'gracro', 'order_status': 1}, 'sitting_order': {'order_id': 2, 'instrument': 'NK225', 'isbid': False, 'volume': 10, 'price': 55, 'username': 'gracro', 'order_status': 1}, 'traded_volume': 5, 'traded_price': 55}]
    #status change, price change, volume change expected
    assert order == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 2, 'price': 55, 'username': 'gracro', 'volume': 0}
    # Only sell order left in book expected
    assert json.loads(order_book.to_json()) == {"0": [], "5": [], "10": [], "15": [], "20": [], "25": [], "30": [], "35": [], "40": [], "45": [], "50": [], "55": [{'instrument': 'NK225', 'isbid': False, 'order_id': 2, 'order_status': 1, 'price': 55, 'username': 'gracro', 'volume': 5}], "60": [], "65": [], "70": [], "75": [], "80": [], "85": [], "90": [], "95": [], "100": []}

#TODO tests for this module:
# - edge cases and silly cases, like deleting stuff that doesnt exist
# - testing get_order