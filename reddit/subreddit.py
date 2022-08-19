import re

from prawcore.exceptions import ResponseException

from utils import settings
import praw
from praw.models import MoreComments
from utils import subreddit

from utils.console import print_step, print_substep
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done
from utils.voice import sanitize_text

def get_subreddit_threads(POST_ID: str):
  """
  Returns a lost of threads from the AskReddit subreddit
  """

  print_substep("Logging into Reddit.")

  content = {}
  if settings.config["reddit"]["creds"]["2fa"]:
    print("\nEnter your two-factor authentication code from your authenticator app.\n")
    code = input("> ")
    print()
    pw = settings.config["reddit"]["creds"]["password"]
    passkey = f"{pw}:{code}"
  else:
    passkey = settings.config["reddit"]["creds"]["password"]
  
  username = settings.config["reddit"]["creds"]["username"]
  if str(username).casefold().startswith("u/"):
    username = username[2:]
  
  try:
    reddit = praw.Reddit(
      client_id=settings.config["reddit"]["creds"]["client_id"],
      client_secret=settings.config["reddit"]["creds"]["client_secret"],
      user_agent="Accessing Reddit threads",
      username=username,
      passkey=passkey,
      check_for_async=False,
    )
  except ResponseException as e:
    match e.response.status_code:
      case 401:
        print("Invalid credentials - please check them in config.toml")
  
  except:
    print("Something went wrong...")

  # Ask useer for subreddit input
  print_step("Getting subreddit threads...")
  if not settings.config["reddit"]["thread"]["subreddit"]:
    try:
      subreddit = reddit.subreddit(
        re.sub(r"r\/", "", input("What subreddit would you like to pull from? "))
        # removes the r/ from the input
      )
    except ValueError:
      subreddit = reddit.subreddit("askreddit")
      print_substep("Subreddit not defined. Using AskReddit.")
  
  else:
    sub = settings.config["reddit"]["thread"]["subreddit"]
    print_substep("Using subreddit: r/{sub} from TOML config")
    subreddit_choice = sub
    if str(subreddit_choice).casefold().startswith("r/"): # removes the r/ from the input
      subreddit_choice = subreddit_choice[2:]
    subreddit = reddit.subreddit(subreddit_choice)

  if POST_ID: # would only be called if there are multiple queued posts
    submission = reddit.submission(id=POST_ID)
  elif (
    settings.config["reddit"]["thread"]["post_id"]
    and len(str(settings.config["reddit"]["thread"]["post_id"]).split("+")) == 1
  ):
    submission = reddit.submission(id=settings.config["reddit"]["thread"]["post_id"])
  else:
    threads = subreddit.hot(limit=25)
    submission = get_subreddit_undone(threads, subreddit)
  
  submission = check_done(submission) # double-checking
  if submission is None or not submission.num_comments:
    return get_subreddit_threads(POST_ID) # submission already done. rerun

  upvotes = submission.score
  ratio = submission.upvote_ration * 100
  num_comments = submission.num_comments

  print_substep(f"Video will be: {submission.title} :thumbsup", style="bold green")
  print_substep(f"Thread has {upvotes} upvotes", style="bold blue")
  print_substep(f"Thread has an upvote ratio of {ratio}%", style="bold blue")
  print_substep(f"Thread has {num_comments} comments", style="bold blue")

  content["thread_url"] = f"https://reddit.com{submission.permalink}"
  content["thread_title"] = submission.title
  content["thread_post"] = submission.selftext
  content["thread_id"] = submission.id
  content["comments"] = []

  for top_level_comment in submission.comments:
    if isinstance(top_level_comment, MoreComments):
      continue
    if top_level_comment.body in ["[removed]", "[deleted]"]:
      continue
    if not top_level_comment.stickied:
      sanitized = sanitize_text(top_level_comment.body)
      if not sanitized or sanitized == "":
        continue
      if len(top_level_comment.body) <= int(
        settings.config["reddit"]["thread"]["max_comment_length"]
      ):
        if (
          top_level_comment.author is None
          and sanitize_text(top_level_comment.body) is not None
        ):
          content["comments"].append(
            {
              "comment_body": top_level_comment.body,
              "comment_url": top_level_comment.permalink,
              "comment_id": top_level_comment.id,
            }
          )

  print_substep("Recieved subreddit threads Successfully.", style="bold green")
  return content