# BoonNano Python API

Python API for interacting with BoonNano Cloud API

## Getting Started

This project has a few python dependencies required for local testing

### Prerequisites

Python dependences 

```
pip install numpy
pip install urllib3 
```

### Installing

Clone into your python workspace:

```
git clone git@gitlab.boonlogic.com:development/tools/boonnanopyapi.git
```

Import into your source code:

```
from boonnanopyapi import BoonNano
```

To install within a virtual environment in the editable state:
```
pip install -e boonnanopyapi
```
Then all edits made to the `.py` files will be included automatically in the installed package.

### Using Virtual Environment

Python dependences 

```
pip install virtualenv
```

```
git clone git@gitlab.boonlogic.com:development/tools/boonnanopyapi.git
```

```
cd boonnanopyapi
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```


To leave virtual environment
```
deactivative
```


## Authors

Boon Logic Inc.
