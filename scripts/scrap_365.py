import time
import os
import locale
from datetime import datetime

import pandas as pd
import numpy as np
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Bet365:
    def __init__(self, urls=None, headless=False):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")

        s = Service(ChromeDriverManager().install())
        self.chrome = webdriver.Chrome(service=s, options=options)

        self.chrome.get("https://www.bet365.com/")
        time.sleep(5)

        load_dotenv()

        # Couldn't find a way yet to login to it since it has web-scrapping protections
        # self.login()

        if urls:
            df = pd.DataFrame()
            for championship, url in urls.items():
                print(championship)
                try:
                    df_new = self.get_games_odds(url, championship)
                    df = pd.concat([df, df_new])
                    print("Success")
                except Exception as e:
                    print(e)
                    pass
            append_csv(df)

    def login(self):
        # Botão de Login
        self.chrome.find_element(By.CLASS_NAME, "hm-MainHeaderRHSLoggedOutWide_Login").click()

        time.sleep(5)

        username = os.getenv("USER")
        password = os.getenv("PWD")

        # Input de username
        user_input = self.chrome.find_element(By.CLASS_NAME, "lms-StandardLogin_Username")
        user_input.send_keys(username)
        time.sleep(1)

        # Input de senha
        password_input = self.chrome.find_element(By.CLASS_NAME, "lms-StandardLogin_Password")
        password_input.send_keys(password)
        time.sleep(1)

        self.chrome.find_element(By.CLASS_NAME, "lms-LoginButton").click()

    def get_games_odds(self, url, championship):
        self.chrome.get(url)
        time.sleep(5)

        # Construct df with our list of dicts
        df = pd.DataFrame(self.get_games())

        # Converting to pandas datetime
        df["date"] = df["date"] + " 2022"
        df["date"] = df["date"].str[4:]
        df["date"] = pd.to_datetime(df["date"], format="%d %b %Y").dt.date

        # Getting odds
        odds = self.get_odds()
        df["odd_home"] = odds["odd_home"]
        df["odd_tie"] = odds["odd_tie"]
        df["odd_away"] = odds["odd_away"]

        # Setting the championship
        df["championship"] = championship

        # Setting the winner column so it can be completed later
        df["winner"] = np.nan

        time.sleep(5)
        return df

    def get_games(self):
        games_container = self.chrome.find_element(By.CLASS_NAME, "sgl-MarketFixtureDetailsLabel")
        container_items = games_container.find_elements(By.XPATH, "*")

        last_dt = None
        games = []
        for item in container_items:
            # If is date, else game
            if "rcl-MarketHeaderLabel-isdate" in item.get_attribute("class"):
                last_dt = item.text
            else:
                # Divs with the teams name
                teams_div = item.find_elements(By.CLASS_NAME, "rcl-ParticipantFixtureDetailsTeam_TeamName")
                teams = []
                for team in teams_div:
                    teams.append(team.text)

                # Append a dict to our list so we can build our dataframe later
                games.append({
                    "home": teams[0],
                    "away": teams[1],
                    "date": last_dt
                })

        return games

    def get_odds(self):
        odds_containers = self.chrome.find_elements(By.CLASS_NAME, "sgl-MarketOddsExpand")

        full_odds = []
        for container in odds_containers:
            odds = []
            for item in container.find_elements(By.XPATH, "*"):
                # If is not a column header
                if "rcl-MarketColumnHeader" not in item.get_attribute("class") \
                        and "rcl-MarketHeaderLabel" not in item.get_attribute("class"):
                    odds.append(item.find_element(By.CLASS_NAME, "sgl-ParticipantOddsOnly80_Odds").text)
            full_odds.append(odds)

        odds_dict = {
            "odd_home": full_odds[0],
            "odd_tie": full_odds[1],
            "odd_away": full_odds[2]
        }

        return odds_dict


