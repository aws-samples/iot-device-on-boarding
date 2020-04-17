<h1>Introduction</h1>
<p>This repository contains the files for the "Secure and Consistent IoT Device On-
boarding with Just-In-Time-Provisioning (JITP) and Certificate Rotation" blog. 
I ncluded are all the files necessary to create the cloud components, initialize 
the cloud with a device, and simulate the device on-boarding to the cloud.</p>

<p>IoT Core, IoT Rules, IoT Registered Certificate Authority (CA), IoT Certificates
, IoT Certificate Policies, JITP, IoT Things, Lambda, DynamoDB, Cloud Formation,
 and AWS System Manager (SSM) parameter store are AWS components. Boto3 and AWS 
CLI interface with the cloud.</p>

<p>OpenSSL command line and OpenSSL python module perform X.509 certificate related
 actions, which include creating self-signed certificate authority (CA) certific
ates, certificate signing requests (CSR), certificates, and private keys. CA 
private keys are stored in SSM parameter store.</p>

<h1>Setup</h1>
<p>Install the AWS CLI using these instructions:</p>
'''bash
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
'''

<p>Install OpenSSL command line on the machine acting like the linux device.</p>
```bash
https://www.howtoforge.com/tutorial/how-to-install-openssl-from-source-on-linux/
http://macappstore.org/openssl/
```
<p>For additional tips see this file from the blog code:</p>
```bash
~/aws_cloud/certs_etc/OpenSSLCommands.txt
```

<p>Clone this repository on your MacOS or Linux machine:</p>
```bash
https://github.com/aws-samples/iot-device-on-boarding
```

<p>The directory structure of the code is:</p>
```bash
~/aws_cloud/cloud_formation/cert_rotation_lambda
~/aws_cloud/cloud_formation
~/aws_cloud/certs_etc
~/linux_devce
```
First, determine the best S3 bucket name for your deployment following these rules:

https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules

. Edit the below file and modify the variable named S3_BUCKET.

~/aws_cloud/cloud_formation/config.bash

Create a new virtual python3 environment then source that environment. 
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/python-development-environment.html

Install python modules. 

> cd ~/aws_cloud/certs_etc
> sudo pip3 install -r requirements.txt
> cd ~/linux_device
> sudo pip3 install -r requirements.txt

If installing on a linux machine, then run the following:

> cd ~/aws_cloud/cloud_formation/cert_rotation_lambda
> sudo pip3 install -r requirements.txt -t ./package

If installing on a Mac, then you have to spin-up a docker container to install the lambda python modules to run on ubuntu, which is the default AWS lambda instance. Install docker then, do the following:

> cd ~/aws_cloud/cloud_formation/cert_rotation_lambda
> pwd
> docker run -v _<full path name to cert_rotation_lambda dir__>_:/lambda -it --rm ubuntu
> apt-get update && apt-get install -y -qq python3-pip git && cd /usr/local/bin && ln -s /usr/bin/python3 python && python3 -m pip install --upgrade pip && python3 -m pip install ipython && rm -rf /var/lib/apt/lists/* 
> apt-get update && apt-get install zip 
> cd /lambda
> pip3 install -r requirements.txt -t ./package
> exit


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
