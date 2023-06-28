import unittest
from api_gpt.base import init_firebase_handlers
from api_gpt.nlp.exploration import parse_response_bruteforce

SAMPLE_RESPONSE = """
There are a few ways to interpret this task, so I will provide two possible sequences of API calls:

Option 1: If the user already has a kanban board set up on Asana and wants to view it:
1. Get the user's Asana user ID.
2. Get a list of the user's workspaces.
3. Get a list of projects in the user's workspaces.
4. Find the kanban board project in the list of projects.
5. Get a list of tasks in the kanban board project.
6. Return the list of tasks to the user.

api_calls:
----
[
{
  "description": "Get user ID",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/users/me",
  "inputs": [],
  "input_values": [],
  "outputs": ["user ID"]
},
{
  "description": "Get user's workspaces",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/workspaces",
  "inputs": ["user ID"],
  "input_values": ["{1. user ID}"],
  "outputs": ["list of workspaces"]
},
{
  "description": "Get projects in workspace",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/workspaces/{workspace ID}/projects",
  "inputs": ["workspace ID"],
  "input_values": ["{1. list of workspaces[0].id}"],
  "outputs": ["list of projects"]
},
{
  "description": "Find kanban board project",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/projects/{project ID}/tasks",
  "inputs": ["project ID"],
  "input_values": ["{3. list of projects.find(project => project.name === 'Kanban Board').id}"],
  "outputs": ["list of tasks"]
}
]
----

Option 2: If the user wants to create a new kanban board on Asana and view it:
1. Create a new project in Asana with the name "Kanban Board".
2. Create a new section in the kanban board project with the name "To Do".
3. Create a new section in the kanban board project with the name "In Progress".
4. Create a new section in the kanban board project with the name "Done".
5. Return the kanban board project to the user.

api_calls:
----
[
{
  "description": "Create new project",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/projects",
  "inputs": ["project name"],
  "input_values": ["Kanban Board"],
  "outputs": ["project ID"]
},
{
  "description": "Create 'To Do' section",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/sections",
  "inputs": ["project ID", "section name"],
  "input_values": ["{1. project ID}", "To Do"],
  "outputs": ["section ID"]
},
{
  "description": "Create 'In Progress' section",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/sections",
  "inputs": ["project ID", "section name"],
  "input_values": ["{1. project ID}", "In Progress"],
  "outputs": ["section ID"]
},
{
  "description": "Create 'Done' section",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/sections",
  "inputs": ["project ID", "section name"],
  "input_values": ["{1. project ID}", "Done"],
  "outputs": ["section ID"]
},
{
  "description": "Get kanban board project",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/projects/{project ID}/tasks",
  "inputs": ["project ID"],
  "input_values": ["{1. project ID}"],
  "outputs": ["kanban board project"]
}
]
----
##################################################
trying parse 2 for :  There are a few ways to interpret this task, so I will provide two possible sequences of API calls:

Option 1: If the user already has a kanban board set up on Asana and wants to view it:
1. Get the user's Asana user ID.
2. Get a list of the user's workspaces.
3. Get a list of projects in the user's workspaces.
4. Find the kanban board project in the list of projects.
5. Get a list of tasks in the kanban board project.
6. Return the list of tasks to the user.

api_calls:
----
[
{
  "description": "Get user ID",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/users/me",
  "inputs": [],
  "input_values": [],
  "outputs": ["user ID"]
},
{
  "description": "Get user's workspaces",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/workspaces",
  "inputs": ["user ID"],
  "input_values": ["{1. user ID}"],
  "outputs": ["list of workspaces"]
},
{
  "description": "Get projects in workspace",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/workspaces/{workspace ID}/projects",
  "inputs": ["workspace ID"],
  "input_values": ["{1. list of workspaces[0].id}"],
  "outputs": ["list of projects"]
},
{
  "description": "Find kanban board project",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/projects/{project ID}/tasks",
  "inputs": ["project ID"],
  "input_values": ["{3. list of projects.find(project => project.name === 'Kanban Board').id}"],
  "outputs": ["list of tasks"]
}
]
----

Option 2: If the user wants to create a new kanban board on Asana and view it:
1. Create a new project in Asana with the name "Kanban Board".
2. Create a new section in the kanban board project with the name "To Do".
3. Create a new section in the kanban board project with the name "In Progress".
4. Create a new section in the kanban board project with the name "Done".
5. Return the kanban board project to the user.

api_calls:
----
[
{
  "description": "Create new project",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/projects",
  "inputs": ["project name"],
  "input_values": ["Kanban Board"],
  "outputs": ["project ID"]
},
{
  "description": "Create 'To Do' section",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/sections",
  "inputs": ["project ID", "section name"],
  "input_values": ["{1. project ID}", "To Do"],
  "outputs": ["section ID"]
},
{
  "description": "Create 'In Progress' section",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/sections",
  "inputs": ["project ID", "section name"],
  "input_values": ["{1. project ID}", "In Progress"],
  "outputs": ["section ID"]
},
{
  "description": "Create 'Done' section",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/sections",
  "inputs": ["project ID", "section name"],
  "input_values": ["{1. project ID}", "Done"],
  "outputs": ["section ID"]
},
{
  "description": "Get kanban board project",
  "app_name": "Asana",
  "endpoint_url": "https://app.asana.com/api/1.0/projects/{project ID}/tasks",
  "inputs": ["project ID"],
  "input_values": ["{1. project ID}"],
  "outputs": ["kanban board project"]
}
]
----
##################################################
"""

