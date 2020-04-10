This directory contains the files that are part of the "Secure and Consistent IoT Device On-boarding with Just-In-Time-Provisioning (JITP) and Certificate Rotation"
blog. This directory has all the files necessary to create the cloud components, initialize the cloud with a device, and simulate the device on-boarding to the cloud. 

AWS Services and functionality utilized by this code include Cloudformation, IoT Core, IoT Rule, Iot Registered CAs, Lambda, DynamoDB, SSM parameter store. Boto3 and AWS CLI interface with the cloud. OpenSSL command line and python module create certficate authority certs, certifiactes, and certificate signing requests. The CA private keys are securely stored in the ssm parameter store.

Before starting edit one file to make a globally unique S3 bucket name.  Change S3_BUCKET in:

'''bash
   ~/aws_cloud/cloud_formation/config.bash
'''


Three steps to deploy the code:

1) Start cloud formation

'''bash
    > cd ~/aws_cloud/cloud_formation
    > bash deploy.bash
'''


2) Initialize the system

    > cd ~/aws_cloud/cloud_formation

    > python certs_etc.py --create

3) On board the linux device

    > cd ~/linux_device


Device on-boarding has three steps:

a) JITP device & cert

    > python mqtt_client.py --jitp

b) Create manufacturer cert

    > python mqtt_client.py --create_cert

c) Acknowledge manufacturer cert

    > python mqtt_client.py --ack_cert


Two steps to cleanup everything in the AWS account:

1) Remove devices and certs in IoT Core

    > cd ../aws_cloud/certs_etc

    > python certs_etc —delete

2) Tear down cloud formation

    > cd ../cloud_formation

    > bash delete_cf.bash
        

