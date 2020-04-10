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
    This file creates, deletes, and lists CA Certs and Device Certs.

    CA Certs get registered with AWS IOT Core.
    Device Certs get registered as device certs with AWS IOT Core..

    CA Certs can optional be configured JITP, which means that the first time 
    a device connects using a cert from CA with JITP then a message is sent
    to IoT core with the following topic '$aws/events/certificates/registered/'.
'''
import boto3
import os
import argparse
import logging
from config import *
from aws_acct_vals import create_policy_document_text, get_account_id
from device_dyn_db import read_man_cert_id, read_vendor_cert_id

'''
    Local remove with existence check and exception
'''
def local_remove_file(filename):
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except:
            pass

'''
    Create new CA Cert
'''
def new_ca(ca_name, subj_str, days, jitr=False, jitp=False):
    rc = True
    try: 
        # Generate RootCA private key and cert 
        gen_ca_key_cmd = 'openssl genrsa -out {}{}_rootCA.key 2048 >> {} 2>> {} '.format(data_dir, ca_name, ssl_stdout, ssl_stderr)
        ca_subj_str = subj_str.format(ca_name)
        gen_ca_crt_cmd = 'openssl req -x509 -new -nodes -key {}{}_rootCA.key -sha256 -days {} -out {}{}_rootCA.pem -subj \"{}\" >> {} 2>> {}'.\
            format(data_dir, ca_name, days, data_dir, ca_name, ca_subj_str, ssl_stdout, ssl_stderr)

        os.system(gen_ca_key_cmd)
        os.system(gen_ca_crt_cmd)

        # Get CA registration code from AWS
        get_aws_ca_reg_code_cmd = 'aws iot get-registration-code --output text > temp.txt'
        os.system(get_aws_ca_reg_code_cmd)
        with open('temp.txt', 'r') as file:
            reg_code = file.read().replace('\n', '')

        local_remove_file('temp.txt')
        logging.info('reg_code = {}'.format(reg_code))

        # Use reg code to generate verification key, csr, and cert
        ver_crt_subj_str = subj_str.format(reg_code)
        gen_ver_key_cmd = 'openssl genrsa -out verificationCert.key 2048 >> {} 2>> {}'.format(ssl_stdout, ssl_stderr)
        gen_ver_csr_cmd = 'openssl req -new -key verificationCert.key -out verificationCert.csr -subj \"{}\" >> {} 2>> {}'.\
            format(ver_crt_subj_str, ssl_stdout, ssl_stderr)
        gen_ver_crt_cmd = 'openssl x509 -req -in verificationCert.csr -CA {}{}_rootCA.pem -CAkey {}{}_rootCA.key -CAcreateserial -out verificationCert.pem -days {} -sha256 >> {} 2>> {}'.\
            format(data_dir, ca_name, data_dir, ca_name, days, ssl_stdout, ssl_stderr)

        os.system(gen_ver_key_cmd)
        os.system(gen_ver_csr_cmd)
        os.system(gen_ver_crt_cmd)

        # Register the CA with the verification cert 
        reg_ca_cmd = 'aws iot register-ca-certificate --ca-certificate file://{}{}_rootCA.pem --verification-cert file://verificationCert.pem --output text | awk \'{{print $2}}\' > {}{}_ca_cert_id.txt'.\
            format(data_dir, ca_name, data_dir, ca_name)
        os.system(reg_ca_cmd)

        # Remove verification cert files
        local_remove_file('verificationCert.key')
        local_remove_file('verificationCert.csr')
        local_remove_file('verificationCert.pem')

        # Get ca_cert-id
        ca_cert_id_file_name = '{}{}_ca_cert_id.txt'.format(data_dir, ca_name)
        with open(ca_cert_id_file_name, 'r') as file:
            ca_cert_id = file.read().replace('\n', '')

        logging.info('Root ca cert id = {}'.format(ca_cert_id))

        # Activate the rootCA
        act_root_ca_cmd = 'aws iot update-ca-certificate --certificate-id {} --new-status ACTIVE --output json'.\
            format(ca_cert_id)
        os.system(act_root_ca_cmd)

        if jitr:
            # Enable Just-in-time-registration (JITR) on the CA
            jitr_enable_cmd = 'aws iot update-ca-certificate --certificate-id {} --new-auto-registration-status ENABLE'.\
                format(ca_cert_id)
            os.system(jitr_enable_cmd)
        if jitp:
            # Enable Just-in-time-provisioning (JITP) on the CA
            logging.info('*********** JITP ***************')

            # Get the policy and replace current account number
            account_id = get_account_id()

            with open(jitp_filename) as f:
              data = f.read()

            data = data.replace('BLOG_ACCNT', account_id)

            with open('./temp.txt', 'w') as f:
              f.write(data)

            jitp_enable_cmd = 'aws iot update-ca-certificate --certificate-id {} --new-auto-registration-status ENABLE --registration-config file://./temp.txt'.format(ca_cert_id)
            os.system(jitp_enable_cmd)
            local_remove_file('temp.txt')

    except Exception as e:
        logging.error('new_ca(): Exception = {}'.format(str(e)))
        rc = False
    return rc

'''
    Create new Device Cert
