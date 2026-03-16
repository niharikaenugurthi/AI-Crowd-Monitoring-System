import boto3

# connect to AWS S3
s3 = boto3.client('s3')

bucket_name = "crowd-monitoring-project"

def upload_image(file_name):
    try:
        s3.upload_file(file_name, bucket_name, file_name)
        print("Image uploaded to S3")
    except Exception as e:
        print("Upload failed:", e)