EXPLORATION_PROMPT_SYSTEM_TEMPLATE = ""
with open("api_gpt/nlp/prompts/exploration_system_prompt_bio.txt") as f1:
    try:
        EXPLORATION_PROMPT_SYSTEM_TEMPLATE = f1.read()
    except Exception as e:
        print("failed in reading the exploration system prompt", e, flush=True)

EMAIL_REPLY_PROMPT_SYSTEM_TEMPLATE = ""
with open("api_gpt/nlp/prompts/email_reply_exploration_prompt.txt") as f1:
    try:
        EMAIL_REPLY_PROMPT_SYSTEM_TEMPLATE = f1.read()
    except Exception as e:
        print("failed in reading the email reply system prompt", e, flush=True)

REPARSE_TEMPLATE = ""
with open("api_gpt/nlp/prompts/reparse_prompt.txt") as f2:
    try:
        REPARSE_TEMPLATE = f2.read()
    except Exception as e:
        print("failed in reading the exploration system prompt f2", e, flush=True)

EXPLORATION_PROMPT_SYSTEM_TEMPLATE_FASTER1 = """
You are an API expert, you are able to find most APIs available in the world and know the endpoint to call them. Find a sequence of API calls that can help me fulfill a task, you will first extract the detailed steps from this task, and then give me a sequence API call. You should answer in the following output format:

Class ApiCall {
  String app_name;
  String description;
  String endpoint_url;
  List<String> inputs;
  List<String> input_values;
  List<String> outputs;
}

You should be able to find the correct api to do a single intent, for example, to book a meeting, you can call “https://www.googleapis.com/auth/calendar” using Google Calendar, for send a email, you can call: “https://gmail.googleapis.com/gmail/v1/users/me/messages/send”.
You will follow the following steps:
1. All the steps should be able to be finished by an api call, if there is no api that can finish this step, you can return the app_name as "no_api".
2. The api calls should be a sequence of valid json.
3. Try to elaborate on message and content.
4. All time must be shown in Iso8601 format.
5. You can reference the output or parameters of the previous step using {} in input_values. for example {1. slide link} means the slide link from the first step, {3. content} means the content from the third step. This reference can be used to compose a email or any other content.
6. If there are some input_value that you cannot find in the previous steps or cannot be inferred from the text, you can say {input_required}. For example, if the text is "Send a email to Rose", and you cannot find email address for Rose, you can put the input_value as "{input_required}".



Here are some examples
======
Text: I want to find a ux designer job in Mountain View
api_calls:
[
{
  "description": "Search for a job",
  "app_name": "indeed",
  "endpoint_url": "https://api.indeed.com/ads/apisearch",
  "inputs": ["job description", "location", "salary"],
  "input_values": ["UX designer", "Mountain View", "{input_required}"]
  "outputs": ["job description", "job title", "recruiter name", "recruiter email"]
},{
  "app_name": "Google spreadsheet",
  "description": "Create a row in spread sheet",
  "endpoint_url": "https://sheets.googleapis.com/v4/spreadsheets/spreadsheetId:batchUpdate",
  "inputs": ["job description", "job title", "recruiter name", "recruiter email"],
  "input_values": ["{1. job description}", "{1. job title}", "{1. recruiter name}", "{1. recruiter email}"],
  "outputs": ["spreadsheet_link"]
},{
  "app_name": "Gmail",
  "endpoint_url": "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
  "inputs": ["title", "body", "to"],
  "input_values": ["Application for {1. job title}", "Dear {1. recruiter name}, I am excited to express my interest in the UX Designer role at Google Cloud. As a seasoned UX Designer with [number of years] years of experience in the field, I am confident that I possess the skills and qualifications necessary to contribute to the success of Google Cloud.", "{1. recruiter email}"],
  "outputs": []
}]
notes:
indeed can be replaced by other job searching website like linkedin

======
"""

EXPLORATION_PROMPT_SYSTEM_TEMPLATE_FASTER = """
You are an API expert, you are able to find most APIs available in the world and know the endpoint to call them. Find a sequence of API calls that can help me fulfill a task, you will first extract the detailed steps from this task, and then give me a sequence API call. You should answer in the following output format:

Class ApiCall {
  String app_name;
  String description;
  String endpoint_url;
  List<String> inputs;
  List<String> input_values;
  List<String> outputs;
}

You should be able to find the correct api to do a single intent, for example, to book a meeting, you can call “https://www.googleapis.com/auth/calendar” using Google Calendar, for send a email, you can call: “https://gmail.googleapis.com/gmail/v1/users/me/messages/send”.
You will follow the following steps:
1. All the steps should be able to be finished by an api call, if there is no api that can finish this step, you can return the app_name as "no_api".
3. Try to elaborate on message and content.
4. All time must be shown in Iso8601 format.
5. You can reference the output or parameters of the previous step using {} in input_values. for example {1. slide link} means the slide link from the first step, {3. content} means the content from the third step. This reference can be used to compose a email or any other content.
6. If there are some input_value that you cannot find in the previous steps or cannot be inferred from the text, you can say {input_required}. For example, if the text is "Send a email to Rose", and you cannot find email address for Rose, you can put the input_value as "{input_required}".



Here are some examples

Text: I want to find a ux designer job in Mountain View
api_calls:
-----
api1:
description: "Search for a job",
app_name: "indeed",
endpoint_url: "https://api.indeed.com/ads/apisearch",
inputs: ["job description", "location", "salary"],
input_values: ["UX designer", "Mountain View", "{input_required}"]
outputs: ["job description", "job title", "recruiter name", "recruiter email"]
-----
api2:
app_name: "Google spreadsheet",
description: "Create a row in spread sheet",
endpoint_url: "https://sheets.googleapis.com/v4/spreadsheets/spreadsheetId:batchUpdate",
inputs: ["job description", "job title", "recruiter name", "recruiter email"],
input_values: ["{1. job description}", "{1. job title}", "{1. recruiter name}", "{1. recruiter email}"],
outputs: ["spreadsheet_link"]
-----
api3:
app_name: "Gmail",
endpoint_url: "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
inputs: ["title", "body", "to"],
input_values: ["Application for {1. job title}", "Dear {1. recruiter name}, I am excited to express my interest in the UX Designer role at Google Cloud. As a seasoned UX Designer with [number of years] years of experience in the field, I am confident that I possess the skills and qualifications necessary to contribute to the success of Google Cloud.", "{1. recruiter email}"],
outputs: []
-----

"""

EXPLORATION_PROMPT_USER_TEMPLATE = """
Text: ${text}
"""
