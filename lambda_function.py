import http.client
import json
import ssl
import smtplib
import asyncio
from email_config import *


MESSAGE = """From: Jinglong Wu <{0}>
Subject: H-4 Processing Time of {1}
    
{2}
"""

CASE_STATUS_MESSAGE = """From: Jinglong Wu <{0}>
Subject: H-4 Case Status
"""

def send_email(message, receivers):
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

def processing_times(service_center):
    indice = SUBTYPE_INDEX.get(service_center)

    loop = asyncio.get_event_loop()
    tasks = get_539_status(service_center, indice), get_765_status(service_center, indice)
    status_539, status_765 = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    status = status_539 + '\n' + status_765

    message = MESSAGE.format(SENDER, CENTER_NAME.get(service_center), status)
    receivers = RECEIVERS.get(service_center)

    send_email(message, receivers)

def get_case_status(receipt_num):
    connection = http.client.HTTPSConnection(
        'egov.uscis.gov',
        context=ssl._create_unverified_context()
    )

    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://egov.uscis.gov",
        "Content-Length": 133,
        "Referer": "https://egov.uscis.gov/casestatus/mycasestatus.do"
    }

    data = ("changeLocale=&completedActionsCurrentPage=0&upcomingActionsCurrentPage=0"
            "&appReceiptNum={}&caseStatusSearchBtn=CHECK+STATUS").format(receipt_num)

    connection.request('POST', '/casestatus/mycasestatus.do', data, header)

    response = connection.getresponse()
    html = response.read().decode()

    import re
    pattern = \
        r'<div class="rows text-center">\s*<h1>(.*)<\/h1>\s*<p>(.*)If you move,.*<\/p>\s*<\/div>'
    matches = re.search(pattern, html)
    if matches:
        return matches.group(1), matches.group(2)

    return "Regex not match", "Regex not match"

def case_status(receipt_nums):
    message = CASE_STATUS_MESSAGE
    for num in receipt_nums:
        status, details = get_case_status(num)
        message += num +"\n\n"+status+"\n\n"+details+"\n\n--------------------------\n\n"

    send_email(message, [CASE_STATUS_RECEIVER])


def lambda_handler(event, context):
    print(event)
    if 'service_center' in event:
        processing_times(event['service_center'])
    if 'receipt_nums' in event:
        case_status(event['receipt_nums'])

if __name__ == "__main__":
    processing_times('ESC')
    #case_status("")
