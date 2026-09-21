from share.repository import BaseRepository

from .models import UserPassword


class UserPasswordRepository(BaseRepository):
    model = UserPassword
