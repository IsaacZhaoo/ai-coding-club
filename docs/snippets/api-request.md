---
sidebar_position: 4
title: "API Request Snippets"
description: "Small Python snippets for making API requests, reading JSON, handling errors, and saving responses."
keywords: [API requests, Python, requests, JSON, automation]
---

# API Request Snippets

APIs let your script fetch or send data to another service. These snippets use Python and the requests package.

Install requests if needed:

~~~bash
pip install requests
~~~

## GET JSON

~~~python
import requests

url = "https://api.example.com/items"
response = requests.get(url, timeout=20)
response.raise_for_status()

data = response.json()
print(data)
~~~

## Add Query Parameters

~~~python
import requests

url = "https://api.example.com/search"
params = {"q": "ai coding", "limit": 10}

response = requests.get(url, params=params, timeout=20)
response.raise_for_status()
print(response.json())
~~~

## Add Headers

~~~python
import requests

url = "https://api.example.com/items"
headers = {
    "Authorization": "Bearer YOUR_TOKEN_HERE",
    "Accept": "application/json",
}

response = requests.get(url, headers=headers, timeout=20)
response.raise_for_status()
print(response.json())
~~~

## POST JSON

~~~python
import requests

url = "https://api.example.com/items"
payload = {"name": "Example", "status": "draft"}

response = requests.post(url, json=payload, timeout=20)
response.raise_for_status()
print(response.json())
~~~

## Save Response To A File

~~~python
import json
import requests

response = requests.get("https://api.example.com/items", timeout=20)
response.raise_for_status()

with open("items.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=2)
~~~

## Handle Common Errors

~~~python
import requests

try:
    response = requests.get("https://api.example.com/items", timeout=20)
    response.raise_for_status()
except requests.exceptions.Timeout:
    print("The request timed out.")
except requests.exceptions.HTTPError as exc:
    print("The API returned an error:", exc)
except requests.exceptions.RequestException as exc:
    print("The request failed:", exc)
else:
    print(response.json())
~~~

## Prompt To Adapt A Request

~~~text
Help me write a Python API request.
Endpoint:
Method:
Auth type:
Headers:
Query parameters:
Request body:
Expected response:
Please include error handling and show how to save the result.
~~~
