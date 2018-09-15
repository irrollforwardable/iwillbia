# Iwillbia (pre-alpha version)
Iwillbia /pronounced [aɪ'wɪlbɪa]/ derived from "I will be", means absolutely nothing, just a cool title in my opinion :)

"Notepady"-looking platformer game involving jumping over the words from the top of any text file in order to reach its end, as well as collecting coins, avoiding the bad guys and trasforming into words of that file.
![Alt Text](https://media.giphy.com/media/clskiCrKMRob9G9bsM/giphy.gif)

There is a lot of work ahead to make such visual representations of all the words in the world. Currently there are just a few, including that sheriff above :D

## Detailed game description
Iwillbia automatically starts in totorial mode, which provides a player with the basic understanding of game mechanics.
*Detailed description coming soon*

## Answering "why" questions
##### Why it resembles a standard windowed application and not a game with cool visual effects?
  - That was exactly my idea of the game’s UI, so that it looks like a text editor.
##### Why is it written in Python and why exactly version 2.7?
  - The game started as a prototype and Python, in my opinion, is a good choice for prototyping. I then prototyped further, having no straight goal/idea about what the game is going to become, and when a playable prototype was finished I had no desire to rewrite it in other programming language.
  - No real reason for version 2.7 other than my personal preference: I must admit that I have never even tried the 3-rd version. I also read somewhere that 2.7 tends to deal with lists faster than 3, but who knows…
  - Another advantage of Python is that it has all required functionality built in: Tkinter for GUI, sqlite3 for SQLite database.
  - Python, however, has its disadvantages relevant for this project:
    - Not compiled to native code, meaning slower performance, which is especially observed during concationation of large amount of strings
    - Dynamic typing is not my style.
##### Why not an online web app?
  - I like desktop apps more. This is my personal old-fashioned preference.
  - Someone would certainly get suspicious about the algorithm of uploading files (the ones that are used for the game) to the server: maybe I store them somewhere and run some kind of AI stuff upon them in order to gather sensitive information about players :D
  
## Contribution #1
I would be glad if someone would help the project with:
- Creating new game content (*TODO: link to wiki*)
- Ideas of further game concepts that I might have not even thought of (*TODO: link to wiki*)
- UI improvements (*TODO: link to wiki*)
- Translate the app into other languages (requires both technical and linguistic input) (*TODO: link to wiki*)
- Testing, catching bugs and reporting those to "Issues" section (*TODO: link to "Issues"*)
- Wiki pages
- Code refactoring: some pieces of code are real monstrosities, a lot of "TODO" comments here and there

## Contribution #2:
I cannot think of how the following would work, however this is urgently required, thus I encourage anyone to throw ideas into Wiki discussion
- Multi-user delivery of new content to database (sequences of primary key ids would be broken if everyone is simply pushing SQL INSERT statements)

## Build from source
Use [PyInstaller](https://www.pyinstaller.org/) for building.
### Windows
1. Navigate to the folder containing app.py module
2. Make sure that `is_mac` value is passed as False to Controller object inside app.py file: `app_controller = Controller(settings, is_mac=False)`
3. From this folder run the following command: `pyinstaller app.py --windowed --name="Iwillbia" --icon="icon.ico" --add-binary="data.db;." --add-binary="icon.ico;." --add-data="LICENSE;." --add-data="README.md;."`
4. Built distribution is placed inside `dist` folder

## Run
Two options:
- Run binary (*coming soon*)
- Run app.py from source (requires Python 2.7)
  - Windows and Linux: pass `is_mac` value as False to Controller object inside app.py file: `app_controller = Controller(settings, is_mac=False)`
  - Mac OS X: pass `is_mac` value as True to Controller object inside app.py file: `app_controller = Controller(settings, is_mac=True)`

## License
- Source code: GNU General Public License v3.0
- Game content: not decided yet :)
