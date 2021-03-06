#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
import ctypes
import logging
from ctypes import Structure, Union, c_uint8, c_int32, POINTER, byref, CFUNCTYPE, pointer, ARRAY, create_string_buffer
import enum

from common import ModuleIDs
from wildfire.ffi import FFI
from et import Et
from utl import Utl

STATUS_T = ctypes.c_uint16

MSG_LEN = 22
MAX_APDU_LEN = 14
MAX_PROP_DATA_LEN = 10

class Services(enum.IntEnum):
    INIT                      = 0x00
    ALLOCATE_BUFFER           = 0x01
    ALLOCATE_BUFFER_WRAPPER   = 0x02
    RELEASE_BUFFER            = 0x03
    CLEAR_BUFFER              = 0x04
    POST                      = 0x05
    GET                       = 0x06
    SET_LEN                   = 0x07
    GET_LEN                   = 0x08
    SET_ROUTING_COUNT         = 0x09
    GET_ROUTING_COUNT         = 0x0a
    GET_BUFFER_ADDRESS        = 0x0b
    GET_BUFFER_NUMBER         = 0x0c
    CLEAR_MESSAGE_BUFFER      = 0x0d


class Errors(enum.IntEnum):
    UNINIT                        = 0x01
    NULL_PTR                      = 0x02
    NO_BUFFER_AVAIL               = 0x03
    INVALID_BUFFER                = 0x04
    NOT_ALLOCATED                 = 0x05

class KnxMsg_StandardFrameType(Structure):
    _fields_ = [
        ("ctrl", c_uint8),
        ("source", c_uint8 * 2),
        ("dest", c_uint8 * 2),
        ("npci", c_uint8),
        ("tpci", c_uint8),
        ("apci", c_uint8),
        ("data", c_uint8 * MAX_APDU_LEN),
    ]
    _pack_ = 1


class KnxMsg_PropertyFrameType(Structure):
    _fields_ = [
        ("ctrl", c_uint8),
        ("source", c_uint8 * 2),
        ("dest", c_uint8 * 2),
        ("npci", c_uint8),
        ("tpci", c_uint8),
        ("apci", c_uint8),
        ("obj_id", c_uint8),
        ("prop_id", c_uint8),
        ("num_elems", c_uint8),
        ("start_index", c_uint8),
        ("data", c_uint8 * MAX_PROP_DATA_LEN),
    ]
    _pack_ = 1


class KnxMsg_PollingFrameType(Structure):
    _fields_ = [
        ("ctrl", c_uint8),
        ("source", c_uint8 * 2),
        ("poll_addr", c_uint8 * 2),
        ("num_slots", c_uint8),
        ("slot", c_uint8 * MAX_APDU_LEN),
    ]
    _pack_ = 1


class MessageUnion(Union):
    _fields_ = [
        ("raw", c_uint8 * MSG_LEN),
        ("standard", KnxMsg_StandardFrameType),
        ("property", KnxMsg_PropertyFrameType),
        ("polling", KnxMsg_PollingFrameType),
    ]
    _pack_ = 1


class KnxMsg_Buffer(Structure):
    _fields_ = [
        ("next", c_uint8),
        ("len", c_uint8),
        ("service", c_uint8),
        ("sap", c_uint8),
        ("status", c_uint8),
        ("msg", MessageUnion),
    ]
    _pack_ = 1

class KnxMsg_DebugBufferCounters(Structure):
    _fields_ = [
        ("used", c_uint8),
        ("free", c_uint8),
    ]
    _pack_ = 1


KnxMsg_Buffer_Ptr = POINTER(KnxMsg_Buffer)
CounterType = namedtuple("CounterType", "free used")

class Messaging(FFI):

    _functions_ = (
        ("KnxMsg_Init", None, []),
        ("KnxMsg_Deinit", None, []),
        ("KnxMsg_AllocateBuffer", STATUS_T, [POINTER(KnxMsg_Buffer_Ptr)]),
        ("KnxMsg_AllocateBufferWrapper", KnxMsg_Buffer_Ptr, []),
        ("KnxMsg_ReleaseBuffer", STATUS_T, [KnxMsg_Buffer_Ptr]),
        ("KnxMsg_ClearBuffer", STATUS_T, [KnxMsg_Buffer_Ptr]),
        ("KnxMsg_Post", STATUS_T, [KnxMsg_Buffer_Ptr]),
        ("KnxMsg_Get", KnxMsg_Buffer_Ptr, [c_uint8]),
        ("KnxMsg_SetLen", None, [KnxMsg_Buffer_Ptr, c_uint8]),
        ("KnxMsg_GetLen", c_uint8, [KnxMsg_Buffer_Ptr]),
        ("KnxMsg_GetRoutingCount", c_uint8, [KnxMsg_Buffer_Ptr]),
        ("KnxMsg_SetRoutingCount", None, [KnxMsg_Buffer_Ptr]),
        ("KnxMsg_SetRoutingCtrl", None, [KnxMsg_Buffer_Ptr, c_uint8]),
        ("KnxMsg_DebugGetBufferCounters", None, [POINTER(KnxMsg_DebugBufferCounters)]),
        ("KnxMsg_DebugGetBuffers", None, [POINTER(KnxMsg_Buffer * 4)]),

    )

    def __init__(self, dll = None, parent = None):
        super(Messaging, self).__init__(dll, parent)
        self.utl = Utl(parent = self)
        self.et = Et(parent = self)

    def init(self):
        self.KnxMsg_Init()

    def deinit(self):
        self.KnxMsg_Deinit()

    def getBufferCounters(self):
        counters = KnxMsg_DebugBufferCounters()
        self.KnxMsg_DebugGetBufferCounters(byref(counters))
        return CounterType(counters.free, counters.used)

    def getBuffers(self):
        ptr = (KnxMsg_Buffer * 4)()
        self.KnxMsg_DebugGetBuffers(pointer(ptr))
        return ptr

    def allocateBuffer(self):
        ptr = KnxMsg_Buffer_Ptr()
        result = self.KnxMsg_AllocateBuffer(byref(ptr))
        if ptr:
            return ptr.contents
        else:
            return None

    def allocateBufferWrapper(self):
        return self.KnxMsg_AllocateBufferWrapper()

    def releaseBuffer(self, buffer):
        return self.KnxMsg_ReleaseBuffer(buffer)

    def clearBuffer(self, buffer):
        return self.KnxMsg_ClearBuffer(buffer)

    def post(self, buffer):
        return self.KnxMsg_Post(buffer)

    def get(self, layer):
        buffer =  self.KnxMsg_Get(layer)
        print("Buffah {0} - Null? {1}".format(buffer, not bool(buffer)))
        if buffer:
            return buffer.contents
        else:
            return None
        return buffer

