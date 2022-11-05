"""Handles keeping track of the user"""

from flask_login import UserMixin
from botocore.exceptions import ClientError
from .db import get_db


class User(UserMixin):
    """Class that stores userinformation"""

    def __init__(
        self,
        id_,
        name,
        email,
        profile_pic,
        paid=False,
        expires=None,
        amount=0,
        family_name=None,
        gender=None,
        locale=None,
    ):
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
    def get(user_id):
        """Grab existing user"""
        db = get_db()
        response = db.get_item(Key={"userid": user_id})
        if "Item" not in response:
            return None
        item = response["Item"]
        user = User(
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
        return user

    @staticmethod
    def create(
        id_,
        name,
        email,
        profile_pic,
        paid=False,
        expires=None,
        amount=0,
        family_name=None,
        gender=None,
        locale=None,
    ):
        """Create new user"""
        db = get_db()
        try:
            db.put_item(
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
        except ClientError as e:
            # Ignore the ConditionalCheckFailedException, bubble up
            # other exceptions.
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            error = f"User {name} with email {email} is already registered."

    @staticmethod
    def updateDonation(id_, amount):
        """Update user"""
        try:
            db = get_db()
            user = db.update_item(
                Key={"userid": id_},
                UpdateExpression="add amount :d set paid = :p",
                ExpressionAttributeValues={":p": True, ":d": amount},
                ReturnValues="ALL_NEW",
            )["Attributes"]
            return True, user
        except Exception as e:
            return False, e
