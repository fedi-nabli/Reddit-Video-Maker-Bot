import json

from pathlib import Path
import re
from typing import Dict
from utils import settings
from playwright.async_api import async_playwright # pylint: disable=unused-import

# do not remove the above line

from playwright.sync_api import sync_playwright, ViewportSize
from rich.progress import track
import translators as ts

from utils.console import print_step, print_substep

story_mode = False

def download_screenshot_of_reddit_posts(reddit_object: dict, sceenshot_num: int):
  """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png
  
  Args:
    reddit_object (Dict): Reddit object received from reddit/subreddit.py
    screenshot_num (int): Number of screenshots to download
  """

  print_step("Downloading screenshots of reddit posts...")
  id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
  # ! Make sure the reddit screenshots folder exists
  Path(f"assets/temp/{id}/png").mkdir(parents=True, exist_ok=True)

  with sync_playwright() as p:
    print_substep("Launching Headless Browser...")

    browser = p.chromium.launch()
    context = browser.new_context()

    if settings.config["settings"]["theme"] ==  "dark":
      cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
    else:
      cookie_file = open("./video_creation/data/cookie-light-mode.json", encoding="utf-8")
    
    cookies = json.load(cookie_file)
    context.add_cookies(cookies) # load preference cookies
    # Get the thread screenshot
    page = context.new_page()
    page.goto(reddit_object["thread_url"], timeout=0)
    page.set_viewport_size(ViewportSize(width=1920, height=1080))
    
    if page.locator('[data-testid="content-gate"]').is_visible():
      # This means the post is NSFW and requires to click the proceed button.

      print_substep("Post is NSFW. You are spicy...")
      page.locator('[data-testid="content-gate"] button').click()
      page.wait_for_load_state() # Wait for page to fully load

      if page.locator('[data-click-id="text"] button').is_visible():
        page.locator(
          '[data-click-id="text"] button'
        ).click() # Remove "Click to see nsfw" Button in Screenshot
    
    # translate code

    if settings.config["reddit"]["thread"]["post_lang"]:
      print_substep("Translating post...")
      texts_in_tl = ts.google(
        reddit_object["thread_title"],
        to_language=settings.config["reddit"]["thread"]["post_lang"]
      )

      page.evaluate(
        "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > div').textContent = tl_content",
        texts_in_tl
      )
    else:
      print_substep("Skipping translation...")

    post_content_path = f"assets/temp/{id}/png/title.png"
    page.locator('[data-test-id="post-content"]').screenshot(path=post_content_path)

    if story_mode:
      page.locator('[data-click-id="text"]').screenshot(
        path=f"assets/temp/{id}/png/story_content.png"
      )
    else:
      for idx, comment in enumerate(
        track(reddit_object["comments"], "Downloading screenshots...")
      ):
        # Stop if we have reached the screenshot_num
        if idx >= sceenshot_num:
          break

        if page.locator('[data-testid="content-gate"]').is_visible():
          page.locator('[data-testid="content-gate"] button').click()
        
        page.goto(f'https://reddit.com{comment["comment_url"]}', timeout=0)

        # translate code

        if settings.config["reddit"]["thread"]["post_lang"]:
          comment_tl = ts.google(
            comment["comment_body"],
            to_language=settings.config["reddit"]["thread"]["post_lang"],
          )

          page.evaluate(
            '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > div[data-testid="comment"] > div`).textContent = tl_content',
            [comment_tl, comment["comment_id"]],
          )
        
        try:
          page.locator(f"#t1_{comment['comment_id']}").screenshot(
            path=f"assets/temp/{id}/png/comment_{idx}.png"
          )
        except TimeoutError:
          del reddit_object["comments"]
          sceenshot_num += 1
          print("TimeoutError: Skipping screenshot...")
          continue
    
    print_substep("Screenshots downloaded Successfully.", style="bold green")