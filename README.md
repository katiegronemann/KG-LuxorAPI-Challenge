# KG-LuxorAPI-Challenge
This program is designed to showcase my python abilies. This script manages the daily schedule for miner(s) running LuxOS.

### Dependencies
This script requires the `time`, `datetime`, `schedule` and `requests` libraries, please `pip install` these packages.


### Execution
To run this script:
- First ensure the LuxOS sample API is running and listening on `localhost:5000`
- Execute this script by running `python main.py` on Windows CMD or `python3 main.py` on select Linux systems.

### What It Does

## Requested Functionality

- The system is designed to cycle from overclock to normal, underclock, and curtailment in six-hour intervals for a set of miners.
- The program successfully implements this specified requirement and handles many edge cases and errors safely.
- Additionally, a demonstration mode has been implemented to enhance the visual representation of the program's execution.

## Demonstration Loop

The program runs through an indefinite demonstration loop, illustrating its behavior in various scenarios:

- Seamless cycling through the four modes defined in the assignment.
- Robust handling of invalid entries for both Profile and Mode inputs.
- Activation of miners into an "active" mode upon valid profile changes.
