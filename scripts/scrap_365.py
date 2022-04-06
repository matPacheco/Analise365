import time
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Bet365:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")

        s = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=s, options=options)

        self.chrome.get("https://www.bet365.com/")
        time.sleep(5)

        load_dotenv()

        self.login()

    def login(self):
        # Botão de Login
        self.chrome.find_element(By.CLASS_NAME, "hm-MainHeaderRHSLoggedOutWide_Login").click()

        time.sleep(5)

        username = os.getenv("USER")
        password = os.getenv("PWD")

        # Input de username
        user_input = self.chrome.find_element(By.CLASS_NAME, "lms-StandardLogin_Username")
        user_input.send_keys(username)

        # Input de senha
        password_input = self.chrome.find_element(By.CLASS_NAME, "lms-StandardLogin_Password")
        password_input.send_keys(password)

        self.chrome.find_element(By.CLASS_NAME, "lms-LoginButton").click()

        time.sleep(600000)


if __name__ == "__main__":
    Bet365()

