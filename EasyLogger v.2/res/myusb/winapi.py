##################################################

# HID structures and functions, thanks to pywinusb

##################################################

import platform
from ctypes import *
from ctypes.wintypes import ULONG, BOOLEAN, BYTE, WORD, DWORD, HANDLE, BOOL, WCHAR, LPWSTR, LPCWSTR


TCHAR = WCHAR
if platform.architecture()[0].startswith('64'):
    WIN_PACK = 8
else:
    WIN_PACK = 1


GENERIC_READ     = (-2147483648)
GENERIC_WRITE    = (1073741824)
FILE_SHARE_READ  = 1
FILE_SHARE_WRITE = 2
OPEN_EXISTING   = 3
FILE_ATTRIBUTE_NORMAL   = 128
FILE_FLAG_OVERLAPPED    = 1073741824
INVALID_HANDLE_VALUE = HANDLE(-1)


setup_api               = windll.setupapi
CreateFile              = windll.kernel32.CreateFileW
ReadFile                = windll.kernel32.ReadFile

CloseHandle             = windll.kernel32.CloseHandle
CloseHandle.restype     = BOOL
CloseHandle.argtypes    = [HANDLE]


class GUID(Structure):
    """GUID Windows OS structure"""
    _pack_ = 1
    _fields_ = [("data1", DWORD),
                ("data2", WORD),
                ("data3", WORD),
                ("data4", BYTE * 8)]

class SP_DEVINFO_DATA(Structure):
    """
    typedef struct _SP_DEVINFO_DATA {
      DWORD     cbSize;
      GUID      ClassGuid;
      DWORD     DevInst;
      ULONG_PTR Reserved;
    } SP_DEVINFO_DATA, *PSP_DEVINFO_DATA;
    """
    _pack_ = WIN_PACK
    _fields_ = [ \
            ("cb_size",     DWORD),
            ("class_guid",  GUID),
            ("dev_inst",    DWORD),
            ("reserved",    POINTER(ULONG)),
    ]

class DIGCF:
    """
    Flags controlling what is included in the device information set built
    by SetupDiGetClassDevs
    """
    DEFAULT         = 0x00000001  # only valid with DIGCF.DEVICEINTERFACE
    PRESENT         = 0x00000002
    ALLCLASSES      = 0x00000004
    PROFILE         = 0x00000008
    DEVICEINTERFACE = 0x00000010

class SP_DEVICE_INTERFACE_DATA(Structure):
    """
    typedef struct _SP_DEVICE_INTERFACE_DATA {
      DWORD     cbSize;
      GUID      InterfaceClassGuid;
      DWORD     Flags;
      ULONG_PTR Reserved;
    } SP_DEVICE_INTERFACE_DATA, *PSP_DEVICE_INTERFACE_DATA;
    """
    _pack_ = WIN_PACK
    _fields_ = [ \
            ("cb_size",              DWORD),
            ("interface_class_guid", GUID),
            ("flags",                DWORD),
            ("reserved",             POINTER(ULONG))
    ]

class SP_DEVICE_INTERFACE_DETAIL_DATA(Structure):
    """
    typedef struct _SP_DEVICE_INTERFACE_DETAIL_DATA {
      DWORD cbSize;
      TCHAR DevicePath[ANYSIZE_ARRAY];
    } SP_DEVICE_INTERFACE_DETAIL_DATA, *PSP_DEVICE_INTERFACE_DETAIL_DATA;
    """
    _pack_ = WIN_PACK
    _fields_ = [ \
            ("cb_size",     DWORD),
            ("device_path", TCHAR * 1) # device_path[1]
    ]
    def get_string(self):
        """Retreive stored string"""
        return wstring_at(byref(self, sizeof(DWORD)))

class HIDP_CAPS(Structure):
    _fields_ = [
        ("usage", c_ushort), #usage id
        ("usage_page", c_ushort), #usage page
        ("input_report_byte_length", c_ushort),
        ("output_report_byte_length", c_ushort),
        ("feature_report_byte_length", c_ushort),
        ("reserved", c_ushort * 17),
        ("number_link_collection_nodes", c_ushort),
        ("number_input_button_caps", c_ushort),
        ("number_input_value_caps", c_ushort),
        ("number_input_data_indices", c_ushort),
        ("number_output_button_caps", c_ushort),
        ("number_output_value_caps", c_ushort),
        ("number_output_data_indices", c_ushort),
        ("number_feature_button_caps", c_ushort),
        ("number_feature_value_caps", c_ushort),
        ("number_feature_data_indices", c_ushort)
    ]