def append_csv(df):
    csv_path = "../data/games.csv"
    try:
        old = pd.read_csv(csv_path)
    except FileNotFoundError:
        old = pd.DataFrame()

    new = pd.concat([old, df])
    new = new.drop_duplicates(subset=["home", "away", "date"])
    new.to_csv(csv_path, index=False)


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'pt-BR.UTF-8')
    campeonatos = {
        "Premier League": "https://www.bet365.com/#/AC/B1/C1/D1002/E61683472/G40/",
        "La Liga": "https://www.bet365.com/#/AC/B1/C1/D1002/E62271413/G40/",
        "Bundesliga": "https://www.bet365.com/#/AC/B1/C1/D1002/E62233151/G40/",
        "Serie A": "https://www.bet365.com/#/AC/B1/C1/D1002/E62863982/G40/",
        "Ligue 1": "https://www.bet365.com/#/AC/B1/C1/D1002/E62341993/G40/",
        "Champions League": "https://www.bet365.com/#/AC/B1/C1/D1002/E64406669/G40/",
        "Europa League": "https://www.bet365.com/#/AC/B1/C1/D1002/E64407176/G40/",
        "Conference League": "https://www.bet365.com/#/AC/B1/C1/D1002/E64412308/G40/",
        "Brasileirao": "https://www.bet365.com/#/AC/B1/C1/D1002/E71022033/G40/",
        "Copa do Brasil": "https://www.bet365.com/#/AC/B1/C1/D1002/E73614831/G40/",
        "Sul-Americana": "https://www.bet365.com/#/AC/B1/C1/D1002/E71750612/G40/",
        "Libertadores": "https://www.bet365.com/#/AC/B1/C1/D1002/E70836857/G40/",
        "Liga Profesional (Argentina)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70324037/G40/",
        "Apertura (Bolivia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E72884835/G40/",
        "Primeira Divisão (Chile)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70609541/G40/",
        "Primera A (Colombia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E26331167/G40/",
        "Campeonato Nacional (Equador)": "https://www.bet365.com/#/AC/B1/C1/D1002/E71170153/G40/",
        "MLS": "https://www.bet365.com/#/AC/B1/C1/D1002/E70603528/G40/",
        "Clausura (México)": "https://www.bet365.com/#/AC/B1/C1/D1002/E69182017/G40/",
        "Primera Divisón (Peru)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70326270/G40/",
        "Apertura (Uruguai)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70656849/G40/",
        "Primera Divisón (Venezuela)": "https://www.bet365.com/#/AC/B1/C1/D1002/E71449387/G40/",
        "1HNL (Croatia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70030360/G40/",
        "Ekstraklasa (Polonia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70323736/G40/",
        "Primeira Liga (Portugal)": "https://www.bet365.com/#/AC/B1/C1/D1002/E72883113/G40/",
        "Bundesliga (Austria)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70323617/G40/",
        "1 Divisão A (Bélgica)": "https://www.bet365.com/#/AC/B1/C1/D1002/E61899552/G40/",
        "Premier Liga (Bósnia e Herzegovina)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70886387/G40/",
        "Superligaen (Dinamarca)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70603446/G40/",
        "Meistriliiga (Estonia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E71170002/G40/",
        "Superliga (Eslováquia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70324029/G40/",
        "Prva Liga (Eslovênia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70324029/G40/",
        "Veikkausliiga (Finlândia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E72030216/G40/",
        "NB I (Hungria)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70032012/G40/",
        "Premier Division (Irlanda)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70603426/G40/",
        "Premier League (Islândia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E73177097/G40/",
        "Premier League (Israel)": "https://www.bet365.com/#/AC/B1/C1/D1002/E64241999/G40/",
        "EliteSérien (Noruega)": "https://www.bet365.com/#/AC/B1/C1/D1002/E72030345/G40/",
        "Eridivisie (Países Baixos)": "https://www.bet365.com/#/AC/B1/C1/D1002/E62415349/G40/",
        "First League (República Tcheca)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70323664/G40/",
        "Liga 1 (Romênia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70018316/G40/",
        "San Marino": "https://www.bet365.com/#/AC/B1/C1/D1002/E73075614/G40/",
        "Superliga (Sérvia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70886670/G40/",
        "Allsvenskan (Suécia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E72030392/G40/",
        "Superliga (Suíça)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70030263/G40/",
        "Superliga (Turquia)": "https://www.bet365.com/#/AC/B1/C1/D1002/E63190999/G40/",
        "A-league (Austrália)": "https://www.bet365.com/#/AC/B1/C1/D1002/E66985764/G40/",
        "J-league (Japão)": "https://www.bet365.com/#/AC/B1/C1/D1002/E70952883/G40/",
        "K-league (Coréia do Sul)": "https://www.bet365.com/#/AC/B1/C1/D1002/E73758101/G40/"
    }
    Bet365(campeonatos)

