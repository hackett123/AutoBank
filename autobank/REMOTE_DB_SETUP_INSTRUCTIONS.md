# Remote DB Setup Instructions

Had a horrid time setting up my RDS instance for connectability with Django. Takeaways (of things I remember):

- After making your RDS instance, edit the security group to allow MySQL protocol input from all IPs

Django End:

- First, you need to dump the contents of your data without the headers. Command is `python3 manage.py dumpdata --exclude contenttypes > datadump.json`
- Now, go to settings.py and setup your databases object. Comment out the default object content and replace with this structure:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD']
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': str(BASE_DIR / "db.sqlite3"),
    }
}
```

- Now you need to actually connect to your mysql db and create a database. You can do something like this:

```python
import os, pymysql

connection = pymysql.connect(host=os.environ['RDS_HOSTNAME'], user=os.environ['RDS_USERNAME'], password=os.environ['RDS_PASSWORD'],
                             db='', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
connection.cursor().execute('create database <DATABASE NAME HERE>')
```

Note that we make a connection with an empty db string, as no db exists yet in our RDS instance. Once we create the database with the same name we put in our RDS_DB_NAME environment variable, we are set to sync our data. To do so:

```bash
python3 manage.py loaddata datadump.json
```

If necessary, first do this:

```bash
python3 manage.py flush
python3 manage.py syncdata
python3 manage.py loaddata datadump.json
```

Now you should be able to run your server (note that you should now use the start_server.sh script you made to first export all the necessary environment variables).
