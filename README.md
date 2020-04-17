<h1>Introduction</h1>
This repository contains the files for the "Secure and Consistent IoT Device On-
boarding with Just-In-Time-Provisioning (JITP) and Certificate Rotation" blog. 
I ncluded are all the files necessary to create the cloud components, initialize 
the cloud with a device, and simulate the device on-boarding to the cloud. 

IoT Core, IoT Rules, IoT Registered Certificate Authority (CA), IoT Certificates
, IoT Certificate Policies, JITP, IoT Things, Lambda, DynamoDB, Cloud Formation,
 and AWS System Manager (SSM) parameter store are AWS components. Boto3 and AWS 
CLI interface with the cloud. 

OpenSSL command line and OpenSSL python module perform X.509 certificate related
 actions, which include creating self-signed certificate authority (CA) certific
ates, certificate signing requests (CSR), certificates, and private keys. CA 
private keys are stored in SSM parameter store.

First, determine the best S3 bucket name for your deployment following these 
rules:
```
https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules
```
Edit the below file and modify the variable named S3_BUCKET.
```bash
   ~/aws_cloud/cloud_formation/config.bash
```

Three steps to deploy the code:
1) Start cloud formation
```bash
    > cd ~/aws_cloud/cloud_formation
    > bash deploy_cf.bash
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

a) JITP device & certificate
```bash
    > python mqtt_client.py --jitp
```
b) Create manufacturer certificate
```bash
    > python mqtt_client.py --create_cert
```
c) Acknowledge manufacturer certificate
```bash
    > python mqtt_client.py --ack_cert
```

Two steps to cleanup everything in the AWS account:
1) Remove devices and certificates in IoT Core
```bash
    > cd ../aws_cloud/certs_etc
    > python certs_etc —delete
```
2) Tear down cloud formation
```bash
    > cd ../cloud_formation
    > bash delete_cf.bash
```