class HIDP_VALUE_CAPS(Structure):
    class RANGE_NOT_RANGE(Union):
        class RANGE(Structure):
            _fields_ = [
                ("usage_min", c_ushort),     ("usage_max", c_ushort),
                ("string_min", c_ushort),    ("string_max", c_ushort),
                ("designator_min", c_ushort),("designator_max", c_ushort),
                ("data_index_min", c_ushort), ("data_index_max", c_ushort)
            ]

        class NOT_RANGE(Structure):
            _fields_ = [
                ("usage", c_ushort),            ("reserved1", c_ushort),
                ("string_index", c_ushort),      ("reserved2", c_ushort),
                ("designator_index", c_ushort),  ("reserved3", c_ushort),
                ("data_index", c_ushort),        ("reserved4", c_ushort)
            ]
        _fields_ = [
            ("range", RANGE),
            ("not_range", NOT_RANGE)
        ]

    _fields_ = [
        ("usage_page", c_ushort),
        ("report_id", c_ubyte),
        ("is_alias", BOOLEAN),
        ("bit_field", c_ushort),
        ("link_collection", c_ushort),
        ("link_usage", c_ushort),
        ("link_usage_page", c_ushort),
        ("is_range", BOOLEAN),
        ("is_string_range", BOOLEAN),
        ("is_designator_range", BOOLEAN),
        ("is_absolute", BOOLEAN),
        ("has_null", BOOLEAN),
        ("reserved", c_ubyte),
        ("bit_size", c_ushort),
        ("report_count", c_ushort),
        ("reserved2", c_ushort * 5),
        ("units_exp", c_ulong),
        ("units", c_ulong),
        ("logical_min", c_long),
        ("logical_max", c_long),
        ("physical_min", c_long),
        ("physical_max", c_long),
        ("union", RANGE_NOT_RANGE)
    ]


FACILITY_HID_ERROR_CODE = 0x11
def HIDP_ERROR_CODES(sev, code):
    return (((sev) << 28) | (FACILITY_HID_ERROR_CODE << 16) | (code)) & 0xFFFFFFFF

class HidStatus(object):
    HIDP_STATUS_SUCCESS                  = ( HIDP_ERROR_CODES(0x0, 0) )
    HIDP_STATUS_NULL                     = ( HIDP_ERROR_CODES(0x8, 1) )
    HIDP_STATUS_INVALID_PREPARSED_DATA   = ( HIDP_ERROR_CODES(0xC, 1) )
    HIDP_STATUS_INVALID_REPORT_TYPE      = ( HIDP_ERROR_CODES(0xC, 2) )
    HIDP_STATUS_INVALID_REPORT_LENGTH    = ( HIDP_ERROR_CODES(0xC, 3) )
    HIDP_STATUS_USAGE_NOT_FOUND          = ( HIDP_ERROR_CODES(0xC, 4) )
    HIDP_STATUS_VALUE_OUT_OF_RANGE       = ( HIDP_ERROR_CODES(0xC, 5) )
    HIDP_STATUS_BAD_LOG_PHY_VALUES       = ( HIDP_ERROR_CODES(0xC, 6) )
    HIDP_STATUS_BUFFER_TOO_SMALL         = ( HIDP_ERROR_CODES(0xC, 7) )
    HIDP_STATUS_INTERNAL_ERROR           = ( HIDP_ERROR_CODES(0xC, 8) )
    HIDP_STATUS_I8042_TRANS_UNKNOWN      = ( HIDP_ERROR_CODES(0xC, 9) )
    HIDP_STATUS_INCOMPATIBLE_REPORT_ID   = ( HIDP_ERROR_CODES(0xC, 0xA) )
    HIDP_STATUS_NOT_VALUE_ARRAY          = ( HIDP_ERROR_CODES(0xC, 0xB) )
    HIDP_STATUS_IS_VALUE_ARRAY           = ( HIDP_ERROR_CODES(0xC, 0xC) )
    HIDP_STATUS_DATA_INDEX_NOT_FOUND     = ( HIDP_ERROR_CODES(0xC, 0xD) )
    HIDP_STATUS_DATA_INDEX_OUT_OF_RANGE  = ( HIDP_ERROR_CODES(0xC, 0xE) )
    HIDP_STATUS_BUTTON_NOT_PRESSED       = ( HIDP_ERROR_CODES(0xC, 0xF) )
    HIDP_STATUS_REPORT_DOES_NOT_EXIST    = ( HIDP_ERROR_CODES(0xC, 0x10) )
    HIDP_STATUS_NOT_IMPLEMENTED          = ( HIDP_ERROR_CODES(0xC, 0x20) )

    error_message_dict = {
        HIDP_STATUS_SUCCESS                  : "success",
        HIDP_STATUS_NULL                     : "null",
        HIDP_STATUS_INVALID_PREPARSED_DATA   : "invalid preparsed data",
        HIDP_STATUS_INVALID_REPORT_TYPE      : "invalid report type",
        HIDP_STATUS_INVALID_REPORT_LENGTH    : "invalid report length",
        HIDP_STATUS_USAGE_NOT_FOUND          : "usage not found",
        HIDP_STATUS_VALUE_OUT_OF_RANGE       : "value out of range",
        HIDP_STATUS_BAD_LOG_PHY_VALUES       : "bad log phy values",
        HIDP_STATUS_BUFFER_TOO_SMALL         : "buffer too small",
        HIDP_STATUS_INTERNAL_ERROR           : "internal error",
        HIDP_STATUS_I8042_TRANS_UNKNOWN      : "i8042/I8242 trans unknown",
        HIDP_STATUS_INCOMPATIBLE_REPORT_ID   : "incompatible report ID",
        HIDP_STATUS_NOT_VALUE_ARRAY          : "not value array",
        HIDP_STATUS_IS_VALUE_ARRAY           : "is value array",
        HIDP_STATUS_DATA_INDEX_NOT_FOUND     : "data index not found",
        HIDP_STATUS_DATA_INDEX_OUT_OF_RANGE  : "data index out of range",
        HIDP_STATUS_BUTTON_NOT_PRESSED       : "button not pressed",
        HIDP_STATUS_REPORT_DOES_NOT_EXIST    : "report does not exist",
        HIDP_STATUS_NOT_IMPLEMENTED          : "not implemented"
    }

    def __init__(self, error_code):
        error_code &= 0xFFFFFFFF
        self.error_code = error_code
        if error_code != self.HIDP_STATUS_SUCCESS:
            if error_code in self.error_message_dict:
                raise Exception("hidP error: %s" % self.error_message_dict[error_code])
            else:
                raise Exception("Unknown HidP error (%s)" % hex(error_code))


