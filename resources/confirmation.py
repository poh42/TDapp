import traceback

from flask import make_response, render_template
from flask_restful import Resource
from models.user import UserModel
from models.confirmation import ConfirmationModel
from utils.mailgun import MailgunException


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Returns confirmation HTML page"""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": "Confirmation not found"}, 404
        if confirmation.expired:
            return {"message": "Confirmation link expired"}, 400
        if confirmation.confirmed:
            return {"message": "Confirmation link already confirmed"}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type": "application/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def post(cls, user_id):
        """Resends confirmation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": "Confirmation already sent"}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "Confirmation resend successful"}, 201
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": "Confirmation resend failed"}, 500
