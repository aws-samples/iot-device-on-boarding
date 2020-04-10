Copy key and cert from thing directory after running "python Setup.py setup"
Copy RootCA.pem from Amazon.
Get the endpoint from AWS IoT->Settings.

Edit the config.py file set cert files and endpoint.

Edit mqtt-client.py to change the topics, sub, pub, etc.
