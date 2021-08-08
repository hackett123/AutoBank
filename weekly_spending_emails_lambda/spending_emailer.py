"""
Script processes all purchases from the last week and aggregates spending, sending an email report to michael.
The email body contains the aggregate values and contains a csv attachment to an itemized spending list.

Prerequirements: OS variables must be set

Assumptions: We assume and hardcode the name of the mysql db and table names. We assume RDS variables will remain constant.
"""

import json
import os
import sys
import pymysql
import datetime

def get_yesterday_dt():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    return yesterday


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

    # TODO - rewrite query
    cur.execute(f'SELECT * FROM {table_name} WHERE DAY(date)="{day}" AND MONTH(date)="{month}" AND YEAR(date)="{year}"')

    items = [row for row in cur]

    # need to convert objs to a string so that it's json serializable
    for item in items:
        item['date'] = str(item['date'])
        item['price'] = str(item['price'])

    items_json = json.dumps(items, indent=4)
    return items_json


def spending_emailer():
    # get last week's purchases
    pass

# for local testing
if __name__ == '__main__':
    spending_emailer(sys.argv[1])

