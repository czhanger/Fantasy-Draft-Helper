from yfpy.query import YahooFantasySportsQuery
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

load_dotenv()

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


def get_drafted_players(players: list):
    draft_results = query.get_league_draft_results()
    for i, draft_result in enumerate(draft_results):
        if not draft_result.player_key:
            break
        # only query for player data, if player is new
        if i + 1 > len(players):  # if player # is greater than the last player drafted 
            player = query.get_player_ownership(draft_result.player_key)
            players.append(player)
            print(f"{i + 1}:{player.full_name}")


players = []


while True:
    again = input("query?")
    if again == "1":
        get_drafted_players(players)
    else:
        break