import boto3
import os

aws_access_key_id = "AKIAXYKJVMCCCSU3267B"
aws_secret_access_key = "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"

# Function to upload transcript to S3
def upload_transcript(transcript, id):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    bucket_name = 'sukoontest'

    # Constructing the filename
    filename = f"{id}.txt"

    # Writing transcript to a temporary file
    with open(filename, 'w') as file: 
        file.write(transcript)

    # Uploading the file to S3
    with open(filename, 'rb') as data:
        s3.upload_fileobj(data, bucket_name, filename)

    # Deleting the temporary file
    os.remove(filename)

    url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"

    return url