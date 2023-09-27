# Changelog

# 2023.9.26.0

### Added
- Custom data in plugins (name, requirements, version, etc)
- Now you can use pre- and post- load/save
- Drag'n'drop for files
- Update checker on start
- New plugin: Replays history

### Changed
- Some refactoring (check commits with "refac" tag)

# 2023.8.9.0

### Added
- Dynamic preview changing
- App globals saved in different file

### Changed
- Updated pyosutools to 0.2.5
- Better plugins
- More renaming

### Fixed
- Removed selecting area with rmb
- Typing "\*e\*" in "total score" field now don't break

# 2023.7.20.1
Hotfix

### Changed
- Better error popup

### Fixed
- Error because no assets (i forgot about them D: )
- Error on launch without replay

# 2023.7.20.0

### Added
- Title now have path to current replay
- Caching for loading osu.db file
- Deleting points
- Lifebar now have preview

### Changed
- Saving replay will change working replay path to saved
- Interface was been rewrited
- Lifebar was reworked

### Fixed
- Opening corrupted replay "crashes" program
- Don't allow save empty replay

### Removed
- Removed CLI tool (moved to [another](https://github.com/OlegSuperBro/cli-replay-editor) repository)

# 2023.7.15.0

### Added
- Quering for life graph, for easier editing
- Config class
- Adding new point to life graph

### Changed
- Life graph now have same size as osu!
- Two graphs, first for viewing, second for editing
- Interface now is separated
- Windows now hiding, not closing

# 2023.7.10.1

First alpha release!

### Added
- Handling **FileNotFoundException** in CLI

### Fixed
- Trying to call ```--info``` calls **TypeError**

### Changed
- All main CLI lines now in func ```CLI_run```
- Now using default windows file dialog

### Removed
- Some debug prints in interface

## 2023.7.10.0

### Added
- More TODO's
- Started work with rendering

### Changed
- Replaced pyosudb with pyosutools

## 2023.7.6.0

### Added
- Replays lifebar data is now smaller
### Changed

- Now using DearPyGUI instead PySimpleGui

## 2023.7.2.0

### Added

- Changing lifebar data via CLI
- Changing lifebar with UI using matplotlib

### Chaged
- UI was been reworked a bit

### Fixed

- Perfect bug (was always true)

## 2023.6.26.0

### Added

- Life graph viewer (no editing for now)

### Changed

- Small clean up
- All windows now using template window
- Mods now have full names
- No more dicts for mods with name->code and code->name

### Removed

- Target practice mod from mod list (can break replay)

## 2023.6.24.0

### Added

- Some info on side:
  - Beatmap name
  - Real time accuracy
  - Real time pp
- Selector for date and time when replay was played
- Button to copy CLI command in clipboard

## 2023.6.12.1

### Added

- Configurations via yaml
- Function to generate command for CLI
- CLI command at bottom of window

### Changed

- Inteface now works throug commands to CLI.py
- Changing funcs order in **App** class
- Allow edit replay properties withot opening one (used for CLI command generation)

### Removed

- Andvanced layout type

## 2023.6.12.0

### Added

- Calculations for some info that can be only generated/calculated

### Changed

- Now CLI work from CLI.py, no more main.py
- Interface now changes dynamically

### Deleted

- main.py

## 2023.6.04.1

### Added

- simple interface
- limits for some arguments
- func for checking limit

## 2023.6.04.0

### Added

- Functions in **utils.py** to convert mods to code, code to mods, code to mode, mode to code

### Changed

- Moved source files to **scr** folder

## 2023.5.21.0

### Changed

- Deleting tmp_replay in main.py

### Fixed

- Saving file not in folder, but with name of this folder (how i missed this lol)

## 2023.5.20.0

### Added

- Changelog

### Changed

- Some things moved in **utils.py**
- ```-o``` now not required
- Now to get info from replay argument ```--info``` should be used
