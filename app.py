import streamlit as st
import requests
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
from googletrans import Translator
import speech_recognition as sr

# Initialize the translator
translator = Translator()

# Function for speech-to-text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service."

# Function for text-to-speech using gTTS
def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_audio_file:
        tts.save(temp_audio_file.name)
        temp_audio_file.seek(0)

        # Load the audio file into pydub and play it
        audio = AudioSegment.from_file(temp_audio_file.name)
        play(audio)

# Function to search the query using the custom search engine
def search_query(query):
    api_key = 'AIzaSyA-SzDdfHqkcHZwSTRXdy2VaVvrescYDUU'
    cse_id = "f794d76b57d7b4f03"
    search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"

    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json()
        if 'items' in results:
            return results['items']
        else:
            return []
    else:
        return []

# Function to summarize the search results using LLAMA API
def summarize_results_with_llama(search_results):
    # Prepare the content for LLAMA API
    text_to_summarize = "\n".join([f"{item['title']}: {item['snippet']}" for item in search_results])
    
    # Call LLAMA API
    llm_api_url = "https://sakksham.streamlit.app"  # Replace with actual LLAMA API endpoint
    llm_api_key = "LA-d54c3eb8a64f43e481ec890f62d1f212adc5085475324374a8692c2f853be9c4"  # Your LLAMA API key

    payload = {
        "text": text_to_summarize,
        "max_length": 200,  # Adjust as needed
        "temperature": 0.5  # Adjust creativity
    }
    
    headers = {
        "Authorization": f"Bearer {llm_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(llm_api_url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result.get('summary', 'No summary available.')
    else:
        return "Failed to summarize results."

# Function to translate text into the selected language
def translate_text(text, target_language):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return f"Translation error: {str(e)}"

# Streamlit App Code
st.title("Banno - Your Financial Assistant")
st.subheader("Ask your questions about finance")

user_input = st.text_input("Type your question here:")
# Language options for the dropdown menu, displayed in native scripts
languages = {
    'en': 'English',
    'hi': 'हिन्दी (Hindi)',
    'ta': 'தமிழ் (Tamil)',
    'bn': 'বাংলা (Bengali)',
    'te': 'తెలుగు (Telugu)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'mr': 'मराठी (Marathi)',
    'ml': 'മലയാളം (Malayalam)',
    'gu': 'ગુજરાતી (Gujarati)',
    'pa': 'ਪੰਜਾਬੀ (Punjabi)',
    'ur': 'اُردُو (Urdu)',
}

# Dropdown for language selection
target_language = st.selectbox("Select language for response:", options=list(languages.keys()), format_func=lambda x: languages[x])

if st.button("Submit"):
    if user_input:
        # Search the query
        search_results = search_query(user_input)
        if search_results:
            # Summarize the search results using LLAMA API
            summarized_results = summarize_results_with_llama(search_results)
        else:
            summarized_results = "No results found."

        # Translate the summarized text into the selected language
        translated_summary = translate_text(summarized_results, target_language)

        st.write("### Answer to Your Question:")
        st.write(translated_summary)

if st.button("Speak to Banno"):
    st.write("Click the button and start speaking.")
    spoken_text = speech_to_text()
    if spoken_text:
        st.write(f"You said: {spoken_text}")

        # Search the query
        search_results = search_query(spoken_text)
        if search_results:
            # Summarize the search results using LLAMA API
            summarized_results = summarize_results_with_llama(search_results)
        else:
            summarized_results = "No results found."

        # Translate the summarized text into the selected language
        translated_summary = translate_text(summarized_results, target_language)

        st.write("### Answer to Your Question:")
        st.write(translated_summary)
