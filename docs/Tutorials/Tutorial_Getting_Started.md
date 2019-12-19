# Tutorial: Getting Started

Import the python client library from PyPI from the command line:
```sh
pip install boonnano
```

Then follow the steps below to create the file to run the data:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')
success, ver = bn.get_version(nano)
print(ver)
bn.close_nano(nano)
```

### Load the python client library
[Python3](https://programwithus.com/learn-to-code/install-python3-mac/) is needed to run the python client library for the Nano API.

Import the python client library from PyPI from the command line:
```sh
pip install boonnano
```

### Setting up client library
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoVersion.py`.

One the first line import the boonnano library:
```python
import boonnano as bn
```
On the next line, start up a nano. Input a label and the user whose authentication criteria you want to use.
```python
success,nano = bn.open_nano('example','username')
```
Enter down a few lines and close the nano.
```python
bn.close_nano(nano)
```
Save the file.

All the following code will be entered between the open and close nano calls.

### Get the version number
Finally, on line 4 and 5, call the function get_version to return which Boon Nano is associated with your account and print the result.
```python
success,ver = bn.get_version(nano)
print(ver)
```

Save the file.

Go to the terminal and cd into the folder where the .py file is saved. Run `NanoVersion.py`.
```sh
$ python3 NanoVersion.py
```
You should see the output:
```sh
{'api-version': '2.0.pre', 'boon-nano': 'cc6a6997', 'expert-api': '40c0bfcb', 'expert-common': '17c5eafb'}
```
Where the second to last line is the version number of the BoonNano.

Congratulations! The client library successfully connected to Nano API.
<br/>
<br/>

See [Tutorial: Posting a Configuration](./Tutorial_Posting_a_Configuration.md) for the next step in the process.

<br/>

[Return to documentation homepage](../python-docs.md)
