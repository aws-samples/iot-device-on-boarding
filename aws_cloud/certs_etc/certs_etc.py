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
    filename: certs_etc.py

    This is the main entry point for all python scripts in this 
    directory related to the Cert Rotation Blog. 

    Actions:
        - loads the devices into the DynamoDB table - whitelist
        - creates and deletes the CAs, certs, ect
        - creates and deletes the CAs, certs, ect
        - generate config and header files for afr and linux devices
        - manage files in S3 bucket, afr_device/data_io, and linux_device/data_io
'''

import argparse
from cert_auth import *
from device_dyn_db import *
from local_json import get_json_array_dicts
import logging
from config import *
from manage_files import *

'''
  Create CAa, devices, certificates, certificate policies, 
  attach certificate polices to certificates based on 
  ca_list_filename and device_list_filename.

  Based on the ca_list_filename and device_list_filename
  used for this blog, here is the net result:
    - CA for Vendor
    - CA for Manufacture
    - One JITP Vendor device cert on local hard drive
        Note: this JITP cert does not exist in IoT Core until after 
        device connects to IoT core to register the cert, create thing
    - Cert Policy for all Vendor certificates
    - Cert Policy for all Manufacturer certificates
'''
def create_ca_dev():
    ca_array_dicts = get_json_array_dicts(ca_list_filename)
    device_array_dicts = get_json_array_dicts(device_list_filename)
    for ca_dict in ca_array_dicts:
        ca_name = ca_dict.get('ca_name', None)
        subj_str = ca_dict.get('subj_str', None)
        devices = ca_dict.get('devices', None)
        jitp = ca_dict.get('jitp', None)
        days = ca_dict.get('days', None)
        policy_name = ca_dict.get('policy_name', None)
        if ca_name and subj_str and devices and jitp and days and policy_name:
            devices = (devices == 'True')
            jitp = (jitp == 'True')
            new_ca(ca_name, subj_str, days, jitp=jitp)
            if ca_name == 'Manufacturer':
                put_secure_store(ca_name)
                if device_array_dicts:
                    device_dict = device_array_dicts[0]
                    file_name = '{}{}_ca_cert_id.txt'.format(data_dir, ca_name)
                    with open(file_name, 'r') as file:
                        ca_cert_id = file.read().replace('\n', '')
                    write_man_ca_cert_id(dev, ca_cert_id)

            if devices:
                for device_dict in device_array_dicts:
                    dev = device_dict.get('SerialNumber', None)

                    if dev:
                        logging.info('new_dev({})'.format(dev))
                        new_dev(ca_name, dev, subj_str, days, policy_name, jitp=jitp)
                logging.info('*********** DEVICE CERTS FOR CA {} ***********'.format(ca_name))
                list_dev_certs()
                logging.info('*********** END DEVICE CERTS FOR CA {} *******'.format(ca_name))

    logging.info('*********** CA CERTS ***********')
    list_ca_certs()
    logging.info('*********** END CERTS ***********')

    logging.info('*********** CERT POLICIES ***********')
    list_cert_policies()
    logging.info('*********** END CERT POLICIES ***********')

'''
    Delete the rule and lambda permissions (if they exist)
'''
def del_rule_and_lambda_permissions():
    del_rule()
    del_lambda_permission()

'''
  Delete CAa, things, certificates, certificate policies, 
  attach certificate polices to certificates based on 
  ca_list_filename and device_list_filename.
'''
def del_ca_dev():
    ca_array_dicts = get_json_array_dicts(ca_list_filename)
    device_array_dicts = get_json_array_dicts(device_list_filename)

    for ca_dict in ca_array_dicts:
        ca_name = ca_dict.get('ca_name', None)
        subj_str = ca_dict.get('subj_str', None)
        devices = ca_dict.get('devices', None)
        jitp = ca_dict.get('jitp', None)
        days = ca_dict.get('days', None)
        policy_name = ca_dict.get('policy_name', None)
        if ca_name and subj_str and devices and jitp and days and policy_name:
            if devices:
                for device_dict in device_array_dicts:
                    dev = device_dict.get('SerialNumber', None)

                    if dev:
                        del_dev(dev, policy_name)

    for ca_dict in ca_array_dicts:
        ca_name = ca_dict.get('ca_name', None)
        subj_str = ca_dict.get('subj_str', None)
        devices = ca_dict.get('devices', None)
        jitp = ca_dict.get('jitp', None)
        days = ca_dict.get('days', None)
        policy_name = ca_dict.get('policy_name', None)
        if ca_name and subj_str and devices and jitp and days and policy_name:
            if ca_name == 'Manufacturer':
                del_secure_store(ca_name)
            del_ca(ca_name)

    logging.info('*********** DEVICE CERTS FOR CA {} ***********'.format(ca_name))
    list_dev_certs()
    logging.info('*********** END DEVICE CERTS FOR CA {} *******'.format(ca_name))

    logging.info('*********** CA CERTS ***********')
    list_ca_certs()
    logging.info('*********** END CERTS ***********')

    logging.info('*********** CERT POLICIES ***********')
    list_cert_policies()
    logging.info('*********** END CERT POLICIES ***********')

'''
    Entry point for everything in this directory related to Cert Rotation blog.
'''
def main():
    argp = argparse.ArgumentParser(description='AWS Cert Rotation Blog')
    argp.add_argument('--create', action='store_true', help='--create Create Vendor and Manufacturer self-signed CAs, etc.')
    argp.add_argument('--delete', action='store_true', help='--delete Delete Vendor and Manufacturer self-signed CAs, etc.')

    args = argp.parse_args()

    logging.info('create = {create}, delete = {delete}'.\
        format(create=args.create, delete=args.delete))

    if args.create != args.delete:
        if args.create:
            load_devices_into_dyn_db()
            create_ca_dev()
            gen_files()
            copy_files()

        if args.delete:
            del_ca_dev()
            delete_devices_from_dyn_db()
            remove_files()

    else:
        argp.print_help()

if __name__ == "__main__":
    main()
