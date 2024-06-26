# AudioX

AudioX is an application that transcribes audio files and attempts to detect foul language in the audio. This project was an implementation based on a real-world case for a client in Indonesia. The client was part of a customer service team that needed to process many recorded calls that may be under the suspicion of harrassment. The implementation made here is that it would be able to process many recordings and flag any recordings that contained foul language.

**DISCLAIMER**: The project is still under works, so there may be bugs that may turn up when you try to run the application. Feel free to use the application for your own use, but please be aware that there are no guarantees that this application can run in a secure manner. Until then, use at own risk.

## Prerequisites
In order to start using the application, there are certain requirements that are needed before starting the application. Because it uses Amazon Web Service (AWS), it requires some setup in order to get started.

The following requirements are as follows:
* pip (on terminal of your choice, so that the packages can be installed)
* AWS CLI (can be installed through pip)
* Access Key from AWS (for accessing S3 Bucket and Transcribe)
* AWS Account
* Amazon S3 Bucket (related to your AWS Account)
* Amazon Transcribe
* Repository cloned to local folder

Another thing is to make sure that the **Amazon S3 Bucket** and **Amazon Transcribe** remains empty, so to ensure no performance issue with the application itself.

## Credentials
Please put in the required credentials in order for the application to work. Follow the following format below:
```
TRANSCRIBEBUCKET=mys3bucketname
AWS_REGION=ap-southeast-1
```

## Setup
A virtual environment will be made in order to not tamper with other source files on the local computer. This will ease the use of the required packages for this application

First, let us set up our virtual environment. We need to move into the repository
```bash
cd audiox/web_app
```
Now let us activate the virtual environment
```bash
source bin/activate
```

We are now inside our virtual environment and with this virtual environment, any packages that we install will remain within the virtual environment, as to not tamper with any of the files in the local machine. **Always remember to install and run any related files in the virtual environment, in order to ensure that no performance issue occurs**

The application runs mainly on Python on the backend, so we will need to install Flask and SQLAlchemy. We can run the following code to install the packages

### Installing pip ###
Start by updating the package list
```bash
sudo apt update
```
Install pip
```bash
sudo apt install python3-pip
```
Make sure to type in 'Y' to complete the installation

Once the installation is done, you can confirm by checking the version using this command
```bash
pip3 --version
```

### Installing AWS CLI ###
Install AWS CLI with this code
```bash
sudo apt install awscli
```

Then set up the AWS credentials
```bash
aws configure
```
A command will show up to enter your secret access key obtained from AWS. Make sure to fill that in. The AWS region should match with the region where your AWS instances (S3 Bucket and Transcribe) is.

Now we have access to our AWS account and therefore we can make API calls. Note that depending on how much access you have from accessing your account through the terminal completely depends on how you set up your access key.

### Installing Flask ###
This application uses Flask to create a web application in the form of Python code. We will start by installing Flask
```bash
pip install flask
```
Install SQLAlchemy as well
```bash
pip install flask-sqlalchemy
```

### Installing Boto3 ###
Boto3 is an AWS SDK for Python that is specifically designed to manage our created instances on the AWS platform. We will require this to make API calls to the AWS platform.
```bash
pip install boto3
```

### Running the application ###
Before running our application, there are still a few configurations that needs to be done before being able to have our application fully functioning.

The database needs to be set up before being able to fully use the application
Run the code below to open python
```bash
flask shell
```
Once the command is entered, python will show up and we will prepare the database using this
```python
from app import db
```
```python
db.create_all()
```
What we are putting into the python console is that it will prepare our database and create all the table for us. The database tables are already defined in web_app/app.py

Type the command below to exit python
```python
exit()
```

Then finally you can run the application
```bash
python3 app.py
```
Setup is complete and you can access the website through the public IP address at port 5000!







