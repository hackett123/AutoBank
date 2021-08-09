"""
Script processes all purchases from the last week and aggregates spending, sending an email report to michael.
The email body contains the aggregate values and contains a csv attachment to an itemized spending list.

If the script is not run on a Sunday, it will find the most recent Sunday and give results on the previous week. For example,
if we run this on Wednesday, August 11, it will deliver a spending report for Sunday August 1 -> Saturday August 8.

Prerequirements: OS variables must be set

Assumptions: We assume and hardcode the name of the mysql db and table names. We assume RDS variables will remain constant.
"""

import boto3
import json
import os
import pymysql
import datetime

def get_datetimes_for_last_week():
    # returns value [0, ..., 6] for [Monday, ..., Sunday]
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    today_dow = today.weekday()

    # monday: 0 to 5, output 2, tuesday: 2 to 5, output 3, wednesday: 3 to 5, output 4, saturday: 5 to 5, output 0, sunday: 6 to 5, output 1
    # formula: (dow + 2) % 7
    days_back_until_saturday = (today_dow + 2) % 7
    saturday_dt = today - datetime.timedelta(days=days_back_until_saturday)
    last_sunday_dt = saturday_dt - datetime.timedelta(days=6)
    return last_sunday_dt, saturday_dt

def query_to_json(query):
    
    # cursor object executes a query and stores the result in itself, which is an iterator.
    connection = pymysql.connect(host=os.environ['RDS_HOSTNAME'], user=os.environ['RDS_USERNAME'], password=os.environ['RDS_PASSWORD'],
                             db='', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = connection.cursor()
    cur.execute(f'use {os.environ["RDS_DB_NAME"]}')
    cur.execute(query)

    # need to convert objs to a string so that it's json serializable
    items = [row for row in cur]
    for item in items:
        if 'date' in item:
            item['date'] = str(item['date'])
        if 'price' in item:
            item['price'] = str(item['price'])

    items_json = json.dumps(items, indent=4)
    return items_json

def purchases_sum_by_shop(date_between_clause):
    purchases_query_grouped_by_shop = f"""
        SELECT main_shop.name AS shop, bought_for, auth_user.first_name AS user, SUM(price) AS price
        FROM main_purchase
        JOIN main_shop ON main_purchase.shop_id=main_shop.id
        JOIN auth_user ON main_purchase.purchased_by_id=auth_user.id
        WHERE {date_between_clause}
        GROUP BY main_shop.name, bought_for, auth_user.first_name
        ORDER BY auth_user.first_name, main_shop.name, bought_for
    """
    return query_to_json(purchases_query_grouped_by_shop)

def purchases_sum_by_type(date_between_clause):
    purchases_query_grouped_by_type = f"""
        SELECT main_purchasetype.type AS type, bought_for, auth_user.first_name AS user, SUM(price) AS price
        FROM main_purchase
        JOIN main_purchasetype ON main_purchase.purchase_type_id=main_purchasetype.id
        JOIN auth_user ON main_purchase.purchased_by_id=auth_user.id
        WHERE {date_between_clause}
        GROUP BY main_purchasetype.type, bought_for, auth_user.first_name
        ORDER BY auth_user.first_name, main_purchasetype.type, bought_for
    """
    return query_to_json(purchases_query_grouped_by_type)



def get_overall_spending(date_between_clause):
    components = []
    components.append('========== PURCHASES BY MICHAEL ==========')
    by_michael_for_both = sum_purchases_bought_by_x_for_y('Michael', 'BOTH', date_between_clause)
    by_michael_for_michael = sum_purchases_bought_by_x_for_y('Michael', 'Michelle', date_between_clause)
    by_michael_for_michelle = sum_purchases_bought_by_x_for_y('Michael', 'Michael', date_between_clause)
    by_michael_total_spent = round(sum([by_michael_for_both, by_michael_for_michael, by_michael_for_michelle]), 2)
    components.append(f'For Both: ${by_michael_for_both}')
    components.append(f'For Michelle: ${by_michael_for_michael}')
    components.append(f'For Himself: ${by_michael_for_michelle}')
    components.append(f'In Total: ${by_michael_total_spent}')

    components.append('========== PURCHASES BY MICHELLE ==========')
    by_michelle_for_both = sum_purchases_bought_by_x_for_y('Michelle', 'BOTH', date_between_clause)
    by_michelle_for_michael = sum_purchases_bought_by_x_for_y('Michelle', 'Michael', date_between_clause)
    by_michelle_for_michelle = sum_purchases_bought_by_x_for_y('Michelle', 'Michelle', date_between_clause)
    by_michelle_total_spent = round(sum([by_michelle_for_both, by_michelle_for_michael, by_michelle_for_michelle]), 2)
    components.append(f'For Both: ${by_michelle_for_both}')
    components.append(f'For Michael: ${by_michelle_for_michael}')
    components.append(f'For Herself: ${by_michelle_for_michelle}')
    components.append(f'In Total: ${by_michelle_total_spent}')

    components.append('========== INTERPAYMENTS ==========')
    components.append(f'From Michelle to Michael: ${interpayments_sum("Michelle", date_between_clause)}')
    components.append(f'From Michael to Michelle: ${interpayments_sum("Michael", date_between_clause)}')



    return '\n'.join(components)

def sum_purchases_bought_by_x_for_y(bought_by, bought_for, date_clause):
    query = f"""
        SELECT auth_user.first_name, SUM(price) as price
        FROM main_purchase
        JOIN auth_user ON main_purchase.purchased_by_id=auth_user.id
        WHERE {date_clause} AND auth_user.first_name="{bought_by}" AND bought_for="{bought_for}"
        GROUP BY auth_user.first_name
    """
    return pull_sum_price_from_json_str(query_to_json(query))

def interpayments(by_who, date_between_clause):
    interpayments_query_from_x = f"""
        WITH in_between AS (
            SELECT date, price, payment_for, auth_user.first_name AS from_user, to_user_id
            FROM main_interpayment
            JOIN auth_user ON from_user_id=auth_user.id
            WHERE {date_between_clause}
        ) SELECT date, price, payment_for, from_user, auth_user.first_name AS to_user
        FROM in_between
        JOIN auth_user ON to_user_id=auth_user.id
        WHERE from_user="{by_who}"    
    """
    return query_to_json(interpayments_query_from_x)

def interpayments_sum(by_who, date_between_clause):
    json_output = interpayments(by_who, date_between_clause)
    return pull_sum_price_from_json_str(json_output)


def pull_sum_price_from_json_str(str):
    return round(sum([float(item['price']) for item in json.loads(str)]), 2)

def generate_email_body(overall_spending_str, start_dt, end_dt, s3_loc):
    return f"""
Spending Overview this week:
{overall_spending_str}

To see a more detailed breakdown, please visit the abababa stats page,
or inspect the files in s3.
    """

import smtplib, ssl, email
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
def send_email(email_content, start_dt, end_dt, attachments):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.environ['GMAIL_USERNAME']
    receiver_email = "mhackett10@gmail.com, miczhou99@gmail.com"  # Enter receiver address
    password = os.environ['GMAIL_PASSWORD']
    subject = f'Spending Overview for {start_dt.strftime("%Y-%m-%d")} to {end_dt.strftime("%Y-%m-%d")}'

    message_obj = MIMEMultipart()
    message_obj["From"] = sender_email
    message_obj["To"] = receiver_email
    message_obj["Bcc"] = os.environ['GMAIL_USERNAME']
    message_obj["Subject"] = subject
    if attachments:
        for file_loc in attachments:
            with open(file_loc, 'r') as file_obj:
                part = MIMEApplication(file_obj.read(), Name=os.path.basename(file_loc))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_loc)}"'
            message_obj.attach(part)
    message_obj.attach(MIMEText(email_content))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message_obj.as_string())

