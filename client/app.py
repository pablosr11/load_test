import click
import requests

BASE = "http://0.0.0.0:8000"
SMS = BASE + "/sms/"
HEADERS = {"Content-type": "application/json"}


@click.group()
def cli():
    pass


# get all requests | GET http://0.0.0.0:8000/sms/
@cli.command()
def get_messages():
    response = requests.get(SMS)
    print(response.status_code, response.json())


# get all replies for 1 request
@cli.command()
@click.argument("sms_id")
def get_replies(sms_id: int):
    REPLY_URL = SMS + str(sms_id)
    response = requests.get(REPLY_URL)
    print(response.status_code, response.json())


# create a request
@cli.command()
@click.argument("text")
def send_message(text: str):
    payload = {"message": text}
    response = requests.post(SMS, json=payload)
    print(response.status_code, response.json())


# create a reply to a request
@cli.command()
@click.argument("text")
@click.argument("sms_id")
def send_reply(text: str, sms_id: int):
    REPLY_URL = SMS + str(sms_id)
    payload = {"message": text}
    response = requests.post(REPLY_URL, json=payload)
    print(response.status_code, response.json())


# homesite
@cli.command()
def get_homesite():
    response = requests.get(BASE)
    print(response.status_code, response.json())


if __name__ == "__main__":
    print("hello")
    cli()
