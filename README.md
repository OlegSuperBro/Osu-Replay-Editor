# Osu-Replay-Editor

This thing let you edit .osr files (osu! replays)

## Installation

1. Install python (i used 3.11)
2. Install requirements by running ```pip install -r requirements```
3. Run main file ```python main.py```

There only 1 known issue:

Replay that have skips, getting broken. It's problem in osrparse module and i'm trying to fix it!

Also i recommend use virtual environment.

I used [venv](https://docs.python.org/3/library/venv.html)

## How to use it

**Right now exists only CLI mode.** But GUI is planned

### CLI

| Argument   | Usage                                    | Description                     |
|------------|:----------------------------------------:|---------------------------------|
| path       | ``` main.py [path] ```                   | Path to replay/directory with replays|
| -o         | ``` main.py -o [path] ```                | Can be either file name (for single file) or directory (for single and multiple files). If it's file name, write edited replay in \[path\]. If it's directory, write all replays in that directory with names from 0 to inf (0.osr, 1.osr, ...) |
| --info     | ``` main.py --info ```                   | Show info about replay/replays (Show info AFTER changing)|
| --nickname | ``` main.py --nickname [name] ```        | Change nickname in replay to provided |
| --n300     | ``` main.py --n300 [0-65535] ```         | Change amount of 300s. Represented as unsigned short |
| --n100     | ``` main.py --n100 [0-65535] ```         | Change amount of 100s. Represented as unsigned short |
| --n50      | ``` main.py --n50 [0-65535] ```          | Change amount of 50s. Represented as unsigned short |
| --ngekis   | ``` main.py --ngekis [0-65535] ```       | Change amount of gekus. Represented as unsigned short |
| --nkatus   | ``` main.py --nkatus [0-65535] ```       | Change amount of katus. Represented as unsigned short |
| --nmisses  | ``` main.py --n300 [0-65535] ```         | Change amount of misses. Represented as unsigned short |
| --score    | ``` main.py --score [0-2147483647] ```   | Change displayed total score. Represented as int (can be negative if bigger than 2.147.483.647 ) |
| --maxcombo | ``` main.py --maxcombo [0-65535] ```     | Change displayed maximum combo. Represented as unsigned short |
| --pfc      | ``` main.py --pfc [True/False] ```       | Change visibility of "Perfect" text in life graph. |
| --mods     | ``` main.py --mods [mod,mod,...] ```     | Change mods. Gameplay changing mods (hr, mr) can possibly break replay (but you can still make ez+hr :D) |
| --rawmods  | ``` main.py --rawmods [0-2147483647] ``` | Same as ```--mods``` but you can use [mod codes](https://osu.ppy.sh/wiki/en/Client/File_formats/Osr_(file_format)) |
| --time     | ``` main.py --time [0-inf] ```           | Change when replay was played. Use [converter](https://www.datetimetoticks-converter.com/) |
