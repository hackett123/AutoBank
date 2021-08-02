# PROCEDURE

## Uploading to Lambda and setting permissions

- pip3 install your dependencies target destination this directory
- Zip the whole folder
- Upload to lambda
- Go to IAM: Find the policy that was created for your lambda and add s3:putObject to our s3 bucket
- deploy code
  
## Adding Trigger

- Add EventBridge (CW) Trigger with rate expression of rate(1 day) to tell it to trigger once a day every day.