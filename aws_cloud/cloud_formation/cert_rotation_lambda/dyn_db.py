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
    filename: dyn_db.py

    Dynamo DB table wrapper for Cert Rotation.

    Each table row has the following contents:
        "SerialNumber":  Manufacturer serial number - primary key
        "State" : State of cert ration for this device

    The dynamo DB table is created and deleted as part of the cloud formation stack.
    Data for a device is added to the DynamoDB table for a single device as part 
    of the Cert Rotation blog. The data is entered when running
        > python certs_etc.py --create
    in the ~/aws_cloud/certs_etc/ directory.

    The cert rotation lambda code only:
        - reads (e.g. get_item) rows based on SerialNumber
        - writes (e.g. put_item) the State in a row with a matching SerialNumber
          or VendorSerial value
'''
import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging
from config import *

# db_table_name must equal DDB_NAME in ../config.bash.
# Cloud formation used DDB_NAME when creating the DDB table.
ddb_table_name = 'CertRotationDevices'

def get_table():
    ddb_table = None
    try:
        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(ddb_table_name)
    except Exception as e:
        ddb_table = None
        logging.error("get_table(): Exception: {}".format(str(e)))
    return(ddb_table)

def write_state(serial_number, state):
    rc = False
    if state in cr_states :
        ddb_table = get_table()
        try:

            response = ddb_table.get_item(Key={'SerialNumber':serial_number})
            item = response.get('Item', None)
            if item:
                item.update({'CrState':state})
                ddb_table.put_item(Item=item)
            else:
                print('write_state(): get_item failed for serial_number = {}'.\
                    format(serial_number))

        except Exception as e:
            logging.error('write_state(): Exception = {}'.format(str(e)))
            pass


def read_state(serial_number):

    CrState = None

    try:
        ddb_table = get_table()
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)

        CrState = item.get('CrState', None)

    except Exception as e:
        logging.error('read_state(): Exception = {}'.format(str(e)))
        pass

    return CrState

def write_man_cert_id(serial_number, cert_id):
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)
        if item:
            item.update({'ManufacturerCertId':cert_id})
            ddb_table.put_item(Item=item)
        else:
            print('write_man_cert_id(): get_item failed for serial_number = {}'.\
                    format(serial_number))

    except Exception as e:
        logging.error('write_man_cert_id(): Exception = {}'.format(str(e)))

def read_man_ca_cert_id(serial_number):
    cert_id = None
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)

        print('read_man_ca_cert_id: item = {}'.format(item))
        ca_cert_id = item.get('ManufacturerCaCertId', '')
    except Exception as e:
        logging.error('read_man_cert_id(): Exception = {}'.format(str(e)))
    return ca_cert_id

def read_man_cert_id(serial_number):
    cert_id = None
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)

        print('read_man_cert_id: item = {}'.format(item))
        cert_id = item.get('ManufacturerCertId', '')
    except Exception as e:
        logging.error('read_man_cert_id(): Exception = {}'.format(str(e)))
    return cert_id

def write_vendor_cert_id(serial_number, cert_id):
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)
        if item:
            if cert_id:
                item.update({'VendorCertId':cert_id})
                print('write_vendor_cert_id(): update')
            else:
                # If no cert_id then remove VendorCertId this field from the entry
                print('write_vendor_cert_id(): pop')
                item.pop('VendorCertId')
            ddb_table.put_item(Item=item)
        else:
            print('write_vendor_cert_id(): get_item failed for serial_number = {}'.\
                    format(serial_number))

    except Exception as e:
        logging.error('write_vendor_cert_id(): Exception = {}'.format(str(e)))

def read_vendor_cert_id(serial_number):
    cert_id = None
    ddb_table = get_table()
    try:
        response = ddb_table.get_item(Key={'SerialNumber':serial_number})
        item = response.get('Item', None)

        print('read_vendor_cert_id: item = {}'.format(item))
        cert_id = item.get('VendorCertId', '')
    except Exception as e:
        logging.error('read_vendor_cert_id(): Exception = {}'.format(str(e)))
    return cert_id

