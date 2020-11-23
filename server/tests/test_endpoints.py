from http import HTTPStatus

MSG_BASE = "/api/sms/"


def test_read_main(client):
    welcome_page = client.get(MSG_BASE + "hello")
    assert welcome_page.status_code == HTTPStatus.OK

    # Create one message
    payload = {"message": "brum"}
    first_message = client.post(MSG_BASE, json=payload)
    assert first_message.status_code == HTTPStatus.CREATED
    assert first_message.json().get("id") == 1

    # Respond to it
    reply = client.post(MSG_BASE + "1", json=payload)
    assert reply.status_code == HTTPStatus.CREATED
    assert reply.json().get("replies_to") == 1

    # Get all messages and check you get both
    all_messages = client.get(MSG_BASE)
    assert all_messages.status_code == HTTPStatus.OK
    assert len(all_messages.json()) == 2

    # Get the original message and check the single reply
    msg_with_replies = client.get(MSG_BASE + "1")
    assert msg_with_replies.status_code == HTTPStatus.OK
    assert len(msg_with_replies.json().get("replies")) == 1


def test_database_gets_clean(client):
    all_messages = client.get(MSG_BASE)
    assert all_messages.status_code == HTTPStatus.OK
    assert not all_messages.json()  # empty list
