import sqlite3

def create_database():
    # Create or connect to SQLite database
    conn = sqlite3.connect("commands.db")
    cursor = conn.cursor()

    # Create table if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            image_path TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def listen_for_command():
    # Simulate listening for a command (replace with actual implementation)
    command = input("Please enter a command: ")
    return command.strip()

def capture_image():
    # Simulate capturing an image (replace with actual implementation)
    # For example, integrate a camera module to save an image and return its path
    image_path = "path/to/image.jpg"  # Replace with actual image path
    print(f"Captured image saved at: {image_path}")
    return image_path

def save_to_database(command, image_path):
    # Save command and image path to SQLite database
    conn = sqlite3.connect("commands.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO commands (command, image_path) VALUES (?, ?)", (command, image_path))

    conn.commit()
    conn.close()

def main():
    create_database()

    command = listen_for_command()
    if command:
        image_path = capture_image()
        if image_path:
            save_to_database(command, image_path)
            print("Command and image saved successfully.")

if __name__ == "__main__":
    main()
כן


