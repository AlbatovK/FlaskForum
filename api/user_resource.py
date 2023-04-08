import datetime

from flask import jsonify
from flask_apispec import MethodResource, doc, marshal_with, use_kwargs
from flask_restful import Resource, reqparse, abort
from marshmallow import Schema, fields

from data import db_session
from data.user import User

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('about', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)


class UserRequestSchema(Schema):
    name = fields.String(required=True, description="name")
    about = fields.String(required=True, description="about")
    email = fields.String(required=True, description="email")
    password = fields.String(required=True, description="password")


class UserResponseSchema(Schema):
    name = fields.String(default='name')
    about = fields.String(default='about')
    email = fields.String(default='email')
    id = fields.String(default='id')
    created_date = fields.DateTime(default=datetime.datetime.now())


class UserNotFoundErrorSchema(Schema):
    message = fields.String(default='error_message')


class ResponseStatusSchema(Schema):
    success = fields.String(default='success_status')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User with id {user_id} not found")


class UserResource(MethodResource, Resource):

    @doc(description='Получить пользователя с данным id')
    @marshal_with(UserResponseSchema, code='200')
    @marshal_with(UserNotFoundErrorSchema, code='404')
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify(
            user.to_dict(
                only=('name', 'email', 'about', 'id', 'created_date')
            )
        )

    @doc(description='Удалить пользователя с данным id')
    @marshal_with(ResponseStatusSchema, code='200')
    @marshal_with(UserNotFoundErrorSchema, code='404')
    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify(
            {
                'success': 'OK'
            }
        )


class UserListResource(MethodResource, Resource):

    @doc(description='Получить всех пользователей')
    @marshal_with(UserResponseSchema, code='200')
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            [
                x.to_dict(
                    only=('name', 'email', 'about', 'id', 'created_date')
                ) for x in users]
        )

    @doc(description='Создать пользователя')
    @use_kwargs(UserRequestSchema, location='json')
    @marshal_with(ResponseStatusSchema)
    def post(self, about, name, password, email):
        args = parser.parse_args()

        password = args['password']
        if password.strip() == '' or not password:
            return jsonify(
                {
                    'success': 'Failed - password is invalid'
                }
            )

        user = User(
            name=args['name'],
            about=args['about'],
            email=args['email'],
        )

        user.set_password(password)
        session = db_session.create_session()
        session.add(user)
        session.commit()
        return jsonify(
            {
                'success': 'OK'
            }
        )
