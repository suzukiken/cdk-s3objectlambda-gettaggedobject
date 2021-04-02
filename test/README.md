
To send messages, do this at the root directory of this repository.

```
python -m venv test/env
source test/env/bin/activate
pip install -r test/requirements.txt
source test/setenv.sh
python3 test/delete_object.py
python3 test/put_object.py
python3 test/get_object.py
```
