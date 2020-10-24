from ma import ma
from models.user_photo import UserPhotoModel


class UserPhotoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserPhotoModel
        dump_only = ("id", "created_at", "updated_at")
        load_instance = True
