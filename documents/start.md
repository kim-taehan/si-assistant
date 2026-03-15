# venv 
## 가상환경 활성화
```text
python3 -m venv venv

source venv/bin/activate

pip freeze > requirements.txt

pip install -r requirements.txt

deactivate
```

## 로컬 개발
```bash
# 백엔드 실행
cd server && uvicorn main:app --reload

# 프론트엔드 실행
cd client && streamlit run pages/document.py
```