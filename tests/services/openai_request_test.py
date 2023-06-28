import pytest
import responses
import openai
import json
from api_gpt.services.openai_request import (
    get_chat_gpt_response,
    get_gpt3_generation_result,
    get_openai_response_string,
)


@responses.activate
def test_get_chat_gpt_response():
    # Define a mock response
    mock_response = {"choices": [{"message": {"content": "Generated text"}}]}

    # Add a mock response to the responses library
    responses.add(
        responses.POST,
        "https://api.openai.com/v1/chat/completions",
        json=mock_response,
        status=200,
    )

    # Call the function with test parameters
    result = get_chat_gpt_response(max_tokens=10, system="System", content="User")

    # Assert the function returned the correct value
    assert result == mock_response

    # Assert the request was made with the correct parameters
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}",
    }
    expected_data = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 10,
        "messages": [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "User"},
        ],
    }

    request = responses.calls[0].request
    assert request.url == "https://api.openai.com/v1/chat/completions"
    assert request.headers["Authorization"] == expected_headers["Authorization"]
    assert request.headers["Content-Type"] == expected_headers["Content-Type"]
    assert json.loads(request.body) == expected_data


# Then, we test get_gpt3_generation_result
@responses.activate
def test_get_gpt3_generation_result():
    # Define a mock response
    mock_response = {"choices": [{"text": "Generated text"}]}

    # Add a mock response to the responses library
    responses.add(
        responses.POST,
        "https://api.openai.com/v1/completions",
        json=mock_response,
        status=200,
    )

    # Call the function with test parameters
    result = get_gpt3_generation_result(
        model="text-davinci-003",
        max_tokens=10,
        system_prompt="System",
        user_prompt="User",
    )

    # Assert the function returned the correct value
    assert result == mock_response


# Finally, we test get_openai_response_string
@responses.activate
def test_get_openai_response_string():
    # Define a mock response
    mock_chat_gpt_response = {"choices": [{"message": {"content": "Generated text"}}]}
    mock_gpt_3_response = {"choices": [{"text": "Generated text"}]}

    # Add a mock response to the responses library for both endpoints
    responses.add(
        responses.POST,
        "https://api.openai.com/v1/chat/completions",
        json=mock_chat_gpt_response,
        status=200,
    )
    responses.add(
        responses.POST,
        "https://api.openai.com/v1/completions",
        json=mock_gpt_3_response,
        status=200,
    )

    # Call the function with test parameters for a "gpt-3.5-turbo" model
    result = get_openai_response_string(
        model="gpt-3.5-turbo", max_tokens=10, system_prompt="System", user_prompt="User"
    )

    # Assert the function returned the correct value
    assert result == "Generated text"

    # Call the function with test parameters for a different model
    result = get_openai_response_string(
        model="text-davinci-003",
        max_tokens=10,
        system_prompt="System",
        user_prompt="User",
    )

    # Assert the function returned the correct value
    assert result == "Generated text"
