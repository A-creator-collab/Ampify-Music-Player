
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
- **Playlist Management** — Create custom playlists and add or remove songs.
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

- **Hash Table** — For fast lookups in the song library and user data.
- **Queue (Deque)** — For managing the song playback queue.
- **Quick Sort** — For sorting songs by title, artist, or duration.
- **Linear Search** — For filtering and searching through the library.

---

## 🗄️ Database Schema

Ampify uses a MySQL database with the following tables:

```sql
-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Songs Table
CREATE TABLE songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    album VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,
    duration INT
);

-- Playlists Table
CREATE TABLE playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Playlist Songs Table (Junction Table)
CREATE TABLE playlist_songs (
    playlist_id INT,
    song_id INT,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

-- Favorites Table
CREATE TABLE favorites (
    user_id INT,
    song_id INT,
    PRIMARY KEY (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);
```

---

## 🚀 Installation & Setup

Follow these steps to get Ampify running on your local machine.

### 1. Prerequisites

- **Python 3.8 or higher** — [Download here](https://www.python.org/downloads/)
- **MySQL Server** — [Download here](https://dev.mysql.com/downloads/installer/)
- **Git** — [Download here](https://git-scm.com/)

### 2. Clone the Repository

```bash
git clone https://github.com/A-creator-collab/Ampify-Music-Player.git
cd Ampify-Music-Player
```

### 3. Set Up a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Database

1.  Open your MySQL client (e.g., MySQL Workbench, command line).
2.  Create a new database:

    ```sql
    CREATE DATABASE ampify_db;
    ```

3.  Execute the SQL statements from the **Database Schema** section above to create the necessary tables.
4.  Create a `.env` file in the project root and add your database credentials:

    ```env
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=your_mysql_password
    DB_NAME=ampify_db
    ```

### 6. Run the Application

```bash
python main.py
```

---

## 📁 Project Structure

```
Ampify-Music-Player/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── auth.py             # Authentication logic (bcrypt)
│   ├── database.py         # MySQL connection and queries
│   ├── player.py           # Pygame audio playback logic
│   ├── playlist.py         # Playlist management logic
│   ├── queue.py            # Song queue management
│   ├── search.py           # Search and filter functions
│   ├── sort.py             # Quick sort implementation
│   └── theme.py            # Dark/Light theme configuration
│
├── assets/                 # Icons, images, and styles
│   ├── icons/
│   └── styles/
│
└── .env                    # Environment variables (not committed)
```

> **Note:** The actual structure may vary slightly. Update this section to match your repository's layout.

---

## 🖥️ Usage

1.  **Launch the application** by running `python main.py`.
2.  **Register** a new account or **log in** with your credentials.
3.  **Add songs** to your library by providing the file path.
4.  **Create playlists** and add your favorite tracks.
5.  Use the **playback controls** to play, pause, skip, and adjust volume.
6.  Toggle between **Dark and Light themes** from the settings menu.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve Ampify, please follow these steps:

1.  Fork the repository.
2.  Create a new branch: `git checkout -b feature/your-feature-name`.
3.  Make your changes and commit them: `git commit -m "Add your feature"`.
4.  Push to the branch: `git push origin feature/your-feature-name`.
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

---

## 👨‍💻 Author

**Atharv Singh**

---

## 🙏 Acknowledgements

- [Pygame](https://www.pygame.org/) for audio playback.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework.
- [ttkthemes](https://github.com/TkinterEP/ttkthemes) for modern widget themes.
- [bcrypt](https://github.com/pyca/bcrypt/) for secure password hashing.

---

> ⭐ If you find this project useful, please consider giving it a star on GitHub!