def aws_interactions(uploadables, s3_loc):
    session = boto3.Session()
    s3 = session.client("s3")
    for filename, object_content in uploadables.items():
        upload_to_s3(s3, object_content, f'weekly_statements/{s3_loc}/{filename}')

# Warning: This does not scale at all lol
def upload_to_s3(s3_obj, json_str, path):
    BUCKET_NAME = 'autobank-abababa'
    encoded = json_str.encode("utf-8")
    print(f'UPLOADING TO {path}')
    out = s3_obj.put_object(Bucket=BUCKET_NAME, Key=path, Body=encoded)
    print(out['ResponseMetadata']['HTTPStatusCode'])

def s3_path(target_date):
    year, month, day = target_date.strftime('%Y-%m-%d').split('-')
    return f'{year}/{month}/{day}'

def make_temp_files(file_dict):
    for filename, body in file_dict.items():
        file_obj = open(filename, 'w')
        file_obj.write(body)
        file_obj.close()
    return file_dict.keys()

def delete_temp_files(file_dict):
    for filename, _ in file_dict.items():
        os.remove(os.path.basename(filename))

def spending_emailer():
    # range for our emails and aggregates
    last_sunday_dt, this_saturday_dt = get_datetimes_for_last_week()
    date_between_clause = f'DATE(date) BETWEEN "{last_sunday_dt}" AND "{this_saturday_dt}"'

    # where to store files and email content as backups
    s3_loc = s3_path(this_saturday_dt)

    # run our queries and get our aggregate values
    overall_spending_str = get_overall_spending(date_between_clause)
    shop_purchases = purchases_sum_by_shop(date_between_clause)
    type_purchases = purchases_sum_by_type(date_between_clause)
    
    # generate email content
    email_content = generate_email_body(overall_spending_str, last_sunday_dt, this_saturday_dt, s3_loc)

    # maintain key/value store for what to send to s3. format (filename => object)
    uploadables_to_s3 = {
        'by_shop.json': shop_purchases,
        'by_type.json': type_purchases,
        'email.txt': email_content
    }

    # create temporary files. returns filenames.
    attachment_locations = make_temp_files(uploadables_to_s3)
    
    # upload all to s3
    aws_interactions(uploadables_to_s3, s3_loc)

    # finally, send email
    send_email(email_content, last_sunday_dt, this_saturday_dt, attachment_locations)

    delete_temp_files(uploadables_to_s3)

# for local testing
if __name__ == '__main__':
    spending_emailer()

