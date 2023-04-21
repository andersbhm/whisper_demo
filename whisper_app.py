import datetime
import os
import datetime
import time
from pathlib import Path
import whisper

from stable_whisper import modify_model
import streamlit as st
st.set_page_config(page_title="Whisper transcriper", page_icon=":computer:")


#@st.cache_resource
def get_whisper_model(name="medium", modify=True):
    '''Get a model from the whisper package. If modify is True, the model will be modified to work with the stable_whisper package.'''
    model = whisper.load_model(name)
    if modify: modify_model(model)
    return model

#@st.cache_resource
def transcripe_audio(audio_file_name, model, language=None):
    '''Transcribe an audio file with whisper.'''
    t1 = datetime.datetime.now()
    result = model.transcribe(audio_file_name, verbose=True, fp16=False, language=language)
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

def main():
    with st.container():
        st.title("Audio Transcriber")
        st.write("This app transcribes audio files to text.")
        
            
        model_name = st.selectbox("Whisper model:", ("tiny", "base", "small", "medium", "large", "large-v2"))
        
        language = st.selectbox("Spoken Language:", ("automatic", "English", "Norwegian",))
        if language == "automatic": language = None

        audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

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

                model = get_whisper_model(name=model_name, modify=True)

                st.write(f"Writing transcription with whisper model {model_name}. This takes some time...")
                result, dt = transcripe_audio(audio_file_name, model, language)
                srt = convert_to_srt(result)
                #save_srt(srt, audio_file_name)
                st.write(f"Transcription took {dt}")
                st.write("The transcription is shown below.")

                #download_button(srt, f"{audio_file.name}.srt")
                os.remove(audio_file_name)
                st.code(srt)

main()


