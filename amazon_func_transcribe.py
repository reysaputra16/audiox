import botocore.exceptions as botoe

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
    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=transcriptionJobName,
        LanguageCode=languageCode,
        MediaFormat=mediaFormat,
        Media={
            'MediaFileUri': media_uri,
        },
    )

def get_transcribe_job(transcribe_client, job_name):
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        job = response['TranscriptionJob']
        return job
    except botoe.ClientError:
        return None