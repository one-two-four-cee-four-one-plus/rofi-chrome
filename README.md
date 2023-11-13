# rofi-chrome
`rofi-chrome` is a chrome extensions that allows user to manage tabs without leaving the keyboard. It is inspired by buffer management in emacs. `rofi-chrome` consists of three parts: a chrome extension, a python server and collection of scripts utilizing rofi. Python server listens for http requests sent by scripts and then passes them to chrome extension via native messaging. Chrome extension then executes the commands.

## Installation
1. Clone the repository
2. Install the extension
    1. Open chrome://extensions/
    2. Enable developer mode
    3. Click on "Load unpacked" and select the extension folder
3. Run the server (no installation required)
    1. `cd` into the server folder
    2. Run `python3 server.py`
4. Bind scripts to keyboard shortcuts
5. Enjoy!

## Caveats
On start extension won't load automatically. You have to click on the extension icon to load it. This is because chrome doesn't allow extensions to run native messaging hosts automatically.