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

    zip_lambda.bash    

DESCRIPTION

    Zips a lambda function.

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
    lambda_func=$1
    #echo ${lambda_func}
    cd ./${lambda_func}
    rm -f ${lambda_func}.zip
    rm -f ${lambda_func}.zip
    cd ./package
    zip -r9 ${OLDPWD}/${lambda_func}.zip .
    cd $OLDPWD
    zip ${lambda_func}.zip *.py
    cd ..
fi
