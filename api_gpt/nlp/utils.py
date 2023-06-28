import json


def extract_first_json(string):
    start_index = string.find('{')
    end_index = start_index + 1
    brace_count = 1
    while brace_count > 0 and end_index < len(string):
        if string[end_index] == '{':
            brace_count += 1
        elif string[end_index] == '}':
            brace_count -= 1
        end_index += 1
    if brace_count != 0:
        raise ValueError('No JSON object found in string.')
    json_str = string[start_index:end_index]
    return json.loads(json_str)