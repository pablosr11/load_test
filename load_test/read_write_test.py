from random import choice, random
from string import ascii_lowercase

from locust import HttpUser, between, task


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def index_page(self):
        self.client.get("/")

    @task
    def view_messages_with_replies(self):
        # generate random number 1-500
        rnd = int(500 * random()) + 1
        self.client.get(f"/sms/{rnd}", name="/detail-sms")

    @task
    def view_all_messages(self):
        self.client.get("/sms/")

    @task
    def view_all_messages_limited_10(self):
        self.client.get("/sms/?limit=10")

    @task
    def view_all_messages_limited_500(self):
        self.client.get("/sms/?limit=500")

    @task
    def write_message(self):
        # generate random string
        payload = "".join([choice(ascii_lowercase) for _ in range(8)])
        self.client.post("/sms/", json={"message": payload})

    @task
    def write_reply(self):
        # generate random number 1-500
        rnd = int(500 * random()) + 1

        # generate random string
        payload = "".join([choice(ascii_lowercase) for _ in range(5)])

        self.client.post(f"/sms/{rnd}", json={"message": payload}, name="/detail-sms")
