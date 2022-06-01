import os
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv
import json


load_dotenv()
URL_LIST = os.getenv("API_LIST_DEVICE")
URL_CREATE = os.getenv("API_CREATE_DEVICE")
URL_REQUEST = os.getenv("API_REQUESTS")

# GET list device


def get_devices():
    response = requests.get(URL_LIST)
    print(response.json())


def get_request():
    response = requests.get(URL_REQUEST)
    return response.json()


# POST new device
def create_device(deviceInfo):
    headers_config = {
        'content-type': 'application/json',
        'Accept': 'application/json',
        'connection': 'keep-alive',
        'Expect': '100-continue',
    }
    #format: {"name": "loc_test_6"}
    payload = json.dumps(deviceInfo)
    response = requests.post(
        URL_CREATE, data=payload, headers=headers_config)
    print(response.text)
