from typing import Tuple
from api_gpt.data_structures.proto.generated.workflow_template_pb2 import (
    WorkflowTemplate,
)
from api_gpt.settings.debug import global_debug_flag
from api_gpt.workflows.db.workflow_template import get_workflow_template_handler

USER_PROMPT_TEMPLATE_2STEPS_IDENTIFY = """
Input: {text}
Output: 
"""

SYSTEM_PROMPT_TEMPLATE_2STEPS_IDENTIFY = """
You are a task classifier, current time is {current_time}
your task is to identify the intent for a piece of text, intent means the things this piece of text is trying to accomplish. You have to answer with one of the following text:
{workflow_names_list}.

Here are some examples:
{example_str}
"""

EXAMPLE_TEMPLATE_2STEPS_IDENTIFY = """Input: {input}
Output: {output}
"""

SYSTEM_PROMPT_TEMPLATE_2STEPS_FILL_PARAMETER = """
Your task is to extract the important entities mentioned in a text, you will {extract_parameters}.


You will follow the following rules: 
1. All time must be be shown in Iso8601 format.
2. Current time is {current_time}, all the time must be relative to the current time.
Desired format:
{desired_format}

Here are some examples:
{examples_str}
"""

USER_PROMPT_TEMPLATE_2STEPS_FILL_PARAMETER = """
text: {text}, current_time is {current_time}.
"""


def build_identify_prompt_2_steps(current_time: str, text: str) -> Tuple[str, str]:
    workflow_names = []
    example_strs = []
    i = 0
    workflow_templates_handler = get_workflow_template_handler()
    for type, _ in sorted(workflow_templates_handler.workflow_templates.items()):
        workflow_template = workflow_templates_handler.get_workflow_template(type)
        name = workflow_template.type
        prompt_name = f"{i}. {workflow_template.name}"
        workflow_names.append(prompt_name)
        for example in workflow_template.examples:
            example_str = EXAMPLE_TEMPLATE_2STEPS_IDENTIFY.format(
                input=example.trigger_string, output=prompt_name
            )
            example_strs.append(example_str)
        i += 1
    system_prompt = SYSTEM_PROMPT_TEMPLATE_2STEPS_IDENTIFY.format(
        current_time=current_time,
        workflow_names_list=",".join(workflow_names),
        example_str="\n".join(example_strs),
    )
    user_prompt = USER_PROMPT_TEMPLATE_2STEPS_IDENTIFY.format(text=text)
    if global_debug_flag:
        print(f"2 steps identify system: {system_prompt}", flush=True)
        print(f"2 steps identify user: {user_prompt}", flush=True)
    return system_prompt, user_prompt


def build_parameter_prompt_2_steps(
    current_time: str, text: str, workflow_template: WorkflowTemplate
) -> Tuple[str, str]:
    extract_parameters_str = ""
    parameter_id = 0
    for i in range(len(workflow_template.intents)):
        intent = workflow_template.intents[i]
        for input in intent.inputs:
            if parameter_id == 0:
                extract_parameters_str += f"first extract {i}.{input.parameter.name}"
            else:
                extract_parameters_str += f", then extract {i}.{input.parameter.name}"

        parameter_id += 1
    desired_format_str = ""

    for i in range(len(workflow_template.intents)):
        intent = workflow_template.intents[i]
        for input in intent.inputs:
            if parameter_id == 0:
                desired_format_str += (
                    f"{i}.{input.parameter.name}: {input.parameter.value}\n"
                )
            else:
                desired_format_str += (
                    f"{i}.{input.parameter.name}: {input.parameter.value}\n"
                )

    examples_str = ""
    for example in workflow_template.examples:
        examples_str += "text: "
        workflow_data = example.workflow
        for i in range(len(workflow_data.intent_data)):
            intent = workflow_data.intent_data[i]
            for input in intent.inputs:
                examples_str += f"{i}.{input.parameter.name}: {input.parameter.value}\n"
        examples_str += "\n" * 3

    system_prompt = SYSTEM_PROMPT_TEMPLATE_2STEPS_FILL_PARAMETER.format(
        current_time=current_time,
        extract_parameters=extract_parameters_str,
        desired_format=desired_format_str,
        examples_str=examples_str,
    )
    user_prompt = USER_PROMPT_TEMPLATE_2STEPS_FILL_PARAMETER.format(
        current_time=current_time, text=text
    )
    return system_prompt, user_prompt
