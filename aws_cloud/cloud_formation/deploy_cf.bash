#!/bin/bash
# MIT No Attribution
# 
# Copyright Amazon Web Services
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


set -e

function help_message {
    cat << EOF

NAME

    cfn_deploy.bash    

DESCRIPTION

    Deploys cloud formation for the Cert Rotation Blog

MANDATORY ARGUMENTS:

    None

OPTIONAL ARGUMENTS:

    -h - help

DEPENDENCIES REQUIRED:

    aws-cli
    
EOF
}

if [ "$1" = "-h" ] || [ "$1" = "-help" ] ; then
    help_message
else
    . ./config.bash
    . ./zip_lambda.bash ${CERT_ROTATION_LAMBDA_NAME}

    function bucketstatus { aws s3api head-bucket --bucket ${S3_BUCKET} 2>&1  | grep 'Not Found' | awk '{print $4}'; }
    if [[ $(bucketstatus) == "(404)" ]] ;
    then
      echo "Bucket doesn't exist. Making bucket ${S3_BUCKET}";
      function getRegion { aws configure get region ; }
      region=$(getRegion)
      aws s3 mb s3://${S3_BUCKET} --region ${region};
    fi

    aws s3 cp ${CERT_ROTATION_LAMBDA_NAME}/${CERT_ROTATION_LAMBDA_ZIP_NAME} s3://${S3_BUCKET}

    echo "Deploy CertRotation Cloudformation"
    aws cloudformation deploy \
      --template-file cfn_cert_rotation.json \
      --parameter-overrides \
        CertRotationLambdaName=${CERT_ROTATION_LAMBDA_NAME} \
        CertRotationLambdaZipName=${CERT_ROTATION_LAMBDA_ZIP_NAME} \
        S3BucketName=${S3_BUCKET} \
      --stack-name CertRotationStack \
      --capabilities CAPABILITY_NAMED_IAM

fi
