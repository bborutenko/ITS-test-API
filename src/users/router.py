from fastapi import APIRouter, Depends

from auth.utils import get_current_user

from . import schemas as sch
from .models import User

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
) -> sch.UserDisplayS:
    return sch.UserDisplayS(id=user.id, email=user.email)
