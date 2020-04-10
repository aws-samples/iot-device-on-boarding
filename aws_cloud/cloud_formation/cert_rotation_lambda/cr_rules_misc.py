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
#

import boto3
import logging
from config import *
from certs import *
import os
import json

def get_ca_cert_id(cert_id):
    client = boto3.client('iot')
    ca_cert_id = None
    try:
        result = client.describe_certificate(certificateId=cert_id)
        ca_cert_id = result['certificateDescription']['caCertificateId']

    except Exception as e:
        logging.error('jitr_iot_rule(): Failed describe_certifiacte(): {}'.format(str(e)))
    
    return ca_cert_id


def get_cert_arn(cert_id):
    cert_arn = None
    client = boto3.client('iot')
    try:
        result = client.describe_certificate(certificateId=cert_id)
    except Exception as e:
        logging.error('get_cert_arn(): Failed describe_certifiacte(): {}'.format(str(e)))

    try:
        cert_arn = result['certificateDescription']['certificateArn']

    except Exception as e:
        logging.error('get_cert_arn(): Failed result[certificateDescription][certificateArn]: {}'.format(str(e)))

    return cert_arn

def get_cert_pem(cert_id):
    cert_pem = None
    client = boto3.client('iot')
    try:
        result = client.describe_certificate(certificateId=cert_id)
    except Exception as e:
        logging.error('get_cert_arn(): Failed describe_certifiacte(): {}'.format(str(e)))

    try:
        cert_pem = result['certificateDescription']['certificatePem']

    except Exception as e:
        logging.error('get_cert_pem(): Failed result[certificateDescription][certificatePem]: {}'.format(str(e)))

    return cert_pem

'''
    Detach Cert Policy from Cert
'''
def detach_policy(cert_id, policy_name):

    logging.info('detach_policy(): cert_id = {}, policy_name = {}'.format(cert_id, policy_name))

    cert_arn = get_cert_arn(cert_id)

    client = boto3.client('iot')
    try:
        result = client.detach_policy(policyName=policy_name, target=cert_arn)
        logging.info('detach_policy(): result = {}'.format(result))

    except Exception as e:
        logging.error('detach_policy(): Failed describe_certifiacte(): {}'.format(str(e)))

'''
    Attach Cert Policy to Cert
'''
def attach_policy(cert_id, policy_name):

    logging.info('attach_policy(): cert_id = {}, policy_name = {}'.format(cert_id, policy_name))

    cert_arn = get_cert_arn(cert_id)

    client = boto3.client('iot')

    try:
        result = client.attach_policy(policyName=policy_name, target=cert_arn)
        logging.info('attach_policy(): result = {}'.format(result))
    except Exception as e:
        logging.error('attach_cert_policy(): Failed attach_policy(): {}'.format(str(e)))


'''
    Create a certificate based on CSR using the Manufacture CA
    Attach policy to cert
    Return cert arn
'''
def create_man_cert(csr, serial_number):
    # or just read the cert from an S3 bucket ... for now
    man_cert_arn = ''
    man_cert_id = ''
    man_cert_pem_string = ''
    man_cert_key_string = ''

    man_ca_cert_pem_string = get_ca_cert_pem_string(serial_number)
    man_cert_pem_string = create_cert_pem_string(serial_number, csr)

    if man_ca_cert_pem_string and man_cert_pem_string:
        try:
            client = boto3.client('iot')

            response = client.register_certificate(
                certificatePem=man_cert_pem_string,
                caCertificatePem=man_ca_cert_pem_string,
                setAsActive=True)
                #status='ACTIVE')

            man_cert_arn = response['certificateArn']
            man_cert_id = response['certificateId']
            logging.info('man_cert_arn = {}'.format(man_cert_arn))
            logging.info('man_cert_id = {}'.format(man_cert_id))

            attach_policy(man_cert_id, cert_pol_name_complete)

        except Exception as e:
            logging.error('create_man_cert(): Failed register_certificate(): {}'.format(str(e)))
        
    else:
        logging.error('create_man_cert(): pem string.')
        logging.error('\tman ca cert pem string = {}'.format(man_ca_cert_pem_string ))
        logging.error('\tman cert pem string = {}'.format(man_cert_pem_string ))

    return man_cert_arn, man_cert_id, man_cert_pem_string 

def describe_endpoint():
    client = boto3.client('iot')
    endpoint = client.describe_endpoint(endpointType='iot:Data-ATS')
    return endpoint['endpointAddress']

def get_account_id():
    client = boto3.client('sts')
    aws_account_id = client.get_caller_identity()['Account']
    return aws_account_id.strip('\n')

def get_aws_region():
    my_session = boto3.session.Session()
    aws_region = my_session.region_name
    return aws_region.strip('\n')

