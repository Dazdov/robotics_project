import cv2
import sqlite3
import speech_recognition as sr

# Create the database and table
def create_database():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, command TEXT, image BLOB)''')
    conn.commit()
    conn.close()

# Save the command and image to the database
def save_to_database(command, image_path):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    with open(image_path, 'rb') as file:
        img_data = file.read()

    cursor.execute("INSERT INTO entries (command, image) VALUES (?, ?)", (command, img_data))
    conn.commit()
    conn.close()

# Capture a voice command from the microphone
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say your command:")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language="he-IL")  # Recognizing Hebrew
        print(f"Command received: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand the command")
        return None
    except sr.RequestError:
        print("Error with the speech recognition service")
        return None

# Capture an image using the camera
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        image_path = "captured_image.jpg"
        cv2.imwrite(image_path, frame)
        print("Image captured and saved")
        cap.release()
        return image_path
    else:
        print("Failed to capture image")
        cap.release()
        return None

# Main process
def main():
    create_database()  # Ensure the database is ready

    command = listen_for_command()  # Capture voice command
    if command:
        image_path = capture_image()  # Capture image if a command was received
        if image_path:
            save_to_database(command, image_path)  # Save both to the database
            print("Command and image saved successfully")

# Run the program
if __name__ == "__main__":
    main()

