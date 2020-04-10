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
 filename: mqtt_client.py

 MQTT client. 

 MQTT connections 1, 2, and 3 for the Cert Rotation Blog.
    - jitp - just-in-time-provisioning
    - create_cert - Create Manufacturer Cert
    - ack_cert - Ack Manufacturer Cert 

'''
import time
import argparse
import datetime
import os
import json
import paho
import paho.mqtt.client as mqtt
import ssl
import logging
from config import *
from gen_csr import *
from aws_acct_vals import get_endpoint

#############################
WAIT_SUB = 5 # Give time for MQTT sub to complete
WAIT_PUB = 10 # Give time for MQTT pub to complete
WAIT_CONNECT = 10 # Give time for MQTT connect to complete
WAIT_JITP_ATTEMPT = 10 # Wait between JITP attempts
WAIT_MAN_CERT_ATTEMPT = 10 # Wait between MAN_CERT attempts
JITP_ATTEMPTS = 10 # JITP attempts 
MAN_CERT_ATTEMPTS = 5 # MAN_CERT attempts

class MQTTClient(mqtt.Client):
    """ 
    Class for Thing MQTT connection 

    Note: A second instance of this class using an client_id with active
    connection connection closes the first connection. MQTT only allows one
    connection for a client id at a time.

    """
    def __init__(self, client_id, cert_filename):
        """
        Create the mqtt connection for a Thing
        """
        super().__init__(client_id)
        self.sub_flag=False
        self.pub_flag=False
        self.connect_flag=False
        self.disconnect_flag=False
        self.create_man_cert_flag = False
        self.ack_man_cert_flag = False
        self.man_cert_pem = ''
        self.man_cert_id = ''
        self.pub_msg_count=0
        self.rcv_msg_count=0
        self.sub_topics = []
        try :
            self.mqttc = mqtt.Client(client_id=client_id)

            self.mqttc.on_log = self.on_log
            self.mqttc.on_connect = self.on_connect
            self.mqttc.on_disconnect = self.on_disconnect
            self.mqttc.on_message = self.on_message
            self.mqttc.on_publish = self.on_publish
            self.mqttc.on_subscribe = self.on_subscribe
            self.mqttc.on_unsubscribe = self.on_unsubscribe

            logging.info('__init__(): MQTT connection: key = {}, cert = {}, ca = {}'.\
                format(cert_filename, vendor_key_filename, \
                aws_rootca_filename))

            rc = self.mqttc.tls_set(certfile=cert_filename, keyfile=vendor_key_filename, ca_certs=aws_rootca_filename, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

            logging.info('__init__(): MQTT tls_set rc = {}'.format(rc))

            aws_endpoint = get_endpoint()
            rc = self.mqttc.connect(aws_endpoint, 8883, keepalive=120)
            logging.info('__init__(): MQTT Connect rc = {}'.format(rc))

            self.mqttc.loop_start()
            time.sleep(WAIT_CONNECT)
        except Exception as e:
            logging.error("__init__(): MQTT connect exception: {}".format(str(e)))
            self.mqttc = None

    def on_connect(self, mqttc, obj, flags, rc): 
        if self.sub_topics:
            self.mqtt_sub(self.sub_topics)
        if rc == 0:
            self.connect_flag=True
            self.disconnect_flag=False
        logging.info('on_connect(): rc = {}'.format(rc))

    def on_disconnect(self, mqttc, obj, rc): 
        self.disconnect_flag=True
        self.connect_flag=False
        self.sub_flag = False
        self.pub_flag = False

        logging.info('on_disconnect(): rc = {}'.format(rc))

    def on_message_ack_man_cert(self, msg):
        payload_dict = json.loads(msg.payload)
        logging.info('on_message_ack_man_cert : payload dict keys = {}'.format(payload_dict.keys()))
        if 'cert_id' in payload_dict :
            self.ack_man_cert_flag = True
            self.man_cert_id = payload_dict['cert_id']
        logging.info('on_message_ack_man_cert(): ack_man_cert_flag = {}'.\
            format(self.ack_man_cert_flag))

    def on_message_create_man_cert(self, msg):
        payload_dict = json.loads(msg.payload)
        logging.info('on_message_create_man_cert: payload dict keys = {}'.format(payload_dict.keys()))
        if 'pem' in payload_dict:
            self.create_man_cert_flag = True
            self.man_cert_pem = payload_dict['pem']
            self.man_cert_id = payload_dict['cert_id']
            self.create_man_cert_flag = True
        logging.info('on_message_create_man_cert(): create_man_cert_flag = {}'.\
            format(self.create_man_cert_flag))

    def on_message(self, mqttc, obj, msg):
        self.rcv_msg_count += 1
        # Topic is:
        if '/cert-rotation/create-man-cert/{}/rspn'.format(serial_number)\
            in msg.topic:
                logging.info('on_message_create_man_cert match ')
                self.on_message_create_man_cert(msg)
        elif '/cert-rotation/ack-man-cert/{}/rspn'.format(serial_number)\
            in msg.topic:
                logging.info('on_message_ack_man_cert match ')
                self.on_message_ack_man_cert(msg)
        logging.info('on_message(): ********************************')
        logging.info('on_message(): topic = {}, qos = {}, msg = {}'.
            format (msg.topic, msg.qos, msg.payload))

    def on_publish(self, mqttc, obj, mid):
        self.pub_msg_count += 1
        self.pub_flag=False
        logging.info('on_publish(): mid: {}'.format(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.sub_flag=True
        logging.info('on_subscribe(): mid = {}, granted qos = {}'.
            format(mid, granted_qos))

    def on_unsubscribe(self, mqttc, userdata, mid):
        self.sub_flag=False
        logging.info('on_subscribe(): userdata = {}, mid = {}'.
            format(userdata ,mid))

    def on_log(self, mqttc, obj, level, string):
        if 'CONNACK' in string:
            self.connect_flag = True
        logging.info('on_log(): msg: {}'.format(string))
        logging.info('log flags: connect {}, disconnect {}, pub = {}, sub = {}, rcv cnt = {}, pub cnt = {}, '.format(self.connect_flag, self.disconnect_flag, self.pub_flag, self.sub_flag, self.rcv_msg_count, self.pub_msg_count))

    def mqtt_sub(self, sub_topics):
        """
        Subscribe to topics
        """
        if sub_topics:
            self.sub_topics += sub_topics

        for topic in sub_topics:
            try:
                logging.info('mqtt_sub(): {}'.format(topic))
                result, mid = self.mqttc.subscribe(topic, qos=1)
                logging.info('mqtt_sub(): result = {}, mid = {}'.\
                    format(result, mid))
                time.sleep(WAIT_SUB)
            except Exception as e:
                logging.error("mqtt_sub(): MQTT Sub connect execption: {}".format(str(e)))

    def mqtt_unsub(self):
        """
        Unsubscribe to topics
        """
        for topic in self.sub_topics:
            try:
                logging.info('mqtt_unsub(): {}'.format(topic))
                self.sub_flag = False
                self.mqttc.unsubscribe(topic)
                time.sleep(WAIT_SUB)
            except Exception as e:
                logging.error("mqtt_unsub(): MQTT unsub connect execption: {}".format(str(e)))
        self.sub_topics = []

    def mqtt_pub(self, topic, msg):
        """
        Publish msg to topic
        """

        if self.sub_topics:
            while not self.sub_flag:
                # wait for subscribe to complete
                time.sleep(WAIT_PUB)

        try:
            logging.info('mqtt pub: topic = {}'.format(topic))
            self.pub_flag = True
            self.mqttc.publish(topic, json.dumps(msg), qos=1)
            time.sleep(WAIT_PUB)
        except Exception as e:
            logging.error("MQTT Pub connect execption: {}".format(str(e)))

    def create_man_cert(self):
        rc = False

        sub_topics = ['/cert-rotation/create-man-cert/{}/rspn'.\
                format(serial_number)]

        pub_topic = '/cert-rotation/create-man-cert/{}/rqst'.\
            format(serial_number)

        with open ('{}{}.csr'.format(data_dir, serial_number), 'r') as f:
            csr_text = f.read()

        logging.info('csr = {:.40}'.format(csr_text))

        value = {'csr':'{}'.format(csr_text)}
        for i in range(MAN_CERT_ATTEMPTS):
            # Man Cert Pub attempts
            self.create_man_cert_flag = False
            if not self.sub_flag:
                self.mqtt_sub(sub_topics)
                time.sleep(WAIT_SUB)
            if self.sub_flag:
                self.mqtt_pub(pub_topic, value)
            time.sleep(WAIT_MAN_CERT_ATTEMPT)
            if self.create_man_cert_flag:
                rc = True
                break
        return rc

    def ack_man_cert(self):
        rc = False

        sub_topics = ['/cert-rotation/ack-man-cert/{}/rspn'.\
                format(serial_number)]

        pub_topic = '/cert-rotation/ack-man-cert/{}/rqst'.\
            format(serial_number)

        with open('{}{}_man_cert_id.txt'.format(data_dir, serial_number), 'r') as f:
            cert_id_text = f.read().replace('\n', '')

        logging.info('man cert id = {}'.format(cert_id_text))
        value = {'cert_id':'{}'.format(cert_id_text)}
        for i in range(MAN_CERT_ATTEMPTS):
            # Man Cert Pub attempts
            self.ack_man_cert_flag = False
            if not self.sub_flag:
                self.mqtt_sub(sub_topics)
                time.sleep(WAIT_SUB)
            if self.sub_flag:
                self.mqtt_pub(pub_topic, value)
            time.sleep(WAIT_MAN_CERT_ATTEMPT)
            if self.ack_man_cert_flag :
                rc = True
                break
        return rc

'''
    Just-in-time-provisioning - activate cert, attach policy, create thing, attach cert to thing
