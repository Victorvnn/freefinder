from dotenv import load_dotenv
load_dotenv(encoding="utf-8-sig")
from app.worker import main
if __name__=='__main__': main()