SAMPLE_RESPONSE_2 = """
'Here are the API calls to fulfill the task:\n\n----\n[\n{\n  "description": "Create a new Google Slides presentation",\n  "app_name": "Google Slides",\n  "endpoint_url": "https://slides.googleapis.com/v1/presentations",\n  "inputs": ["title"],\n  "input_values": ["Executable Doc using AI"],\n  "outputs": ["presentation_id"]\n},\n{\n  "description": "Add a slide to the presentation",\n  "app_name": "Google Slides",\n  "endpoint_url": "https://slides.googleapis.com/v1/presentations/{1. presentation_id}/pages",\n  "inputs": ["presentation_id"],\n  "input_values": ["{1. presentation_id}"],\n  "outputs": ["slide_id"]\n},\n{\n  "description": "Insert an image to the slide",\n  "app_name": "Google Slides",\n  "endpoint_url": "https://slides.googleapis.com/v1/presentations/{1. presentation_id}/pages/{2. slide_id}/elements",\n  "inputs": ["presentation_id", "slide_id", "image_url", "width", "height", "x_pos", "y_pos"],\n  "input_values": ["{1. presentation_id}", "{2. slide_id}", "{input_required}", "600", "400", "100", "100"],\n  "outputs": ["image_id"]\n},\n{\n  "description": "Insert a text box to the slide",\n  "app_name": "Google Slides",\n  "endpoint_url": "https://slides.googleapis.com/v1/presentations/{1. presentation_id}/pages/{2. slide_id}/elements",\n  "inputs": ["presentation_id", "slide_id", "text", "font_size", "x_pos", "y_pos"],\n  "input_values": ["{1. presentation_id}", "{2. slide_id}", "Executable Doc using AI", "48", "700", "100"],\n  "outputs": ["text_box_id"]\n},\n{\n  "description": "Share the presentation with Rose",\n  "app_name": "Google Drive",\n  "endpoint_url": "https://www.googleapis.com/drive/v3/files/{1. presentation_id}/permissions",\n  "inputs": ["presentation_id", "email_address"],\n  "input_values": ["{1. presentation_id}", "rose@example.com"],\n  "outputs": []\n},\n{\n  "description": "Send an email to Rose with the link to the presentation",\n  "app_name": "Gmail",\n  "endpoint_url": "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",\n  "inputs": ["to", "subject", "body"],\n  "input_values": ["rose@example.com", "Executable Doc using AI", "Dear Rose,\\n\\nPlease find attached the slide to promote the idea of executable doc using AI.\\n\\nLink: https://docs.google.com/presentation/d/{1. presentation_id}\\n\\nBest regards,\\nYour Name",],\n  "outputs": []\n}\n]\n----\n\nNote: You need to replace {input_required} with the URL of the image you want to insert into the slide.'
"""


class TestExecute(unittest.TestCase):
    def setUp(self):
        init_firebase_handlers(testing_environment=True)

    def test_parse(self):
        workflow = parse_response_bruteforce(SAMPLE_RESPONSE, "text")
        self.assertNotEqual(workflow, None)
        self.assertTrue(len(workflow.intent_data) > 0)

    def test_parse2(self):
        workflow = parse_response_bruteforce(SAMPLE_RESPONSE_2, "text")
        self.assertNotEqual(workflow, None)
        self.assertTrue(len(workflow.intent_data) > 0)


if __name__ == "__main__":
    unittest.main()
