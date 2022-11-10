# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        tsmasterbasic.py
# @Author:      lizhe
# @Created:     2021/10/28 - 21:06
# --------------------------------------------------------
from ctypes import c_int, c_uint8, c_int32, c_uint64, Structure, c_ubyte, c_ulonglong

TRUE = c_int(1)
FALSE = c_int(0)

APP_CHANNEL = {
    1: c_int(0),
    2: c_int(1),
    3: c_int(2),
    4: c_int(3)
}

# TLIBCANFDControllerType
TLIBCANFDControllerType = {
    "CAN": c_int(0),
    "ISOCAN": c_int(1),
    "NonISOCAN": c_int(2)
}

TLIBCANFDControllerMode = {
    "Normal": c_int(0),  # 正常工作模式(lfdmNormal = 0),
    "ACKOff": c_int(1),  # 关闭ACK模式(lfdmACKOff = 1)
    "Restricted": c_int(2)  # 受限制模式(lfdmRestricted = 2)
}


# typedef union {
# 	u8 value;
# 	struct {
# 		u8 istx : 1;
# 		u8 remoteframe : 1;
# 		u8 extframe : 1;
# 		u8 tbd : 4;
# 		u8 iserrorframe : 1;
# 	}bits;
# }TCANProperty;

# typedef struct _TLibCAN {
# 	u8 FIdxChn;           // channel index starting from 0
# 	TCANProperty FProperties;       // default 0, masked status:
# 						  // [7] 0-normal frame, 1-error frame
# 						  // [6-3] tbd
# 						  // [2] 0-std frame, 1-extended frame
# 						  // [1] 0-data frame, 1-remote frame
# 						  // [0] dir: 0-RX, 1-TX
# 	u8 FDLC;              // dlc from 0 to 8
# 	u8 FReserved;         // reserved to keep alignment
# 	s32 FIdentifier;      // CAN identifier
# 	u64 FTimeUS;          // timestamp in us  //Modified by Eric 0321
# 	u8x8 FData;           // 8 data bytes to send
# } TLibCAN,*PLibCAN;

class TLibCAN(Structure):
    _pack_ = 1
    _fields_ = [
        ("FIdxChn", c_uint8),
        ("FProperties", c_uint8),
        ("FDLC", c_uint8),
        ("FReserved", c_uint8),
        ("FIdentifier", c_int32),
        ("FTimeUS", c_uint64),
        ("FData", c_uint8 * 8)
    ]


# typedef union {
# 	u8 value;
# 	struct {
# 		u8 EDL : 1;
# 		u8 BRS : 1;
# 		u8 ESI : 1;
# 		u8 tbd : 5;
# 	}bits;
# }TCANFDProperty;
# // CAN FD frame definition = 80 B
#   // CAN FD frame definition = 80 B
# typedef struct _TLibCANFD {
# 	u8 FIdxChn;           // channel index starting from 0        = CAN
# 	TCANProperty FProperties;       // default 0, masked status:            = CAN
# 						   // [7] 0-normal frame, 1-error frame
# 						   // [6] 0-not logged, 1-already logged
# 						   // [5-3] tbd
# 						   // [2] 0-std frame, 1-extended frame
# 						   // [1] 0-data frame, 1-remote frame
# 						   // [0] dir: 0-RX, 1-TX
# 	u8 FDLC;              // dlc from 0 to 15                     = CAN
# 	TCANFDProperty FFDProperties;      // [7-3] tbd                            <> CAN
# 						   // [2] ESI, The E RROR S TATE I NDICATOR (ESI) flag is transmitted dominant by error active nodes, recessive by error passive nodes. ESI does not exist in CAN format frames
# 						   // [1] BRS, If the bit is transmitted recessive, the bit rate is switched from the standard bit rate of the A RBITRATION P HASE to the preconfigured alternate bit rate of the D ATA P HASE . If it is transmitted dominant, the bit rate is not switched. BRS does not exist in CAN format frames.
# 						   // [0] EDL: 0-normal CAN frame, 1-FD frame, added 2020-02-12, The E XTENDED D ATA L ENGTH (EDL) bit is recessive. It only exists in CAN FD format frames
# 	s32  FIdentifier;      // CAN identifier                       = CAN
# 	u64 FTimeUS;          // timestamp in us                      = CAN
#     u8x64 FData;          // 64 data bytes to send                <> CAN
# }TLibCANFD, * PLibCANFD;

class TLibCANFD(Structure):
    _pack_ = 1
    _fields_ = [
        ("FIdxChn", c_ubyte),
        ("FProperties", c_ubyte),
        ("FDLC", c_ubyte),
        ("FFDProperties", c_ubyte),  # 0:普通can数据帧 1：canfd数据帧
        ("FIdentifier", c_int),
        ("FTimeUS", c_ulonglong),
        ("FData", c_ubyte * 64)
    ]


