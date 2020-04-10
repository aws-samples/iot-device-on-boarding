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
    filename: jitr.py

    Jitr rule processing
'''
import boto3
import logging
from config import *
from cr_rules_misc import *
from certs import *
import json
from dyn_db import write_man_cert_id, read_man_cert_id, write_vendor_cert_id, read_vendor_cert_id

'''
    cr_rule_create_man_cert():
        rcv CSR
        generate new certificate
        register cert
        attach policy to cert
        write cert id to DB
        publish new certificate to '/cert-rotation/create-man-cert/{}/rspn'.\
'''
def cr_rule_create_man_cert(csr, serial_number, re_pub=False):

    logging.info('Enter cr_rule_create_man_cert')

    rc = False
    thing_name = serial_number

    man_cert_arn = ''
    man_cert_pem_string = ''

    man_cert_id = read_man_cert_id(serial_number)

    if man_cert_id == '' and not re_pub:
        # No stored cert id and no rep, so go create the man cert
        man_cert_arn, man_cert_id, man_cert_pem_string = create_man_cert(csr, serial_number)

        try:
            client = boto3.client('iot')
        except Exception as e:
            logging.error('cr_rule_create_man_cert(): Failed to boto3.client: {}'.format(str(e)))
            return rc

        try:
            result = client.attach_thing_principal(thingName=thing_name, principal=man_cert_arn)
        except Exception as e:
            logging.error('cr_rule_create_man_cert(): Failed attach_thing_principal(): {}'.format(str(e)))
            return rc

        write_man_cert_id(serial_number, man_cert_id)

    elif man_cert_id != '' and re_pub:
        man_cert_pem_string  = get_cert_pem(man_cert_id)
        if man_cert_pem_string == '':
            logging.info('cr_rule_create_man_cert(): No man cert key or pem on re-pub. Unknown state.')
            return rc
    else:
        logging.info('cr_rule_create_man_cert(): No man cert id on re-pub or man cert on no rep. Unknown state.')
        return rc

    if man_cert_pem_string != '' and man_cert_id != '':
        topic = '/cert-rotation/create-man-cert/{}/rspn'.\
            format(serial_number)
        logging.info('cr_rule_create_man_cert(): topic = {}'.format(topic))

        message = {}
        message.update({'pem':man_cert_pem_string})
        message.update({'cert_id':man_cert_id})


        logging.info('cr_rule_create_man_cert(): pem = {:.60}'.format(message.get('pem', None)))
        logging.info('cr_rule_create_man_cert(): cert_id = {:.10}'.format(message.get('cert_id', None)))

        try:
            client = boto3.client('iot-data', config=pub_retries)
            client.publish(topic=topic, qos=1, payload=json.dumps(message))
            rc = True
        except Exception as e:
            logging.error('cr_rule_create_man_cert(): Failed to publish message: {}'.format(str(e)))

    return rc

'''
    cr_rule_ack_man_cert():
'''
def cr_rule_ack_man_cert(serial_number, msg_cert_id, re_pub=False):

    logging.info('Enter cr_rule_ack_man_cert')

    rc = False
    thing_name = serial_number

    man_cert_arn = ''
    man_cert_pem_string = ''
    man_cert_key_string = ''

    man_cert_id = read_man_cert_id(serial_number)
    if man_cert_id == msg_cert_id:

        vendor_cert_id = read_vendor_cert_id(serial_number)
        vendor_cert_arn = get_cert_arn(vendor_cert_id)

        logging.info('vendor_cert_id = {}'.format(vendor_cert_id))
        logging.info('vendor_cert_arn = {}'.format(vendor_cert_arn))
        logging.info('thing_name = {}'.format(thing_name))

        try:
            client = boto3.client('iot')
        except Exception as e:
            logging.error('cr_rule_ack_man_cert(): Failed to boto3.client: {}'.format(str(e)))
            return rc

        try:
            result = client.detach_thing_principal(thingName=thing_name, principal=vendor_cert_arn)
        except Exception as e:
            logging.error('cr_rule_ack_man_cert(): Failed detach_thing_principal(): {}'.format(str(e)))
            return rc

        try:
            client.update_certificate(certificateId=vendor_cert_id, newStatus='INACTIVE')
        except Exception as e:
            logging.error('cr_rule_ack_man_cert(): Failed update_certificate(): {}'.format(str(e)))
            return rc

        try:
            client.delete_certificate(certificateId=vendor_cert_id, forceDelete=True)
        except Exception as e:
            logging.error('cr_rule_ack_man_cert(): Failed delete_certificate(): {}'.format(str(e)))
            return rc

        # Delete the si vendor cert id entry from the db.
        write_vendor_cert_id(serial_number, None)

        topic = '/cert-rotation/ack-man-cert/{}/rspn'.\
            format(serial_number)
        logging.info('cr_rule_ack_man_cert(): topic = {}'.format(topic))
        message = {'cert_id':man_cert_id}

        logging.info('cr_rule_ack_man_cert(): cert_id = {:.10}'.format(message.get('cert_id', None)))

        try:
            client = boto3.client('iot-data', config=pub_retries)
            client.publish(topic=topic, qos=1, payload=json.dumps(message))
            rc = True
        except Exception as e:
            logging.error('cr_rule_ack_man_cert(): Failed to publish message: {}'.format(str(e)))

    return rc
