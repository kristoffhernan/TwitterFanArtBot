import stat
import shutil
import os
import smtplib
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import config


# https://stackoverflow.com/questions/26124281/convert-a-str-to-path-type
# dir = directory to zip | filename = zip file name
def zip_dir(dir, zip_path, zip_filname):
    """Zip the provided directory without navigating to that directory using `pathlib` module"""
    filename = os.path.join(zip_path, zip_filname)

    # Convert to Path object
    dir = Path(dir)

    # creating zip file
    with ZipFile(filename, "w", ZIP_DEFLATED) as zip_file:
        for entry in dir.rglob("*"):
            zip_file.write(entry, entry.relative_to(dir))


# https://stackoverflow.com/questions/1889597/deleting-read-only-directory-in-python
# to bypass [WinErorr 5] Access denied when trying to delete a folder
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_folder_contents(content_folder):
    def delete_file(file_path):
        # check if its a file
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        # check if its a folder
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path, onerror=remove_readonly)

    # https://stackoverflow.com/questions/29206384/python-folder-names-in-the-directory
    folders = [os.path.join(content_folder, directory) for directory in os.listdir(
        content_folder) if os.path.isdir(content_folder)]

    for folder in folders:
        # listdir(folder) of zip isnt a directory so it produces err
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                # if os.path.isfile is a directory, OSError occurs
                try:
                    delete_file(file_path)

                except OSError as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        except NotADirectoryError as e:
            # if there are no directory inside data or zip, just delete whatever is inside
            delete_file(folder)
        print(f'{os.path.split(folder)[1]} content deleted.')


# https://docs.python.org/3/library/email.examples.html
# https://djangocentral.com/sending-email-with-zip-files-using-python/
def send_email(zip_folder, zip_filename, EMAIL_ADDRESS, EMAIL_PASSWORD):
    msg = MIMEMultipart()
    body = MIMEText('Weekly Update', 'plain')
    msg['Subject'] = 'TrashTaste Twitter Bot'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    # Add body to email
    msg.attach(body)

    # open and read the zip file in binary
    with open(os.path.join(zip_folder, zip_filename), 'rb') as file:
        # Attach the file with filename to the email
        msg.attach(MIMEApplication(file.read(), Name=zip_filename))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

        # SMTP_SSL identifies ourselves with the gmail server and encrypt traffic

        # login to email server
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)
        print('Email sent.')


def send_email_test():
    EMAIL_ADDRESS = config.EMAIL_ADDRESS
    # https://support.google.com/accounts/answer/185833?hl=en
    # cant just use real password, have to use gmail app passwords
    EMAIL_PASSWORD = config.GMAIL_APP_PASS

    # directory variables
    cwd = os.getcwd()
    data_folder = os.path.join(cwd, 'data')
    zip_folder = os.path.join(cwd, 'zip')

    # compress data dir as zip file
    today = date.today()
    last_week = date.today() - timedelta(days=7)
    zip_filename = f'TT-Data-{last_week}-{today}.zip'
    zip_dir(data_folder, zip_folder, zip_filename)

    # remove_folder_contents(data_folder)

    send_email(zip_folder, zip_filename, EMAIL_ADDRESS, EMAIL_PASSWORD)

    # remove_folder_contents(zip_folder)


if __name__ == '__main__':
    send_email_test()
