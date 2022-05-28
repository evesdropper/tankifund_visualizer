 # necessary imports - scraping and heroku being retarded
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils as utils
import requests
from bs4 import BeautifulSoup

# data analysis
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# big capital letters
CWD = os.getcwd()
SAVE_DIR = os.path.join(CWD, "saved")
SAVEFILE = os.path.join(SAVE_DIR, "fund.txt")

URL = "https://tankionline.com/pages/tanki-birthday-2022/" # when new fund website
CHECKPOINTS = [3] + list(range(6, 16))
REWARDS = ["Prot Slot", "Prot Slot", "Skin Cont", "Skin Cont", "Prot Slot", "Hyperion", "Blaster", "Armadillo", "Pulsar", "Crisis", "Surprise"]

# fund entries
class FundEntry():
    
    def __init__(self, value):
        self.time = datetime.datetime.utcnow().strftime('%m-%d %H:%M')
        self.value = value    
    
    def __repr__(self):
        return f"{self.time}: {self.value}"
    
    def __str__(self):
        return f"Fund at {self.time}: {self.value}"

# start a new fund array
def initialize_arr():
    funds_arr = np.array([])
    utils.save_entry(funds_arr, SAVEFILE)

# reset fund data
def reset():
    utils.clean(SAVEFILE)
    initialize_arr()

# fund 
def get_entry():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    fund = soup.find_all("span", class_="ms-3")
    funds_arr = utils.load_entry(SAVEFILE)
    funds_arr = np.append(funds_arr, FundEntry(fund[0].text))
    utils.save_entry(funds_arr, SAVEFILE)
    return fund[0].text

def entries():
    funds_arr = utils.load_entry(SAVEFILE)
    return funds_arr

# xlims
def get_xlim():
    today = datetime.datetime.utcnow().date()
    end_x = (today + datetime.timedelta(days=1))
    return pd.Timestamp(end_x)

# scuffed :sob:
def visualize():
    funds_arr = utils.load_entry(SAVEFILE)
    x, y = [fund.time for fund in funds_arr], [(int(fund.value) / 1000000) for fund in funds_arr]
    fig = plt.figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)
    plt.subplots_adjust(bottom=0.25)
    ax.scatter(mdates.datestr2num(x), y)
    plt.title("Tanki Fund over Time", fontsize=20)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.set_xlim(pd.Timestamp('2022-05-27 12:00:00'), get_xlim())
    plt.xticks(rotation=60)
    plt.xlabel("Time")
    y_upper = 1.2 * max(y)
    ax.set_ylim(0, y_upper)
    # checkpoint lines
    for i in range(len(CHECKPOINTS)):
        if CHECKPOINTS[i] < max(y):
            plt.axhline(CHECKPOINTS[i], color='green', linestyle='--', label=REWARDS[i])
        elif CHECKPOINTS[i] < y_upper:
            plt.axhline(CHECKPOINTS[i], color='red', linestyle='--', label=REWARDS[i])
    plt.ylabel("Fund (in millions)")
    plt.legend(loc=2)
    return fig

def fund_delta():
    funds_arr = utils.load_entry(SAVEFILE)
    if len(funds_arr) > 1:
        return int(funds_arr[-1].value) - int(funds_arr[-2].value)
    else:
        return 0