import os
import subprocess
from datetime import datetime
from voice.speaker import speak
from voice.listener import listen
from ai.gemini_ai import get_response
from tasks.general_tasks import execute_command

# --- Tamil to Hindi Translator Imports ---
from translator.speech_input import recognize_speech
from translator.translator_engine import translate_tamil_to_hindi
from translator.speech_output import speak_text

# --- GIF Display Imports ---
import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

# --- Spotify Integration Imports ---
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

# --- Logging Function ---
def log_conversation(role, message):
    log_path = os.path.join(os.getcwd(), "conversation_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {role}: {message}\n")

# --- GIF Display Configuration ---
speech_to_gif = {
    "hello": "hello.gif",
    "thank you": "thanks.gif",
    "yes": "yes.gif",
    "no": "no.gif"
}

def listen_and_show_gif():
    """Listen for speech and display corresponding GIF"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎤 Listening for GIF trigger words...")
        speak("GIF முறையில் கேட்கிறேன்...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"🗣️ You said: {command}")
        log_conversation("User", command)
        
        for word in speech_to_gif:
            if word in command:
                gif_path = f"zara_assets/gif_output/{speech_to_gif[word]}"
                show_gif(gif_path)
                break
        else:
            print("❌ No matching GIF found for command")
            speak("அந்த வார்த்தைக்கு GIF கிடைக்கவில்லை.")
    except Exception as e:
        print(f"❌ Could not understand audio: {e}")
        speak("உங்கள் பேச்சை புரிந்துகொள்ள முடியவில்லை.")

def show_gif(gif_path):
    """Display animated GIF in a window"""
    if not os.path.exists(gif_path):
        print(f"❌ GIF file not found: {gif_path}")
        speak("GIF கோப்பு காணவில்லை.")
        return
    
    try:
        root = tk.Tk()
        root.title("Zara GIF Output")
        root.geometry("400x400")

        gif = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(gif)]
        
        label = tk.Label(root)
        label.pack(expand=True)

        def update(index):
            frame = frames[index]
            index = (index + 1) % len(frames)
            label.configure(image=frame)
            root.after(100, update, index)

        root.after(0, update, 0)
        
        # Auto close after 5 seconds
        root.after(5000, root.destroy)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error displaying GIF: {e}")
        speak("GIF காட்ட முடியவில்லை.")

# --- Spotify Integration Configuration ---
SPOTIFY_SCOPE = "user-modify-playback-state user-read-playback-state playlist-modify-public"

def clear_spotify_cache():
    """Clear Spotify authentication cache"""
    cache_files = [".cache", ".cache-*"]
    for pattern in cache_files:
        import glob
        for cache_file in glob.glob(pattern):
            try:
                os.remove(cache_file)
                print(f"🗑️ Removed cache file: {cache_file}")
            except Exception as e:
                print(f"❌ Could not remove {cache_file}: {e}")

def initialize_spotify():
    """Initialize Spotify client with authentication"""
    try:
        # Clear any existing cache file
        cache_path = ".cache"
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print("🗑️ Cleared Spotify cache")
        
        sp_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE,
            cache_path=cache_path
        )
        
        spotify = spotipy.Spotify(auth_manager=sp_oauth)
        return spotify
    except Exception as e:
        print(f"❌ Spotify authentication failed: {e}")
        speak("Spotify இணைப்பு தோல்வியடைந்தது.")
        return None

def search_and_play_song_no_auth(song_query):
    """No authentication version - just open Spotify search"""
    try:
        # Direct Spotify web search without API
        search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
        webbrowser.open(search_url)
        
        success_msg = f"{song_query} Spotify இல் தேடப்பட்டது!"
        print(f"🌐 {success_msg}")
        speak(f"{song_query} Spotify இல் தேடுகிறேன்.")
        log_conversation("Assistant", f"Searched Spotify for: {song_query}")
        return True
        
    except Exception as e:
        error_msg = f"பிழை: {e}"
        print(f"❌ {error_msg}")
        speak("Spotify தேடலில் பிழை.")
        return False

def search_and_play_song_simple(song_query):
    """Simple version - search and open in web browser"""
    try:
        spotify = initialize_spotify()
        if not spotify:
            # Fallback: search on web without authentication
            search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
            webbrowser.open(search_url)
            fallback_msg = f"{song_query} வெப் பிளேயரில் தேடுகிறேன்."
            print(f"🌐 {fallback_msg}")
            speak(fallback_msg)
            return True
        
        print(f"🔍 Searching for: {song_query}")
        speak(f"{song_query} தேடுகிறேன்...")
        
        # Search for the song
        results = spotify.search(q=song_query, type='track', limit=1)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            
            print(f"🎵 Found: {track_name} by {artist_name}")
            speak(f"{track_name} கண்டுபிடித்தேன். வெப் பிளேயரில் திறக்கிறேன்...")
            log_conversation("Assistant", f"Opening: {track_name} by {artist_name}")
            
            # Always open in web browser (simpler approach)
            spotify_url = f"https://open.spotify.com/track/{track['id']}"
            webbrowser.open(spotify_url)
            
            success_msg = f"{track_name} வெப் பிளேயரில் திறக்கப்பட்டது!"
            print(f"✅ {success_msg}")
            speak(success_msg)
            return True
        else:
            not_found_msg = f"{song_query} பாடல் கண்டுபிடிக்க முடியவில்லை."
            print(f"❌ {not_found_msg}")
            speak(not_found_msg)
            return False
            
    except Exception as e:
        # Fallback: direct web search
        search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
        webbrowser.open(search_url)
        fallback_msg = f"{song_query} வெப் பிளேயரில் தேடுகிறேன்."
        print(f"🌐 {fallback_msg}")
        speak(fallback_msg)
        return True

def search_and_play_song(song_query):
    """Search for a song on Spotify and play it"""
    try:
        spotify = initialize_spotify()
        if not spotify:
            return False
        
        print(f"🔍 Searching for: {song_query}")
        speak(f"{song_query} தேடுகிறேன்...")
        
        # Search for the song
        results = spotify.search(q=song_query, type='track', limit=1)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            track_uri = track['uri']
            
            print(f"🎵 Found: {track_name} by {artist_name}")
            speak(f"{track_name} கண்டுபிடித்தேன். இசைக்கிறேன்...")
            log_conversation("Assistant", f"Playing: {track_name} by {artist_name}")
            
            # Get available devices
            devices = spotify.devices()
            if devices['devices']:
                # Play the song on the first available device
                device_id = devices['devices'][0]['id']
                spotify.start_playback(device_id=device_id, uris=[track_uri])
                
                success_msg = f"{track_name} இசைக்கப்படுகிறது!"
                print(f"✅ {success_msg}")
                speak(success_msg)
                return True
            else:
                # No active device found, open Spotify web player
                spotify_url = f"https://open.spotify.com/track/{track['id']}"
                webbrowser.open(spotify_url)
                
                fallback_msg = "Spotify சாதனம் இல்லை. வெப் பிளேயரில் திறக்கிறேன்."
                print(f"⚠️ {fallback_msg}")
                speak(fallback_msg)
                return True
        else:
            not_found_msg = f"{song_query} பாடல் கண்டுபிடிக்க முடியவில்லை."
            print(f"❌ {not_found_msg}")
            speak(not_found_msg)
            return False
            
    except Exception as e:
        error_msg = f"Spotify பிழை: {e}"
        print(f"❌ {error_msg}")
        speak("Spotify இல் பிழை ஏற்பட்டது.")
        return False

def listen_for_song_request():
    """Listen for song name and search/play it"""
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        speak("எந்த பாடலை கேட்க விரும்புகிறீர்கள்?")
        print("🎤 Listening for song request...")
        
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10)
        
        song_query = recognizer.recognize_google(audio)
        print(f"🎵 Song request: {song_query}")
        log_conversation("User", f"Song request: {song_query}")
        
        return search_and_play_song_no_auth(song_query)  # Use no-auth version
        
    except sr.WaitTimeoutError:
        timeout_msg = "நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்."
        print(f"⏰ {timeout_msg}")
        speak(timeout_msg)
        return False
    except Exception as e:
        error_msg = f"பாடல் கோரிக்கை புரிந்துகொள்ள முடியவில்லை: {e}"
        print(f"❌ {error_msg}")
        speak("பாடல் கோரிக்கை புரிந்துகொள்ள முடியவில்லை.")
        return False

# Function to open gesture recognition window
def open_gesture_window():
    try:
        gesture_script_path = os.path.join(os.getcwd(), "gesture", "gesture.py")
        if os.path.exists(gesture_script_path):
            subprocess.Popen(["python", gesture_script_path])
            speak("கை சைகை விண்டோ திறக்கப்படுகிறது...")
            log_conversation("Assistant", "கை சைகை விண்டோ திறக்கப்படுகிறது...")
        else:
            speak("கை சைகை கோப்பு காணவில்லை.")
            log_conversation("Assistant", "கை சைகை கோப்பு காணவில்லை.")
            print(f"[ERROR] Gesture file not found: {gesture_script_path}")
    except Exception as e:
        speak("கை சைகை முறை செயல்படவில்லை.")
        log_conversation("Assistant", "கை சைகை முறை செயல்படவில்லை.")
        print(f"[ERROR] Failed to open gesture window: {e}")

# Tamil to Hindi translation loop
def tamil_to_hindi_loop():
    speak("தமிழில் பேசுங்கள். ஹிந்தியில் மொழிபெயர்க்கப்படுகிறது. நிறுத்த 'niruthu' அல்லது 'stop' என்று சொல்லுங்கள்.")
    log_conversation("Assistant", "தமிழில் பேசுங்கள். ஹிந்தியில் மொழிபெயர்க்கப்படுகிறது. நிறுத்த 'niruthu' அல்லது 'stop' என்று சொல்லுங்கள்.")
    print("🟢 Tamil ➡️ Hindi translator running. Say something in Tamil.")
    while True:
        input_text = recognize_speech()
        log_conversation("User", input_text)

        if input_text.lower() in ["niruthu", "stop", "exit","நிறுத்து", "நிற்கவும்", "வெளியேறு", "வெளியே"]:
            speak("மொழிபெயர்ப்பு நிறுத்தப்பட்டது.")
            log_conversation("Assistant", "மொழிபெயர்ப்பு நிறுத்தப்பட்டது.")
            print("🛑 Exiting translator.")
            break

        if input_text.strip() == "":
            continue

        print(f"🗣️ Tamil: {input_text}")
        hindi_output = translate_tamil_to_hindi(input_text)
        print(f"📝 Hindi: {hindi_output}")
        log_conversation("Assistant", hindi_output)
        speak_text(hindi_output)

# Process user commands
def process_command(command):
    if not command:
        return

    print(f"[USER COMMAND]: {command}")
    log_conversation("User", command)

    # If gesture command
    if any(kw in command.lower() for kw in ["gesture", "கை சைகை", "open gesture", "start gesture"]):
        open_gesture_window()
        return

    # If GIF display command
    if any(kw in command.lower() for kw in ["gif", "show gif", "display gif", "GIF காட்டு", "gif காட்டு"]):
        listen_and_show_gif()
        return

    # If Spotify/music command
    if any(kw in command.lower() for kw in ["play song", "play music", "spotify", "பாடல் இசை", "இசை இசை", "song play", "music play"]):
        listen_for_song_request()
        return

    # If direct song search (contains "play" + song name)
    if "play" in command.lower() and len(command.split()) > 1:
        # Extract song name after "play"
        parts = command.lower().split("play", 1)
        if len(parts) > 1:
            song_name = parts[1].strip()
            if song_name:
                search_and_play_song_no_auth(song_name)  # Use no-auth version
                return

    # If user wants translator mode
    if any(kw in command.lower() for kw in ["translator", "translate", "மொழிபெயர்ப்பு", "tamil to hindi"]):
        tamil_to_hindi_loop()
        return

    # If general task command
    if execute_command(command):
        log_conversation("Assistant", "Executed general task command.")
        return

    # If none of the above, use Gemini AI to respond
    response = get_response(command)
    log_conversation("Assistant", response)
    speak(response)

# Entry point
if __name__ == "__main__":
    welcome_msg = "வணக்கம்! நான் ஜாரா. இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்? கை சைகை, மொழிபெயர்ப்பு, GIF காட்ட, அல்லது பாடல் இசைக்க சொல்லுங்கள்!"
    speak(welcome_msg)
    log_conversation("Assistant", welcome_msg)
    while True:
        command = listen()
        process_command(command)