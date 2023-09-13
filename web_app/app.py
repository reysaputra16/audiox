import sys
import os
sys.path.append('..')

from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import botocore

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

class UnwantedWords(db.Model):
    word = db.Column(db.String(100), primary_key=True, nullable=False)

    def __repr__(self):
        return'<UnwantedWords %r>' % self.word
    
class MarkedAudioFiles(db.Model):
    filename = db.Column(db.String(50), primary_key=True)
    data = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<MarkedAudioFiles %r>' % self.filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AudioFiles():
    FILE_UPLOAD = ""
    #TODO: Make sure the unwanted words are stored in a database

#Define audio files class as variable
audio_files = AudioFiles()

def check_unwanted_words(split_transcription):
    query = UnwantedWords.query.all()
    unwanted_words = []
    for row in query:
        unwanted_words.append(row.word)
    bool_bad = 'N'
    for word in split_transcription:
        if word in unwanted_words:
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
                                                    completed=1, foul_lang=2)
                    upload_to_db(new_audio_file)
                    #s3.download_file(main.s3_client, main.s3_uri_bucket, file)
                    

    return render_template("audio_list.html", audio_files=list_audio_files, transcribed=is_transcribed,
                            transcriptions=transcriptions, is_bad=is_bad, error="0")

@app.route("/assessment")
def detected_audio():
    audio_files = DetectedFiles.query.all()
    return render_template("detected_audio_list.html", files=DetectedFiles.query.all(), filename="", filelink="")

@app.route("/upload_file", methods=['POST', 'GET'])
def upload_file():
    try:
        if request.method == 'POST':
            fileobj = request.files['file-to-save']
            #Makes sure file name is secure from SQL Injections
            new_filename = secure_filename(fileobj.filename)
            if s3.upload_fileobj(main.s3_client, fileobj, main.s3_uri_bucket, new_filename):
                return render_template("/upload.html", msg="Y")
            else:
                return render_template("upload.html", msg="N")
    except botocore.exceptions.ParamValidationError:
        return render_template("upload.html", msg="NoFile")

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

@app.route("/no_foul_language", methods=['POST', 'GET'])
def no_foul_language():
    if request.method == 'POST':
        file_name = request.form['filename']
        print("Got filename! " + file_name)
        updated_file = DetectedFiles.query.filter_by(filename=file_name).first()
        updated_file.completed = 2
        updated_file.foul_lang = 0
        print("Got file from DB")
        db.session.add(updated_file)
        db.session.commit()
    
    return redirect("/assessment")

@app.route("/foul_language", methods=['POST', 'GET'])
def foul_language():
    if request.method == 'POST':
        file_name = request.form['filename']
        print("Got filename! " + file_name)
        updated_file = DetectedFiles.query.filter_by(filename=file_name).first()
        updated_file.completed = 2
        updated_file.foul_lang = 1
        print("Got file from DB")

        db.session.add(updated_file)
        db.session.commit()

    return redirect("/assessment")

@app.route("/revert_assessment", methods=['POST'])
def revert_assessment():
    if request.method == 'POST':
        file_name = request.form['filename']
        print("Got filename! " + file_name)
        updated_file = DetectedFiles.query.filter_by(filename=file_name).first()
        updated_file.completed = 1
        updated_file.foul_lang = 2
        print("Got file from DB")

        db.session.add(updated_file)
        db.session.commit()

    return redirect("/assessment")

@app.route("/download_file", methods=['POST'])
def download_file():
    if request.method == 'POST':
        command = 'aws s3 presign s3://' + main.s3_uri_bucket + '/' + request.form['filename'] + ' --expires-in 15'
        output = os.popen(command).read()
        #proc = subprocess.Popen(["aws", "s3", "presign", "s3://" + main.s3_uri_bucket + "/" + request.form['filename'],
        #                         "--expires-in", '30'], stdout=subprocess.PIPE, shell=True)
        #(out, err) = proc.communicate()
        #print(output)
        #file = request.

        #marked_audio_file = MarkedAudioFiles(filename=request.form['filename'], data=)
        
    return render_template("detected_audio_list.html", files=DetectedFiles.query.all(), filename=request.form['filename'],
                            filelink=output)
    
@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/about", methods=['POST', 'GET'])
def about_page():
    if request.method == 'POST':
        main.s3_uri_bucket = request.form['bucket_name']
        main.AWS_REGION = request.form['aws_region']
        main.languageCode = request.form['transcript_lang']
        print("Updated...")
        print("Bucket name: " + main.s3_uri_bucket)
        print("AWS Region: " + main.AWS_REGION)
        print("Transcript Language: " + main.languageCode)
    return render_template("about.html", bucket_name=main.s3_uri_bucket,
                           aws_region=main.AWS_REGION, transcript_lang=main.languageCode,
                           words=UnwantedWords.query.all())

@app.route("/add_word", methods=['POST'])
def add_word():
    if request.method == 'POST':
        queryWords = UnwantedWords.query.all()
        listWords = []
        new_word = request.form['word_to_add']
        for query in queryWords:
            listWords.append(query.word)
        if new_word in listWords:
            print("ERROR: Word already exists")
        else:
            word_to_add = UnwantedWords(word=new_word)
            db.session.add(word_to_add)
            db.session.commit()
        return redirect("/about")

@app.route("/remove_word", methods=['POST'])
def remove_word():
    if request.method == 'POST':
        new_word = request.form['word_to_remove']
        UnwantedWords.query.filter_by(word=new_word).delete()
        db.session.commit()
    return redirect("/about")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    