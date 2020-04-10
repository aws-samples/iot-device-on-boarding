Initialize after starting the cloudformation, then use this script to initialize everthing. 
When completed, use this script to delete whatever was created during initialization and
execution. 

Initialize the Dynamo DB table with a device, create the two self-signed CAs, and create 
the Vendor cert for the device. 

Delete two self signed CAs, Vendor cert (if not already deleted), Manufacturer Cert,
and Thing.


Initialize:
    > python certs_etc.py --create

Cleanup
    > python certs_etc.py --delete
