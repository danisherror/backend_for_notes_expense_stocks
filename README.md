# File structure
backend_for_notes_expense_stocks
  ├─ auth
  │  ├─ __pycache__
  │  │  └─ auth.cpython-312.pyc
  │  └─ auth.py
  ├─ database
  │  ├─ __pycache__
  │  │  └─ database.cpython-312.pyc
  │  └─ database.py
  ├─ main
  │  ├─ __pycache__
  │  │  └─ app.cpython-312.pyc
  │  └─ app.py
  ├─ models
  │  ├─ __pycache__
  │  │  └─ model.cpython-312.pyc
  │  └─ model.py
  ├─ routes
  │  ├─ __pycache__
  │  │  ├─ buy_stocks.cpython-312.pyc
  │  │  ├─ expense.cpython-312.pyc
  │  │  ├─ notes.cpython-312.pyc
  │  │  ├─ sold_stocks.cpython-312.pyc
  │  │  ├─ stock_historical_data.cpython-312.pyc
  │  │  ├─ transaction.cpython-312.pyc
  │  │  ├─ user_stocks.cpython-312.pyc
  │  │  └─ user.cpython-312.pyc
  │  ├─ buy_stocks.py
  │  ├─ expense.py
  │  ├─ notes.py
  │  ├─ sold_stocks.py
  │  ├─ stock_historical_data.py
  │  ├─ symbols_results.xlsx
  │  ├─ transaction.py
  │  ├─ user_stocks.py
  │  └─ user.py
  ├─].env (ignored)
  ├─ .gitattributes
  ├─ .gitignore
  ├─ README.md
  └─ requirements.txt

# Deployed site

```
https://backend-for-notes-expense-stocks.onrender.com
```


# .evc

```
MONGODB_URL=<your mongodb url>
SECRET_KEY= <your key
```

# run command

```
uvicorn main.app:app --reload
```

# Facing jwt error

- pip uninstall JWT
- pip uninstall PyJWT
- pip install PyJWT  
