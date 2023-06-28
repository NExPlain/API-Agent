import unittest

from api_gpt.nlp.parse import convert_json_response_to_workflow
from api_gpt.nlp.generation import parse_response
from google.protobuf.json_format import MessageToJson
import json

JSON_RESPONSE_TEMPLATE = {
    "workflow": "Find a UX designer job in San Jose with a salary higher than 35000 USD",
    "skills": [
        {
            "skill_name": "Search for a job",
            "parameters": [
                {
                    "name": "job description",
                    "value": "UX designer job in San Jose with salary higher than 35000 USD",
                }
            ],
            "returns": [
                {"name": "Job title", "value": ""},
                {"name": "Job description", "value": ""},
                {"name": "Recruiter email", "value": ""},
            ],
            "apis": [],
        },
        {
            "skill_name": "Create spreadsheet",
            "parameters": [{"name": "title", "value": "Job Status Tracker"}],
            "returns": [{"name": "spreadsheet link", "value": ""}],
            "apis": ["Google Sheets API"],
        },
        {
            "skill_name": "Add row to spreadsheet",
            "parameters": [
                {"name": "spreadsheet link", "value": "{2. spreadsheet link}"},
                {
                    "name": "columns",
                    "value": "{1. Job title},{1. Job description},{1. Recruiter email},Not contacted",
                },
            ],
            "returns": [{"name": "spreadsheet row", "value": ""}],
            "apis": ["Google Sheets API"],
        },
        {
            "skill_name": "Send email",
            "parameters": [
                {"name": "title", "value": "New job found: {1. Job title}"},
                {
                    "name": "content",
                    "value": "A new job has been found that matches your criteria:\n\nJob title: {1. Job title}\nJob description: {1. Job description}\nRecruiter email: {1. Recruiter email}\n\nPlease follow up with the recruiter to apply for the job.",
                },
                {"name": "recipient", "value": "youremail@example.com"},
            ],
            "returns": [],
            "apis": ["SMTP API"],
        },
    ],
}

EXPECTED_JSON_RESPONSE = {
    "name": "Find a UX designer job in San Jose with a salary higher than 35000 USD",
    "intentData": [
        {
            "name": "Search for a job",
            "inputs": [
                {
                    "parameter": {
                        "name": "job description",
                        "value": "UX designer job in San Jose with salary higher than 35000 USD",
                    }
                }
            ],
            "outputs": [
                {"parameter": {"name": "Job title"}},
                {"parameter": {"name": "Job description"}},
                {"parameter": {"name": "Recruiter email"}},
            ],
        },
        {
            "name": "Create spreadsheet",
            "inputs": [{"parameter": {"name": "title", "value": "Job Status Tracker"}}],
            "outputs": [{"parameter": {"name": "spreadsheet link"}}],
        },
        {
            "name": "Add row to spreadsheet",
            "inputs": [
                {
                    "parameter": {
                        "name": "spreadsheet link",
                        "value": "{2. spreadsheet link}",
                    }
                },
                {
                    "parameter": {
                        "name": "columns",
                        "value": "{1. Job title},{1. Job description},{1. Recruiter email},Not contacted",
                    }
                },
            ],
            "outputs": [{"parameter": {"name": "spreadsheet row"}}],
        },
        {
            "name": "Send email",
            "inputs": [
                {
                    "parameter": {
                        "name": "title",
                        "value": "New job found: {1. Job title}",
                    }
                },
                {
                    "parameter": {
                        "name": "content",
                        "value": "A new job has been found that matches your criteria:\n\nJob title: {1. Job title}\nJob description: {1. Job description}\nRecruiter email: {1. Recruiter email}\n\nPlease follow up with the recruiter to apply for the job.",
                    }
                },
                {"parameter": {"name": "recipient", "value": "youremail@example.com"}},
            ],
        },
    ],
}


class TestWorkflow(unittest.TestCase):
    def test_convert_json_response_to_workflow(self):
        workflow_data = convert_json_response_to_workflow(JSON_RESPONSE_TEMPLATE)
        self.assertEqual(
            json.loads(MessageToJson(workflow_data)), EXPECTED_JSON_RESPONSE
        )

    def test_parse_response(self):
        parse_success, workflow_data = parse_response(
            "ashd9ashd " + json.dumps(JSON_RESPONSE_TEMPLATE) + "}daso8rgh27893{}"
        )
        self.assertEqual(parse_success, True)
        self.assertEqual(
            json.loads(MessageToJson(workflow_data)), EXPECTED_JSON_RESPONSE
        )


if __name__ == "__main__":
    unittest.main()
