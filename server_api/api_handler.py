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
        self.url = os.getenv("API_URL")
    
    # GET list device
    def _get_devices(self):
        CREATE_DEVICE = urljoin(self.url, 'createDevice')
        response = requests.get(CREATE_DEVICE)
        print(response.json())
    
    # POST new device
    def _create_device(self, deviceInfo):
        CREATE_DEVICE = urljoin(self.url, 'createDevice')
        headers_config = {
            'content-type': 'application/json',
            'Accept':'application/json',
            'connection': 'keep-alive',
            'Expect': '100-continue',
            }
        #format: {"name": "loc_test_6"}
        payload = json.dumps(deviceInfo)
        response = requests.post(CREATE_DEVICE, data=payload, headers=headers_config)
        print(response.text)
