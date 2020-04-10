This repository contains the files for the "Secure and Consistent IoT Device On-boarding with Just-In-Time-Provisioning (JITP) and Certificate Rotation" blog. Included are all the files necessary to create the cloud components, initialize the cloud with a device, and simulate the device on-boarding to the cloud. 

Cloudformation, IoT Core, IoT Rule, Iot Registered CAs, Lambda, DynamoDB, SSM parameter store are AWS components. Boto3 and AWS CLI interface with the cloud. OpenSSL command line and python module create certficate authority certs, certifiactes, and certificate signing requests. The CA private keys are securely stored in the SSM parameter store.

First, determine the best S3 bucket name for your deployment. The S3 bucket name has to be globally unique amongst all other s3 buckets in AWS, so choose a unique name. The name must be lower case letters, dashes, no underscores. Edit the below file and modify the variable named S3_BUCKET.
```bash
   ~/aws_cloud/cloud_formation/config.bash
```

Three steps to deploy the code:
1) Start cloud formation
```bash
    > cd ~/aws_cloud/cloud_formation
    > bash deploy.bash
```
2) Initialize the system
```bash
    > cd ~/aws_cloud/cloud_formation
    > python certs_etc.py --create
```
3) On board the linux device
```bash
    > cd ~/linux_device
```
Device on-boarding has three steps:
a) JITP device & cert
```bash
    > python mqtt_client.py --jitp
```
b) Create manufacturer cert
```bash
    > python mqtt_client.py --create_cert
```
c) Acknowledge manufacturer cert
```bash
    > python mqtt_client.py --ack_cert
```

Two steps to cleanup everything in the AWS account:
1) Remove devices and certs in IoT Core
```bash
    > cd ../aws_cloud/certs_etc
    > python certs_etc —delete
```
2) Tear down cloud formation
```bash
    > cd ../cloud_formation
    > bash delete_cf.bash
```
