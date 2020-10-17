# USCIS-Processing-Time-Puller
An AWS Lambda/Python based program that pulling from USCIS Processing Time and send emails to subscribers.

Example of `email_config.py`
```python
# Google:
USER = 'user@gmail.com'
PASS = 'google_password'
SENDER = 'user@gmail.com'
RECEIVERS = [
    "receiver1@gmail.com",
    "receiver2@gmail.com"
]

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587

URI_539 = '/processing-times/api/processingtime/I-539/ESC'
INDEX_539 = 10
URI_765 = '/processing-times/api/processingtime/I-765/ESC'
INDEX_765 = 3

HEADERS = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://egov.uscis.gov/processing-times/'
}
```

Use `create_zip.sh` to generate `aws_lambda.zip` then upload to AWS Lambda.