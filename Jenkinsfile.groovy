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
                    
                    email = "${Email}"
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
                        sh "flask s3 downloadFile"
                        sh terraform+' init -reconfigure -backend-config=backend.hcl -backend-config="key=batch$(cat number)/terraform.tfstate"'
                        sh terraform+" apply " + instancecount + amiid + instancetype + " --auto-approve"
                        sh "flask s3 uploadFile"
                        sh "flask ses sendLaunchMail --email "+email+" --number_of_ec2 "+instancecountnumber
                    }
                    else{

                        sh terraform+ ' init -reconfigure -backend-config=backend.hcl -backend-config=key=batch'+batch+'/terraform.tfstate'
                        sh terraform+ ' plan -destroy -out=file'
                        sh terraform+ ' show -json file > file1.json'
                        sh terraform+ ' destroy --auto-approve'
                        if(batch=="1"){
                            sh 'flask s3 deleteFile'
                        }
                        sh "flask ses sendTerminateMail --email "+email
                    }
                }
           }
        }
    }
    post{
        failure{
            sh 'echo This batch is not found.'
        }
    }
}