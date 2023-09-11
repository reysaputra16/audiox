import sys
sys.path.append('..')

from flask import Flask, render_template, url_for, request, redirect
from tkinter.filedialog import askopenfilename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import botocore.exceptions as botoe
import amazon_func_main as main
import amazon_func_s3 as s3
import amazon_func_transcribe as transcribe

app = Flask(__name__, template_folder="templates")
ALLOWED_EXTENSIONS = {'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""
Optional: Settings for setting up a database
"""
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#db =SQLAlchemy(app)

class AudioFiles():
    FILE_UPLOAD = ""
    unwanted_words = ["busuk", "benci", "sialan"]
    
    def upload_file(self):
        try:
            self.FILE_UPLOAD = askopenfilename()
            print(self.FILE_UPLOAD)
            list_of_files = s3.list_objects(main.s3_uri_bucket, main.s3_client)
            if self.FILE_UPLOAD.split("/")[-1] in list_of_files:
                print("File with same name already exists!")
                return render_template('index.html')
            else:
                s3.upload_file(self.FILE_UPLOAD, main.s3_client, main.s3_uri_bucket, self.FILE_UPLOAD.split("/")[-1])
                print("File uploaded successful")
                return render_template('index.html')
        except botoe.ClientError:
            print("Upload error!")
            return render_template('index.html')
        except FileNotFoundError:
            print("File does not exist!")
            return render_template('index.html')

audio_files = AudioFiles()

        
@app.route("/")
def home():
    """
    Setup certain parameters
    """
    return render_template("home.html")

@app.route("/audio_list", methods=['POST', 'GET'])
def index():
    list_audio_files = s3.list_objects(main.s3_uri_bucket, main.s3_client)
    is_transcribed = []
    transcriptions = []
    is_bad = []
    for file in list_audio_files:
        transcribe_job = transcribe.get_transcribe_job(main.transcribe_client, file)
        if transcribe_job == None:
            is_transcribed.append("Not Transcribed")   #Cross in HTML
            transcriptions.append("")
            is_bad.append('U')
        else:
            if transcribe_job['TranscriptionJobStatus'] == 'IN_PROGRESS':
                is_transcribed.append('In Progress')
                transcriptions.append('')
                is_bad.append('U')
            elif transcribe_job['TranscriptionJobStatus'] == 'FAILED':
                is_transcribed.append('Failed')
                transcriptions.append('')
                is_bad.append('U')
            else:
                is_transcribed.append('Transcribed')   #Tick in HTML
                transcription = transcribe.get_transcription(main.transcribe_client, file)
                transcriptions.append(transcription)
                split_transcription = transcription.split(" ")
                bool_bad = 'N'
                for word in split_transcription:
                    if word in audio_files.unwanted_words:
                        bool_bad = 'Y'
                        break
                is_bad.append(bool_bad)

    return render_template("audio_list.html", audio_files=list_audio_files, transcribed=is_transcribed,
                           transcriptions=transcriptions, is_bad=is_bad)

@app.route("/upload_file", methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        print("Hello!")
    """
    print("File uploaded!")
    if not allowed_file(uploaded_file.filename):
        print("File not allowed. Redirecting to previous page")
        return redirect("/audio_list")
    else:
        main.s3_client.upload_fileobj(uploaded_file, main.s3_uri_bucket, uploaded_file.filename)
        print("File successfully uploaded!")
        return redirect("/audio_list")
    """
    return redirect("/audio_list")

@app.route("/delete_file", methods=['POST', 'GET'])
def delete_file():
    if request.method == 'POST':
        file_name = request.form['filename']
        print("Deleting " + file_name + "...")
        if transcribe.get_transcribe_job(main.transcribe_client, file_name) != None:
            transcribe.delete_transcribe_job(main.transcribe_client, file_name)
        s3.delete_file(main.s3_client, main.s3_uri_bucket, file_name)
        return redirect("/audio_list")
    else:
        return redirect("/audio_list")

@app.route("/transcribe_file", methods=['POST', 'GET'])
def transcribe_file():
    if request.method == 'POST':
        file_name = request.form['filename']
        print("Starting Transcription Job for " + file_name + "...")
        transcribe.start_transcribe_job(file_name, main.languageCode, main.mediaFormat, main.s3_uri_root + "/" + file_name,
                                        main.transcribe_client)
        return redirect("/audio_list")
    else:
        return redirect("/audio_list")
    
@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/about")
def about_page():
    return render_template("about.html")


    