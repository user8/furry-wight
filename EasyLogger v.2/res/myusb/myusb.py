#################################################

# Access to HID, thanks to pywinusb

#################################################

import ctypes, res.myusb.winapi as winapi

hid_dll = ctypes.windll.hid

class HIDInputDevice():

    def __init__(self, vid, pid):
        self.device_path = self.find_device_path(vid, pid)


    def find_device_path(self, vid, pid):
        "Finds all HID devices connected to the system"

        # get HID device class guid
        guid = winapi.GetHidGuid()

        info_data         = winapi.SP_DEVINFO_DATA()
        info_data.cb_size = ctypes.sizeof(winapi.SP_DEVINFO_DATA)

        with winapi.DeviceInterfaceSetInfo(guid) as h_info:
            for interface_data in winapi.enum_device_interfaces(h_info, guid):
                device_path = winapi.get_device_path(h_info, interface_data, ctypes.byref(info_data))

                if "vid_"+vid in device_path and "pid_"+pid in device_path:
                    return device_path

        raise Exception("Device not found")


    def open(self):
        hid_handle = winapi.CreateFile(
            self.device_path,
            winapi.GENERIC_READ | winapi.GENERIC_WRITE,
            winapi.FILE_SHARE_READ | winapi.FILE_SHARE_WRITE,
            None, # no security
            winapi.OPEN_EXISTING,
            winapi.FILE_ATTRIBUTE_NORMAL | winapi.FILE_FLAG_OVERLAPPED,
            0 )

        if not hid_handle or hid_handle == ctypes.c_void_p(-1).value:
            raise Exception("Error opening device")

        ptr_preparsed_data = ctypes.c_void_p()
        if not hid_dll.HidD_GetPreparsedData(int(hid_handle), ctypes.byref(ptr_preparsed_data)):
            winapi.CloseHandle(int(hid_handle))
            raise Exception("Failure to get HID preparsed data")

        self.hid_handle = hid_handle

        hid_caps = winapi.HIDP_CAPS()
        winapi.HidStatus( hid_dll.HidP_GetCaps(ptr_preparsed_data, ctypes.byref(hid_caps)) )

        max_items = hid_caps.number_input_value_caps

        if not int(max_items):
            raise Exception("This device has no input capabilities")

        ctrl_array_type = winapi.HIDP_VALUE_CAPS * max_items
        ctrl_array_struct = ctrl_array_type()
        caps_length = ctypes.c_ulong()
        caps_length.value = max_items

        winapi.HidStatus( hid_dll.HidP_GetValueCaps(
            0, # <-- winapi.HidP_Input,
            ctypes.byref(ctrl_array_struct),
            ctypes.byref(caps_length),
            ptr_preparsed_data) )

        if not hid_caps.input_report_byte_length:
            raise Exception("Input report has 0 length")

        report_id = 0

        raw_data_type = ctypes.c_ubyte * hid_caps.input_report_byte_length
        self.raw_data = raw_data_type()
        self.raw_data[0] = ctypes.c_ubyte(report_id)

        return True


    def read(self):
        hid_dll.HidD_GetInputReport(int(self.hid_handle), ctypes.byref(self.raw_data), len(self.raw_data) )
        return list(self.raw_data)


    def close(self):
        winapi.CloseHandle(int(self.hid_handle))


if __name__ == "__main__":
    import time
    dev = HIDInputDevice(vid="4242", pid="0002")
    dev.open()
    i = 0
    while time.clock() < 1:
        dev.read()
        i += 1
    print(dev.read(), i)
    dev.close()
