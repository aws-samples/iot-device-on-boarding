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
import logging
from config import *
from dyn_db import *
import OpenSSL 
import os


def get_cert_CN(cert_pem_string):
    cn = ''
    try:
        x_509_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem_string)
        subj_obj = x_509_cert.get_subject()
        cn = subj_obj.CN
    except Exception as e:
        logging.error('get_cert_CN(): Exception = {}'.format(str(e)))

    return cn

def get_ca_cert_pem_string(serial_number):
    ca_cert_pem_string = ''
    ca_cert_id =  read_man_ca_cert_id(serial_number)
    if ca_cert_id:
        try:
            client = boto3.client('iot')
            response = client.describe_ca_certificate(certificateId=ca_cert_id)
            certificateDescription = response.get('certificateDescription', None)

            if certificateDescription:
                ca_cert_pem_string = certificateDescription.get('certificatePem', None)
            else:
                logging.error('get_ca_cert_pem_string(): bad certDescription')

        except Exception as e:
            logging.error('get_ca_cert_pem_string(): Exception = {}'.format(str(e)))
    else:
        logging.error('get_ca_cert_pem_string(): bad ca_cert_id')

    return ca_cert_pem_string

def get_ca_key_pem_string(serial_number):
    ca_cert_id =  read_man_ca_cert_id(serial_number)
    return get_secure_store(ca_cert_id)


def create_cert_pem_string(serial_number, csr_pem_string):
    man_cert_pem_str = ''
    ca_cert_pem_string = get_ca_cert_pem_string(serial_number)
    ca_key_pem_string = get_ca_key_pem_string(serial_number)

    if ca_cert_pem_string and ca_key_pem_string:
        try:
            # create csr object from csr_pem_string
            csr_obj = OpenSSL.crypto.load_certificate_request(OpenSSL.crypto.FILETYPE_PEM, csr_pem_string)
            # create ca cert object from ca_cert_pem_string
            ca_cert_obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, 
                ca_cert_pem_string)
            # create ca key object from ca_key_pem_string
            ca_key_obj = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, 
                ca_key_pem_string)

            # create blank man cert object then add to it
            man_cert_obj = OpenSSL.crypto.X509()
            man_cert_obj.gmtime_adj_notBefore(0)
            man_cert_obj.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60) # Expires in 10 years
            man_cert_obj.set_issuer(ca_cert_obj.get_subject())
            man_cert_obj.set_subject(csr_obj.get_subject())
            man_cert_obj.set_pubkey(csr_obj.get_pubkey())
            man_cert_obj.sign(ca_key_obj, 'sha256')

            # Generate serialized pem string from cert object
            man_cert_pem_bytes = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, man_cert_obj)
            man_cert_pem_str = man_cert_pem_bytes.decode()
            man_cert_pem_str = man_cert_pem_str.replace('\\n', '\n')
            
        except Exception as e:
            logging.error('create_cert_pem_string(): Exception = {}'.format(str(e)))
    else:
        logging.error('create_cert_pem_string(): bad pem string.')
        logging.error('\tcert pem = {}'.format(ca_cert_pem_string))
        logging.error('\tkey pem = {}'.format(ca_key_pem_string))

    return man_cert_pem_str

'''
    Get key from secure store 
'''
def get_secure_store(ca_cert_id):

    value = ''

    try:
        client = boto3.client('ssm')
        response = client.get_parameter(\
            Name='cr-ca-key-{}'.format(ca_cert_id),
            WithDecryption=True)

        parameter = response.get('Parameter', None)
        if parameter:
            value = parameter.get('Value', None)
            if not value:
                print('get_secure_store{}: Parameter = {}'.format(parameter))
        else:
            print('get_secure_store{}: repsonse = {}'.format(response))

    except Exception as e:
        print('get_secure_store(): exception = {}'.format(str(e)))

    return value


def get_cert_arn(cert_id):
    cert_arn = None
    client = boto3.client('iot')
    try:
        result = client.describe_certificate(certificateId=cert_id)
    except Exception as e:
        logging.error('get_cert_arn(): Failed describe_certifiacte(): {}'.format(str(e)))
        return cert_arn

    try:
        cert_arn = result['certificateDescription']['certificateArn']

    except Exception as e:
        logging.error('get_cert_arn(): Failed result[certificateDescription][certificateArn]: {}'.format(str(e)))

    return cert_arn

