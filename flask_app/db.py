"""Grabs and unsets the dynamo db."""
from typing import Optional

import boto3
import click
from botocore.exceptions import ClientError
from flask import Flask, current_app, g
from mypy_boto3_dynamodb.service_resource import Table

from .helpers import check_error_code


def get_db() -> Table:
    """Grab the db.

    Raises:
        ClientError: If there was a dynamodb error that was
            NOT a ResourceInUseException.
    """
    if "db" not in g:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
            region_name=current_app.config["AWS_DEFAULT_REGION"],
        )
        try:
            table: Table = dynamodb.create_table(
                TableName=current_app.config["DATABASE"],
                KeySchema=[{"AttributeName": "userid", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "userid", "AttributeType": "S"}
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            table.wait_until_exists()
        except ClientError as e:
            if check_error_code(e, "ResourceInUseException"):
                # could also delete and recreate it
                # and then recreate it (is faster than deleting all entries one by one)
                table = dynamodb.Table(current_app.config["DATABASE"])
            else:
                raise
        g.db = table
    return g.db


def close_db(_e: Optional[BaseException] = None) -> None:
    """Unset the db."""
    _ = g.pop("db", None)


def init_db() -> None:
    """Initialize the database."""
    _ = get_db()


@click.command("init-db")
def init_db_command() -> None:
    """Grab or create new table.

    Could also be: Clear existing data and create new table if desired.
    """
    init_db()
    click.echo("Initialized the database")


def init_app(app: Flask) -> None:
    """Call when initializing app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
