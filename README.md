# Abababa (Autobank)

## Design

### Deployment

We have deployed our backend server to EC2 where it is running on a single t2.micro instance that we manually ssh into when we need to pull changes and restart the server.

### Frontend Site

We have a django site running at http://ec2-3-89-160-69.compute-1.amazonaws.com:8000/ until we decide to pay for a real domain name.

### Backend Server

**Django** is our web server of choice. It connects to our remote MySQL db and handles all http requests.

### Database

We are hosting a remote MySQL db on AWS RDS for around $12/month once the free tier expires.

## Additional Components

### Backup DB

### Weekly Spending Emails

### Weekly Budget Emails

## Development

Right now we have a primitive SDLC. Changes are pushed to git, then we ssh to the ec2 instance hosting the server, git pull, enter the tmux session, kill the server, and restart it. This is fine because Abababa is just for Michelle and me, but if we ever intend to make this scale this needs to change.

## CI and CD TODO (if we want)

- Look into AWS CodeDeploy
  - or alternatively: write a cronjob that runs a script to see if there's a new commit on main, and if there is, pull and restart the server.
- Look into automating the ec2 setup (already written in `ec2_setup.sh`)
