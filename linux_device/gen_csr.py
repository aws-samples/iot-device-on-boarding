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
import boto3
import os
import logging
from config import *

'''
    Create CSR, cert, private key
'''
def gen_cert_info():

    dev = serial_number
    existing_private_key = serial_number
    ca_name = manufacturer_ca_name
    dev_subj_str = manufacture_subj_str.format(dev)
    days = 365*10

    try: 
        gen_dev_csr_cmd = 'openssl req -new -key {}{}_ven.key -out {}{}.csr -subj \"{}\">> {} 2>> {}  '.\
            format(data_dir, existing_private_key, data_dir, dev, dev_subj_str, ssl_stdout, ssl_stderr)
        logging.info('gen csr cmd = {}'.format(gen_dev_csr_cmd))
        os.system(gen_dev_csr_cmd)

    except Exception as e:
        logging.error('gen_cert_info(): Exception = {}'.format(str(e)))


def unit_test():
    gen_cert_info()
    copy_cert_key_s3()

if __name__ == '__main__':
    unit_test()
