from flask import Flask
import json
from typing import Dict, List, Any, Tuple, Set
from collections import Counter, defaultdict
from statistics import mean, median
# from fastapi import FastAPI
import ssl, smtplib, mimetypes
from email.message import EmailMessage

def custom_auto_emailer(_body, _subject='|| Test Mail ||'):
    _context = ssl.create_default_context()
    _host = 'smtp.gmail.com'
    # _host = 'smtp.outlook.com'
    _port = 587
    # _port = 25
    _user = 'anirudh07072003@gmail.com'
    # _user = 'vakalohithreddy2014@gmail.com333@outlook.com'
    with smtplib.SMTP(host=_host, port=_port) as _server:
        _server.starttls(context=_context)
        _server.login(_user, 'fgpl nyno sjsm avdg')
        _server.sendmail(from_addr='anirudh07072003@gmail.com', \
                         to_addrs='vakalohithreddy2014@gmail.com',\
                         msg=f"""Subject: {_subject} 
                                 \n\n {_body}""")
    return True

custom_auto_emailer("lohith","evfdyakfyub")\