'''
def jitp():
    logging.info('*********** Start JITP  ***********')
    for i in range(JITP_ATTEMPTS):
        mqtt_client = MQTTClient(serial_number, \
            vendor_device_cert_and_cacert_filename)
        if mqtt_client.connect_flag:
            # JITP process complete
            logging.info('********** JITP Successful ***********')
            break
        else:
            logging.info('---------JITP attempt {} failed --------.'.format(i))
            time.sleep(WAIT_JITP_ATTEMPT)
    mqtt_client.disconnect()

'''
    Connection 2: gen & send CSR, receive Manufacturer Cert 
'''
def create_cert():
    logging.info('************* Manufacturer Cert Create start ************')
    gen_cert_info()
    for i in range(MAN_CERT_ATTEMPTS):
        # Connection attempts
        mqtt_client = MQTTClient(serial_number, \
            vendor_device_cert_and_cacert_filename)
        if mqtt_client.connect_flag:
            if mqtt_client.create_man_cert():
                logging.info('*********** Manufacturer Cert Create Success **************')
                logging.info('pem = {:.20}'.format(mqtt_client.man_cert_pem))
                logging.info('cert_id = {:.10}'.format(mqtt_client.man_cert_id))
                with open('{}{}_man_cert_id.txt'.format(data_dir, serial_number), 'w') as f:
                    f.write(mqtt_client.man_cert_id)

                with open('{}{}_man.pem'.format(data_dir, serial_number), 'w') as f:
                    f.write(mqtt_client.man_cert_pem)

                break
        logging.info('--------- Manufacturer Cert Create attempt {} failed --------.'.format(i))
        mqtt_client.disconnect()
        time.sleep(WAIT_MAN_CERT_ATTEMPT)

'''
    Connection 3: Connect with new cert
