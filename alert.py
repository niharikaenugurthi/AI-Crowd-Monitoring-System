import boto3

sns = boto3.client('sns')

TOPIC_ARN = "arn:aws:sns:ap-south-1:668226797255:crowd-alert-system"

def send_alert(count):
    
    message = f"⚠ Crowd density HIGH. People detected: {count}"

    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=message,
        Subject="Crowd Monitoring Alert"
    )

    print("Alert sent!")