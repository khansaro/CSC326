#!/usr/bin/python
import boto.ec2
import sys

if len(sys.argv) != 2:
    print "incorrect number of arguments"
    print "Usage: python delete_instance.py <instance_id>"
    sys.exit()
    
instance_id = sys.argv[1]
print instance_id

try:
    with open ("credentials.csv", "r") as myfile:
        data=myfile.readlines()
except Exception as e:
    print e
    sys.exit()

#line contains 3 fields split by commas
access_key = data[1].split(',')

#connect to us-east-1 using access keys
conn = boto.ec2.connect_to_region("us-east-1", 
                                  aws_access_key_id = access_key[1].replace('/r/n',''),
                                  aws_secret_access_key = access_key[2].replace('/r/n','').split()[0])

                                  
ls = conn.terminate_instances(instance_id.split())

if ls[0].id == instance_id:
    print "Termination successful"
else:
    print "Termination unsuccessful. Try again with correct instance id"
    
