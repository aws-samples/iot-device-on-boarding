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
    filename: manage_files.py

    Copy and delete files to/from S3, linux_device, and afr_device
    Gen and delete config files used in linux_device, and afr_device

'''

import os
import shutil
import aws_acct_vals
import logging
from config import *
import boto3
import json

'''
    Generate the to_filename_list and the from_filename_list
'''
def gen_filename_lists(to_dir, from_dir, filename_list):
    to_filename_list = []
    from_filename_list = []
    for filename in filename_list:
        to_filename_list.append('{}{}'.format(to_dir, filename))
        from_filename_list.append('{}{}'.format(from_dir, filename))
    return to_filename_list, from_filename_list

'''
    Generate the list of filenames to be moved into linux_device/data_io
'''
def gen_linux_device_filename_lists(remove=False):
    to_dir = './../../linux_device/data_io/'
    from_dir = './data_io/'
    filename_list = [
        'VendorDeviceCertAndCACert.pem',
        '{}_ven.pem'.format(serial_number),
        '{}_ven.key'.format(serial_number)
        ]
    if remove:
        filename_list.append('open_ssl_stdout.txt')
        filename_list.append('open_ssl_stderr.txt')
        filename_list.append('{}_man.csr'.format(serial_number))
        filename_list.append('{}_man.key'.format(serial_number))
        filename_list.append('{}_man.pem'.format(serial_number))
        filename_list.append('{}_man_cert_id.txt'.format(serial_number))
        filename_list.append('{}_man_fake.key'.format(serial_number))
        filename_list.append('{}_man_fake.pem'.format(serial_number))
        filename_list.append('ManufacturerDeviceCertAndCACert.pem')
        filename_list.append('Manufacturer_rootCA.srl')
        filename_list.append('{}_ven.csr'.format(serial_number))
        filename_list.append('{}.csr'.format(serial_number))
        filename_list.append('Manufacturer_rootCA.pem')
        filename_list.append('Manufacturer_rootCA.key')
        filename_list.append('Manufacturer_ca_cert_id.txt')
        filename_list.append('Vendor_rootCA.pem')
        filename_list.append('Vendor_rootCA.key')
        filename_list.append('Vendor_rootCA.srl')
        filename_list.append('Vendor_ca_cert_id.txt')

    return gen_filename_lists(to_dir, from_dir, filename_list)


'''
    Copy files 
'''
def copy_dir_files(to_filename_list, from_filename_list):
    # Verify counts of lists match
    if (len(to_filename_list) == len(from_filename_list)):
        to_dir = os.path.dirname(to_filename_list[0])
        from_dir = os.path.dirname(from_filename_list[0])
        file_cnt = len(to_filename_list)

        # Verify the to directory exists
        if os.path.exists(to_dir) and os.path.exists(from_dir):
            for to_file, from_file in \
                zip(to_filename_list, from_filename_list):

                # Verify from file exists
                if os.path.exists(from_file):
                    try:
                        shutil.copy(from_file, to_file)
                    except Exception as e:
                        logging.error('copy_dir_files(): shutil.copy file = {}, excpetion = {}'.format(from_file, str(e)))
                        pass
                else:
                    logging.info('copy_dir_files(): from file does not exists: file = {}'.format(from_file))
        else:
            logging.info('copy_dir_files(): to or from directory does not exists: to = {}, from = {}'.format(to_dir, from_dir))
    else:
        logging.info('copy_dir_files(): lists do not have matching counts')


'''
    Remove files after verifying the exist
'''
def remove_dir_files(filename_list):
    for filename in filename_list:
        if os.path.exists(filename):
            os.remove(filename)

'''
    Copy files to S3_bucket, linux_device/data_io, afr_device/data_io
'''
def copy_files():

    copy_dir_files(*(gen_linux_device_filename_lists()))


'''
    Remove files from S3_bucket, linux_device/data_io, afr_device/data_io
'''
def remove_files():
    # S3 files are deleted when the S3 bucket is deleted using --force

    to_filename_list, from_filename_list = \
            gen_linux_device_filename_lists(remove=True)
    remove_dir_files(to_filename_list)
    remove_dir_files(from_filename_list)

'''
    Generate files for linux_device
'''
def gen_linux_device_files():
    cat_cmd = 'cat ./data_io/{}_ven.pem ./data_io/Vendor_rootCA.pem > ./data_io/VendorDeviceCertAndCACert.pem'.format(serial_number)
    os.system(cat_cmd)

'''
    Generate files for afr_device
'''
def gen_afr_device_files():
    dummy = 0

'''
    Generate files for S3_bucket, linux_device/data_io, afr_device/data_io
'''
def gen_files():
    gen_linux_device_files()
    gen_afr_device_files()

def get_account_id():
    client = boto3.client('sts')
    aws_account_id = client.get_caller_identity()['Account']
    return aws_account_id.strip('\n')

def get_aws_region():
    my_session = boto3.session.Session()
    aws_region = my_session.region_name
    return aws_region.strip('\n')
