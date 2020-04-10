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
  filename: mqtt_config.py

  Config file for MQTT client. 
'''
import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

# TLS connection cert related files
data_dir = './data_io/'

######################################################
# Remove when key generation happens on the cloud lambda
ssl_stdout = '{}open_ssl_stdout.txt'.format(data_dir)
ssl_stderr = '{}open_ssl_stderr.txt'.format(data_dir)

######################################################
# These values should be automatically generated from
# ~/aws_cloud/certs_etc/certs_etc.py
manufacture_subj_str='/C=US/ST=Kansas/L=Kansas City/O=MCICoffeMaker/OU=Manufacturing/CN={}'
serial_number='IUQWXALODJESC1'
manufacturer_ca_name='Manufacturer'
######################################################

vendor_device_cert_and_cacert_filename='{}VendorDeviceCertAndCACert.pem'.format(data_dir)
manufacturer_device_cert_and_cacert_filename='{}ManufacturerDeviceCertAndCACert.pem'.format(data_dir)

vendor_cert_filename='{}{}_ven.pem'.format(data_dir, serial_number)
vendor_key_filename='{}{}_ven.key'.format(data_dir, serial_number)

manufacturer_rootCA_filename='{}{}_rootCA.pem'.format(data_dir, manufacturer_ca_name)
manufacturer_cert_filename='{}{}_man.pem'.format(data_dir, serial_number)

aws_rootca_filename='{}RootCA.pem'.format(data_dir)

