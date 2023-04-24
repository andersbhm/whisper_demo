# whisper_demo
Streamlit whisper demo


## Install packages
pip install -r requirements.txt 

## Run app
streamlit run whisper_app.py 

## Docker 
docker build -t whisper_demo .

docker run -dp 8501:8501 whisper_demo