'''
def new_dev(ca_name, dev, subj_str, days, policy_name, jitr=False, jitp=False):

    rc = True
    try: 
        # Generate device key, csr, and cert
        dev_subj_str = subj_str.format(dev)

        if ca_name == 'Manufacturer':
            dev = '{}_man'.format(dev)
        else:
            dev = '{}_ven'.format(dev)

        gen_dev_key_cmd = 'openssl genrsa -out {}{}.key 2048 >> {} 2>> {} '.\
            format(data_dir, dev, ssl_stdout, ssl_stderr)
        gen_dev_csr_cmd = 'openssl req -new -key {}{}.key -out {}{}.csr -subj \"{}\">> {} 2>> {}  '.\
            format(data_dir, dev, data_dir, dev, dev_subj_str, ssl_stdout, ssl_stderr)
        gen_dev_crt_cmd = 'openssl x509 -req -in {}{}.csr -CA {}{}_rootCA.pem -CAkey {}{}_rootCA.key -CAcreateserial -out {}{}.pem -days {} -sha256>> {} 2>> {} '.\
            format(data_dir, dev, data_dir, ca_name, data_dir, ca_name, data_dir, dev, days, ssl_stdout, ssl_stderr)
        os.system(gen_dev_key_cmd)
        os.system(gen_dev_csr_cmd)
        os.system(gen_dev_crt_cmd)

        if not jitr and not jitp:
            # Register and activate the cert in AWS unless this is a JITR cert or JITP cert
            reg_dev_cmd = 'aws iot register-certificate --certificate-pem file://{}{}.pem --ca-certificate-pem file://{}{}_rootCA.pem --set-as-active --output text | awk \'{{print $2}}\' > {}{}_cert_id.txt'.format(data_dir, dev, data_dir, ca_name, data_dir, dev)
            os.system(reg_dev_cmd)

            cert_id_filename = '{}{}_cert_id.txt'.format(data_dir, dev)
            with open(cert_id_filename,'r') as cert_id_file:
                cert_id = cert_id_file.read().replace('\n', '')

            attach_cert_policy(cert_id, policy_name)

    except Exception as e:
        logging.error('new_dev(): Exception = {}'.format(str(e)))
        rc = False
    return rc

'''
    Attach Cert Policy to Cert
'''
def attach_cert_policy(cert_id, policy_name):
    client = boto3.client('iot')

    cert_arn = get_cert_arn(cert_id)

    if cert_arn:
        try:
            client.attach_policy(policyName=policy_name, target=cert_arn)
        except Exception as e:
            logging.error('attach_cert_policy(): Failed attach_policy(): {}'.format(str(e)))
    else:
        logging.info('attach_cert_policy(): no arn for cert_id {}'.format(cert_id))

'''
    Detach Cert Policy from Cert
'''
def detach_policy(cert_id, policy_name):

    logging.info('detach_policy(): cert_id = {}, policy_name = {}'.format(cert_id, policy_name))

    cert_arn = get_cert_arn(cert_id)

    if cert_arn:
        client = boto3.client('iot')
        try:
            result = client.detach_policy(policyName=policy_name, target=cert_arn)
            logging.info('detach_policy(): result = {}'.format(result))

        except Exception as e:
            logging.error('detach_policy(): Failed describe_certifiacte(): {}'.format(str(e)))
    else:
        logging.info('detach_policy(): no arn for cert_id {}'.format(cert_id))

'''
    Delete CA Cert
'''
def del_ca(ca_name):

    rc = True
    try: 
        # Get the cert-id
        file_name = '{}{}_ca_cert_id.txt'.format(data_dir, ca_name)
        with open(file_name, 'r') as file:
            ca_cert_id = file.read().replace('\n', '')

        logging.info('Root ca cert id = {}'.format(ca_cert_id))

        # Deativate and delete the rootCA on AWS
        act_root_ca_cmd = 'aws iot update-ca-certificate --certificate-id {} --new-status INACTIVE --output json'.format(ca_cert_id)
        os.system(act_root_ca_cmd)

        del_ca_cert_cmd = 'aws iot delete-ca-certificate --certificate-id {}'.format(ca_cert_id)
        os.system(del_ca_cert_cmd)
        
    except Exception as e:
        logging.error('del_ca(): Exception = {}'.format(str(e)))
        rc = False

    return rc

'''
    Delete Device, Cert, and detach Policy
