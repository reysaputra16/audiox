import botocore.exceptions as botoe

def create_bucket(bucket_name, s3_client, location):
    response = s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': location,
        },
    )
    print(response)

def delete_bucket(bucket_name, s3_client):
    response = s3_client.delete_bucket(
        Bucket=bucket_name,

    )
    print(response)


def list_objects(bucket_name, s3_client):
    response = s3_client.list_objects_v2(
        Bucket=bucket_name
    )

    responseContent = response['Contents']
    result = []
    for obj in responseContent:
        result.append(obj['Key'])
    return result

def get_object(bucket_name, key_object, s3_client):
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=key_object,
    )
    print(response)

def upload_file(fileLoc, s3_client, bucket_name, objName):
    try:
        s3_client.upload_file(fileLoc, bucket_name, objName)
    except botoe.ClientError:
        print("File does not exist.. Please make sure that the location is correct...")
