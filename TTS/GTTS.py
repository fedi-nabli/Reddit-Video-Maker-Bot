import random
from utils import settings
from gtts import gTTS

max_chars = 0

class GTTS:
  def __init__(self):
    self.max_chars = 5000
    self.voices = []

  def run(self, text, filepath):
    tts = gTTS(
      text=text,
      lang=settings.config["reddit"]["thread"]["post_lang"] or "en",
      slow=False,
    )
    tts.save(filepath)

  def random_voice(self):
    return random.choice(self.voices)