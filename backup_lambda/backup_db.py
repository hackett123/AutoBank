"""
Script runs in AWS Lambda daily. How it works:

S3 bucket is named "autobank-abababa". The directory structure is year -> month -> day in format YYYY/MM/DD.
Within this folder we have a file for purchases and a file for interpayments. The absence of a file means nothing occurred on
that day.

Backup pulls yesterday's data (so that we have the full 24 hours) and uploads it to s3. The script will execute sometime
during day n to reflect and backup day n-1.

Prerequirements: OS variables must be set

Assumptions: We assume and hardcode the name of the mysql db and table names. We assume RDS variables will remain constant.
"""

import boto3
import json
import os
import pymysql
import datetime

BUCKET_NAME = 'autobank-abababa'

def get_yesterday_dt():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    return yesterday

def determine_path():
    yesterday = get_yesterday_dt()
    year, month, day = yesterday.strftime('%Y-%m-%d').split('-')
    path = f'{year}/{month}/{day}'
    print(path)
    return path

def get_rows_to_str(table_name):
    yesterday = get_yesterday_dt().date()
    day = yesterday.day
    month = yesterday.month
    year = yesterday.year

    # cursor object executes a query and stores the result in itself, which is an iterator.
    connection = pymysql.connect(host=os.environ['RDS_HOSTNAME'], user=os.environ['RDS_USERNAME'], password=os.environ['RDS_PASSWORD'],
                             db='', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = connection.cursor()
    cur.execute(f'use {os.environ["RDS_DB_NAME"]}')
    cur.execute(f'SELECT * FROM {table_name} WHERE DAY(date)="{day}" AND MONTH(date)="{month}" AND YEAR(date)="{year}"')

    items = [row for row in cur]

    # need to convert objs to a string so that it's json serializable
    for item in items:
        item['date'] = str(item['date'])
        item['price'] = str(item['price'])

    items_json = json.dumps(items, indent=4)
    return items_json


def lambda_handler(event, context):
    # create s3 objs
    session = boto3.Session()
    s3 = session.client("s3")
    print(s3)
    # bucket = s3.Bucket(BUCKET_NAME)
    file_path = determine_path()
    daily_purchases = get_rows_to_str('main_purchase')
    daily_interpayments = get_rows_to_str('main_interpayment')
    
    encoded_purchases = daily_purchases.encode("utf-8")
    encoded_interpayments = daily_interpayments.encode("utf-8")

    if len(encoded_purchases):
        s3.put_object(Bucket=BUCKET_NAME, Key=file_path + '/purchases.json', Body=encoded_purchases)
    if len(encoded_interpayments):
        s3.put_object(Bucket=BUCKET_NAME, Key=file_path + '/interpayments.json', Body=encoded_interpayments)
    

# for local testing
if __name__ == '__main__':
    lambda_handler(None, None)

