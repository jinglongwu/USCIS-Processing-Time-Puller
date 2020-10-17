# USCIS-Processing-Time-Puller
An AWS Lambda/Python based program that pulling from USCIS Processing Time and send emails to subscribers.

Example of `email_config.py`
```python
# Google:
USER = 'user@gmail.com'
PASS = 'googlepassword'
SENDER = 'user@gmail.com'

RECEIVERS = {
    'ESC': [
        "user1@gmail.com",
        "user2@gmail.com",
    ],
    'CSC': [
        'user2@gmail.com',
        'user2@nyu.edu',
    ],
    'SSC':[
        'user1@gmail.com'
    ]
}

CENTER_NAME = {
    'ESE': 'Vermont Service Center',
    'CSC': 'California Service Center',
    'SSC': 'Texas Service Center'
}

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587

SUBTYPE_INDEX = {
    'ESC': (10, 6, 3),
    'CSC': (1, 6, 2),
    'SSC': (1, 6, 2)
}

URI_539 = '/processing-times/api/processingtime/I-539/{0}'
URI_765 = '/processing-times/api/processingtime/I-765/{0}'

HEADERS = {
        'Content-type': 'application/json',
        'Referer': 'https://egov.uscis.gov/processing-times/'
}

```

Use `create_zip.sh` to generate `aws_lambda.zip` then upload to AWS Lambda.

The event should have `service_center` as input tag with value of ESC/CSC/SSC etc.