SetupDiGetClassDevs          = setup_api.SetupDiGetClassDevsW
SetupDiGetClassDevs.restype  = HANDLE
SetupDiGetClassDevs.argtypes = [
    POINTER(GUID), # __in_opt  const GUID *ClassGuid,
    LPCWSTR, # __in_opt  PCTSTR Enumerator,
    HANDLE,  # __in_opt  HWND hwndParent,
    DWORD,   # __in      DWORD Flags
    ]


SetupDiGetDeviceInterfaceDetail = setup_api.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.restype = BOOL
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HANDLE, # __in       HDEVINFO DeviceInfoSet,
    POINTER(SP_DEVICE_INTERFACE_DATA), # __in PSP_DEVICE_INTERFACE_DATA DeviceIn
    # __out_opt  PSP_DEVICE_INTERFACE_DETAIL_DATA DeviceInterfaceDetailData,
    POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA),
    DWORD, # __in       DWORD DeviceInterfaceDetailDataSize,
    POINTER(DWORD), # __out_opt  PDWORD RequiredSize,
    POINTER(SP_DEVINFO_DATA), # __out_opt  PSP_DEVINFO_DATA DeviceInfoData
    ]


def GetHidGuid():
    "Get system-defined GUID for HIDClass devices"
    hid_guid = GUID()
    windll.hid.HidD_GetHidGuid(byref(hid_guid))
    return hid_guid

class DeviceInterfaceSetInfo(object):
    """Context manager for SetupDiGetClassDevs / SetupDiDestroyDeviceInfoList
    resource allocation / cleanup
    """
    def __init__(self, guid_target):
        self.guid = guid_target
        self.h_info = None

    def __enter__(self):
        """Context manager initializer, calls self.open()"""
        return self.open()

    def open(self):
        """
        Calls SetupDiGetClassDevs to obtain a handle to an opaque device
        information set that describes the device interfaces supported by all
        the USB collections currently installed in the system. The
        application should specify DIGCF.PRESENT and DIGCF.INTERFACEDEVICE
        in the Flags parameter passed to SetupDiGetClassDevs.
        """
        self.h_info = SetupDiGetClassDevs(byref(self.guid), None, None,
                (DIGCF.PRESENT | DIGCF.DEVICEINTERFACE) )

        return self.h_info

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager clean up, calls self.close()"""
        self.close()

    def close(self):
        """Destroy allocated storage"""
        if self.h_info and self.h_info != INVALID_HANDLE_VALUE:
            # clean up
            setup_api.SetupDiDestroyDeviceInfoList(self.h_info)
        self.h_info = None

def enum_device_interfaces(h_info, guid):
    """Function generator that returns a device_interface_data enumerator
    for the given device interface info and GUID parameters
    """
    dev_interface_data = SP_DEVICE_INTERFACE_DATA()
    dev_interface_data.cb_size = sizeof(dev_interface_data)

    device_index = 0
    while setup_api.SetupDiEnumDeviceInterfaces(h_info,
            None,
            byref(guid),
            device_index,
            byref(dev_interface_data) ):
        yield dev_interface_data
        device_index += 1
    del dev_interface_data

def get_device_path(h_info, interface_data, ptr_info_data = None):
    """"Returns Hardware device path
    Parameters:
        h_info,         interface set info handler
        interface_data, device interface enumeration data
        ptr_info_data,  pointer to SP_DEVINFO_DATA() instance to receive details
    """
    required_size = c_ulong(0)

    dev_inter_detail_data         = SP_DEVICE_INTERFACE_DETAIL_DATA()
    dev_inter_detail_data.cb_size = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA)

    # get actual storage requirement
    SetupDiGetDeviceInterfaceDetail(h_info, byref(interface_data),
            None, 0, byref(required_size),
            None)

    resize(dev_inter_detail_data, required_size.value)

    # read value
    SetupDiGetDeviceInterfaceDetail(h_info, byref(interface_data),
            byref(dev_inter_detail_data), required_size, None,
            ptr_info_data)

    # extract string only
    return dev_inter_detail_data.get_string()
