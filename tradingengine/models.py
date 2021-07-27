from flask import current_app
from tradingengine import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)

class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    max_price = db.Column(db.Integer, nullable=False)
    min_price = db.Column(db.Integer, nullable=False)
    tick_size = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    instrument = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    isbid = db.Column(db.Boolean, nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # This is an ENUM, TODO set that up properly for sql
    status = db.Column(db.Integer, nullable=False)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agg_ord = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    sit_ord = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    instrument = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)