from flask import request
from flask_restful import Resource

from decorators import check_token
from schemas.image import ImageSchema
from utils import image_helper
from secrets import token_hex
from flask_uploads import UploadNotAllowed
from utils.file_manager import upload_file_to_bucket
import os
import logging

log = logging.getLogger(__name__)

image_schema = ImageSchema()


class ImageUpload(Resource):
    @classmethod
    @check_token
    def post(cls):
        """
        Used to upload an image file.
        It uses JWT to retrieve user information and then saves the image to the user's folder
        If there's a filename conflict, it appends a number at the end
        """
        data = image_schema.load(request.files)  # { image: FileStorage }
        folder = "data"  # static/images/user_1
        name = token_hex() + image_helper.get_extension(data["image"])
        bucket = os.getenv("AWS_BUCKET", None)
        if not bucket:
            log.warning("Bucket not configured")
            raise ValueError("Bucket not configured")
        try:
            image_path = image_helper.save_image(
                data["image"], folder=folder, name=name
            )
            complete_path = image_helper.get_path(name, folder)
            url = upload_file_to_bucket(bucket, complete_path, data["image"].mimetype)
            os.unlink(complete_path)
            basename = image_helper.get_basename(image_path)
            return {"message": f"Image {basename} uploaded", "url": url}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return (
                {"message": "Illegal extension {}".format(extension)},
                400,
            )
