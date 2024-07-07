from flask.views import MethodView
from flask_smorest import Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required

from app.main import db
from app.models import UserModel, OrgModel
from app.schema import UserRegSchema, UserLoginSchema

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route("/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            return {"status": "Bad request",
                    "message": "Registration unsuccessful",
                    'statusCode': 400
                    }, 400

        user = UserModel(
            firstName=user_data["firstName"],
            lastName=user_data["lastName"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            phone=user_data["phone"]
        )
        db.session.add(user)
        db.session.commit()

        org = OrgModel(
            name=user_data["firstName"] + "'s Organization",
            description=f"This organization was created by {user_data["firstName"]}"
        )
        org.users.append(user)
        db.session.add(org)
        db.session.commit()

        return {"status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": create_access_token(identity=user.userId),
                    "user": user.to_dict()
                }
                }, 201

    # def get(self):
    #     users = UserModel.query.all()
    #     return jsonify([user.to_dict() for user in users])


@blp.route("/auth/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(email=user_data["email"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.userId)
            return {"status": "success",
                    "message": "Login successful",
                    "data": {
                        "access_token": access_token,
                        "user": user.to_dict()
                    }

                    }, 200

        return {"status": "Bad request",
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
