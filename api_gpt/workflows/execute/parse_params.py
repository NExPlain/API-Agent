from typing import List, Optional
from api_gpt.data_structures.proto.generated.intent_data_pb2 import IntentData


def parse_value_from_intent(keys: List[str], intent_data: IntentData) -> Optional[str]:
    """
    Extracts the parameter value from the intent data based on provided keys.

    The function iterates over all the inputs in the given intent data and checks if the name of the input parameter
    matches (or partially matches) any of the provided keys. If it does, the function returns the corresponding
    input parameter value.

    If a key contains spaces, they are replaced with underscores for a matching attempt. If no value is found after
    iterating all inputs and keys, a ValueError is raised.

    Args:
        keys (List[str]): The list of keys used to match against input parameter names.
        intent_data (IntentData): An object representing the intent data, containing inputs each with a parameter
            name and value.

    Returns:
        Optional[str]: The value of the matched parameter if found, None otherwise.

    Raises:
        ValueError: If no matching parameter value is found in the intent data for the provided keys.
    """
    for input in intent_data.inputs:
        input_key = input.parameter.name
        for key in keys:
            if key in input_key:
                return input.parameter.value
            if " " in key and key.replace(" ", "_") in input_key:
                return input.parameter.value
    raise ValueError(f"Parse error, did not get the value for {keys}")