'''
def del_dev(dev, policy_name):
    logging.info('del_dev = {}'.format(dev))
    rc = True

    try:
        manufacturer_cert_id = read_man_cert_id(dev)
        logging.info('man cert {}'.format(manufacturer_cert_id))
        if manufacturer_cert_id:
            detach_policy(manufacturer_cert_id, policy_name)
            del_cert(manufacturer_cert_id, dev)
    except Exception as e:
        logging.error('del_dev(): Del man cert  = {}'.format(str(e)))
        rc = False
    
    try:
        vendor_cert_id = read_vendor_cert_id(dev)
        logging.info('vend cert {}'.format(vendor_cert_id))
        if vendor_cert_id:
            detach_policy(vendor_cert_id, policy_name)
            del_cert(vendor_cert_id, dev)
    except Exception as e:
        logging.error('del_dev(): Del vendor cert = {}'.format(str(e)))
        rc = False

    try:
        del_thing(dev)
    except Exception as e:
        logging.error('del_dev(): Del thing = {}'.format(str(e)))
        rc = False

    return rc


'''
    Delete Thing
'''
def del_thing(thing_name):
    logging.info('delete thing {}'.format(thing_name))
    try: 
        client = boto3.client('iot')
        client.delete_thing(thingName=thing_name)
    except Exception as e:
        logging.error('del_thing(): Thing delete exception: {}'.format(str(e)))

'''
    Delete Cert 
'''
def del_cert(cert_id, dev):
    logging.info('delete cert {} {}'.format(cert_id, dev))
    try: 
        client = boto3.client('iot')
    except Exception as e:
        logging.error('del_cert(): Failed boto3.client(): {}'.format(str(e)))

    cert_arn = get_cert_arn(cert_id)

    if cert_arn:
        try:
            client.detach_thing_principal(thingName=dev, principal=cert_arn)
        except Exception as e:
            logging.error('del_cert(): Failed detach_thing_principal(): {}'.format(str(e)))
            return

        try:
            client.update_certificate(certificateId=cert_id, newStatus='INACTIVE')
        except Exception as e:
            logging.error('del_cert(): Failed update_certificate(): {}'.format(str(e)))
            return

        try:
            client.delete_certificate(certificateId=cert_id, forceDelete=True)
        except Exception as e:
            logging.error('del_cert(): Cert delete exception: {}'.format(str(e)))
            return
    else:
        logging.info('del_cert(): no arn for cert_id {}'.format(cert_id))

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

'''
    List CA Certs
'''
def list_ca_certs():
    # aws iot describe-ca-certificate --certificate-id <cert-id>
    list_ca_certs_cmd = 'aws iot list-ca-certificates --output json'
    os.system(list_ca_certs_cmd)

'''
    List Device Certs
'''
def list_dev_certs():
    # aws iot describe-certificate --certificate-id <cert-id>
    list_ca_certs_cmd = 'aws iot list-certificates --output json'
    os.system(list_ca_certs_cmd)

'''
    List Cert Policies
'''
def list_cert_policies():
    # aws iot describe-certificate --certificate-id <cert-id>
    list_cert_policies_cmd = 'aws iot list-policies --output json'
    os.system(list_cert_policies_cmd)

'''
    Delete from secure store 
'''
def del_secure_store(ca_name):
    try: 

        ca_cert_id_file_name = '{}{}_ca_cert_id.txt'.format(data_dir, ca_name)
        with open(ca_cert_id_file_name, 'r') as file:
            ca_cert_id = file.read().replace('\n', '')

        client = boto3.client('ssm')
        response = client.delete_parameter(Name='cr-ca-key-{}'.format(ca_cert_id))

        logging.info('delete_secure_store(): delete_parameter_response = {}'.format(str(response)))

    except Exception as e:
        logging.error('delete_secure_store(): exception = {}'.format(str(e)))

'''
    Get key from secure store 
'''
def get_secure_store(ca_name):
    try: 
        ca_cert_id_file_name = '{}{}_ca_cert_id.txt'.format(data_dir, ca_name)
        with open(ca_cert_id_file_name, 'r') as file:
            ca_cert_id = file.read().replace('\n', '')

        client = boto3.client('ssm')
        response = client.get_parameter(\
            Name='cr-ca-key-{}'.format(ca_cert_id),
            WithDecryption=True)

        logging.info('get_secure_store(): get_parameter_response = {}'.format(str(response)))

    except Exception as e:
        logging.error('get_secure_store(): exception = {}'.format(str(e)))


'''
    Securely store the Ca private key
'''
def put_secure_store(ca_name):

    try:
        with open('{}{}_rootCA.key'.format(data_dir, ca_name)) as f:
            private_key = f.read()

        ca_cert_id_file_name = '{}{}_ca_cert_id.txt'.format(data_dir, ca_name)
        with open(ca_cert_id_file_name, 'r') as file:
            ca_cert_id = file.read().replace('\n', '')
        file.close()

        client = boto3.client('ssm')
        response = client.put_parameter(\
            Name='cr-ca-key-{}'.format(ca_cert_id),
            Description='{} CA private key'.format(ca_name),
            Value=private_key,
            Type='SecureString')
        
        logging.info('put_secure_stores(): put_parameter_response = {}'.format(str(response)))

    except Exception as e:
        logging.error('put_secure_store(): exception = {}'.format(str(e)))

