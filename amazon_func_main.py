import boto3
import amazon_func_s3 as s3
import amazon_func_transcribe as transcribe
from time import sleep
import urllib.request
import json
import sys

AWS_REGION = 'ap-southeast-1'
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
transcribe_client = boto3.client('transcribe')
s3_uri_bucket = "transcribebucket-sisnet"
s3_uri_root = "s3://" + s3_uri_bucket
mediaFormat = 'mp3'
languageCode = 'id-ID'

"""
Step 1 : Audio files are uploaded to the S3 bucket
Step 2 : Create transcribe jobs by using the key of
         S3 Bucket (so to differentiate in case of same object name)
Step 3 : With the transcribe jobs name using key, it would be easier to 
        associate the jobs with the original audio file name
"""

#Create transcribe jobs for audios that have not been transcribed (takes all files from the bucket)
def create_transcribe_jobs():
    objectsInBucket = s3.list_objects(s3_uri_bucket, s3_client)
    fileNames = []
    for obj in objectsInBucket:
        fileNames.append(obj['Key'])
    print(fileNames)
    print('Starting to check for transcribed jobs...')
    countTranscribed = 0
    countUntranscribed = 0
    print("\n")
    for fileName in fileNames:
        if transcribe.get_transcribe_job(transcribe_client, fileName) == None:
            s3uri = s3_uri_root + "/" + fileName
            transcribe.start_transcribe_job(fileName, languageCode, mediaFormat, s3uri, transcribe_client)
            print("PROCESS: " + fileName + " is being processed for transcription...\n")
            countTranscribed += 1
        else:
            print("SKIP: " + fileName + " has already been processed before. Skipping process...\n")
            countUntranscribed += 1
    print("Finished transcribing %d out of %d untranscribed audio files.." % (countTranscribed, len(fileNames)))
    print("%d files weren't transcribed, because there is an existing transcription.." % (countUntranscribed))

def check_unwanted_words(unwantedWords, transcribe_client, object):
    transcribedObj = transcribe.get_transcribe_job(transcribe_client, object['Key'])['Transcript']
    transcriptFileUri = transcribedObj['TranscriptFileUri']
    with urllib.request.urlopen(transcriptFileUri) as uri:
        current_transcript = json.loads(uri.read().decode())['results']['transcripts'][0]['transcript']
        split_transcript = current_transcript.split(" ")
        for word in split_transcript:
            for unwantedWord in unwantedWords:
                if unwantedWord in word:
                    return True
        return False  

def get_data_for_php():
   objects = s3.list_objects(s3_uri_bucket, s3_client)
   str_object = ""
   for obj in objects:
      str_object += obj['Key'] + " "
   str_object = str_object[:-1]
   return str_object

def check_all_transcripts():
    objectsBucket = s3.list_objects(s3_uri_bucket, s3_client)
    for obj in objectsBucket:
        print(obj['Key'] + " : " + str(check_unwanted_words([], transcribe_client, obj)))
