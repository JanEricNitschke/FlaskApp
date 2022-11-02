"""Grabs and unsets the dynamo db"""
import boto3
from botocore.exceptions import ClientError

import click
from flask import current_app, g


def get_db():
    """grab the db"""
    if "db" not in g:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        )
        try:
            table = dynamodb.create_table(
                TableName=current_app.config["DATABASE"],
                KeySchema=[{"AttributeName": "userid", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "userid", "AttributeType": "S"}
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            table.wait_until_exists()
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                # could also delete and recreate it
                # table.delete()
                # table.wait_until_not_exists()
                # and then recreate it (is faster than deleting all entries one by one)
                table = dynamodb.Table(current_app.config["DATABASE"])
            else:
                raise
        g.db = table
    return g.db


def close_db(e=None):
    """unset the db"""
    _ = g.pop("db", None)


def init_db():
    """Initialize the database"""
    _ = get_db()


@click.command("init-db")
def init_db_command():
    """Grab or create new table
    Could also be: Clear existing data and create new table if desired"""
    init_db()
    click.echo("Initialized the database")


def init_app(app):
    """Call when initializing app"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
