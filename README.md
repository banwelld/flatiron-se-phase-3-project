# Trivia Team Tracker

Trivia Team Tracker is an application that enables a trivia league to keep track of their current teams and the members of each team.

## Table of Contents

[Project Overview](#project-overview)  
[Features](#features)  
[Installation](#installation)  
[Usage](#usage)  
[API Endpoints](#api-endpoints)  
[Components](#components)  
[Custom Hooks](#custom-hooks)  
[Technologies Used](#technologies-used)  
[Contributing](#contributing)  
[License](#license)

## Project Overview

The user-facing front end comprises a command-line interface that accepts input from the user, enabling them to perform operations such as creating a team, creating a new participant, adding and removing participants from teams, deleting teams or participants, and updating participant or team names.

Control flow is managed via a loop and a stack upon which every operation appends a tuple containing both a function representing the next operation to be performed and the state data with which it will be performed. The loop continuously invokes the function in the top-most tuple on the stack.

At any point in the flow, a user can use the back option to return to the previous step, which is facillitated by removing the top-most tuple from the stack and invoking the function in the previous tuple and replacing the current state data with the historical state data from the tuple.

The loop terminates only when the stack is empty. This is achievable only by use of a quit function that clears the stack.

The back end is a database with 2 tables, participant and team. Front and back end communication is facilitated by a team model and a participant model.

## Features

**Select Team**: This acts as the main menu and enables a user to select from any of the leagues teams or to create a new team. Users have the option to select from the menu options or quit the session.

**Select Operation**: This secondary menu displays a table showing the selected team along with its entire participant list or a message indicating that a team has no players if the list is vacant. Users have the option to select any of the operations or to select back to last step or quit the session.

**Team/User Management Operations**: If the selected operation requires a participant, the user will be directed to select from the team's participant list. If an operation requires user input (new team, new member, update name) the screen will be cleared and a table will be displayed showing the selected team and the selected member (in the case of a member operation). The user will be prompted for all necessary data.

When an operation has all necessary information from the user, the CLI will be cleared and a confirmation prompt will appear, asking the user to confirm their intention to persist the changes that they've made. If the user enters "y" or "Y", the changes will be persisted and a success message will be displayed, along with a prompt requiring the user to click "enter" in order to continue. If the user selects "n" or "N", a cancellation message will appear along with the instructions to press "enter" to continue.

Because it is expected that more than one operation might be performed on a team, the control stack is evacuated and returned to its historical state just after team selection so that the user can select another operation to be performed on the same team.

**Input Validation**: User input is validated at every step to ensure optimal application performance.

Menu selections are validated to ensure that:

- the user's response represents a valid menu item
- an operation can be done on the selected team (e.g., only allow additions to teams that are under the maximum capacity)

Team and participant names and birth dates are validated to ensure that:

- names are within specified length parameters
- participant names don't contain digits
- names don't contain special characters not normally associated with a name
- birth dates are formatted yyyy-mm-dd
- birth dates are valid dates

## Installation

To set up Trivia Team Tracker locally, complete the following steps:

1. Go to this github repo and fork it: https://github.com/banwelld/flatiron-se-phase-3-project

2. Clone the repo in your terminal (using the url for your fork) and change directories into the project directory:

```bash
git clone https://github.com/banwelld/flatiron-se-phase-3-project.git
cd flatiron-se-phase-3-project
```

3. Install the virtual environment

```bash
pipenv install
```

4. Change directories to the database setup directory

```bash
cd lib/data/setup
```

5. Run the database initializer to ensure that you're starting name

```bash
python db_initializer.py
```

6. (OPTIONAL) Run the database seeder, which will populate your database with artificial teams and players 

```bash
python db_seeder.py
```

## Usage

To use Trivia Team Tracker, return to the project's outermost directory, type the following into the command line and hit "enter"

```bash
python lib/cli.py
```

You’ll be presented with a team selection menu, which is the entrypoint to the entire application.

## Technologies Used

**Frontend**: Python

**Database**: SQLite database

**ORM**: Custom based on Participant and Team models

**Additional Libraries**: JSON, pathlib, os, sys

## Contributing

If you'd like to contribute to MedTracker:

- Fork the repository
- Create a new branch (git checkout -b feature/YourFeature)
- Make your changes and commit (git commit -m 'Add new feature')
- Push to the branch (git push origin feature/YourFeature)
- Open a Pull Request

## License

See the license tab
