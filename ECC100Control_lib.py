"""
ECC 100 motion controller via USB - python interface

This file contains a class that can be used to send python commands to a ECC100 motion controller connected to the computer via a USB connection. The class makes use of a dynamical link library (dll) provided by the Attocube software(links below). Documentation on the library functions is provided by the company in the .zip files.

The functions are adapted from an example provided by Attocube for using the dll library with C#. The functions defined below allow the user to
- connect to and disconnect from an ECC 100 motion controller
- set voltage and frequency parameters for single step movement along different axes
- make single steps forward or backward along a particular axis
These are not an exhaustive list of the functions available to communicate with the motion controller; using the dll library documentation, python versions of additional dll functions could be easily added as necessary following the format of the functions already defined below. If you write additional functions feel free to send a pull request.

Before implementing this on your computer, be sure specify the correct .dll path on your PC.

From Attocube:
Manual: https://www.attocube.com/FTP/download/_Manuals/ECC100/Manual_ECC100.pdf
Driver: https://www.attocube.com/FTP/download/_Software/ECC100/Software_ECC100.zip

Python version: python 3.6

Author: Simone Eizagirre <se410@cam.ac.uk>
"""

import ctypes
import time

dll_path=r'C:\Code\Software_ECC100_1.6.8\ECC100_DLL\Win64\ecc.dll'

class ECC100Control:
    
    #Define the error codes returned by the ECC library functions
    NCB_Ok = 0
    NCB_Error = -1
    NCB_Timeout = 1
    NCB_NotConnected = 2
    NCB_DriverError = 3
    NCB_DeviceLocked = 7
    NCB_InvalidParam = 11
    NCB_FeatureNotAvailable = 12
    

    def __init__(self):
        
        #Use path to open the library, which we will call ecc_dll in future code
        self.ecc_dll = ctypes.CDLL(dll_path)

        #Defines the function names for the program, imported from the dll
        #the argument types and return types of each function are also specified to help with troubleshooting
  
        self.ECC_Check = self.ecc_dll.ECC_Check
        self.ECC_Check.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.ECC_Check.restype = ctypes.c_int32

        self.ECC_getDeviceInfo = self.ecc_dll.ECC_getDeviceInfo
        self.ECC_getDeviceInfo.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
        self.ECC_getDeviceInfo.restype = ctypes.c_int32
        
        self.ECC_Connect = self.ecc_dll.ECC_Connect
        self.ECC_Connect.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
        self.ECC_Connect.restype = ctypes.c_int32
        self.ECC_Check.restype = ctypes.c_int32

        self.ECC_Close = self.ecc_dll.ECC_Close
        self.ECC_Close.argtypes = [ctypes.c_int32]
        self.ECC_Close.restype = ctypes.c_int32

        self.ECC_controlAmplitude = self.ecc_dll.ECC_controlAmplitude
        self.ECC_controlAmplitude.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]
        self.ECC_controlAmplitude.restype = ctypes.c_int32

        self.ECC_controlFrequency = self.ecc_dll.ECC_controlFrequency
        self.ECC_controlFrequency.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]
        self.ECC_controlFrequency.restype = ctypes.c_int32

        self.ECC_setSingleStep = self.ecc_dll.ECC_setSingleStep
        self.ECC_setSingleStep.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_bool]


    def check_error(self, context, code):
        if code != self.NCB_Ok:
            raise Exception("Error calling {}: {}".format(context, self.get_message(code)))

    def get_message(self, code):
        error_messages = {
            self.NCB_Ok: "",
            self.NCB_Error: "Unspecified error",
            self.NCB_Timeout: "Communication timeout",
            self.NCB_NotConnected: "No active connection to device",
            self.NCB_DriverError: "Error in communication with driver",
            self.NCB_DeviceLocked: "Device is already in use by another",
            self.NCB_InvalidParam: "Parameter out of range",
            self.NCB_FeatureNotAvailable: "Feature not available"
        }
        return error_messages.get(code, "Unknown error code")

    def select_device(self):
        dev_count = self.ECC_Check(None)
        if dev_count <= 0:
            raise Exception("No devices found")

        for i in range(dev_count):
            dev_id = ctypes.c_int32(0)
            locked = ctypes.c_int32(0)
            rc = self.ECC_getDeviceInfo(i, ctypes.byref(dev_id), ctypes.byref(locked))
            self.check_error("ECC_getDeviceInfo", rc)
            if locked.value != 0:
                print(f"Device {i}: locked")
            else:
                print(f"Device {i}: Id={dev_id.value}")

        dev_no = 0
        if dev_count > 1:
            dev_no = int(input("Select device: "))
            dev_no = min(max(dev_no, 0), dev_count - 1)

        return dev_no

    def connect(self, dev_no):
        handle=ctypes.c_int32(0)
        rc=self.ECC_Connect(dev_no, ctypes.byref(handle))
        self.check_error("ECC_Connect", rc)
        return handle.value

    def control_amplitude(self, handle, axis, amplitude):
        amp = ctypes.c_int32(amplitude)
        rc = self.ECC_controlAmplitude(handle, axis, ctypes.byref(amp), 1)
        self.check_error("ECC_controlAmplitude", rc)
        print('Amplitude value updated correctly')

    def control_frequency(self, handle, axis, frequency):
        freq = ctypes.c_int32(frequency)
        rc = self.ECC_controlFrequency(handle, axis, ctypes.byref(freq), 1)
        self.check_error("ECC_controlFrequency", rc)
        print('Frequency value updated correctly')
        
    def step(self,handle, axis, backward):
        back = ctypes.c_bool(backward)
        rc = self.ECC_setSingleStep(handle, axis, back)
        self.check_error("ECC_setSingleStep", rc)
        
    def step_forward(self,handle,axis):
        rc = self.ECC_setSingleStep(handle,axis, ctypes.c_bool(False))
        self.check_error("ECC_setSingleStep", rc)
        
    def step_backward(self,handle,axis):
        rc = self.ECC_setSingleStep(handle,axis, ctypes.c_bool(True))
        self.check_error("ECC_setSingleStep", rc)
    
    def close_device(self,handle):
        rc = self.ECC_Close(handle)
        print('Device disconnected')