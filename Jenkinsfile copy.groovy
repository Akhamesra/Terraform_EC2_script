pipeline {
    agent {node {label "${env.AGENT_LABEL}"}}
    environment{
        FLASK_APP='app'
    }
    stage('Setup Flask CLI Project') {
            steps {
                script{
                    //Git Credentials
                    // NonProdGitCredentialsId = 'gitlabapicaller'
                    ProdGitCredentialsId = 'gitlabapicaller'

                    FLASKCLI = "source venv/bin/activate && flask "
                    ENVIRONMENT = "${ENVIRONMENT}"

                    if(ENVIRONMENT == "PROD"){
                        ENVIRONMENT = "prd"
                        BUCKET_NAME = "bfsd-prod-envconfigs-mum"
                        GitCredentialsId = ProdGitCredentialsId
                        AWS_ARN = 574680025548
                    }
                    
                }
            }
        }

    stages {
        stage('Code checkout'){
            steps{
                git branch: 'main', credentialsId: ProdGitCredentialsId, url: 'https://github.com/Akhamesra/Terraform_EC2_script.git'
                echo 'Code Checkout Done'
                sh 'pip3 install virtualenv' 
              	sh 'python3 -m virtualenv venv'
               	sh 'source venv/bin/activate && pip3 install -r requirements.txt'
                // sh 'source venv/bin/activate && sudo yum install -y yum-utils'
            }
        }
        stage('set variables'){
            steps{
                script{
                    TERRAFORM = 'cd terraform_modules/EC2 && terraform '
                    instancecount = "-var instance_count=${instance_count} "
                    amiid = "-var ami=${AMI_ID} "
                    instancetype = "-var instancetype=${Instance_type} "
                    
                    run = "${env.Run}"
                    batch = "${env.Batch}"
                    instancecountnumber = "${instance_count}"
                    
                }
            }
        }
        
        stage ("Launch EC2 instances") {
            steps {
                script{
                    if(run=='Launch'){
                        def flaskOutput = sh(returnStdout: true, script: FLASKCLI+' ec2 choosesubnet -i '+instancecountnumber)
                        def subnetid = flaskOutput.replaceAll("\\s+", "")
                        sh FLASKCLI+" s3 downloadFile"
                        sh 'echo "Batch - $(cat terraform_modules/EC2/next_batch_number)" >> terraform_modules/EC2/instance_ips.txt'
                        sh TERRAFORM+' init -reconfigure -backend-config=backend.hcl -backend-config="key=batch$(cat next_batch_number)/terraform.tfstate"'
                        sh TERRAFORM+" apply " + instancecount + amiid + instancetype + "-var subnetid=${subnetid} --auto-approve"
                        sh FLASK+" s3 uploadFile"
                        sh FLASK+" ses sendLaunchMail --number_of_ec2 "+instancecountnumber
                    }
                    else{

                        sh TERRAFORM+ ' init -reconfigure -backend-config=backend.hcl -backend-config=key=batch'+batch+'/terraform.tfstate'
                        sh TERRAFORM+ ' plan -destroy -out=file'
                        sh TERRAFORM+ ' show -json file > file1.json'
                        sh TERRAFORM+ ' destroy --auto-approve'
                        if(batch=="1"){
                            sh FLASK+' s3 deleteFile'
                        }
                        sh FLASK+" ses sendTerminateMail"
                    }
                }
           }
        }
    }
    
}