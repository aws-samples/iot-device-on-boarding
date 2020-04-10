#!/usr/bin/env python3
'''
MIT No Attribution

Copyright Amazon Web Services

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
'''
    filename: device_dyn_db.py

    This is a wrapper for dynmaoDB to add and delete devices for whitelisting
    purposes.

    Actions:
        - add all devices in the device_list_filename to the dynamoDB table
        - remove all devices in the device_list_filename from the dynamoDB table
'''

import boto3
import json
import logging
from config import *
import argparse
import os
from local_json import get_json_array_dicts

def get_table():
    ddb_table = None
    try:
        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(DDB_NAME)
    except Exception as e:
        ddb_table = None
        logging.error("get_table(): Exception: {}".format(str(e)))
    return(ddb_table)

'''
    Add a device from device_dict into dynamo db table.
'''
def add_device(ddb_table, device_dict):
    rc = None
    try:
        response = ddb_table.put_item(Item={\
            'SerialNumber':device_dict.get('SerialNumber',None),
            'CrState':device_dict.get('CrState',None)
            })

        responseMetadata = response.get('ResponseMetadata', None)
        httpStatusCode = None
        if responseMetadata:
            httpStatusCode = responseMetadata.get('HTTPStatusCode', None)
            if httpStatusCode:
                if httpStatusCode >= 200 and httpStatusCode < 300 :
                    rc = True

        if not rc:
            logging.info('add_device(): responseMetadata = {}'.format('responseMetadata'))
            logging.info('add_device(): httpStatusCode = {}'.format('httpStatusCode'))

    except Exception as e:
        logging.error('add_device(): Exception = {}'.format(str(e)))
        pass
    return rc

'''
    Delete a device from device_dict from dynamo db table.
'''
def del_device(ddb_table, device_dict):
    rc = None
    try:
        response = ddb_table.delete_item(Key={'SerialNumber':\
            device_dict.get('SerialNumber', None)}, ReturnValues='ALL_OLD')
        rc = response.get('Attributes', None)

        if not rc:
            logging.info('del_device(): response = {}'.format('response'))

    except Exception as e:
        logging.error('del_device(): Exception = {}'.format(str(e)))
        pass

    return rc

'''
    Load all devices in the device_list_filename to the dynamo db table.
'''
def load_devices_into_dyn_db():

    device_array_dicts = get_json_array_dicts(device_list_filename)

    logging.info('load_devices_into_dyn_db(): Loading devices')
    logging.info(device_array_dicts)

    devices_loaded = 0

    ddb_table = get_table()

    for device_dict in device_array_dicts:
        if add_device(ddb_table, device_dict):
            logging.info('Loaded Device: SerialNumber = {}'.\
                    format(device_dict.get('SerialNumber',None)))
            devices_loaded += 1
        else:
            logging.info('Device load failed: SerialNumber = {}'.\
                    format(device_dict.get('SerialNumber',None)))

    logging.info('Total Devices Loaded = {}'.format(devices_loaded))
    
'''
    Delete all devices in the device_list_filename from the dynamo db table.
'''
def delete_devices_from_dyn_db():

    device_array_dicts = get_json_array_dicts(device_list_filename)

    logging.info('delete_devices_from_dyn_db(): Deleting devices')
    logging.info(device_array_dicts)

    devices_deleted = 0

    ddb_table = get_table()

    for device_dict in device_array_dicts:
        response = ddb_table.delete_item(Key={'SerialNumber':\
            device_dict.get('SerialNumber',None)})
        if response:
            logging.info('Device: SerialNumber = {}'.\
                    format(device_dict.get('SerialNumber',None)))
            devices_deleted += 1
        else:
            logging.info('Device load failed: SerialNumber = {}'.\
                    format(device_dict.get('SerialNumber',None)))

    logging.info('Total Devices Deleted = {}'.format(devices_deleted))

def read_man_cert_id(serial_number):
    cert_id = None
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)

        logging.info('read_man_cert_id: item = {}'.format(item))
        cert_id = item.get('ManufacturerCertId', '')
    except Exception as e:
        logging.error('read_man_cert_id(): Exception = {}'.format(str(e)))
    return cert_id

def read_vendor_cert_id(serial_number):
    cert_id = None
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)

        logging.info('read_vendor_cert_id: item = {}'.format(item))
        cert_id = item.get('VendorCertId', '')
    except Exception as e:
        logging.error('read_vendor_cert_id(): Exception = {}'.format(str(e)))
    return cert_id

def write_man_ca_cert_id(serial_number, ca_cert_id):
    ddb_table = get_table()
    try:
        print('write_man_ca_cert_id(): ca_cert_id = {}'.format(ca_cert_id))
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)
        if item:
            item.update({'ManufacturerCaCertId':ca_cert_id})
            ddb_table.put_item(Item=item)
        else:
            print('write_man_ca_cert_id(): get_item failed for serial_number = {}'.\
                    format(serial_number))

    except Exception as e:
        logging.error('write_man_ca_cert_id(): Exception = {}'.format(str(e)))


'''
    Unit test the functions this file.
'''
def unit_test():
    argp = argparse.ArgumentParser(description='Load/Delete Devices into/from DynamoDB table {}'.format(DDB_NAME))
    argp.add_argument('--load', action='store_true', help='--load devices into table')
    argp.add_argument('--delete', action='store_true', help='--delete devices from table')
    args = argp.parse_args()

    logging.info('main(): load = {load}, delete = {delete}'.\
        format(load=args.load, delete=args.delete))

    if args.load != args.delete:
        if args.load:
            load_devices_into_dyn_db()
        if args.delete:
            delete_devices_from_dyn_db()

if __name__ == '__main__':
    unit_test()
