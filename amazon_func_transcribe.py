import botocore.exceptions as botoe
import urllib
import json

def list_jobs(job_filter, transcribe_client):
    try:
        response = transcribe_client.list_transcription_jobs(
            JobNameContains=job_filter
        )
        jobs = response['TranscriptionJobSummaries']
        next_token = response.get('NextToken')
        while next_token is not None:
            response = transcribe_client.list_transcription_jobs(
                JobNameContains=job_filter, NextToken=next_token
            )
            jobs += response.get('NextToken')
    except botoe.ClientError:
        print("Couldn't get jobs with filters %s")
        raise
    else:
        return jobs
    

#Helper function to start a single transcribe job
def start_transcribe_job(transcriptionJobName, languageCode, mediaFormat, media_uri, transcribe_client):
    try:
        if get_transcribe_job(transcribe_client, transcriptionJobName) != None:
            print("Transcription already existed. Redirecting to previous page...")
        else:
            response = transcribe_client.start_transcription_job(
                TranscriptionJobName=transcriptionJobName,
                LanguageCode=languageCode,
                MediaFormat=mediaFormat,
                Media={
                    'MediaFileUri': media_uri,
                },
            )
            print("Transcription successful!")
    except botoe.ClientError:
        print("Error transcribing data. Redirecting back to original page")

def get_transcribe_job(transcribe_client, job_name):
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        job = response['TranscriptionJob']
        return job
    except botoe.ClientError:
        return None
    
def delete_transcribe_job(transcribe_client, job_name):
    try:
        response = transcribe_client.delete_transcription_job(
            TranscriptionJobName=job_name
        )
    except botoe.ClientError:
        print("Deleting Transcription Job failed..")
    else:
        print("Transcription Job successfully deleted!")

def get_transcription(transcribe_client, job_name):
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        transcriptUri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        with urllib.request.urlopen(transcriptUri) as uri:
            current_transcript = json.loads(uri.read().decode())['results']['transcripts'][0]['transcript']
            print("Transcription obtained successfully")
            return current_transcript
    except botoe.ClientError:
        print("Problem getting transcription..")