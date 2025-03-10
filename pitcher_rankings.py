import os
import sys
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
from unidecode import unidecode
import time
from bs4 import BeautifulSoup

load_dotenv()

WORKSHEET_NAME = "2025 Pitchers"
PITCHER_COL = 2
PITCHERS = 75

# google sheets api auth
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# create a client that can access sheets
creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
client = gspread.authorize(creds)

# access desired sheet file
sheet_id = "11qN_oLKYCZN8yjeYsK_WCTW3mCzfX49xtX9PUSYvFWw"
workbook = client.open_by_key(sheet_id)

# select sheet from workbook
sheet = workbook.worksheet(WORKSHEET_NAME)

# create Pitcher Ranking List
with open("pitcherlist_400.html") as page:
    soup = BeautifulSoup(page, "html.parser")

names = soup.find_all("a")
pitcher_list = []
for i, name in enumerate(names):
    name = name.contents[0]
    pitcher_list.append(name)


# fill column with Pitcher List Rankings
def fill_col(values: list):
    row = 2
    for pitcher in values:
        sheet.update_cell(row, PITCHER_COL, unidecode(pitcher))
        print(row - 1, pitcher)
        row += 1
        if row - 1 > PITCHERS:
            row -= 1
            break
        time.sleep(0.5)
    print(f"Google Sheet Pitcher Rankings Updated: {row - 1} Pitchers")


# create Yahoo Pitcher ADP
# yahoo api parameters
LEAGUE_ID = 132899  # in yahoo url
PUBLIC_LEAGUE_ID = 132899  # used to test
GAME_CODE = 'mlb'
GAME_ID = 458  # unique code for 2025
NUM_TEAMS = 10  # league size

# google sheets parameters
PLAYER_COL = 2
TRACKER_COL = 4

project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

# create query tool
query = YahooFantasySportsQuery(
    LEAGUE_ID,
    GAME_CODE,
    GAME_ID,
    os.getenv("YAHOO_CONSUMER_KEY"),
    os.getenv("YAHOO_CONSUMER_SECRET"),
    env_file_location=project_dir,
    save_token_data_to_env_file=True
)

fill_col(pitcher_list)
