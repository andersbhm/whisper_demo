# whisper_demo
Streamlit whisper demo


## Install packages
pip install -r requirements.txt 

## Run app
streamlit run whisper_app.py 

## Docker 
docker build -t whisper_demo .

docker run -dp 80:80 whisper_demo
