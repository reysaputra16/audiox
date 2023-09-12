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

ALLOWED_EXTENSIONS = {'mp3'}

app = Flask(__name__, template_folder="templates")
with app.app_context():
    """
    Setting up a database
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db = SQLAlchemy(app)

class DetectedFiles(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    filename = db.Column(db.String(100), primary_key=True, nullable=False)
    transcription = db.Column(db.String(5000))
    completed = db.Column(db.Integer, default=0)    #0=marked for assessment, 1=completed assessment
    foul_lang = db.Column(db.Integer, default=0)    #0=no, 1=yes
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<DetectedFiles %r>' % self.filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AudioFiles():
    FILE_UPLOAD = ""
    #TODO: Make sure the unwanted words are stored in a database
    unwanted_words = ["busuk", "benci", "sialan", "bodoh"]

#Define audio files class as variable
audio_files = AudioFiles()

def check_unwanted_words(split_transcription):
    bool_bad = 'N'
    for word in split_transcription:
        if word in audio_files.unwanted_words:
            bool_bad = 'Y'
            break
    return bool_bad

def upload_to_db(audioFileInfo):
    try:
        db.session.add(audioFileInfo)
        db.session.commit()
    except:
        return "There was an issue adding the audio file to the database"

        
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
                bool_append = check_unwanted_words(split_transcription)
                is_bad.append(bool_append)
                if bool_append == 'Y':
                    new_audio_file = DetectedFiles(filename=file, transcription=transcription, 
                                                    completed=1, foul_lang=1)
                    upload_to_db(new_audio_file)
                    

    return render_template("audio_list.html", audio_files=list_audio_files, transcribed=is_transcribed,
                           transcriptions=transcriptions, is_bad=is_bad)

@app.route("/detected_audio")
def detected_audio():
    audio_files = DetectedFiles.query.all()
    if len(audio_files) == 0:
        audio_file = DetectedFiles(filename="Test", transcription="Bodoh kamu", completed=0, foul_lang=1)
        upload_to_db(audio_file)
    return render_template("detected_audio_list.html", files=DetectedFiles.query.all())

@app.route("/upload_file", methods=['POST', 'GET'])
def upload_file():
    #For now, just redirect to the audio list page
    return redirect("/audio_list")

@app.route("/delete_file", methods=['POST', 'GET'])
def delete_file():
    if request.method == 'POST':
        file_name = request.form['filename']
        print("Deleting " + file_name + "...")
        if transcribe.get_transcribe_job(main.transcribe_client, file_name) != None:
            transcribe.delete_transcribe_job(main.transcribe_client, file_name)
        s3.delete_file(main.s3_client, main.s3_uri_bucket, file_name)

        #Delete file from DB too, if it exists
        DetectedFiles.query.filter_by(filename=file_name).delete()
        db.session.commit()
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
    