# typedef union
# {
# 	u8 value;
# 	struct {
# 		u8 istx : 1;
# 		u8 breaksended : 1;
# 		u8 breakreceived : 1;
# 		u8 syncreceived : 1;
# 		u8 hwtype : 2;
# 		u8 isLogged : 1;
# 		u8 iserrorframe : 1;
# 	}bits;
# }TLINProperty;
# typedef struct _TLIN {
# 	u8 FIdxChn;           // channel index starting from 0
# 	u8 FErrCode;          //  0: normal
# 	TLINProperty FProperties;       // default 0, masked status:
# 						   // [7] tbd
# 						   // [6] 0-not logged, 1-already logged
# 						   // [5-4] FHWType //DEV_MASTER,DEV_SLAVE,DEV_LISTENER
# 						   // [3] 0-not ReceivedSync, 1- ReceivedSync
# 						   // [2] 0-not received FReceiveBreak, 1-Received Break
# 						   // [1] 0-not send FReceiveBreak, 1-send Break
# 						   // [0] dir: 0-RX, 1-TX
# 	u8 FDLC;              // dlc from 0 to 8
# 	u8 FIdentifier;       // LIN identifier:0--64
# 	u8 FChecksum;         // LIN checksum
# 	u8 FStatus;           // place holder 1
# 	u64 FTimeUS;          // timestamp in us  //Modified by Eric 0321
# 	u8x8 FData;           // 8 data bytes to send
# }TLibLIN, *PLibLIN;

class TLibLIN(Structure):
    _pack_ = 1
    _fields_ = [
        ("FIdxChn", c_ubyte),
        ("FErrCode", c_ubyte),
        ("FProperties", c_ubyte),
        ("FDLC", c_uint8),
        ("FIdentifier", c_ubyte),
        ("FChecksum", c_ubyte),
        ("FStatus", c_ubyte),
        ("FTimeUS", c_ulonglong),
        ("FData", c_uint8 * 8)
    ]


