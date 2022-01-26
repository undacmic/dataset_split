# Project bootstrap

In the project directory, use the following commands (as appropriate to your computer) to create and activate a virtual environment named .venv based on your current interpreter

## Linux
`sudo apt-get install python3-venv`

`python3 -m venv .venv`

`source .venv/bin/activate`


## macOS
`python3 -m venv .venv`

`source .venv/bin/activate`

## Windows
`py -3 -m venv .venv`

`.venv\scripts\activate`

## Update pip in the virtual environment by running the following command in the VS Code:

`python -m pip install --upgrade pip`

## Install python project dependencies

`pip install -r requirements.txt`


## Start the Flask backend

Runs the REST server that will parse and respond to the requests with JSON files\
containing statistics and datasets resulted from splitting.

`python -m flask run`

## Start the React frontend

`cd .\http\my-app\`

`npm start`

The development server that runs locally uses port 3000 for the app,\
and the Flask server runs default on pot 5000. In order, to redirect\
the fetch requests to the backend, we configure a proxy entry in the\
package.json file.




