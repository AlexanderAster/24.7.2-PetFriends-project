import os # более безопасный способ передавать личные данные через библиотеку dotenv и системного файла .env
from dotenv import load_dotenv
load_dotenv() # метод берёт данные из скрытого файла .env через окружение.
valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')
invalid_email = os.getenv('invalid_email')
invalid_password = os.getenv('invalid_password')