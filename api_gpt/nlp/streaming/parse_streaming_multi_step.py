import json
from api_gpt.nlp.exploration import api_call_json_to_intent, fix_extracted_str
from api_gpt.data_structures.proto.generated.workflow_pb2 import WorkflowData


def parse_single_api_call(api_call_text: str) -> map:
    ret = {}
    for line in api_call_text.split("\n"):
        if ":" not in line:
            continue
        index = line.find(":")
        key, value = line[:index], line[index + 2 :]
        value = value.strip()
        value = value.strip('"')
        key = key.strip()
        key = key.strip('"')
        if value[0] == "[":
            try:
                value = fix_extracted_str(value)
                value = json.loads(value)
                ret[key] = value
            except Exception as exception:
                print("Error in [] json parsing : ", exception, flush=True)
        else:
            ret[key] = value
    return ret


def parse_api_calls_openai(api_calls, separator="----"):
    api_calls_list = []
    api_calls_str = api_calls.split(separator)[1:]
    for api_call_str in api_calls_str:
        api_call_map = {}
        api_call_lines = api_call_str.strip().split("\n")
        for line in api_call_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                value = fix_extracted_str(value)
                key = fix_extracted_str(key)
                if value[0] == "[":
                    try:
                        api_call_map[key.strip()] = json.loads(value.strip())
                    except Exception as exception:
                        print("Error in [] json parsing : ", exception, flush=True)
                else:
                    api_call_map[key.strip()] = value.strip()

        api_calls_list.append(api_call_map)
    return api_calls_list


def parse_api_call_jsons(response: str, text: str) -> WorkflowData:
    try:
        apis = []
        api_calls = response
        spliters = ["Api Call", "ApiCall", "apicall", "Api call", "Apicall"]
        spliter = spliters[1]
        for _spliter in spliters:
            if _spliter in api_calls:
                spliter = _spliter
        if len(api_calls.strip()) == 0:
            return []
        for api_call in api_calls.split(spliter):
            try:
                api_call = api_call.strip()
                index = 0
                if "app_name" not in api_call.lower():
                    continue
                while index < len(api_call) and api_call[index].isdigit():
                    index += 1
                    continue
                if index >= len(api_call):
                    continue
                api_call = api_call[index:]
                api_call = api_call.strip(" ")
                api_call = api_call.strip("\n")
                api_call = api_call.strip(" ")
                api_call = api_call.strip(":")
                api_call = api_call.strip(" ")
                api_call = api_call.strip("\n")
                end_signs = ["---", "===", "```"]
                for end_sign in end_signs:
                    if end_sign in api_call:
                        index = api_call.find(end_sign)
                        api_call = api_call[:index]
                try:
                    ret = parse_single_api_call(api_call)
                    if "app_name" in ret and ret["app_name"]:
                        apis.append(ret)
                except Exception as exception:
                    print("Error in parsing : ", exception, flush=True)
            except Exception as exception:
                print("Error in parse single api : ", exception, flush=True)
    except Exception as exception:
        return []
    return apis


def parse_workflow_from_multistep_response(response: str, text: str) -> WorkflowData:
    apis = parse_api_call_jsons(response, text)

    workflow_data = WorkflowData()
    workflow_data.name = text
    for api in apis:
        try:
            intent = api_call_json_to_intent(api)
            if not intent.app_name:
                continue
            workflow_data.intent_data.append(intent)
        except Exception as exception:
            print("Error in parsing api json to intent", api, flush=True)
    return workflow_data
