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

def datetime_n_days_back(days_back):
    today = datetime.datetime.today()
    return today - datetime.timedelta(days=days_back)

def determine_path(target_date):
    year, month, day = target_date.strftime('%Y-%m-%d').split('-')
    path = f'{year}/{month}/{day}'
    print(path)
    return path

def get_rows_to_str(table_name, dt):
    
    day = dt.day
    month = dt.month
    year = dt.year

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

    # read last 10 days and backup. means if you forget to add a purcahse for over a week it will be recorded still
    for i in range(1, 10):
        dt = datetime_n_days_back(i).date()
        daily_purchases = get_rows_to_str('main_purchase', dt)
        daily_interpayments = get_rows_to_str('main_interpayment', dt)
        
        encoded_purchases = daily_purchases.encode("utf-8")
        encoded_interpayments = daily_interpayments.encode("utf-8")

        file_path = determine_path(dt)
        if len(encoded_purchases):
            s3.put_object(Bucket=BUCKET_NAME, Key=file_path + '/purchases.json', Body=encoded_purchases)
            print(f'wrote purchases for {i} days ago')
        if len(encoded_interpayments):
            s3.put_object(Bucket=BUCKET_NAME, Key=file_path + '/interpayments.json', Body=encoded_interpayments)
            print(f'wrote interpayments for {i} days ago')
    
    

# for local testing
if __name__ == '__main__':
    lambda_handler(None, None)

