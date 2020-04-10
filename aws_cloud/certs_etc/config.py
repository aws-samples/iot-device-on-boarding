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
    filename: config.py

    Variables and constants used across multiple files or commonly 
    changed by developer.
'''

import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

###################################
# Constants manually copied from ~/cloud_formation/config.bash
#
CERT_ROTATION_LAMBDA_NAME='cert_rotation_lambda'
CERT_ROTATION_LAMBDA_ZIP_NAME='cert_rotation_lambda.zip'
LAMBDA_ROLE_NAME='cert_rotation_lambda_role'
DDB_NAME='CertRotationDevices'
###################################

###################################
# Date input and output variables
###################################
data_dir = './data_io/'
ca_list_filename = '{}ca_list.json'.format(data_dir)
#ca_list_filename = '{}ca_list_test1.json'.format(data_dir) # Test 2 of 4 jitr & device option
#ca_list_filename = '{}ca_list_test2.json'.format(data_dir) # Test 2 of 4 jitr & device option
device_list_filename = '{}device_list.json'.format(data_dir)
jitp_filename = '{}jitp.txt'.format(data_dir)

ssl_stdout = '{}open_ssl_stdout.txt'.format(data_dir)
ssl_stderr = '{}open_ssl_stderr.txt'.format(data_dir)

serial_number = 'IUQWXALODJESC1'
