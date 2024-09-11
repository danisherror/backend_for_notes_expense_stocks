# File structure

backend_for_notes_expense_stocks
├─ auth
│  └─ auth.py
├─ database
│  └─ database.py
├─ main
│  └─ app.py
├─ models
│  └─ model.py
├─ routes
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
