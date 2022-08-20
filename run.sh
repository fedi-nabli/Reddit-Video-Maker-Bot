# If the install fails, then print an error and exit.
function install_fail() {
  echo "Installation failed" 
  exit 1 
}

# This is the help fuction. It helps users withe the options
function Help(){ 
  echo "Usage: install.sh [option]" 
  echo "Options:" 
  echo "  -h: Show this help message and exit" 
  echo "  -d: Install only dependencies" 
  echo "  -p: Install only python dependencies (including playwright)" 
  echo "  -b: Install just the bot"
  echo "  -l: Install the bot and the python dependencies"
}

# Options
while getopts ":hypbl" option; do
  case $option in
    # -h, prints help message
    h)
      Help exit 0;;
    # -y, assumes yes
    y)
      ASSUME_YES=1;;
    # -p install only python dependencies
    p)
      PYTHON_ONLY=1;;
    b)
      JUST_BOT=1;;
    l)
      BOT_AND_PYTHON=1;;
    # if a bad argument is given, then throw an error
      \?)
        echo "Invalid option: -$OPTARG" >&2 Help exit 1;;
      :)
        echo "Option -$OPTARG requires an argument." >&2 Help exit 1;;
  esac
done

function get_the_bot(){ 
  echo "Downloading the bot" 
  rm -rf RedditVideoMakerBot-master
  curl -sL https://github.com/fedi-nabli/Reddit-Video-Maker-Bot/archive/refs/heads/master.zip -o master.zip
  unzip master.zip
  rm -rf master.zip
}

#install python dependencies
function install_python_dep(){ 
  # tell the user that the script is going to install the python dependencies
  echo "Installing python dependencies" 
  # cd into the directory
  cd Reddit-Video-Maker-Bot-main
  # install the dependencies
  pip install -r requirements.txt 
  # cd out
  cd ..
} 

# install playwright function
function install_playwright(){
  # tell the user that the script is going to install playwright 
  echo "Installing playwright"
  # cd into the directory where the script is downloaded
  cd Reddit-Video-Maker-Bot-main
  # run the install script
  python -m playwright install 
  python -m playwright install-deps 
  # give a note
  printf "Note, if these gave any errors, playwright may not be officially supported on your OS, check this issues page for support\nhttps://github.com/microsoft/playwright/issues"
  cd ..
}


# Main function
function install_main(){ 
  # Print that are installing
  echo "Installing..." 
  # if -y (assume yes) continue 
  if [[ ASSUME_YES -eq 1 ]]; then
    echo "Assuming yes"
  # else, ask if they want to continue
  else
    echo "Continue? (y/n)" 
    read answer 
    # if the answer is not yes, then exit
    if [ "$answer" != "y" ]; then
      echo "Aborting" 
      exit 1
    fi
  fi
  if [[ PYTHON_ONLY -eq 1 ]]; then
    # if the -p (only python dependencies) options is selected install just the python dependencies and playwright
    echo "Installing only python dependencies" 
      install_python_dep 
      install_playwright
  # if the -b (only the bot) options is selected install just the bot
  elif [[ JUST_BOT -eq 1 ]]; then
    echo "Installing only the bot"
    get_the_bot
  # if the -l (bot and python) options is selected install just the bot and python dependencies
  elif [[ BOT_AND_PYTHON -eq 1 ]]; then
    echo "Installing only the bot and python dependencies"
    get_the_bot
    install_python_dep
  # else, install everything
  else
    echo "Installing all" 
    get_the_bot 
    install_python_dep
    install_playwright
  fi

  DIR="./Reddit-Video-Maker-Bot-main"
  if [ -d "$DIR" ]; then
    printf "\nThe bot is installed, want to run it?"
    # if -y (assume yes) continue 
    if [[ ASSUME_YES -eq 1 ]]; then
      echo "Assuming yes"
    # else, ask if they want to continue
    else
      echo "Continue? (y/n)" 
      read answer 
      # if the answer is not yes, then exit
      if [ "$answer" != "y" ]; then
        echo "Aborting" 
        exit 1
      fi
    fi
    cd Reddit-Video-Maker-Bot-main
    python main.py
  fi
}

# Run the main function
install_main