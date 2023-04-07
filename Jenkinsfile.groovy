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
                    instance_count = "${instance_count}"
                    email = "${Email}"
                    run = "${env.Run}"
                    batch = "${env.Batch}"
                }
            }
        }
        
        stage ("terraform apply") {
            steps {
                script{
                    if(run=='Launch'){
                        
                        sh "flask s3 downloadFile"
                        sh 'cd terraform_modules/EC2 && terraform init -reconfigure -backend-config=backend.hcl -backend-config="key=batch$(cat number)/terraform.tfstate"'
                        sh "cd terraform_modules/EC2 && terraform apply -var instance_count="+instance_count+" --auto-approve"
                        sh "flask s3 uploadFile"
                        sh "flask ses sendLaunchMail --email "+email+" --number_of_ec2 "+instance_count
                    }
                    else{
                        sh 'cd terraform_modules/EC2 && terraform init -reconfigure -backend-config=backend.hcl -backend-config=key=batch'+batch+'/terraform.tfstate'
                        sh terraform+ 'plan -destroy -out=file'
                        sh terraform+ 'show -json file > file1.json'
                        sh terraform+ 'destroy --auto-approve'
                        // sh "flask s3 deleteFile"
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