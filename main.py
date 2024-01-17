import time
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from CameraController import CameraController as CS

ADDRESS = "ipcamera"
LOGIN = "admin"
PASSWORD = "passwds"

if __name__ == '__main__':
    camera = CS(login=LOGIN, passw=PASSWORD, address=ADDRESS)
    camera.update_current_information()
    camera.printCurrentInfo()
    camera.setDefaultPosition()
