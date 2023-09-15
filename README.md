# AudioX

AudioX is an application that transcribes audio files and attempts to detect foul language in the audio.

## Prerequisites
In order to start using the application, there are certain requirements that are needed before starting the application. Because it uses technology from AWS, it requires some setup in order to get started.

The following requirements are as follows:
* pip (on terminal of your choice, so that the packages can be installed)
* AWS CLI (can be installed through pip)
* Access Key from AWS (for accessing S3 Bucket and Transcribe)
* AWS Account
* Amazon S3 Bucket (related to your AWS Account)
* Amazon Transcribe
* Repository cloned to local folder

Another thing is to make sure that the **Amazon S3 Bucket** and **Amazon Transcribe** remains empty, so to ensure no performance issue with the application itself.

## Setup
A virtual environment will be made in order to not tamper with other source files on the local computer. This will ease the use of the required packages for this application

First, let us set up the AWS credentials
```bash
aws configure
```
A command will show up to enter your secret access key obtained from AWS. Make sure to fill that in. The AWS region should match with the region where your AWS instances (S3 Bucket and Transcribe) is.

Now we have access to our AWS account and therefore we can make API calls. Note that depending on how much access you have from accessing your account through the terminal completely depends on how you set up your access key.

Next, let us set up our virtual environment. We need to move into the repository
```bash
cd audiox/web_app
```
Now let us activate the virtual environment
```bash
source bin/activate
```

We are now inside our virtual environment and with this virtual environment, any packages that we install will remain within the virtual environment, as to not tamper with any of the files in the local machine. **Always remember to install and run any related files in the virtual environment, in order to ensure that no performance issue occurs**

The application runs mainly on Python on the backend, so we will need to install Flask and SQLAlchemy. We can run the following code to install the packages

###(Installing pip)
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






