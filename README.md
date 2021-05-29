# Caleb-Burke-Ids-2021
Caleb Burke's IDS for Science Research Methods 12 2020/2021

Requirments before running program:
- Open command prompt in this dir on type command: pip install -r requirments
- Two options to get face_recognition:
	1. (ON WINDOWS) Download / install cuda and follow https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html
	2. On linux, run command: pip install face_recognition

Running on windows without CUDA and CUDNN will cause facial_recognition to be STUPID slow (30 seconds to scan image on a i7-4510U)

Other important info:
- ips of other nodes on the network will have to be hard coded into /src/data/network_Ips
- Network runs on port 5050
