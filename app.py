from flask import *
from Python_modules import ec2_cli
from Python_modules import s3_cli
from Python_modules import ses_cli

app = Flask(__name__)

app.cli.add_command(ses_cli.ses)
app.cli.add_command(s3_cli.s3)
app.cli.add_command(ec2_cli.ec2)


