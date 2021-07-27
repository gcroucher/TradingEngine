from tradingengine.src.datatypes import Order, OrderBook
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_bcrypt import Bcrypt
#from flask_login import LoginManager
#from flask_mail import Mail
from tradingengine.config import Config

print("TESTING0")

db = SQLAlchemy()
#bcrypt = Bcrypt()
#login_manager = LoginManager()
#login_manager.login_view = 'users.login' #function name of route
#login_manager.login_message_category = 'info' #bootstrap class
#mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    #bcrypt.init_app(app)
    #login_manager.init_app(app)
    #mail.init_app(app)

    #from TradingEngine.users.routes import users #the name of the Blueprint instance
    #from TradingEngine.posts.routes import posts #the name of the Blueprint instance
    from tradingengine.src.main import main #the name of the Blueprint instance
    #from TradingEngine.errors.handlers import errors

    #app.register_blueprint(users)
    #app.register_blueprint(posts)
    app.register_blueprint(main)
    #app.register_blueprint(errors)

    feedcode = "NK225"
    app.order_book = OrderBook(feedcode)
    # Load some Test data
    order_id = app.order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    order_id = app.order_book.insert_order(Order("NK225", True, 5, 50, "gracro"))
    order_id = app.order_book.insert_order(Order("NK225", False, 5, 60, "gracro"))
    print(app.order_book.render())

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
