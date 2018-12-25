# pyBACnet
pyBACnet is a python library to utilize the BACnet stack demo exe files. Please download release zip to get the ```bin``` folder

## Files
Contains two files which are two classes:

* ```classBACNet.py```: low-level to call executable files from ```BACnet Stack``` demo folder, default is ```./``` 
* ```classBACobj.py```: create 'object' for BACnet point (single read/write) and BACnet device (multiple read/write within the device).


## Usage
Make sure you have the ```bin``` folder (download from release page), this ```bin``` folder is for Windows, the BACnet stack is from this [link](https://sourceforge.net/projects/bacnet/):
### Initialization
```python
from classBACNet import classBACNet as cbn 
from classBACobj import classBACobj as cbo
```
Create a BACnet object for BACnet/IP with IP address is ```192.168.2.112``` running on Windows
```python
bacnetObj = cbn( type='IP', os='windows', adapt='192.168.2.112')
```
### Create a BACnet point object to read and write
```python
  Dev1234_AV0 = cbo( bacnet=bacnetObj,   % BACnet object
                     devid=1234,         % Device ID
                     objid=0,            % Object ID
                     objtp="AV",         % Object Type, e.g. AV,BV ...
                     prior=8)            % Priority
```
Read
```python
  Dev1234_AV0.read()
  ```
Write ```0.0```
```python
  Dev1234_AV0.write(value=0.0)
```

