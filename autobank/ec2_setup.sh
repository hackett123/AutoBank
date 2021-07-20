# make sure that you have your pem to ssh and that you have port 8000 open in your security group for TCP traffic
sudo yum update
sudo yum install git
sudo yum install tmux
git clone https://github.com/hackett123/autobank.git
cd autobank/autobank
pip3 install django pymysql
sudo yum install gcc
sudo yum install -y mysql-devel
pip3 install mysqlclient
pip3 install plotly
echo "export RDS_HOSTNAME='autobank-mysql.c66tbaq3niik.us-east-1.rds.amazonaws.com';
export RDS_PORT='3306';
export RDS_DB_NAME='autobankdb';
export RDS_USERNAME='admin';
export RDS_PASSWORD='ilovebaboo';
python3 manage.py runserver 0.0.0.0:8000"
> start_server.sh 
chmod +x start_server.sh
tmux
./start_server.sh

# now vim into settings.py and add the ip to the allowed-hosts array and then you're good to go
