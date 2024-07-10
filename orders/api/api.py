import sys
import os

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.insert(0, project_root)


import json
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask import got_request_exception
from flask import current_app as capp
from db.sql_repository import OrderSrvSQLRepo, Base
from services import OrderService, Order, exceptions
from api.models import CreateOrderReq
from config import Config

# order service flask api

from sqlalchemy import create_engine

class OrderSrvController(Resource):
    def __init__(self, order_service: OrderService) -> None:
        self.order_service = order_service

    def get(self, order_id=None):
        capp.logger.info(f"Get order req for {order_id}")

        try:
            order = self.order_service.get_order_by_id(order_id)
            # TODO: Encode the order entity to json response
            return jsonify(order)
        except exceptions.NoResultFound:
            print(f"Order not found for order_id {order_id}")
            return {}, 404


    def post(self):
        order_data = CreateOrderReq(**request.get_json())
        new_order = Order(
            buyer_id=order_data.buyer_id
        )

        # TODO: All unhandled error as internal service error in a middleware
        self.order_service.create_order(new_order)
        return {'message': 'Order created'}, 200


def log_exception(sender, exception, **extra):
    """ Log an exception to our logging framework """
    sender.logger.debug('Got exception during processing: %s', exception)


def create_app(config_class=Config):
    app = Flask(__name__)
    api = Api(app)

    app.config.from_object(config_class)

    # Use sqlite as DB
    sqlite_engine = create_engine("sqlite:///../orderdb.sqlite", echo=False)
    repo = OrderSrvSQLRepo(sqlite_engine)
    order_srv = OrderService(repo)

    api.add_resource(
        OrderSrvController,
        '/orders', '/orders/<string:order_id>',
        resource_class_args=(order_srv,),
    )

    got_request_exception.connect(log_exception, app)

    return app

if __name__ == '__main__':

    app = create_app()

    app.run(debug=True)
