# eng-software-packet-defintions
This generates a packet definitions JSON/YAML file that can be used in the ground station or other internal apps that parse pod packets.

# General Notes
* Ensure that you have eng-software-pod one folder up from this repo.
* Python3 is the interpreter of choice for this project.

# Standards
* PEP8
  * Rules [TODO] are excluded.
  * Line length 120.
* Python
  * 4 spaces.
* YAML, Markdown
  * 2 spaces.
* All
  * Single newline at the end of file.
* TODO: See what else can be decided upon by the team.

# Layout

## Folders
```sh
packets/ # Node folder container
  node.yml # Packet definitions split by node
```

## Packet definition template
```yaml
# Node name
node: 'Imaginary Node'

# Source code files that correspond to packet transmissions.
# These files checksums will be calculated and saved to .fileSums in the root folder.
# This is so we can automate the process of knowing if anything in the transmission code has changed.
podSources: 
  - FIRMWARE/PROJECT_CODE/LCCM999__RLOOP__IMAGINARY/IMAGINARY_THING/imaginary_thing__moon__ethernet.c

# List of all the packets that file serves.
packets:
  - packetName: 'Imaginary Moon Distance'
    prefix: 'Imaginary Moon ' # Prefix for parameters
    packetType: 0x1337 # Aqquired from pod code
    daq: false # DAQ packet
    parameters:
      - 'Count':
        type: 'uint16' # [u]int[8,16,32,64], float[32,64]
        units: '' # Units to show on the frontend
        size: 2 # Parameter size type / 8 (this can be automated)
        beginLoop: false # optional, defaults to false
        endLoop: false # optional, defaults to false
```

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
