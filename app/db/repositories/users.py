from typing import Optional

from prisma.types import UserUpdateInput

from app.db.errors import EntityDoesNotExist
from app.db.queries.queries import queries
from app.db.repositories.base import BaseRepository
from app.models.domain.users import User, UserInDB


class UsersRepository(BaseRepository):
    async def get_user_by_email(self, *, email: str) -> UserInDB:
        user = await UserInDB.prisma().find_unique(
            where={
                "email": email,
            },
        )
        if user is not None:
            return user

        raise EntityDoesNotExist("user with email {0} does not exist".format(email))

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user = await UserInDB.prisma().find_unique(
            where={
                "username": username,
            },
        )
        if user is not None:
            return user

        raise EntityDoesNotExist(
            "user with username {0} does not exist".format(username),
        )

    async def create_user(
        self,
        *,
        username: str,
        email: str,
        password: str,
    ) -> UserInDB:
        salt, hashed_password = UserInDB.generate_password_hash(password)
        return await UserInDB.prisma().create(
            data={
                "username": username,
                "email": email,
                "salt": salt,
                "hashed_password": hashed_password,
            }
        )

    async def update_user(  # noqa: WPS211
        self,
        *,
        user: User,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        bio: Optional[str] = None,
        image: Optional[str] = None,
    ) -> UserInDB:
        data: UserUpdateInput = {}
        if username is not None:
            data["username"] = username

        if email is not None:
            data["email"] = email

        if bio is not None:
            data["bio"] = bio

        if image is not None:
            data["image"] = image

        if password is not None:
            salt, hashed_password = UserInDB.generate_password_hash(password)
            data["salt"] = salt
            data["hashed_password"] = hashed_password

        user_record = await UserInDB.prisma().update(
            where={
                "username": user.username,
            },
            data=data,
        )
        assert (
            user_record is not None
        ), f"Could not find a user with the username: {username}"
        return user_record
