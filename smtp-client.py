import smtplib
import configparser
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def get_config(name_config_file: str):
    config = configparser.ConfigParser(default_section='')
    config.optionxform = str
    config.read(name_config_file, encoding='utf8')

    return config


class Message:
    def __init__(self,
                 name_config_folder: str = 'config',
                 name_config_file: str = 'config.ini',
                 name_letter_file: str = 'letter.txt'):

        config = get_config(os.path.join(name_config_folder, name_config_file))

        self.config_folder = name_config_folder
        self.title = config['MESSAGE']['title']
        self.attachments = config['MESSAGE']['attachments'].split(',')
        self.recipients = config['MESSAGE']['recipients'].split(',')
        with open(os.path.join(name_config_folder, name_letter_file), 'r') as _letter_file:
            self.text = _letter_file.read()


class Client:
    def __init__(self,
                 name_config_folder: str = 'config',
                 name_config_file: str = 'config.ini'):
        config = get_config(os.path.join(name_config_folder, name_config_file))

        self.login = config['CLIENT']['login']
        self._password = config['CLIENT']['password']

    def send_letter(self, message: Message):
        letter = MIMEMultipart()
        letter['Subject'] = message.title
        letter['From'] = self.login
        letter.attach(MIMEText(message.text))

        for attachment in message.attachments:
            with open(os.path.join(message.config_folder, attachment), 'rb') as file_attachment:
                _attachment = MIMEApplication(file_attachment.read())
                _attachment.add_header('Content-Disposition', 'attachment', filename=attachment)
                letter.attach(_attachment)

        server = smtplib.SMTP('smtp.mail.ru:587')
        server.ehlo()
        server.starttls()
        server.login(self.login, self._password)
        server.sendmail(self.login, message.recipients, letter.as_string())


if __name__ == '__main__':
    config_folder = 'config'
    config_file = 'config.ini'
    letter_file = 'letter.txt'

    client = Client(config_folder, config_file)
    client.send_letter(Message(config_folder, config_file, letter_file))
