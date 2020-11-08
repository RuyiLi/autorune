# AutoRune
Automagic rune creator for League of Legends. We take care of the pre-game, so you can bring your A-game when the match starts.

[Devpost](https://devpost.com/software/autorune) | [Demo Video](https://www.youtube.com/watch?v=3WDnwsDSlto&ab_channel=RuyiLi)

# Usage
AutoRune has been tested to work on Windows 10. There are no precompiled binaries at the moment, so if you want to use it you'll have to build from the source. Here are the instructions:

1. Clone this repository to your local drive and `cd` into the created directory
2. In `autorune.py`, change the `LEAGUE_PATH` variable to the folder that your League of Legends executable is in (normally `C:\Riot Games\League of Legends`)
3. (Optional) Create a virtual environment (e.g. `python -m venv venv`) and activate it (e.g. `.\venv\Scripts\activate`). AutoRune has been tested to work on Python versions 3.7+, but it should work on any 3.x
4. Install the required dependencies with `pip install -r requirements.txt`
5. Run `python main.py`

And you're done! The AutoRune window should pop up and will automatically update to reflect which champion you're playing and which runes it has selected.