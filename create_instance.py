import boto.ec2
import subprocess as proc
import time

key_pair_name = "newkey1"
#open access key file
with open ("credentials.csv", "r") as myfile:
    data=myfile.readlines()

#line contains 3 fields split by commas
access_key = data[1].split(',')

#connect to us-east-1 using access keys
conn = boto.ec2.connect_to_region("us-east-1", 
       aws_access_key_id = access_key[1].replace('/r/n',''),
       aws_secret_access_key = access_key[2].replace('/r/n','').split()[0])
       
#conn.delete_key_pair(key_pair)       

#create key value pair
try:
    key_pair = conn.create_key_pair(key_pair_name)
    key_pair.save('.')
except Exception as e:
    print e
#save it

#conn.delete_security_group('regular')

#create security group
try:
    sec_group = conn.create_security_group('csc326-group23_test', 'CSC326 Security Group Test')
    print sec_group
except Exception as e:
    rs = conn.get_all_security_groups()
    for i in rs:
        if i.name == 'csc326-group23_test':
            sec_group = i
    print e
#access existing sec group
#rs = conn.get_all_security_groups()
#sec_group = rs[1]

#setup protocols
try: 
    sec_group.authorize('icmp', -1, -1, '0.0.0.0/0')
    sec_group.authorize('tcp', 22, 22, '0.0.0.0/0')
    sec_group.authorize('tcp', 80, 80, '0.0.0.0/0')
    sec_group.authorize('tcp', '8080', '8080', '0.0.0.0/0')
except Exception as e:
    print e

#access existing instances
#instances = conn.get_only_instances()
#list_i = []
#for i in instances :
#    list_i.append(i.id)

#create new instance
reservation = conn.run_instances('ami-8caa1ce4', 
                                key_name=key_pair_name, 
                                instance_type='t1.micro',
                                security_groups=[sec_group.name])
           
#terminate instances given list of instance_id
#conn.terminate_instances(instance_ids=list_i)

instance = reservation.instances[0]

while instance.update() != "running":
    time.sleep(5)

time.sleep(60)
proc.call("scp -i %s.pem -o StrictHostKeyChecking=no -r Lab3-front/ ubuntu@%s:~/" % (key_pair_name, instance.ip_address), shell=True)
proc.Popen(("ssh -i %s.pem ubuntu@%s sudo /bin/bash ~/Lab3-front/install_script.sh" % (key_pair_name, instance.ip_address)).split())

print ("Server is running on %s:8080" % instance.ip_address)