from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_flask_restful import RestfulPlugin
import json
from app import app, api
from schemas.user import UserSchema
from resources.user import User, UserRegister, SetAdminStatus

# Create spec
spec = APISpec(
    title="Top Dog API",
    version="0.0.1",
    openapi_version="3.0.2",
    info=dict(description="Top Dog API Documentation"),
    plugins=[MarshmallowPlugin(), RestfulPlugin()],
)

# Reference your schemas definitions

spec.components.schema("User", schema=UserSchema, example=dict(a=1))

# We need a working context for apispec introspection.
with app.test_request_context():
    spec.path(resource=User, api=api)
    spec.path(resource=UserRegister, api=api)
    spec.path(resource=SetAdminStatus, api=api)

# We're good to go! Save this to a file for now.
with open("docs/swagger.json", "w") as f:
    json.dump(spec.to_dict(), f)
