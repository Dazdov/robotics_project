import cv2
import sqlite3
import speech_recognition as sr
import os

# Create database to store commands and image paths
def create_database():
    try:
        conn = sqlite3.connect("commands.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                image_path TEXT NOT NULL
            )
        """
        )

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
    finally:
        conn.close()


# Function to listen for a command
def listen_for_command(language_code="en-US"):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Please say a command...")

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio, language=language_code)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that. Please try again.")
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}"
            )
    return None


# Function to capture an image from the webcam
def capture_image():
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    if not ret:
        print("Failed to capture image.")
        return None
    image_path = "captured_image.jpg"
    cv2.imwrite(image_path, frame)
    vid.release()
    print(f"Captured image saved at: {image_path}")
    return image_path


# Save command and image path to database
def save_to_database(command, image_path):
    try:
        conn = sqlite3.connect("commands.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO commands (command, image_path) VALUES (?, ?)",
            (command, image_path),
        )

        conn.commit()
        print("Data saved to database successfully.")
    except sqlite3.Error as e:
        print(f"Error saving to database: {e}")
    finally:
        conn.close()


# Main function to tie everything together
def main():
    create_database()

    # Capture video feed and save to file
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("output.avi", fourcc, 20.0, (640, 480))

    # Start video capture
    vid = cv2.VideoCapture(0)
    if not vid.isOpened():
        print("Error: Could not access the camera.")
        return
    while True:
        ret, frame = vid.read()
        if not ret:
            break
        # Display the frame
        cv2.imshow("Video Feed", frame)

        # Write the frame to the output video
        out.write(frame)

        # Check if the user pressed 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        # Wait for a voice command every 5 seconds
        command = listen_for_command(language_code="en-US")
        if command:
            image_path = capture_image()
            if image_path:
                save_to_database(command, image_path)
    # Release resources
    vid.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
