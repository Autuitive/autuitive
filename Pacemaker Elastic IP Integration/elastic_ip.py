#!/usr/bin/python
# -*- coding: utf-8 -*-

import ocfagent.agent, ocfagent.error, ocfagent.parameter
import os
from boto3.session import Session

os.environ['OCF_ROOT'] = '/usr/lib/ocf/'

# You can do what I did and store your elastic IP and instance ID in a file somewhere locally. I did this to make PCS easier to deploy automatically.
# Alternatively, replace everything after "=" with a string containing the correct information.
instance_id = open('/etc/aws/instance_id').read().strip()
elastic_ip = open('/etc/aws/elastic_ip').read().strip()

# Obviously, replace "XXX" with your access and secret key.
session = Session(aws_access_key_id='XXX',
                  aws_secret_access_key='XXX',
                  region_name='us-east-1')

ec2 = session.client('ec2')

class ElasticIP(ocfagent.agent.ResourceAgent):
    '''
    AWS EC2 Elastic IP OCF Agent
    '''
    
    VERSION = '1.0'
    SHORTDESC = 'AWS EC2 Elastic IP OCF Agent'
    LONGDESC = ('This is an OCF resource for automatically migrating elastic '
                'IP\'s between instances, allowing for automatic HA failover of '
                'EC2 instances.')
    
    def address_status(self):
        d = ec2.describe_addresses(PublicIps=[elastic_ip])
        
        # Check if the elastic IP is assigned to the current instance.
        try:
            if d['Addresses'][0]['InstanceId'] == instance_id:
                return True
        
            else:
                return False
        
        except (KeyError, IndexError):
            return False
    
    def handle_start(self, timeout=10):
        if self.address_status():
            raise ocfagent.error.OCFSuccess('Elastic IP already assigned to this instance.')
        
        else:
            ec2.associate_address(InstanceId=instance_id,
                                  PublicIp=elastic_ip,
                                  AllowReassociation=True)
            
            raise ocfagent.error.OCFSuccess('Elastic IP assigned to this instance successfully!')
    
    def handle_stop(self, timeout=10):
        if not self.address_status():
            raise ocfagent.error.OCFSuccess('Elastic IP already not assigned to this instance.')
        
        else:
            ec2.disassociate_address(PublicIp=elastic_ip)
            
            raise ocfagent.error.OCFSuccess('Elastic IP removed from this instance successfully!')
            
    def handle_monitor(self, timeout=10):
        if self.address_status():
            raise ocfagent.error.OCFSuccess('Elastic IP assigned to this instance.')
        
        else:
            raise ocfagent.error.OCFNotRunning('Elastic IP not assigned to this instance.')

if __name__ == '__main__':
    ocf = ElasticIP(testmode=False)
    ocf.cmdline_call()
    