'''
def ack_cert():
    logging.info('************* Manufacturer Cert ACK start ************')
    cat_cmd = 'cat ./data_io/{}_man.pem ./data_io/Manucfacturer_rootCA.pem > ./data_io/ManufacturerDeviceCertAndCACert.pem'.format(serial_number)
    os.system(cat_cmd)

    for i in range(MAN_CERT_ATTEMPTS):
        # Connection attempts
        mqtt_client = MQTTClient(serial_number, \
            manufacturer_device_cert_and_cacert_filename)
        if mqtt_client.connect_flag:
            if mqtt_client.ack_man_cert():
                logging.info('*********** Manufacturer Cert ACK Success **************')
                logging.info('cert_id = {:.20}'.format(mqtt_client.man_cert_id))
                break
        logging.info('--------- Manufacturer Cert ACK attempt {} failed --------.'.format(i))
        mqtt_client.disconnect()
        time.sleep(WAIT_MAN_CERT_ATTEMPT)


def main():
    argp = argparse.ArgumentParser(description='AWS Cert Rotation Blog')
    argp.add_argument('--jitp', action='store_true', help='--jitp JITP')
    argp.add_argument('--create_cert', action='store_true', help='--create_cert - Create Man Cert')
    argp.add_argument('--ack_cert', action='store_true', help='--ack_cert - Ack Man Cert')
    argp.add_argument('--delete', action='store_true', help='--delete Delete and Cleanup')

    args = argp.parse_args()

    logging.info('jitp = {jitp}, create_cert = {create_cert}, ack_cert = {ack_cert}, delete = {delete}'.\
        format(jitp=args.jitp, create_cert=args.create_cert, ack_cert=args.ack_cert, delete=args.delete))

    if args.delete:
        cleanup()
    else :
        if args.jitp and not args.create_cert and not args.ack_cert:
            jitp()
        elif args.create_cert and not args.jitp and not args.ack_cert:
            create_cert()
        elif args.ack_cert and not args.jitp and not args.create_cert:
            ack_cert()
        else:
            logging.info('No MQTT Connection')

if __name__ == "__main__":
    main()
