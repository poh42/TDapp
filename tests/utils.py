from models.user import UserModel

email = "test@topdog.com"
password = "Pa55w0rd"
username = "asdrubal"


def create_dummy_user():
    user = UserModel()
    user.email = email
    user.password = password
    user.username = username
    user.firebase_id = "dummy"
    user.save()
    return user
