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
alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# yahoo api parameters
LEAGUE_ID = 136870  # in yahoo url
PUBLIC_LEAGUE_ID = 132899  # used to test
GAME_CODE = 'mlb'
GAME_ID = 458  # unique code for 2025
NUM_TEAMS = 10  # league size

# google sheets parameters
PLAYER_COL = 2
TRACKER_COL = 4  # used if marking a new row instead of coloring player name

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
    """
    Ask for Sheet Name, Pitcher List or Expert Rankings
    If in Pitcher List mode, only mark players with SP in role eligibility
    Use Gspread to find col titled "Player Names"
    When a player is taken, change cell color to red
    """
    generate_player_map()
    drafted_players = []
    while True:
        again = input("Mark Drafted Players? (Y/N/CurrPick#) ")
        if again.lower() == "y":
            get_drafted_players(drafted_players)
        elif again.lower() == "n":
            break
        elif again.lower() == "r":
            generate_player_map()
        else:
            try:
                int(again)
                print(f"Skipping to Pick {again}")
                get_drafted_players(drafted_players, int(again) - 1)
            except ValueError:
                print("Invalid Input")


def get_drafted_players(drafted_players, curr_pick=0):
    """
    Generates draft object containing all draft picks using yfpy and yahoo API
    If curr_pick is provided, loop does not operate on player picks up until curr_pick
    Google API has a limit of 300 writes per minute
    """
    draft_results = query.get_league_draft_results()
    draft_pick = 1
    for draft_result in draft_results:
        if not draft_result.player_key:  # empty roster spot
            break  # stop searching
        
        # if the current pick # is greater than pick # of last drafted player
        # and current pick is greater than user given skip to pick
        # skip to pick is mostly used in case the program crashes
        if draft_pick > len(drafted_players) and draft_pick > curr_pick:  # query new players
            player = query.get_player_ownership(draft_result.player_key)
            # print(player.eligible_positions)  # use for pitcher list mode
            try:
                # unidecode converts foreign characters to plain text
                player_taken(unidecode(player.full_name))
                curr_pick = draft_pick
                drafted_players.append(player)
                print(f"{draft_pick}:{player.full_name} [{player.eligible_positions[0]}]")
                time.sleep(0.75)  # avoid rate limit
            except:
                print(f"Error: Name Match Error for {player.full_name}")
                print("Adjust the spelling in the Google Sheet to what is shown above and then Press 'R' to update the script")
                break

        draft_pick += 1

    print("Query Complete")
    return curr_pick


def generate_player_map():
    """
    Create a hash map of players
    Key is player's name, value is their ranking / row number on the sheet
    """
    print("Reading Google Sheets player rankings...")
    player_list = sheet.col_values(PLAYER_COL)

    for i, player in enumerate(player_list):
        player_map[player] = i + 1
    print("Google Sheets Player Rankings uploaded.")


def player_taken(player_name):
    row = player_map[player_name]
    # sheet.update_cell(row, TRACKER_COL, "X") # marks an X next to player name in new row
    sheet.format(f"{alpha[PLAYER_COL - 1]}{row}", {
        "backgroundColor": {
            "red": 1.0
        }
    })


main()

"""
TODO: write a function that compares ranking list names with yahoo api names
    does not need to fix the error, just detects it so user can fix it before
    using main function in a real draft

    Change color of name directly, do not use separate column of X's

    skip option ***
"""
