import uvicorn
from index.app import MyApp

def main():
    app=MyApp()
    uvicorn.run(app.app, host='0.0.0.0', port=8000, log_level='info', proxy_headers=True, access_log=False,root_path='', use_colors=False)
    
if __name__ == "__main__":
    main()