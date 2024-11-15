from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

import models as models
from datamanager.database import engine
from routes import (
    user,
    artist,
    track,
    order,
    album,
    order_item,
    user_payment_method
)

app = FastAPI(
    title="HarmonApp API",
    description="Musician and User Oriented Streaming Platform API",
    version="1.0.0"
)

# Create database tables
models.Base.metadata.create_all(bind=engine)


# Custom OpenAPI schema to support multiple auth schemes
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    # automatically generated components (schemas, parameters, etc.)
    openapi_components = openapi_schema.get("components", {})

    # Security schemes
    openapi_schema["components"] = {
        "securitySchemes": {
            "UserAuth": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "users/token",
                        "scopes": {}
                    }
                }
            },
            "ArtistAuth": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "artists/token",
                        "scopes": {}
                    }
                }
            }
        }
    }

    openapi_schema["components"] = openapi_components

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema
app.openapi = custom_openapi

# Include all routers
app.include_router(user.router)
app.include_router(artist.router)
app.include_router(track.router)
app.include_router(album.router)
app.include_router(order.router)
app.include_router(order_item.router)
app.include_router(user_payment_method.router)
