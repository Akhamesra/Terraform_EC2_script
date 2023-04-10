from flask import *
from Python_automation import ec2_cli
from Python_automation import s3_cli
from Python_automation import ses_cli

app = Flask(__name__)

app.cli.add_command(ses_cli.ses)
app.cli.add_command(s3_cli.s3)
app.cli.add_command(ec2_cli.ec2)


