from flask import Flask, jsonify, request, Response
from flask_restful import reqparse, abort, Api, Resource
from flask import got_request_exception
from flask import current_app as capp
from db.sql_repository import UserSQLRepo, Base
from services import UserService, User, exceptions
from api.models import CreateUserReq, User_to_UserResp, UserResp
from config import Config

# user service flask api

from sqlalchemy import create_engine

class UserSrvController(Resource):
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def get(self, username=None):
        capp.logger.info(f"Get user req for {username}")

        user = self.user_service.get_user_by_username(username)
        if user is None:
            return {}, 404

        return Response(
            User_to_UserResp(user).model_dump_json(),
            status=200,
            mimetype='application/json',
        )


    def post(self):
        user_data = CreateUserReq(**request.get_json())
        new_user = User(
            username= user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
        )

        # TODO: All unhandled error as internal service error in a middleware
        self.user_service.create_user(new_user)
        return {'message': 'User created'}, 200


def log_exception(sender, exception, **extra):
    """ Log an exception to our logging framework """
    sender.logger.debug('Got exception during processing: %s', exception)

def create_app(config_class=Config):
    app = Flask(__name__)
    api = Api(app)

    app.config.from_object(config_class)

    # Use sqlite as DB
    # TODO: SQLite filename - Read from config
    sqlite_engine = create_engine(str(app.config.get('USERS_DB_URL')), echo=False)
    repo = UserSQLRepo(sqlite_engine)
    user_srv = UserService(repo)

    api.add_resource(
        UserSrvController,
        '/users', '/users/<string:username>',
        resource_class_args=(user_srv,),
    )

    got_request_exception.connect(log_exception, app)

    return app

