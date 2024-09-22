### Create Vritual Environment:

```python
py -m pip install virtualenv
virtualenv venv
venv\Scripts\activate
pip freeze > requirements.txt
pip install requests
```
### Create DataBase
```import sqlite3
conn = sqlite3.connect("./DATABASE NAME")```