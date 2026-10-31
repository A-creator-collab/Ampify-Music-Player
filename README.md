# 🎵 Ampify Music Player

Ampify is a modern desktop music player application built with **Python** and **Tkinter**. It features a clean interface, a robust MySQL backend for managing your music library, and smooth playback powered by **Pygame**.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)](https://docs.python.org/3/library/tkinter.html)
[![Pygame](https://img.shields.io/badge/Audio-Pygame-green)](https://www.pygame.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL-blue)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- **User Authentication** — Secure registration and login using `bcrypt` hashing.
- **Music Library** — Add, view, and manage your entire song collection.
- **Playlist Management** — Create, delete, and manage custom playlists with ease.
- **Favorites** — Mark songs as favorites for quick access.
- **Song Queue** — View and manage the current playback queue.
- **Recently Played** — Automatically tracks your listening history.
- **Search** — Quickly find songs by title, artist, or album.
- **Dark & Light Theme** — Toggle between themes for comfortable viewing.
- **Playback Controls** — Play, pause, next, previous, volume control, and progress bar.
- **Playlist Playback** — Play an entire playlist sequentially.

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.8+ |
| **GUI Framework** | Tkinter, ttkthemes |
| **Audio Playback** | Pygame |
| **Database** | MySQL |
| **Database Driver** | PyMySQL |
| **Authentication** | bcrypt |
| **Metadata** | Mutagen |

---

## 📚 Data Structures & Algorithms Used

Ampify doesn't just use Python lists for everything. It implements custom data structures to manage data efficiently:
- **Hash Table** — Custom implementation for O(1) fast lookups in the song library and user data.
- **Queue (Custom Class)** — Extracted playback queue logic into a dedicated `PlaybackQueue` class for better separation of concerns.
- **Stack** — Used to manage the "Recently Played" history.
- **Quick Sort** — Custom implementation for sorting songs by title, artist, or year.
- **Linear Search** — For filtering and searching through the library.

---

## 🗄️ Database Schema

Ampify uses a MySQL database with the following tables (these are automatically created by the app on first launch):

```sql
-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100)
);

-- Songs Table
CREATE TABLE songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    year VARCHAR(10),
    genre VARCHAR(100),
    duration INT DEFAULT 0,
    play_count INT DEFAULT 0,
    filepath TEXT NOT NULL
);

-- Playlists Table
CREATE TABLE playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Playlist Songs Table (Junction Table)
CREATE TABLE playlist_songs (
    playlist_id INT,
    song_id INT,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

-- Favorites Table
CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    song_id INT,
    UNIQUE KEY unique_favorite (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);
```
🚀 Installation & Setup

Follow these steps to get Ampify running on your local machine.
1. Prerequisites

    Python 3.8 or higher — Download here

    MySQL Server — Download here

2. Clone the Repository
bash

git clone https://github.com/A-creator-collab/Ampify-Music-Player.git
cd Ampify-Music-Player

3. Set Up a Virtual Environment (Recommended)
bash

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
bash

pip install -r requirements.txt

5. Configure the Database

    Open your MySQL client (e.g., MySQL Workbench, command line).

    The application is configured to automatically create the musicdb database and all required tables on first launch.

    Important: Open main.py and update the database credentials in the Database.connect_database() method to match your local MySQL setup:

python

# Change these lines in main.py
host="localhost",
user="root",
password="12345", # <-- Change to your MySQL password
database="musicdb",

6. Run the Application
bash

python main.py

📁 Project Structure
text

Ampify-Music-Player/
│
├── main.py                 # Application entry point (GUI, DB, Logic)
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore file

🖥️ Usage

    Launch the application by running python main.py.

    Register a new account or log in with your credentials.

    Add songs to your library by providing the file path.

    Create playlists and add your favorite tracks. You can also delete playlists you no longer need.

    Use the playback controls to play, pause, skip, adjust volume, and seek.

    Toggle between Dark and Light themes using the sun/moon icon.

📄 License

This project is licensed under the MIT License.
👨‍💻 Author

Atharv Singh

    GitHub: @A-creator-collab
