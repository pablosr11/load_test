from random import choice, random
from string import ascii_lowercase

from locust import HttpUser, between, task


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def write_message(self):
        # generate random string
        payload = "".join([choice(ascii_lowercase) for _ in range(5)])
        self.client.post("/sms/", json={"message": payload})

    @task
    def write_reply(self):
        # generate random number 1-500
        rnd = int(150 * random()) + 1

        # generate random string
        payload = "".join([choice(ascii_lowercase) for _ in range(5)])

        self.client.post(f"/sms/{rnd}", json={"message": payload}, name="/detail-sms")
