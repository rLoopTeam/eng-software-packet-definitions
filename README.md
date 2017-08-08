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

## Files
```sh
packets/ # Node folder container
  node.yml # Packet definitions split by node

output/ # Persistent data folder
  fileSums.json # Checksums of pod files.
  packetDefinitions.json # Machine friendly combined defintions file.
  packetDefinitions_human.json # Human friendly combined defintions file.
  packetDefinitions.yml # Final combined defintions file.
```

## Packet definition example
```yaml
# Variables to substitute in [optional]
vars:
  nodeName: 'A'

# Node name
node: 'Imaginary Node {nodeName}'

# Source code files that correspond to packet transmissions.
# These files checksums will be calculated and saved to fileSums.json in the output folder.
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
    prefix: 'Imaginary {nodeName} Moon ' # Prefix for parameters
    packetType: 0x1337 # Aqquired from pod code
    parameters:
      - 'Distance':
        type: 'int64' # [u]int[8,16,32,64], float[32,64]
        units: 'km' # Units to show on the frontend, defaults to ''
        beginLoop: false # optional, defaults to false
        endLoop: false # optional, defaults to false

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

# Do some code! :)
````
