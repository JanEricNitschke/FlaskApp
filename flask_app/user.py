"""Handles keeping track of the user."""

from __future__ import annotations

from typing import Optional

from botocore.exceptions import ClientError
from flask_login import UserMixin
from pydantic import BaseModel

from .db import get_db
from .helpers import check_error_code


class User(UserMixin, BaseModel):
    """Class that stores userinformation."""

    userid: str
    name: str
    email: str
    profile_pic: str
    paid: bool = False
    expires: Optional[str] = None
    amount: int = 0
    family_name: Optional[str] = None
    gender: Optional[str] = None
    locale: Optional[str] = None

    @staticmethod
    def get(user_id: str) -> User | None:
        """Grab existing user.

        Returns:
            User | None: Requested user or None if not found in the database.
        """
        database = get_db()
        response = database.get_item(Key={"userid": user_id})
        if "Item" not in response:
            return None
        item = response["Item"]
        return User(**item)  # pyright: ignore [reportArgumentType]

    @staticmethod
    def create(
        *,
        userid: str,
        name: str,
        email: str,
        profile_pic: str,
        paid: bool = False,
        expires: Optional[str] = None,
        amount: int = 0,
        family_name: Optional[str] = None,
        gender: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> Optional[User]:
        """Create new user.

        Raises:
            ClientError: If there was a ClientError when adding to the database
                that was NOT a ConditionalCheckFailedException.
        """
        user = User(
            userid=userid,
            name=name,
            email=email,
            profile_pic=profile_pic,
            family_name=family_name,
            gender=gender,
            locale=locale,
        )
        database = get_db()
        try:
            database.put_item(
                Item={
                    "userid": userid,
                    "email": email,
                    "name": name,
                    "profile_pic": profile_pic,
                    "paid": paid,
                    "expires": expires,
                    "amount": amount,
                    "family_name": family_name,
                    "gender": gender,
                    "locale": locale,
                },
                ConditionExpression="attribute_not_exists(userid)",
            )
            return user
        except ClientError as e:
            # Ignore the ConditionalCheckFailedException, bubble up
            # other exceptions.
            if check_error_code(e, "ConditionalCheckFailedException"):
                return None
            raise

    @staticmethod
    def update_donation(userid: str, amount: int) -> tuple[bool, dict | str]:
        """Update user."""
        try:
            database = get_db()
            user = database.update_item(
                Key={"userid": userid},
                UpdateExpression="add amount :d set paid = :p",
                ExpressionAttributeValues={":p": True, ":d": amount},
                ReturnValues="ALL_NEW",
                ConditionExpression="attribute_exists(userid)",
            )["Attributes"]
            return True, user
        except ClientError as e:
            # if the item does not exist,
            # we will get a ConditionalCheckFailedException, which we need to handle
            if check_error_code(e, "ConditionalCheckFailedException"):
                return False, f"User with id {userid} does not exist in user database."
            return False, repr(e)
        except Exception as e:  # noqa: BLE001 # pylint: disable=broad-except
            return False, repr(e)

    def get_id(self) -> str:
        """Get user id."""
        return self.userid
