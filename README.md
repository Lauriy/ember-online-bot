[![Actions Status](https://github.com/{owner}/{repo}/workflows/{workflow_name}/badge.svg)](https://github.com/{owner}/{repo}/actions)

# Ember Online arena bot
Tested in Bityrn, Canopia, Turenyara, Fort Huldar.

## Install

pywin32 can be retrieved from:
https://github.com/mhammond/pywin32/releases/download/b227/pywin32-227.win-amd64-py3.8.exe

If using it, create your venv after installing pywin32 and 'inherit global site-packages'.

Install requirements, create and edit your own .env file before running.

`pip install -r requirements.txt`

`cp .env.dist .env`

## Running

Relies on the /meditate skill (monk) or drink items for mana recovery (cleric). Only 2 classes supported.

Make sure your macros are in place: red spell, green spell, F1 long term restoration, F2 pot, etc.

## Testing
`pip install -r requirements-test.txt`

`pytest`
