import time
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


class CameraController:
    addressControl = "ISAPI/PTZCtrl/channels/1/continuous"
    addressInfo = "ISAPI/PTZCtrl/channels/1/status"
    dataControl = """
    <?xml version="1.0" encoding="UTF-8"?>
        <PTZData>
          <pan>0</pan>
          <tilt>0</tilt>
          <zoom>0</zoom>
        </PTZData>
    """
    def __init__(self, address, login, passw):
        self.address = address
        self.login = login
        self.passw = passw
        self.angleX = 0
        self.angleY = 0
        self.zoom = 1
        self.addressInfo = f"http://{address}/{self.addressInfo}"
        self.addressControl = f"http://{address}/{self.addressControl}"
        self.userInfo = HTTPDigestAuth(login, passw)
        self.update_current_information()

    def update_current_information(self):
        responsePresets = requests.get(self.addressInfo, auth=self.userInfo)
        #responsePresets.
        f = open("current_information.xml", "w")
        f.write(responsePresets.text)
        f.close()
        tree = ET.parse('current_information.xml')
        root = tree.getroot()
        for child in root:
            if (child.tag.__contains__("AbsoluteHigh")):
                for child1 in child:
                    if child1.tag.__contains__("elevation"):
                        self.angleY = int(child1.text) // 10
                        continue
                    if (child1.tag.__contains__("azimuth")):
                        self.angleX = int(child1.text) // 10
                        continue
                    if (child1.tag.__contains__("absoluteZoom")):
                        self.zoom = int(child1.text) // 10
                        continue
        return

    def getCurrentAngleX(self):
        self.update_current_information()
        return self.angleX

    def getCurrentAngleY(self):
        self.update_current_information()
        return self.angleY

    def getCurrentZoom(self):
        self.update_current_information()
        return self.zoom

    def CameraMove(self, xmlWithParametersSpeed):
        response = requests.put(self.addressControl, auth=self.userInfo, data=xmlWithParametersSpeed)
        return response

    def printCurrentInfo(self):
        self.update_current_information()
        print(f"Position:\n angle X = {self.angleX}, angle Y = {self.angleY}, zoom = {self.zoom}")

    def changeZoom(self, deltaZoom, speed=50):
        print(f"start zoom = {self.getCurrentZoom()}")
        resultZoom = self.zoom + deltaZoom
        startZoom = self.zoom
        if deltaZoom + self.zoom >= 32:
            deltaZoom = 32 - self.zoom
        elif deltaZoom + self.zoom <= 0:
            deltaZoom = -self.zoom
        speed = speed if deltaZoom >= 0 else -speed
        xml = self.createXmlWithParametersSpeed(zoom=speed)
        responseMove = self.CameraMove(xml)
        if responseMove == "excep":
            pass # todo
        currentZoom = self.getCurrentZoom()
        if deltaZoom < 0:
            previousZoom = startZoom
            diff = previousZoom - currentZoom
            summTurn = diff
            while (summTurn < abs(deltaZoom) and currentZoom != 1):
                previousZoom = currentZoom
                currentZoom = self.getCurrentZoom()
                diff = previousZoom - currentZoom
                summTurn += diff
                print(f"previous = {previousZoom}, curr = {currentZoom}, diff = {diff}, summ = {summTurn}")
            self.stopCameraMoving()
        elif deltaZoom > 0:
            previousZoom = startZoom
            diff = currentZoom - previousZoom
            summTurn = diff
            while (summTurn < abs(deltaZoom) and currentZoom != 32):
                previousZoom = currentZoom
                currentZoom = self.getCurrentZoom()
                diff = currentZoom - previousZoom
                summTurn += diff
                print(f"previous = {previousZoom}, curr = {currentZoom}, diff = {diff}, summ = {summTurn}")
            self.stopCameraMoving()
        else:
            self.stopCameraMoving()
        print(f"finish zoom = {self.getCurrentZoom()}")


    def rotateAngleX(self, deltaAngle, speed=50):
        print(f"start angle X = {self.angleX}")
        resultAngle = self.calculateAngleX(self.angleX, deltaAngle)
        startAngle = self.angleX
        speed = speed if deltaAngle >= 0 else -speed
        xml = self.createXmlWithParametersSpeed(angleX=speed)
        responseMove = self.CameraMove(xml)
        if responseMove == "excep":
            pass # todo
        currentAngle = self.getCurrentAngleX()
        if deltaAngle < 0:
            previousAngle = startAngle
            diff = previousAngle - currentAngle
            summTurn = diff + 360 if currentAngle > previousAngle else diff
            while (summTurn < abs(deltaAngle)):
                previousAngle = currentAngle
                currentAngle = self.getCurrentAngleX()
                diff = previousAngle - currentAngle
                summTurn += diff + 360 if currentAngle > previousAngle else diff
                #print(f"previous = {previousAngle}, curr = {currentAngle}, diff = {diff}, summ = {summTurn}")
            self.stopCameraMoving()
        elif deltaAngle > 0:
            previousAngle = startAngle
            diff = currentAngle - previousAngle
            summTurn = diff + 360 if currentAngle < previousAngle else diff
            while (summTurn < deltaAngle):
                previousAngle = currentAngle
                currentAngle = self.getCurrentAngleX()
                diff = currentAngle - previousAngle
                summTurn += diff + 360 if currentAngle < previousAngle else diff
                print(f"previous = {previousAngle}, curr = {currentAngle}, diff = {diff}, summ = {summTurn}")
            self.stopCameraMoving()

        else:
            self.stopCameraMoving()
        print(f"finish angle X = {self.getCurrentAngleX()}")

    def rotateAngleY(self, deltaAngle, speed=50):
        deltaAngle = -deltaAngle
        print(f"start angle Y = {self.angleY}")
        startAngle = self.angleY
        speed = speed if deltaAngle >= 0 else -speed
        if -deltaAngle + startAngle > 90:
            deltaAngle = startAngle
        elif -deltaAngle + startAngle < 0:
            deltaAngle = 90 - startAngle
        xml = self.createXmlWithParametersSpeed(angleY=speed)
        print(xml)
        responseMove = self.CameraMove(xml)
        if responseMove == "excep":
            pass # todo
        currentAngle = self.getCurrentAngleY()
        if deltaAngle < 0:
            previousAngle = startAngle
            diff = currentAngle - previousAngle
            summTurn = diff
            while (summTurn < abs(deltaAngle) and currentAngle != 90):
                previousAngle = currentAngle
                currentAngle = self.getCurrentAngleY()
                diff = currentAngle - previousAngle
                summTurn += abs(diff)
                print(f"previous = {previousAngle}, curr = {currentAngle}, diff = {diff}, summ = {summTurn}")
            self.stopCameraMoving()
        elif deltaAngle > 0:
            previousAngle = startAngle
            diff = previousAngle - currentAngle
            summTurn = diff
            while (summTurn < abs(deltaAngle) and currentAngle != 0):
                previousAngle = currentAngle
                currentAngle = self.getCurrentAngleY()
                diff = previousAngle - currentAngle
                summTurn += abs(diff)
                print(f"previous = {previousAngle}, curr = {currentAngle}, diff = {diff}, summ = {summTurn}")
            self.stopCameraMoving()

        else:
            self.stopCameraMoving()
        print(f"finish angle Y = {self.getCurrentAngleY()}")
    def stopCameraMoving(self):
        xml = self.createXmlWithParametersSpeed()
        self.CameraMove(xml)
    def calculateAngleX(self, current, difference):
        return (current + difference) % 360

    def createXmlWithParametersSpeed(self, angleX=0, angleY=0, zoom=0)-> str:
         result = self.dataControl.replace("<pan>0</pan>", f"<pan>{angleX}</pan>")
         result = result.replace("<tilt>0</tilt>", f"<tilt>{angleY}</tilt>")
         result = result.replace("<zoom>0</zoom>", f"<zoom>{zoom}</zoom>")
         return result

    def setDefaultPosition(self):
        self.changeZoom(-32, speed=100)
        self.rotateAngleX(-self.getCurrentAngleX(), speed=100)
        self.rotateAngleY(-self.getCurrentAngleY(), speed=100)
