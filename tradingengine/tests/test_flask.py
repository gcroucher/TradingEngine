from tradingengine import create_app
import pytest

@pytest.fixture
def client():
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        yield test_client

def test_initialised(client):
    response = client.get('/getorder/1')
    assert response.json['order_details'] == {'instrument': 'NK225', 'isbid': True, 'order_id': 1, 'order_status': 1, 'price': 50, 'username': 'gracro', 'volume': 5}
    assert response.status_code == 200

def test_insert(client):
    response = client.post('/insertorder', data=dict(instrument="NK225", isbid=0, volume=6, price=55, username="fred"))
    assert response.json['order_details'] == {'instrument': 'NK225', 'isbid': False, 'order_id': 4, 'order_status': 1, 'price': 55, 'username': 'fred', 'volume': 6}
    assert response.status_code == 200

def test_trade(client):
    response = client.post('/insertorder', data=dict(instrument="NK225", isbid=0, volume=6, price=55, username="fred"))
    response = client.post('/insertorder', data=dict(instrument="NK225", isbid=1, volume=5, price=55, username="eric"))
    assert response.json['order_details'] == {'instrument': 'NK225', 'isbid': True, 'order_id': 5, 'order_status': 0, 'price': 55, 'username': 'eric', 'volume': 0}
    #This is REALLY fiddly with the order of the stuff in the trade list, like aggressor THEN instrument THEN sitting order. Dunno why.
    assert response.json['trade_list'] == [
                    {'aggressor_order': {'instrument': 'NK225', 'isbid': True, 'order_id': 5, 'order_status': 0, 'price': 55, 'username': 'eric', 'volume': 5},
                    'instrument': 'NK225',
                    'sitting_order': {'instrument': 'NK225', 'isbid': False, 'order_id': 4, 'order_status': 1, 'price': 55, 'username': 'fred', 'volume': 6}, 
                    'trade_id': 1, 'traded_price': 55, 'traded_volume': 5}]
    assert response.status_code == 200

def test_delete(client):
    response = client.post('/deleteorder', data=dict(instrument="NK225", order_id=2))
    assert response.json['order_details'] == {'instrument': 'NK225', 'isbid': True, 'order_id': 2, 'order_status': 4, 'price': 50, 'username': 'gracro', 'volume': 5}
    assert response.status_code == 200