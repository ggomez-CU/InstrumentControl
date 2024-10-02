# Instrument Control Library #

Used to interact with RF instrument controls for lo tuning and PA testing through SCPI commands

### Version History ###

0.1.0 : Initial Build. 

## Additional Editing and Build instructions ##

You need to have the project packaged to be able to run it in a test mode. the commands are:

python3 -m pip install build
python3 -m build --wheel
pip3 install dist/focustuner-0.1.0-py3-none-any.whl

python -m pip install build
python -m build --wheel
pip install dist/focustuner-0.1.0-py3-none-any.whl

and using:

```
python3 -m unittest discover
python -m unittest discover
```

python -m unittest discover

to test the code

### Library Creation ###
This library was created using instructions form https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f
Frankly it was started more than once so there is a high probability there are unnecessary components. It was a valiant effort though. 

try number 2
https://medium.com/@tushar_datascience/creating-a-python-library-a-step-by-step-guide-with-a-simple-example-c87b653b9a4e

You need to set up pypi API token. This is done by creating a API token on pypi and then creating a file in Users/[username]/ called .pypirc with the following:

[pypi]
  username = __token__
  password = [password from pypi]

  If you have done it correctly you will get these instructions (again) from pypi. 

Also you have to delete old dist files when uploading.

```
python -m build
twine upload dist/* --repository pypi --verbose
```

Ensure you update the version number and delete previous tar.gz and whl files for the previous version. This seems to do it.

### Start virtual environment ###

```
python -m venv venv
```

Activate for windows:

```
. venv\Scripts\activate
```

Activate for Mac:

```
. venv/bin/activate
```
