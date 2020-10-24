from flask_restful import Resource
from models.user_photo import UserPhotoModel
from schemas.user_photo import UserPhotoSchema

user_photo_schema = UserPhotoSchema()


class UserPhoto(Resource):
    @classmethod
    def get(cls, user_photo_id):
        user_photo = UserPhotoModel.find_by_id()
        if user_photo is None:
            return {"message": "UserPhoto not found"}, 400
        return (
            {
                "message": "User photo found",
                "user_photo": user_photo_schema.dump(user_photo),
            },
            200,
        )
