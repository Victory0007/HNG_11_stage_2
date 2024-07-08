from flask.views import MethodView
from flask_smorest import Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required
from flask import request, jsonify

from app.main import db
from app.models import UserModel, OrgModel
from app.schema import UserLoginSchema

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route("/auth/register")
class UserRegister(MethodView):
    def post(self):
        req = request.json
        user = UserModel(
            email=req.get("email"),
            firstName=req.get("firstName"),
            lastName=req.get("lastName"),
            password=req.get("password"),
            phone=req.get("phone")
        )
        errors = user.validate_user()
        if errors:
            response = {
                "errors": errors
            }
            return jsonify(response), 422

        # Ensure password is a string before hashing
        if not isinstance(user.password, str):
            errors.append({
                "field": "password",
                "message": "Password must be a string"
            })
            response = {
                "errors": errors
            }
            return jsonify(response), 422

        user.password = pbkdf2_sha256.hash(user.password)

        try:
            # Creating an organisation
            org = OrgModel(name=f"{user.firstName}'s Organisation")
            db.session.add(org)
            # Add the created organisation to the list of organisations that belong to this user
            user.organizations.append(org)

            db.session.add(user)
            db.session.commit()  # save to database

            access_token = create_access_token(identity=user.userId)

            response = {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": access_token,
                    "user": user.to_dict()
                }
            }

            return jsonify(response), 201
        except Exception as e:
            response = {
                "status": "Bad request",
                "message": "Registration unsuccessful",
                "statusCode": 400
            }
            print(e)
            return jsonify(response), 400


@blp.route("/auth/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(email=user_data["email"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.userId)
            return {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "access_token": access_token,
                    "user": user.to_dict()
                }
            }, 200

        return {
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }, 401


@blp.route("/api/users/<string:id>")
class UserDetail(MethodView):
    @jwt_required()
    def get(self, id):
        user = UserModel.query.filter_by(userId=id).first_or_404(description="User not found")
        return {
            "status": "success",
            "message": "User details retrieved",
            "data": user.to_dict()
        }, 200
