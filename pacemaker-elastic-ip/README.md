# Pacemaker + AWS Elastic IP Integration

* Copy the elastic_ip.py file and the ocfagent/ directory into /usr/lib/ocf/resource.d/pacemaker/
* Rename the file to elastic-ip (This is optional, but it makes life easier later.)
* Update the following variables within the script to match your environment:
  * instance_id
  * elastic_ip
  * aws_access_key_id
  * aws_secret_access_key
* Once that's done, feel free to create a resource based on you newly installed agent: `pcs resource create vip ocf:pacemaker:elastic-ip op monitor interval=5s`

