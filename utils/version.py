import requests
from utils.console import print_step

def check_version(__VERSION__):
  response = requests.get(
    "https://api.github.com/repos/fedi-nabli/Reddit-Video-Maker-Bot/releases/latest"
  )
  latest_version = response.json()["tag_name"]
  if __VERSION__ == latest_version:
    print_step(f"You are using the newest version ({__VERSION__}) of the bot")
    return True
  else:
    print_step(
      f"You are using an older version ({__VERSION__}) of the bot. Download the newest version ({latest_version}) from https://api.github.com/repos/fedi-nabli/Reddit-Video-Maker-Bot/releases/latest"
    )