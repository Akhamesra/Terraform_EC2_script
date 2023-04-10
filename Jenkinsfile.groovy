pipeline {
    agent {node {label "${env.AGENT_LABEL}"}}
    environment{
        FLASK_APP='app'
    }
    stages {
        stage('Code checkout'){
            steps{
                git branch: 'main', credentialsId: 'github', url: 'https://github.com/Akhamesra/Terraform_EC2_script.git'
                echo 'Code Checkout Done'
            }
        }
        stage('set variables'){
            steps{
                script{
                    terraform = 'cd terraform_modules/EC2 && terraform '
                    instancecount = "-var instance_count=${instance_count} "
                    amiid = "-var ami=${AMI_ID} "
                    instancetype = "-var instancetype=${Instance_type} "
                    
                    run = "${env.Run}"
                    batch = "${env.Batch}"
                    instancecountnumber = "${instance_count}"
                    
                }
            }
        }
        
        stage ("terraform apply") {
            steps {
                script{
                    if(run=='Launch'){
                        def flaskOutput = sh(returnStdout: true, script: 'flask ec2 choosesubnet -i '+instancecountnumber)
                        def subnetid = flaskOutput.replaceAll("\\s+", "")
                        sh "flask s3 downloadFile"
                        sh 'echo "Batch - $(cat terraform_modules/EC2/number)" >> terraform_modules/EC2/instance_ips.txt'
                        sh terraform+' init -reconfigure -backend-config=backend.hcl -backend-config="key=batch$(cat number)/terraform.tfstate"'
                        sh terraform+" apply " + instancecount + amiid + instancetype + "-var subnetid=${subnetid} --auto-approve"
                        sh "flask s3 uploadFile"
                        sh "flask ses sendLaunchMail --number_of_ec2 "+instancecountnumber
                    }
                    else{

                        sh terraform+ ' init -reconfigure -backend-config=backend.hcl -backend-config=key=batch'+batch+'/terraform.tfstate'
                        sh terraform+ ' plan -destroy -out=file'
                        sh terraform+ ' show -json file > file1.json'
                        sh terraform+ ' destroy --auto-approve'
                        if(batch=="1"){
                            sh 'flask s3 deleteFile'
                        }
                        sh "flask ses sendTerminateMail"
                    }
                }
           }
        }
    }
    
}