from share.repository import BaseRepository

from .models import User


class UserRepository(BaseRepository):
    model = User
