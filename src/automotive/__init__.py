#  这里需要写对外的包
from .tools import Singleton, Utils, deprecated
from .tools.battery import IT6831, KonstanterControl, Konstanter
from .tools.camera import Camera, CameraProperty, MicroPhone
from .tools.images import Images
from .tools.mail import ElectronicMail, EmailObject, EmailConfig
from .tools.onoff import OnOff
from .tools.serial_port import SerialPort
from .tools.speaker import Player
from .tools.ssh import SSHUtils
from .tools.usbrelay import USBRelay
from .can import CANService, Parser
from .android import ADBUtils, AppiumPythonClient

__all__ = [
    "Singleton", "Utils", "deprecated",
    "IT6831", "KonstanterControl", "Konstanter",
    "Camera", "CameraProperty", "MicroPhone",
    "Images",
    "ElectronicMail", "EmailObject", "EmailConfig",
    "OnOff",
    "SerialPort",
    "Player",
    "SSHUtils",
    "USBRelay",
    "CANService", "Parser",
    "ADBUtils", "AppiumPythonClient"
]
