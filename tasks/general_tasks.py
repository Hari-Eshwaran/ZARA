from voice.speaker import speak
import webbrowser
import datetime

def execute_command(command):
    command = command.lower()

    # YouTube - English & Tamil
    if "open youtube" in command or "யூடியூப்" in command or "யூடியூப் திற" in command:
        webbrowser.open("https://www.youtube.com/")
        speak("Opening YouTube")
        return True

    # Time - English & Tamil
    if "what is the time" in command or "சமயம் என்ன" in command or "இப்போது நேரம் என்ன" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return True

    # Carbon Footprint Calculator
    if "open calculator" in command or "கார்பன் கால்குலேட்டர் திற" in command:
        webbrowser.open("https://glaze.neocities.org/Ticket/templates/")
        speak("Opening Carbon Footprint Calculator")
        return True
    # Jayamurugan portfolio
    if "open Jayamurugan portfolio" in command or "ஜெயமுருகன் போர்ட்ஃபோலியோவைத் திற" in command:
        webbrowser.open("https://jayamurugan-31-portfolio.netlify.app/")
        speak("Opening jayamurugan portfolio")
        return True
     # Tastylens
    if "open Tastylens" in command or "டேஸ்டிலென்ஸ் திற" in command:
        webbrowser.open("https://tastylensar.vercel.app/")
        speak("Opening Tastylens")
        return True
    
    

    return False
