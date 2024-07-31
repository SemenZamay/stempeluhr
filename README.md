# stempeluhr

## Description
This simple application helps you track your work time spent

## How to start (on Windows with Visual Studio)
1. Create new repository on GitHub (you can skip this if you want to work localy) and clone it via VS terminal.
2. Create virtual environment `python -m venv venv`.
3. Run virtual environment: `venv/Scripts/activate`, and start installing dependencies:
	`pip install -r requirements.txt`.
4. Run briefcase `briefcase dev`.

## How to use:

You can log in to the application as a user, using the password "user" or as an admin, using the password "admin".

Log in as a user, you can start counting your working time, stop it, and continue if necessary, this time will be summed up and saved in a .json file.

After that, you can log out of the system and log in as an admin and see how much time the user spent on work.

The goal of creating MVP has been achieved, you can further expand and improve the application.