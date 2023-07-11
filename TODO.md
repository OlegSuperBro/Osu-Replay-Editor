# Todo

- Interface:
  - [X] Add timestamp selector
  - Show info on another tab:
    - [X] Beatmap name
    - [X] Accuracy
    - [X] PP

  - [X] Show info in real time
  - [ ] Drag and drop (impossible in pysimplegui. Maybe when i'll rewrite to other GUI library)
  - [ ] Life graph editor
  - [ ] Replay player
  - [ ] Replay data editor
  - [X] Make it work through CLI

- CLI:
  - [X] Make it as separated file (remove main.py)

- Calculations:
  - [X] Calculate acc
  - [X] Calculate pp

- Replay player:
  - Rendering beatmap:
    - [ ] Skin support
    - [ ] Rendering objects:
      - [X] Circles
      - [ ] Sliders
      - [ ] Spiners
    - Apply mods:
      - [X] AR
      - [ ] CS
      - [ ] OD
  
  - Rendering replay:
    - [ ] Cursor
    - [ ] Presses
  
  - Timeline:
    - [ ] Scrolling through replay
    - [ ] Show misses, 50s etc (maybe like in [Rewind](https://github.com/abstrakt8/rewind))
  
  - [ ] Song playing

  - Issues:
    - [ ] Notes fades out sometimes
    - [ ] Full fade in when you should press note (Fade in should be done little before before press)
  