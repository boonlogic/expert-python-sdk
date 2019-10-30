# Tutorial: Getting Started

If the client library is already downloaded from [Gitlab](https://gitlab.boonlogic.com/development/tools/boonnanopyapi), skip to [Setting up client library](#setup)

### Download the python client library
[Python3](https://programwithus.com/learn-to-code/install-python3-mac/) is needed to run the python client library for the Nano API.

Go to the [Python API Github repository](https://gitlab.boonlogic.com/development/tools/boonnanopyapi) and download `BoonNano.py` into the directory

### Setting up client library (Mac OS) {#setup}
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoVersion.py` in the same folder as where `BoonNano.py` is saved.

One the first five lines import the following libraries:
- os
- BoonNano
- time
- numpy
- json

the code should look like this:
```python
import os
import BoonNano
import time
import numpy as np
import json
```

Enter down twice and define the main function on line 8.
```python
def main():
```

On the next line, store the BoonNano class object in a variable, bn. For the second input argument, use the port number assigned to your account and the third input argument is the 32 digit token key generated specifically for your account.
```python
bn = BoonNano.BoonNano('localhost',5007,'2B69F78F61A572DBF8D1E44548B48')
```
Enter down three times and on line 12 and 13, define the initialization call:
```python
if __name__ == "__main__":
    main()
```

Save the file.

### Get the version number
Finally, on line 9 and 10, call the function getVersion to return which Boon Nano is associated with your account and print the result.
```python
succeeded, ver = bn.get_version()
print(ver)
```

Save the file.

Go to the terminal and cd into the folder where the .py files are saved. Run `NanoVersion.py`.
```sh
$ python3 NanoVersion.py
```
You should see the output:
```sh
#################################
Opening BoonNano Client
URL:  http://localhost:5007/expert/v2/
#################################
2.0.pre
Closing Pool
```
Where the second to last line is the version number of the BoonNano.

Congratulations! The client library successfully connected to Nano API.
See [Tutorial: Posting a Configuration](./Tutorial_Posting_a_Configuration.md) for the next step in the process.

<br/>

[Return to documentation homepage](../Python_Landing_Page.md)
