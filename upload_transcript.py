import boto3
import os

# Function to upload transcript to S3
def upload_transcript(transcript, id):
    s3 = boto3.client('s3')
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