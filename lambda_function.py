import http.client
import json
import ssl
import smtplib
import asyncio
from email_config import *


MESSAGE = """From: AWS Lambda <{0}>
Subject: H-4 Processing Time of {1}
    
{2}
"""

async def get_539_status(service_center, subtype_indice):
    connection = http.client.HTTPSConnection(
        'egov.uscis.gov',
        context=ssl._create_unverified_context()
    )

    connection.request('GET', URI_539.format(service_center), headers=HEADERS)

    response = connection.getresponse()
    json_res = json.loads(response.read().decode())

    messages = []
    for i in range(2):
        info = json_res['data']['processing_time']['subtypes']\
            [subtype_indice[i]]['subtype_info_en']
        date = json_res['data']['processing_time']['subtypes']\
            [subtype_indice[i]]['service_request_date_en']
        messages.append(info)
        messages.append(date)
        messages.append('\n')

    return '\n'.join(messages)

async def get_765_status(service_center, subtype_indice):
    connection = http.client.HTTPSConnection(
        'egov.uscis.gov',
        context=ssl._create_unverified_context()
    )

    connection.request('GET', URI_765.format(service_center), headers=HEADERS)

    response = connection.getresponse()
    json_res = json.loads(response.read().decode())

    messages = []
    info = json_res['data']['processing_time']['subtypes']\
        [subtype_indice[2]]['subtype_info_en']
    date = json_res['data']['processing_time']['subtypes']\
        [subtype_indice[2]]['service_request_date_en']
    messages.append(info)
    messages.append(date)

    return '\n'.join(messages)

def main(service_center):
    indice = SUBTYPE_INDEX.get(service_center)

    loop = asyncio.get_event_loop()
    tasks = get_539_status(service_center, indice), get_765_status(service_center, indice)
    status_539, status_765 = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    status = status_539 + '\n' + status_765

    message = MESSAGE.format(SENDER, CENTER_NAME.get(service_center), status)
    receivers = RECEIVERS.get(service_center)

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(USER, PASS)
        server.sendmail(SENDER, receivers, message)
        server.close()
    except Exception as ex:
        print('Something with SMTP went wrong...')
        print(ex)

def lambda_handler(event, context):
    main(event['service_center'])

if __name__ == "__main__":
    #main('ESC')
    main('SSC')