error_code = {
    0: "success",
    1: "Index out of range",
    2: "Connect failed",
    3: "Device not found",
    4: "Error code not valid",
    5: "HID device already connected",
    6: "HID write data failed",
    7: "HID read data failed",
    8: "HID TX buffer overrun",
    9: "HID TX buffer too large",
    10: "HID RX packet report ID invalid",
    11: "HID RX packet length invalid",
    12: "Internal test failed",
    13: "RX packet lost",
    14: "SetupDiGetDeviceInterfaceDetai",
    15: "Create file failed",
    16: "CreateFile failed for read handle",
    17: "CreateFile failed for write handle",
    18: "HidD_SetNumInputBuffers",
    19: "HidD_GetPreparsedData",
    20: "HidP_GetCaps",
    21: "WriteFile",
    22: "GetOverlappedResult",
    23: "HidD_SetFeature",
    24: "HidD_GetFeature",
    25: "Send Feature Report DeviceIoContro",
    26: "Send Feature Report GetOverLappedResult",
    27: "HidD_GetManufacturerString",
    28: "HidD_GetProductString",
    29: "HidD_GetSerialNumberString",
    30: "HidD_GetIndexedString",
    31: "Transmit timed out",
    32: "HW DFU flash write failed",
    33: "HW DFU write without erase",
    34: "HW DFU crc check error",
    35: "HW DFU reset before crc check success",
    36: "HW packet identifier invalid",
    37: "HW packet length invalid",
    38: "HW internal test failed",
    39: "HW rx from pc packet lost",
    40: "HW tx to pc buffer overrun",
    41: "HW API parameter invalid",
    42: "DFU file load failed",
    43: "DFU header write failed",
    44: "Read status timed out",
    45: "Callback already exists",
    46: "Callback not exists",
    47: "File corrupted or not recognized",
    48: "Database unique id not found",
    49: "Software API parameter invalid",
    50: "Software API generic timed out",
    51: "Software API set hw config. failed",
    52: "Index out of bounds",
    53: "RX wait timed out",
    54: "Get I/O failed",
    55: "Set I/O failed",
    56: "An active replay is already running",
    57: "Instance not exists",
    58: "CAN message transmit failed",
    59: "No response from hardware",
    60: "CAN message not found",
    61: "User CAN receive buffer empty",
    62: "CAN total receive count <> desired count",
    63: "LIN config failed",
    64: "LIN frame number out of range",
    65: "LDF config failed",
    66: "LDF config cmd error",
    67: "TSMaster envrionment not ready",
    68: "reserved failed",
    69: "XL driver error",
    70: "index out of range",
    71: "string length out of range",
    72: "key is not initialized",
    73: "key is wrong",
    74: "write not permitted",
    75: "16 bytes multiple",
    76: "LIN channel out of range",
    77: "DLL not ready",
    78: "Feature not supported",
    79: "common service error",
    80: "read parameter overflow",
    81: "Invalid application channel mapping",
    82: "libTSMaster generic operation failed",
    83: "item already exists",
    84: "item not found",
    85: "logical channel invalid",
    86: "file not exists",
    87: "no init access, cannot set baudrate",
    88: "the channel is inactive",
    89: "the channel is not created",
    90: "length of the appname is out of range",
    91: "project is modified",
    92: "signal not found in database",
    93: "message not found in database",
    94: "TSMaster is not installed",
    95: "Library load failed",
    96: "Library function not found",
    97: 'cannot find libTSMaster.dll, use \"set_libtsmaster_location\" to set its location before calling initialize_lib_tsmaster',
    98: "PCAN generic operation error",
    99: "Kvaser generic operation error",
    100: "ZLG generic operation error",
    101: "ICS generic operation error",
    102: "TC1005 generic operation error",
    104: "Incorrect system variable type",
    105: "Message not existing, update failed",
    106: "Specified baudrate not available",
    107: "Device does not support sync. transmit",
    108: "Wait time not satisfied",
    109: "Cannot operate while app is connected",
    110: "Create file failed",
    111: "Execute python failed",
    112: "Current multiplexed signal is not active",
    113: "Get handle by logic channel failed",
    114: "Cannot operate while application is Connected, please stop application first",
    115: "File load failed",
    116: "Read LIN Data Failed",
    117: "FIFO not enabled",
    118: "Invalid handle",
    119: "Read file error",
    120: "Read to EOF",
    121: "Configuration not saved",
    122: "IP port open failed",
    123: "TCP connect failed",
    124: "Directory not exists",
    125: "Current library not supported",
    126: "Test is not running",
    127: "Server response not received",
    128: "Create directory failed",
    129: "Invalid argument type",
    130: "Read Data Package from Device Failed",
    131: "Precise replay is running",
    132: "Replay map is already",
    133: "User cancel input",
    134: "API check result is negative",
    135: "CANable generic error",
    136: "Wait criteria not satisfied",
    137: "Operation requires application connected",
    138: "Project path is used by another application",
    139: "Timeout for the sender to transmit data to the receiver",
    140: "Timeout for the receiver to transmit flow control to the sender",
    141: "Timeout for the sender to send first data frame after receiving FC frame",
    142: "Timeout for the receiver to receiving first CF frame after sending FC frame",
    143: "Serial Number Error",
    144: "Invalid flow status of the flow control frame",
    145: "Unexpected Protocol Data Unit",
    146: "Wait counter of the FC frame out of the maxWFT",
    147: "Buffer of the receiver is overflow",
    148: "TP Module is busy",
    149: "There is error from CAN Driver",
    150: "Handle of the TP Module is not exist",
    151: "UDS event buffer is full",
    152: "Handle pool is full, can not add new UDS module",
    153: "Pointer of UDS module is null",
    154: "UDS message is invalid",
    155: "No uds data received",
    156: "Handle of uds is not existing",
    157: "UDS module is not ready",
    158: "Transmit uds frame data failed",
    159: "This uds Service is not supported",
    160: "Time out to send uds request",
    161: "Time out to get uds response",
    162: "Get uds negative response",
    163: "Get uds negative response with expected NRC",
    164: "Get uds negative response with unexpected NRC",
    165: "UDS can tool is not ready",
    166: "UDS data is out of range",
    167: "Get unexpected UDS frame",
    168: "Receive unexpected positive response frame",
    169: "Receive positive response with wrong data",
    170: "Failed to get positive response",
    171: "Reserved UDS Error Code",
    172: "Receive negative response with unexpected NRC",
    173: "UDS service is busy",
    174: "Request download service must be performed before transfer data",
    175: "Length of the uds reponse is wrong",
    176: "Verdict value smaller than specification",
    177: "Verdict value greater than specification",
    178: "Verdict check failed",
    179: "Automation module not loaded, please load it first",
    180: "Panel not found",
    181: "Control not found in panel",
    182: "Panel not loaded, please load it first",
    183: "STIM signal not found",
    184: "Automation sub module not available",
    185: "Automation variant group not found",
    186: "Control not found in panel",
    187: "Panel control does not support this property",
    188: "RBS engine is not running",
    189: "This message does not support PDU container",
    190: "Data not available",
    191: "J1939 not supported",
    192: "Another J1939 PDU is already being transmitted",
    193: "Transmit J1939 PDU failed due to protocol error",
    194: "Transmit J1939 PDU failed due to node inactive",
    195: "API is called without license support",
    196: "Signal range check violation",
    197: "DataLogger read category failed",
    198: "Check Flash Bootloader Version Failed",
    199: "Log file not created",
    200: "Module is being edited by user",
    201: "The Logger device is busy, can not operation at the same time",
    202: "Master node transmit diagnostic package timeout",
    203: "Master node transmit frame failed",
    204: "Master node receive diagnostic package timeout",
    205: "Master node receive frame failed",
    206: "Internal time runs out before reception is completed ",
    207: "Master node received no response ",
    208: "Serial Number Error when receiving multi frames",
    209: "Slave node transmit diagnostic package timeout",
    210: "Slave node receive diagnostic pacakge timeout",
    211: "Slave node transmit frames error",
    212: "Slave node receive frames error",
}
