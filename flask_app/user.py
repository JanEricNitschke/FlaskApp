"""Handles keeping track of the user."""

from __future__ import annotations

from botocore.exceptions import ClientError
from flask_login import UserMixin

from .db import get_db


class User(UserMixin):
    """Class that stores userinformation."""

    def __init__(
        self,
        *,
        id_: str,
        name: str,
        email: str,
        profile_pic: str,
        paid: bool = False,
        expires: str | None = None,
        amount: int = 0,
        family_name: str | None = None,
        gender: str | None = None,
        locale: str | None = None,
    ) -> None:
        """Initialize the User instance.

        Args:
            id_ (str): Unique user ID
            name (str): (First) name of the user
            email (str): User email address
            profile_pic (str): Link to their profile pic
            paid (bool, optional): Whether the user has donated. Defaults to False.
            expires (str | None, optional): When the paid status expires.
                Defaults to None.
            amount (int, optional): Amount paid/donated. Defaults to 0.
            family_name (str | None, optional): Users family name. Defaults to None.
            gender (str | None, optional): Users gender. Defaults to None.
            locale (str | None, optional): Users locale. Defaults to None.
        """
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.paid = paid
        self.expires = expires
        self.amount = amount
        self.family_name = family_name
        self.gender = gender
        self.locale = locale

    @staticmethod
    def get(user_id: str) -> User | None:
        """Grab existing user."""
        db = get_db()
        response = db.get_item(Key={"userid": user_id})
        if "Item" not in response:
            return None
        item = response["Item"]
        return User(
            id_=item["userid"],
            name=item["name"],
            email=item["email"],
            profile_pic=item["profile_pic"],
            paid=item["paid"],
            expires=item["expires"],
            amount=item["amount"],
            family_name=item["family_name"],
            gender=item["gender"],
            locale=item["locale"],
        )

    @staticmethod
    def create(
        *,
        id_: str,
        name: str,
        email: str,
        profile_pic: str,
        paid: bool = False,
        expires: str | None = None,
        amount: int = 0,
        family_name: str | None = None,
        gender: str | None = None,
        locale: str | None = None,
    ) -> User | None:
        """Create new user."""
        user = User(
            id_=id_,
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
                    "userid": id_,
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
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            return None

    @staticmethod
    def update_donation(id_: str, amount: int) -> tuple[bool, dict | str]:
        """Update user."""
        try:
            database = get_db()
            user = database.update_item(
                Key={"userid": id_},
                UpdateExpression="add amount :d set paid = :p",
                ExpressionAttributeValues={":p": True, ":d": amount},
                ReturnValues="ALL_NEW",
                ConditionExpression="attribute_exists(userid)",
            )["Attributes"]
            return True, user
        except ClientError as e:
            # if the item does not exist,
            # we will get a ConditionalCheckFailedException, which we need to handle
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False, f"User with id {id_} does not exist in user database."
            return False, repr(e)
        except Exception as e:  # noqa: BLE001 # pylint: disable=broad-except
            return False, repr(e)
