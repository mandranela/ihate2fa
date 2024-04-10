# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/BWSAS_package.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aprotos/BWSAS_package.proto\x12\rBWSAS_package\x1a\x1fgoogle/protobuf/timestamp.proto\"\xf2\x03\n\x15\x42WSAS_package_message\x12\x14\n\x0cstation_name\x18\x01 \x01(\t\x12\x39\n\x15measurement_timestamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x17\n\x0f\x61ir_temperature\x18\x03 \x01(\x02\x12\x1c\n\x14wet_bulb_temperature\x18\x04 \x01(\x02\x12\x10\n\x08humidity\x18\x05 \x01(\x03\x12\x16\n\x0erain_intensity\x18\x06 \x01(\x02\x12\x15\n\rinterval_rain\x18\x07 \x01(\x02\x12\x12\n\ntotal_rain\x18\x08 \x01(\x02\x12\x1a\n\x12precipitation_type\x18\t \x01(\x03\x12\x16\n\x0ewind_direction\x18\n \x01(\x03\x12\x12\n\nwind_speed\x18\x0b \x01(\x02\x12\x1a\n\x12maximum_wind_speed\x18\x0c \x01(\x02\x12\x1b\n\x13\x62\x61rometric_pressure\x18\r \x01(\x02\x12\x17\n\x0fsolar_radiation\x18\x0e \x01(\x03\x12\x0f\n\x07heading\x18\x0f \x01(\x03\x12\x14\n\x0c\x62\x61ttery_life\x18\x10 \x01(\x02\x12#\n\x1bmeasurement_timestamp_label\x18\x11 \x01(\t\x12\x16\n\x0emeasurement_id\x18\x12 \x01(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.BWSAS_package_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_BWSAS_PACKAGE_MESSAGE']._serialized_start=79
  _globals['_BWSAS_PACKAGE_MESSAGE']._serialized_end=577
# @@protoc_insertion_point(module_scope)