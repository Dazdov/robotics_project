import speech_recognition as sr


def listen_and_recognize():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Please say something...")

        # Adjust for ambient noise (helps with noise cancellation)
        recognizer.adjust_for_ambient_noise(source)

        # Listen for audio from the microphone
        audio = recognizer.listen(source)

        try:
            # Use Google's speech recognition service to recognize the speech
            print("Recognizing...")

            # Language is set to English (US)
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that. Please try again.")
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}"
            )


if __name__ == "__main__":
    listen_and_recognize()
