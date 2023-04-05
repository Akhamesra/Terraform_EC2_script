from flask import *
from Python_automation import script
app = Flask(__name__)  

app.cli.add_command(script.ses)
app.cli.add_command(script.s3)


