# Changelog

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
