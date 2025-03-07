import os
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()
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


def generate_player_map():
    """
    Create a hash map of players
    Key is player's name, value is their ranking / row number on the sheet
    """
    player_list = sheet.col_values(2)
    player_map = {}

    for i, player in enumerate(player_list):
        player_map[player] = i

    return player_map


def player_taken(player_name):
    row = player_map[player_name]
    sheet.update_cell(row + 1, 4, "X")


player_map = generate_player_map()
