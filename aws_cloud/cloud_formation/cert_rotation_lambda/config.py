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

    All config variables and constants for the all lambda processing
'''

from botocore.config import Config

import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)

##############################################################
# Cert Rotation states stored in State field of DynamoDB table
#
# All other values defined in seqence diagram in the blog.
CR_WHITELISTED = 'CR_WHITELISTED' 
CR_THING_CREATED = 'CR_THING_CREATED'
CR_MAN_CERT_CREATED = 'CR_MAN_CERT_CREATED'
CR_CERT_ROTATION_COMPLETED = 'CR_CERT_ROTATION_COMPLETED'

cr_states = [
    CR_WHITELISTED,
    CR_THING_CREATED,
    CR_MAN_CERT_CREATED,
    CR_CERT_ROTATION_COMPLETED
    ]

######################
# Cert Policy names
cert_pol_name_in_prog  = 'CrInProgressCertPolicy'
cert_pol_name_complete  = 'CrCertRotationCompleteCertPolicy'

pub_retries = Config(retries={'max_attempts': 4})
