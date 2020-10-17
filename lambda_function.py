import http.client
import json
import ssl
import smtplib
import asyncio
from email_config import *


MESSAGE = """From: AWS Lambda <{0}>
Subject: H-4 Processing Time
    
{1}
"""

async def get_h4_status(uri, subtype_index):
    connection = http.client.HTTPSConnection(
        'egov.uscis.gov',
        context=ssl._create_unverified_context()
    )

    connection.request('GET', uri, headers=HEADERS)

    response = connection.getresponse()
    json_res = json.loads(response.read().decode())

    info = json_res['data']['processing_time']['subtypes'][subtype_index]['subtype_info_en']
    date = json_res['data']['processing_time']['subtypes'][subtype_index]['service_request_date_en']

    return "{0}\n{1}\n".format(info, date)

def main():
    loop = asyncio.get_event_loop()
    tasks = get_h4_status(URI_539, INDEX_539), get_h4_status(URI_765, INDEX_765)
    status_539, status_765 = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    status = status_539 + '\n' + status_765

    message = MESSAGE.format(SENDER, status)

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(USER, PASS)
        server.sendmail(SENDER, RECEIVERS, message)
        server.close()
    except Exception as ex:
        print('Something with SMTP went wrong...')
        print(ex)

def lambda_handler(event, context):
    main()

if __name__ == "__main__":
    main()
