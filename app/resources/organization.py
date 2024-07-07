from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.main import db
from app.models import UserModel, OrgModel
from app.schema import OrgSchema

blp = Blueprint("Organisations", __name__, description="Operations on users")


@blp.route("/api/organisations")
class Organisations(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(userId=user_id).first_or_404(description="User not found")
        user_orgs = user.organizations  # Use the relationship to get organizations

        return {
            "status": "success",
            "message": "Organisations retrieved",
            "data": {"organisations": [org.to_dict() for org in user_orgs]}
        }, 200

    @blp.arguments(OrgSchema)
    @jwt_required()
    def post(self, org_data):
        if OrgModel.query.filter(OrgModel.name == org_data["name"]).first():
            return {"status": "Bad request",
                    "message": "Client error",
                    'statusCode': 400
                    }, 400
        org = OrgModel(name=org_data['name'], description=org_data.get('description', ''))
        db.session.add(org)
        db.session.commit()
        return {
            "status": "success",
            "message": "Organisation created successfully",
            "data": org.to_dict()
        }, 201


@blp.route("/api/organisations/<string:orgId>")
class OrganisationDetail(MethodView):
    @jwt_required()
    def get(self, orgId):
        org = OrgModel.query.filter_by(orgId=orgId).first_or_404(description="Organisation not found")
        return {
            "status": "success",
            "message": "Organisation details retrieved",
            "data": org.to_dict()
        }, 200


@blp.route("/api/organisations/<string:orgId>/users")
class AddUserToOrganisation(MethodView):
    @jwt_required()
    def post(self, orgId):
        user_id = get_jwt_identity()
        org = OrgModel.query.filter_by(orgId=orgId).first_or_404(description="Organisation not found")
        user = UserModel.query.filter_by(userId=user_id).first_or_404(description="User not found")
        org.users.append(user)
        db.session.commit()
        return {
            "status": "success",
            "message": "User added to organisation successfully"
        }, 200
