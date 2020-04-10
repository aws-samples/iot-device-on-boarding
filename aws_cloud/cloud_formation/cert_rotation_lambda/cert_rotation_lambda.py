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
    filename: cert_rotation_lambda.py

    IoT rules trigger this lambda. Descriptions for 
    each is below. 
'''
import boto3
import datetime
from dyn_db import *
import logging
from config import *
from cr_rules import *
from cr_rules_misc import *
from certs import *

def cert_rotation_lambda(event, context):
    topic = event.get('topic', None)
    data = event.get('data', None)
    client_id = event.get('client_id', None)
    cert_id = event.get('cert_id', None)

    logging.info('data = {}'.format(data))
    logging.info('topic = {}'.format(topic))
    logging.info('client_id = {}'.format(client_id))
    logging.info('cert_id = {}'.format(cert_id))

    if topic :
        if '$aws/events/certificates/registered' in topic:
            # Note: client_id not available, thus serial number not easily availale
            # Extract serial number from the cert pem file.
            cert_id = data.get('certificateId', None)
            cert_pem_string = get_cert_pem(cert_id)
            serial_number = get_cert_CN(cert_pem_string)
            cr_state = read_state(serial_number)
            if cr_state == CR_WHITELISTED :
                write_state(serial_number, CR_THING_CREATED)
                write_vendor_cert_id(serial_number, cert_id)

        else:
            topic_arr = topic.split('/')
            serial_number = topic_arr[-2]
            cr_state = read_state(serial_number)

            if '/cert-rotation/create-man-cert/{}/rqst'.format(serial_number) in topic:
                if cr_state == CR_THING_CREATED :
                    if cr_rule_create_man_cert(data.get('csr', None), serial_number):
                        write_state(serial_number, CR_MAN_CERT_CREATED)
                elif cr_state == CR_MAN_CERT_CREATED:
                    # Device didn't get the response  message, republish response
                    cr_rule_create_man_cert(data.get('csr', None), serial_number, re_pub=True)
                else: 
                    logging.info('CR_THING_CREATED topic, but state not correct')

            elif '/cert-rotation/ack-man-cert/{}/rqst'.format(serial_number) in topic:
                if cr_state == CR_MAN_CERT_CREATED:
                    if cr_rule_ack_man_cert(serial_number, data.get('cert_id', None)):
                        write_state(serial_number, CR_CERT_ROTATION_COMPLETED)
                elif cr_state == CR_CERT_ROTATION_COMPLETED:
                    # Device didn't get the message, republish
                    cr_rule_ack_man_cert(serial_number, data.get('cert_id', None), re_pub=True)
                else: 
                    logging.info('CR_MAN_CERT_CREATED topic, but state not correct')

            else:
                logging.info('Error. None of the topics matched the rules.')

    return
