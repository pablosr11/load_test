from random import random

from locust import HttpUser, between, task


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)


    @task
    def index_page(self):
        self.client.get("/")

    @task
    def view_messages_with_replies(self):
        # generate random number 1-500
        rnd = int(150 * random())
        self.client.get(f"/sms/{rnd}", name="/detail-sms")
    
    @task
    def view_all_messages(self):
        self.client.get("/sms/")

    