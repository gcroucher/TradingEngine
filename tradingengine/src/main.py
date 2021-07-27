from tradingengine.src.datatypes import Order, OrderBook, OrderStatus
from flask import Flask, request, Blueprint, current_app
from flask_restful import Api, Resource, reqparse, abort
from flask_sqlalchemy import SQLAlchemy

# To run in bash from cmdline
# from parent dir, set FLASK_APP=src/main
# then flask run

main = Blueprint('main', __name__)

order_insert_args = reqparse.RequestParser()
order_insert_args.add_argument("instrument", type=str, help="Feedcode of the instrument is required", required=True)
order_insert_args.add_argument("isbid", type=int, help="isbid 0=False, 1=True is required", required=True)
order_insert_args.add_argument("volume", type=int, help="volume of the order is required", required=True)
order_insert_args.add_argument("price", type=int, help="price of the order is required", required=True)
order_insert_args.add_argument("username", type=str, help="username is required", required=True)

@main.route('/insertorder', methods=['POST'])
def insert_order():
    args = order_insert_args.parse_args()
    # inserting an order returns an order dict, and a list of trade dicts.
    print(f"Calling insert_order with {args}")
    isbid = True if args['isbid'] == 1 else False
    order, trade_list = current_app.order_book.insert_order(Order(args['instrument'], isbid, args['volume'], args['price'], args['username']))
    print(current_app.order_book.render())
    return {"order_details": order, "trade_list": trade_list}

@main.route('/getorder/<int:order_id>', methods=['GET'])
def get_order(order_id):
    return {"order_details": current_app.order_book.get_order(order_id)}

order_delete_args = reqparse.RequestParser()
order_delete_args.add_argument("instrument", type=str, help="Feedcode of the instrument is required", required=True)
order_delete_args.add_argument("order_id", type=int, help="order_id is required", required=True)


@main.route('/deleteorder', methods=['POST'])
def delete_order():
    args = order_delete_args.parse_args()
    print(f"Calling delete_order with {args}")
    order = current_app.order_book.delete_order(args['order_id'])
    print(current_app.order_book.render())
    return {"order_details": order}

order_amend_args = reqparse.RequestParser()
order_amend_args.add_argument("instrument", type=str, help="Feedcode of the instrument is required", required=True)
order_amend_args.add_argument("order_id", type=int, help="order_id is required", required=True)
order_amend_args.add_argument("volume", type=int, help="volume of the order is required", required=False)
order_amend_args.add_argument("price", type=int, help="price of the order is required", required=False)

@main.route('/amendorder', methods=['POST'])
def amend_order():
    args = order_amend_args.parse_args()
    print(f"Calling amend_order functions with {args}")
    if args['volume']: 
        order = current_app.order_book.amend_volume(args['order_id'], args['volume'])
    if args['price']:
        order, trade_list = current_app.order_book.amend_price(args['order_id'], args['price'])
    print(current_app.order_book.render())
    #TODO Handle the no-amending case, where there is no order object.
    if trade_list: 
        return {"order_details": order, "trade_list": trade_list}
    else: #TODO is this going to be ok? having different returns based on input?
        return {"order_details": order}

@main.route('/orderbook/<string:instrument>', methods=['GET'])
def show_orderbook(instrument):
    return {"order_book": current_app.order_book.to_json()}