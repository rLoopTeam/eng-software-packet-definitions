# eng-software-packet-defintions [![Build Status](https://travis-ci.org/rLoopTeam/eng-software-packet-definitions.svg?branch=master)](https://travis-ci.org/rLoopTeam/eng-software-packet-definitions) [![Coverage Status](https://coveralls.io/repos/github/rLoopTeam/eng-software-packet-definitions/badge.svg)](https://coveralls.io/github/rLoopTeam/eng-software-packet-definitions)
This generates a packet definitions JSON/YAML file that can be used in the ground station or other internal apps that parse pod packets.

# Usage
1. Add/edit packet defintions in the packets/ directory.
2. `python rloopDefinitionApp` with the virtual environment active.
3. Grab the output files in output/ and push changes to Git.

# General Notes
* Ensure that you have eng-software-pod one folder up from this repo.

# Standards
* Python
  * Version 3.
* PEP8
  * --ignore=
  * --max-line-length=120
* Python
  * 4 spaces.
* YAML, Markdown
  * 2 spaces.
* All
  * Single newline at the end of file.
* TODO: See what else can be decided upon by the team.

# Layout

## Files
```sh
packets/ # Node folder container
  node.yml # Packet definitions split by node

output/ # Persistent data folder
  file_sums.json # Checksums of pod files.
  gs_definitions.yml # Formatted file for the ground station.
  packet_definitions_v2.json # Machine friendly combined defintions file.
  packet_definitions_human_readable_v2.json # Human friendly combined defintions file.
  packet_definitions_v2.yml # Final combined defintions file.
```

## Packet definition example
```yaml
# Variables to substitute in [optional]
vars:
  nodeName: 'A'

# Node name
node: 'Imaginary Node {nodeName}'

# Source code files that correspond to packet transmissions.
# These files checksums will be calculated and saved to file_sums.json in the output folder.
# This is so we can automate the process of knowing if anything in the transmission code has changed.
podSources: 
  # Imaginary packet types are in here.
  - FIRMWARE/PROJECT_CODE/LCCM655__RLOOP__FCU_CORE/NETWORKING/fcu_core__net__packet_types.h
  # Moon data.
  - FIRMWARE/PROJECT_CODE/LCCM999__RLOOP__IMAGINARY/IMAGINARY_THING/imaginary_thing__moon__ethernet.c

# List of all the packets that file serves.
packets:
  # Normal Packet
  - packetName: 'Imaginary {nodeName} Moon Distance'
    packetType: 0x1337 # Aqquired from pod code
    prefix: 'Imaginary {nodeName} Moon ' # Prefix for parameters
    # TODO: NOT_IMPLEMENTED
    description: 'An optional description of this packet.'
    # TODO: NOT_IMPLEMENTED
    friendlyName: 'Imaginary {nodeName} Moon Distance' # Defaults to packetName if not set.
    # TODO: NOT_IMPLEMENTED
    senders: # List of senders of this packet.
      - IN
    # TODO: NOT_IMPLEMENTED
    receivers: # List of recievers of this packet.
      - GS
    parameters:
      - name: 'Distance'
        type: 'int64' # [u]int[8,16,32,64], float[32,64]
        units: 'km' # Units to show on the frontend, defaults to ''

        # Ground Station specific loop:
        # Only for use at the end of packets.
        beginLoop: false # optional, defaults to false
        endLoop: false # optional, defaults to false

        # Generator specific iteration settings
        # Sets variable {i} in templates to the iteration count.
        # Iterates from (start, end) inclusive unless flagged.
        iterate:
          start: 0 # defaults to 0
          end: 8 # required, end of iteration
          inclusive: false # defaults to true
          beginGroup: true # optional, marks the start of a packet group
          endGroup: false # optional, marks the end of a packet group

  # DAQ Packet
  - packetName: 'IMAGINARY DAQ {nodeName} DISTANCE'
    packetType: 0x1337
    daq: # This has to be defined to make the packet a DAQ packet.
      type: 'int64' # [u]int[8,16,32,64], float[32,64]
```

# Windows Environment Setup
### TODO: How does Windows work? :P

# UNIX Environment Setup
```sh
# Explicit interpreter choice to ensure that our default interpreter is python3.
virtualenv -p python3 env/

# Creates the environment and installs our dependicies.
source env/bin/activate
pip install -r requirements.txt
python setup.py develop

# Do some code! :)
````
