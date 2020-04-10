cd ../aws_cloud/certs_etc
python certs_etc.py --delete
python certs_etc.py --create
cd ../../linux_device
python mqtt_client.py --jitp
python mqtt_client.py --create
python mqtt_client.py --ack
