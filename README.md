<p><img src=frontend/src/assets/images/logo.svg alt="IVYSIM" align="center" /></p>

## What is Ivysim?
Ivysim is a web-based battle prediction and simulation tool for Pokémon Red/Blue.
At this point in time, it allows you to view your likelihood of victory against a CPU trainer from the single-player portion of the game.
The player uses a heuristic AI model while the opposing trainer uses a recreation of the actual AI model from Pokémon Red/Blue.
Since it's AI vs. AI, a single battle can start and end in a fraction of a second, and therefore, you can simulate hundreds of battles in less than a minute.
This of course gets a lot of data that can lead to useful insight and statistics.

## Features of Ivysim
Ivysim lets you:
- Select one of the major battles from Generation 1 (all gym leaders, all rival battles, and the Kanto Elite Four)
- Build your party from scratch using the in-app slot editor or import a party from a `.sav` file
- Choose how many battles you would like to simulate at a time
- Download logs of each battle, seeing what transpired in each battle
- View your statistics such as your recommended party leader and overall win rate

Ivysim supports:
- Importing a `.sav` file from Pokémon Red/Blue (Green/Yellow untested) to bring in your in-game party
- Downloading logs of your simulation to view what transpired in every battle
- Editing hidden stats such as EVs and DVs, as well as visible information such as nickname, moves, and level
- "Illegal" Pokémon such as those who have impossible DVs, are at an impossible level (e.g. a level 1 Ivysaur), or know moves they would otherwise not be able to learn
- Customizing your player and rival names for use in downloaded logs
- All original 151 Pokémon
- All original 165 moves (including Struggle as a selectable move)

## How to Use Ivysim
1. Download the source code
2. Uhhh, make sure you have all of the project dependencies (I'm really bad at this part)
3. If you're on Windows execute the oh so convenient `run.bat` to automatically boot up the app assuming you have everything from step 2

Continue here if you are on any other OS
4. Otherwise, open a terminal in the project directory and type the following:
```
cd backend
python -m uvicorn api.api:app --reload
cd ../frontend
npm run dev
```
5. Open your web browser and navigate to `localhost:5173`
6. Profit(???)
