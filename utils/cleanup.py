from itertools import count
import os
from os.path import exists

def _listdir(d):
  return [os.path.join(d, f) for f in os.listdir(d)]

def cleanup(id) -> int:
  """Deletes all temporary assets in assets/temp
  
  Returns:
    int: How many files were deleted
  """
  if exists("./assets/temp"):
    count = 0
    files = [f for f in os.listdir(".") if f.endswith(".mp4") and "temp" in f.lower()]
    count += len(files)
    for f in files:
      os.remove(f)
    
    REMOVE_DIRS = [f"./assets/temp/{id}/mp3/", f"./assets/temp/{id}/png/"]
    files_to_remove = list(map(_listdir, REMOVE_DIRS))
    for directory in files_to_remove:
      for file in directory:
        count += 1
        os.remove(file)
    return count
  
  return 0