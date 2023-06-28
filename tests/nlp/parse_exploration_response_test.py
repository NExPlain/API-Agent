import unittest
from flask import Flask
from api_gpt.base import create_app, init_firebase_handlers
from api_gpt.nlp.exploration import parse_exploration_response
import os


class TestExecute(unittest.TestCase):
    def setUp(self):
        init_firebase_handlers(testing_environment=True)

    def test_exploration(self):
        SAMPLE_RESPONSE = """
            steps:

            Search for food delivery services in the UK.
            Select a food delivery service, create an order for the food delivery, and get the order ID.
            Retrieve the details of the order with the order ID.
            Track the delivery status of the order.
            api_calls:
            [
            {
            "app_name": "Uber Eats",
            "description": "Search for food delivery services in the UK",
            "endpoint_url": "https://api.uber.com/v1/eats/markets?locale=en-GB",
            "inputs": ["location"],
            "outputs": ["food delivery services"]
            },{
            "app_name": "Uber Eats",
            "description": "Create an order for food delivery",
            "endpoint_url": "https://api.uber.com/v1/eats/orders",
            "inputs": ["restaurant ID", "menu items", "delivery address"],
            "outputs": ["order ID"]
            },{
            "app_name": "Uber Eats",
            "description": "Retrieve the details of the order",
            "endpoint_url": "https://api.uber.com/v1/eats/orders/{order_id}",
            "inputs": ["order ID"],
            "outputs": ["order details"]
            },{
            "app_name": "Uber Eats",
            "description": "Track the delivery status of the order",
            "endpoint_url": "https://api.uber.com/v1/eats/orders/{order_id}/status",
            "inputs": ["order ID"],
            "outputs": ["delivery status"]
            }]
            notes:
            Other food delivery services like Deliveroo, Just Eat, or Grubhub can be used instead of Uber Eats. Additionally, the inputs and outputs for each API call may vary depending on the API specifications.
        """
        response = SAMPLE_RESPONSE
        workflow = parse_exploration_response(response, "Deliver a food in UK")
        self.assertEqual(len(workflow.intent_data), 4)


if __name__ == "__main__":
    unittest.main()
