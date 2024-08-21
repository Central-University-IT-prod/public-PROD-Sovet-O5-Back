"""Avatars routers module"""
import os
from fastapi import Depends, Query, APIRouter, UploadFile
from fastapi.responses import FileResponse

from miniapp_api import helpers


router = APIRouter()

@router.get("/avatars/getAvatar")
async def get_avatar(user_id: str = Query(..., alias="id")):
    """Endpoint to get avatar by user id"""
    filepath = os.path.join("/app/avatars", f"{user_id}.jpg")
    if not os.path.exists(filepath):
        filepath = os.path.join("./graphics", "404.jpeg")
    return FileResponse(filepath)


@router.post(
    "/avatars/uploadAvatar",
    response_model=None
)
async def service_upload_avatar(
    avatar: UploadFile,
    user_id: int = Query(..., alias="id"),
    _service_auth: None = Depends(helpers.service_auth_dependency)
):
    """Endpoint to update current user profile"""
    filepath = os.path.join("/app/avatars", f"{user_id}.jpg")
    with open(filepath, "wb") as f:
        f.write(avatar.file.read())