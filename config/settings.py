bucketname = "akshitkhamesraautomation"

subnets = ['subnet-01e6a2019fe516e70','subnet-041e7143956b0843e']
# subnets = ['subnet-0f40d98eed0d61400','subnet-069aa9597e563e52e']

objectnumber = { 'name' : 'next_batch_number',
                'paths3' : 'automation/analytics/airflow-automated-provision/', #s3/path
                'pathlocal' : 'terraform_modules/EC2/'} #local/path

objectip = { 'name' : 'instance_ips.txt',
             'paths3' : 'automation/analytics/airflow-automated-provision/',   #s3/path
             'pathlocal' : 'terraform_modules/EC2/'} #local/path

sender = { 'name' : 'Akshit',
           'email': 'akhamesra31@gmail.com'}

recipients = ['akhamesra31@gmail.com']
