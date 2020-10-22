from flask import request
from flask_restful import Resource
from schemas.image import ImageSchema
from utils import image_helper
from secrets import token_urlsafe
from flask_uploads import UploadNotAllowed

image_schema = ImageSchema()


class ImageUpload(Resource):
    @classmethod
    def post(cls):
        """
        Used to upload an image file.
        It uses JWT to retrieve user information and then saves the image to the user's folder
        If there's a filename conflict, it appends a number at the end
        """
        data = image_schema.load(request.files)  # { image: FileStorage }
        folder = "data"  # static/images/user_1
        name = token_urlsafe()
        try:
            image_path = image_helper.save_image(
                data["image"], folder=folder, name=name
            )
            basename = image_helper.get_basename(image_path)
            return {"message": f"Image {basename} uploaded"}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return (
                {"message": "Illegal extension {}".format(extension)},
                400,
            )
