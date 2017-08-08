# eng-software-packet-defintions
This generates a packet definitions JSON/YAML file that can be used in the ground station or other internal apps that parse pod packets.

# General Notes
* Ensure that you have eng-software-pod one folder up from this repo.
* Python3 is the interpreter of choice for this project.

# Standards
* PEP8 excluding rules [TODO]
* 4 spaces with a single newline at the end of file
* TODO: See what else can be decided upon by the team.

# Windows Environment Setup
### TODO: How does Windows work? :P

# UNIX Environment Setup
```sh
# Explicit interpreter choice to ensure that our default interpreter is python3.
virtualenv -p python3 env/

source env/bin/activate
pip install -r requirements.txt
# Do some code!
````
