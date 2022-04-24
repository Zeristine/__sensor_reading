import os
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv
import json

class APIHandler:
    """
    Instantiate a multiplication operation.
    Numbers will be multiplied by the given multiplier.
    
    :param multiplier: The multiplier.
    :type multiplier: int
    """

    def __init__(self):
        load_dotenv()
        self.urlList = os.getenv("API_LIST_DEVICE")
        self.urlCreate = os.getenv("API_CREATE_DEVICE")
    
    # GET list device
    def _get_devices(self):
        response = requests.get(self.urlList)
        print(response.json())
    
    def _get_request(self):
        response = requests.get(self.urlRequest)
        return response


    # POST new device
    def _create_device(self, deviceInfo):
        headers_config = {
            'content-type': 'application/json',
            'Accept':'application/json',
            'connection': 'keep-alive',
            'Expect': '100-continue',
            }
        #format: {"name": "loc_test_6"}
        payload = json.dumps(deviceInfo)
        response = requests.post(self.urlCreate, data=payload, headers=headers_config)
        print(response.text)
