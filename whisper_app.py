import datetime
import os
import datetime
import time
from pathlib import Path
import whisper
import torch
import yaml
from yaml.loader import SafeLoader

from stable_whisper import modify_model
import streamlit_authenticator as stauth
import streamlit as st

st.set_page_config(page_title="Whisper transcriper", page_icon=":computer:")


#@st.cache_resource
def get_whisper_model(name="medium", modify=True):
    '''Get a model from the whisper package. If modify is True, the model will be modified to work with the stable_whisper package.'''
    model = whisper.load_model(name)
    if modify: modify_model(model)
    return model

#@st.cache_resource
def transcripe_audio(audio_file_name, model, language=None, use_cuda=False):
    '''Transcribe an audio file with whisper.'''
    t1 = datetime.datetime.now()
    result = model.transcribe(audio_file_name, verbose=True, fp16=use_cuda, language=language)
    dt = (datetime.datetime.now() - t1)
    dt = str(dt)
    return result, dt


def timedelta_to_str(seconds):
    '''Convert a timedelta object to a string in the format hh:mm:ss,ms.'''
    delta = datetime.timedelta(seconds=seconds)
    formatted_delta_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(delta.seconds // 3600, (delta.seconds // 60) % 60, delta.seconds % 60, delta.microseconds // 1000)
    return formatted_delta_str

def convert_seg_element_to_srt_element(seg):
    '''Convert to srt file format.'''
    index = seg["id"] + 1
    start = seg["start"]
    start = timedelta_to_str(start)
    end = seg["end"]
    end = timedelta_to_str(end)
    text = seg["text"].strip()
    srt_element = f"{index}\n{start} --> {end}\n{text}\n\n"
    return srt_element


def convert_to_srt(result):
    '''Convert the result from the transcribe function to a srt file.'''
    segments = result["segments"]
    srt = ""
    for seg in segments:
        srt_element = convert_seg_element_to_srt_element(seg)
        srt = srt + srt_element
    return srt

def save_srt(srt, audio_file_name):
    '''Save the srt file to disk.'''

    filename = audio_file_name + ".srt"
    with open(filename, "w") as f:
        f.write(srt)

    filename = audio_file_name + ".txt"
    with open(filename, "w") as f:
        f.write(srt)


# Create a download button that downloads the text file
def download_button(text, filename):
    """
    Generates a download button that downloads a text file.
    """
    st.download_button(label="Download srt file", data=text,
        file_name=filename, mime="text/plain")



##################
path_audio_files = "audiofiles/"
model_name = None  #tiny, base, small, medium, large, large-v2
language = None
##################
os.makedirs(path_audio_files, exist_ok=True)

def run_app():
    with st.container():
        st.title("Webstep")
        st.header("Whisper audio transcriber demo")
        st.subheader("This app transcribes audio files to text. The app is intended for demo purposes only.")

        st.write("The natural language AI model can be further trained in any language to improve accuracy. The model can run in the cloud or on-premise.")
        
        use_cuda = torch.cuda.is_available()
        #st.write(f"GPU available: {use_cuda}")
            
        #model_name = st.selectbox("Select Whisper model:", ("tiny", "base", "small", "medium", "large", "large-v2"))
        model_name = "large-v2"
        #st.write("Tiny is fast and not accurate. Large is slow and accurate. The other models are in between.")
        
        st.write("")
        language = st.selectbox("Spoken Language:", ("automatic", "English", "Norwegian",))
        if language == "automatic": language = None

        st.write("")
        st.subheader("Please do not upload sensitive data.")

        audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "mp4"])




        if audio_file is None:
            st.warning("Please upload an audio file.")
            return



        if audio_file is not None:

            audio_file_name = f"{audio_file.name}_{time.time()}"
            
            bytes_data = audio_file.read()  # read the content of the file in binary
            with open(f"{path_audio_files}{audio_file_name}", "wb") as f:
                f.write(bytes_data)  # write this content elsewhere


            audio_file_name = path_audio_files + audio_file_name

            if len(audio_file_name) > 0:
                st.write(f"Writing transcription with whisper. This may take a while, but much faster than doing it yourself. Go grab some coffee meanwhile!")
                st.write("Downloading the model...")
                model = get_whisper_model(name=model_name, modify=True)
                st.write("Transcribing audio file...")
                result, dt = transcripe_audio(audio_file_name, model, language, use_cuda)
                srt = convert_to_srt(result)
                #save_srt(srt, audio_file_name)
                st.write(f"Transcription took {dt}")
                st.write("The transcription is shown below.")

                #download_button(srt, f"{audio_file.name}.srt")
                os.remove(audio_file_name)
                st.code(srt)

                st.write("You can copy the text above and save it as a .srt file. You can then use the .srt file to add subtitles to your video using for example VLC video player.")

                st.header("What's next?")
                st.write("This demo is intented for demo purposes only and we can help you customize the model to your needs.")
                st.markdown("- Train on new languages or dialects to improve accuracy")
                st.markdown("- The model can run in the cloud or on-premise for privacy")
                st.markdown("- The text output of the model can be used to create subtitles for videos or just regular text files in any format you want")
                st.markdown("- We can also give timestamps for each word in the transcription and provide a confidence score for each word.")
                
                         
                st.markdown("Please contact [joar.krohn@webstep.no](mailto:joar.krohn@webstep.no) or [knut.andersen@webstep.no](mailto:knut.andersen@webstep.no) for more information.")


def main():

    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
        )
    
    name, authentication_status, username = authenticator.login('Login', 'main')
    print(authentication_status, username  )
    if authentication_status:
        authenticator.logout('Logout', 'main', key='unique_key')
        run_app()

    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

main()


#hashed_passwords = stauth.Hasher(['abc']).generate()
#print(hashed_passwords)