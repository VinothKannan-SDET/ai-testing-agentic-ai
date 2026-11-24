import json

from dotenv import load_dotenv
import os
import requests

load_dotenv(override=True)
URL = "https://api.openai.com/v1/chat/completions"

def load_env_variable():
    """Read api key & model name from .env file"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise SystemExit("OPENAI_API_KEY is missing. Check your .env file.")

    model = os.getenv("OPENAI_MODEL")
    return openai_api_key, model

def post_chat(body, api_key):
    """Send one request to the chat endpoint and return the raw HTTP response."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    return requests.post(URL, headers=headers, json=body, timeout=30)

def ask(messages, api_key, model):
    """Send a conversation and return only the answer text"""
    body = {"model": model, "temperature": 0, "messages": messages}
    response = post_chat(body, api_key)
    return response.json()["choices"][0]["message"]["content"]

def first_request(api_key, model):
    print("\n--- 1. First request ---")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "In one sentence, what is a smoke test?"}],
    }
    response = post_chat(body, api_key)
    print("Status:", response.status_code)
    print(json.dumps(response.json(), indent=2))

    data = response.json()
    print("\nAnswer:", data["choices"][0]["message"]["content"])
    print("Usage:", data["usage"])
    print("Finish reason:", data["choices"][0]["finish_reason"])

def negative_tests(api_key, model):
    print("\n--- 2. Negative tests ---")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "hello"}]
    }

    wrong_key = post_chat(body, api_key="sk-wrong")
    print("Wrong key :", wrong_key.status_code, wrong_key.json()["error"]["message"])
    bad_model = post_chat({**body, "model": "gpt-does-not-exist"}, api_key)
    print("Bad model :", bad_model.status_code, bad_model.json()["error"]["message"])

def memory_test(api_key, model):
    print("\n--- 3.Memory test ---")
    print("Call 1:", ask(
        [{"role": "user", "content": "My name is Vinoth, Remember it."}],
        api_key, model
    ))

    print("Call 2:", ask(
        [{"role": "user", "content": "What is my name?"}],
        api_key, model))

    history = [
        {"role": "user", "content": "My name is Vinoth. Remember it."},
        {"role": "assistant", "content": "Got it, Vinoth."},
        {"role": "user", "content": "What is my name?"},
    ]
    print("Call 3:", ask(history, api_key, model))


if __name__ == "__main__":
    key, model_name = load_env_variable()
    # first_request(key, model_name)
    # negative_tests(key, model_name)
    memory_test(key, model_name)