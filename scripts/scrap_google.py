import time
from datetime import datetime

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class Google:
    def __init__(self, headless=False):
        self.csv_path = "../data/games.csv"
        self.df_full = pd.read_csv(self.csv_path)
        self.df_full["date"] = pd.to_datetime(self.df_full["date"]).dt.date

        self.df = self.df_full[self.df_full["date"] < pd.Timestamp(datetime.now())]

        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")

        s = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=s, options=options)

        self.chrome.get("https://www.google.com/")
        time.sleep(3)

        self.search_games()

    def search_games(self):
        for index, row in self.df.iterrows():
            # search_input = self.chrome.find_element(By.CLASS_NAME, "gLFyf.gsfi")
            search_input = self.chrome.find_element(By.NAME, "q")
            search_input.click()
            search_input.clear()

            search_str = row["home"] + " x " + row["away"]
            search_input.send_keys(search_str)
            search_input.send_keys(Keys.ENTER)

            time.sleep(3)
            try:
                class_home = "imso_mh__l-tm-sc.imso_mh__scr-it.imso-light-font"
                score_home = int(self.chrome.find_element(By.CLASS_NAME, class_home).text)

                class_away = "imso_mh__r-tm-sc.imso_mh__scr-it.imso-light-font"
                score_away = int(self.chrome.find_element(By.CLASS_NAME, class_away).text)

                if score_home > score_away:
                    winner = "home"
                elif score_home == score_away:
                    winner = "tie"
                else:
                    winner = "away"

                self.df_full.at[index, "winner"] = winner
            except:
                pass

        self.df_full.to_csv(self.csv_path, index=False)


if __name__ == "__main__":
    google = Google()