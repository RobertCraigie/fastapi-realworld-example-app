from typing import Tuple, Optional
from prisma.models import User as BaseUser

from app.models.common import IDModelMixin
from app.models.domain.rwmodel import RWModel
from app.services import security


# TODO: this is technically incorrect, we should be inheriting
# from a partial user that has not relational fields


class User(RWModel):
    username: str
    email: str
    bio: str = ""
    image: Optional[str] = None


class UserInDB(IDModelMixin, User, BaseUser):
    def check_password(self, password: str) -> bool:
        hashed = self.hashed_password
        assert hashed is not None
        return security.verify_password(self.salt + password, hashed)

    @staticmethod
    def generate_password_hash(password: str) -> Tuple[str, str]:
        salt = security.generate_salt()
        hashed_password = security.get_password_hash(salt + password)
        return (salt, hashed_password)
