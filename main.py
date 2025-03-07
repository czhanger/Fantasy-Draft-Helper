import os
import sys
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
from unidecode import unidecode
import time

load_dotenv()

project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

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
sheet = workbook.worksheet("Draft Tracker")
player_map = {}

# yahoo api parameters
LEAGUE_ID = 131720  # in yahoo url
GAME_CODE = 'mlb'
GAME_ID = 458  # unique code for 2025
NUM_TEAMS = 10

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


def main():
    generate_player_map()
    drafted_players = []

    while True:
        again = input("Query?(1) ")
        if again == "1":
            get_drafted_players(drafted_players)
        else:
            break


def get_drafted_players(players: list):
    """
    Google API has a limit of 300 writes per minute
    """
    draft_results = query.get_league_draft_results()
    for i, draft_result in enumerate(draft_results):
        if not draft_result.player_key:
            break
        # only query for player data, if player is new
        if i + 1 > len(players):  # if player # is greater than the last player drafted 
            player = query.get_player_ownership(draft_result.player_key)
            try:
                player_taken(unidecode(player.full_name))  # unidecode converts foreign characters to plain text
                players.append(player)
                print(f"{i + 1}:{player.full_name}")
                time.sleep(0.75)  # avoid rate limit
            except:
                print(f"Error: Name Match Error for {player.full_name}")
                break
            


def generate_player_map():
    """
    Create a hash map of players
    Key is player's name, value is their ranking / row number on the sheet
    """
    player_list = sheet.col_values(2)

    for i, player in enumerate(player_list):
        player_map[player] = i


def player_taken(player_name):
    row = player_map[player_name]
    sheet.update_cell(row + 1, 4, "X")


main()