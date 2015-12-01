import boto.ec2

#open access key file
with open ("credentials.csv", "r") as myfile:
    data=myfile.readlines()

#line contains 3 fields split by commas
access_key = data[1].split(',')

#connect to us-east-1 using access keys
conn = boto.ec2.connect_to_region("us-east-1", 
       aws_access_key_id = access_key[1].replace('/r/n',''),
       aws_secret_access_key = access_key[2].replace('/r/n','').split()[0])
       
#conn.delete_key_pair('newkey')       

#create key value pair
key_pair = conn.create_key_pair('newkey')
#save it
key_pair.save('.')

#conn.delete_security_group('regular')

#create security group
sec_group = conn.create_security_group('csc326-group23', 'CSC326 Security Group')

#access existing sec group
rs = conn.get_all_security_groups()
sec_group = rs[1]

#setup protocols
sec_group.authorize('icmp', -1, -1, '0.0.0.0/0')
sec_group.authorize('tcp', 22, 22, '0.0.0.0/0')
sec_group.authorize('tcp', 80, 80, '0.0.0.0/0')

#access existing instances
#instances = conn.get_only_instances()
#list_i = []
#for i in instances :
#    list_i.append(i.id)

#create new instance
instance = conn.run_instances('ami-8caa1ce4', 
                   key_name='newkey', 
		   instance_type='t1.micro',
		   security_groups=['regular'])

#terminate instances given list of instance_id
#conn.terminate_instances(instance_ids=list_i)


