import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import os
import bcrypt
import pymysql
from mutagen.mp3 import MP3
import time
from ttkthemes import ThemedTk
from collections import deque
import random



class HashTable:
    def __init__(self, size=2000):
        self.size = size
        self.table = [[] for _ in range(size)]
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def put(self, key, value):
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))
    
    def get(self, key):
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None


def quick_sort(arr, key=lambda x: x.get('title', '')):
    if len(arr) <= 1:
        return arr
    pivot = key(arr[len(arr) // 2])
    left = [x for x in arr if key(x) < pivot]
    middle = [x for x in arr if key(x) == pivot]
    right = [x for x in arr if key(x) > pivot]
    return quick_sort(left, key) + middle + quick_sort(right, key)


def linear_search(song_list, query):
    results = []
    query_lower = query.lower()
    for song in song_list:
        if query_lower in song.get('title', '').lower() or \
           query_lower in song.get('artist', '').lower():
            results.append(song)
    return results




class Database:
    def __init__(self):
        self.connection = None
        self.connect_database()
        if self.connection:
            self.create_tables()

    def connect_database(self):
        try:
            self.connection = pymysql.connect(
                host="localhost",
                user="root",
                password="12345",
                database="musicdb",
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            print("✅ Database connected successfully!")
            return True
        except pymysql.Error as e:
            print(f"Database connection failed: {e}")
            try:
                temp_conn = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="12345",
                    charset="utf8mb4"
                )
                with temp_conn.cursor() as cursor:
                    cursor.execute("CREATE DATABASE IF NOT EXISTS musicdb")
                temp_conn.close()
                
                self.connection = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="12345",
                    database="musicdb",
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor
                )
                print("✅ Database created and connected!")
                return True
            except:
                messagebox.showerror("Database Error", "Could not connect to MySQL. Please make sure MySQL is running.")
                return False

    def create_tables(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        email VARCHAR(100)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS songs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        artist VARCHAR(255),
                        year VARCHAR(10),
                        genre VARCHAR(100),
                        duration INT DEFAULT 0,
                        play_count INT DEFAULT 0,
                        filepath TEXT NOT NULL
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS playlists (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        name VARCHAR(255) NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS playlist_songs (
                        playlist_id INT,
                        song_id INT,
                        FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                        FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS favorites (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        song_id INT,
                        UNIQUE KEY unique_favorite (user_id, song_id),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
                    )
                """)
                
                self.connection.commit()
                print("✅ Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")

    def register_user(self, username, password, email):
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                             (username, hashed_password.decode('utf-8'), email))
                self.connection.commit()
                return True
        except:
            return False

    def login_user(self, username, password):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    return user
                return None
        except:
            return None

    def get_all_songs(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM songs ORDER BY title")
                return cursor.fetchall()
        except:
            return []

    def add_song(self, title, artist, year, filepath, genre=""):
        try:
            duration = 0
            try:
                audio = MP3(filepath)
                duration = int(audio.info.length)
            except:
                pass
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO songs (title, artist, year, genre, duration, filepath)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (title, artist, year, genre, duration, filepath))
                self.connection.commit()
                return cursor.lastrowid
        except:
            return None

    def update_play_count(self, song_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE songs SET play_count = play_count + 1 WHERE id = %s", (song_id,))
                self.connection.commit()
        except:
            pass

    def create_playlist(self, user_id, name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO playlists (user_id, name) VALUES (%s, %s)", (user_id, name))
                self.connection.commit()
                return cursor.lastrowid
        except:
            return None

    def add_song_to_playlist(self, playlist_id, song_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)", (playlist_id, song_id))
                self.connection.commit()
                return True
        except:
            return False

    def remove_song_from_playlist(self, playlist_id, song_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM playlist_songs WHERE playlist_id = %s AND song_id = %s", (playlist_id, song_id))
                self.connection.commit()
                return True
        except:
            return False

    def get_playlists(self, user_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM playlists WHERE user_id = %s", (user_id,))
                return cursor.fetchall()
        except:
            return []

    def get_playlist_songs(self, playlist_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT songs.* FROM songs
                    JOIN playlist_songs ON songs.id = playlist_songs.song_id
                    WHERE playlist_songs.playlist_id = %s
                """, (playlist_id,))
                return cursor.fetchall()
        except:
            return []

    def add_to_favorites(self, user_id, song_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT IGNORE INTO favorites (user_id, song_id) VALUES (%s, %s)", (user_id, song_id))
                self.connection.commit()
                return True
        except:
            return False

    def remove_from_favorites(self, user_id, song_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM favorites WHERE user_id = %s AND song_id = %s", (user_id, song_id))
                self.connection.commit()
                return True
        except:
            return False

    def get_favorites(self, user_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT songs.* FROM songs
                    JOIN favorites ON songs.id = favorites.song_id
                    WHERE favorites.user_id = %s
                """, (user_id,))
                return cursor.fetchall()
        except:
            return []

    def is_favorite(self, user_id, song_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND song_id = %s", (user_id, song_id))
                return cursor.fetchone() is not None
        except:
            return False




class MusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ampify - Music Player")
        self.root.geometry("1400x900")
        

        self.dark_colors = {
            'bg': '#0a0a0a', 'sidebar': '#1a1a1a', 'accent': '#FF033E',
            'text': '#FFFFFF', 'text_secondary': '#B3B3B3', 'card_bg': '#282828', 'hover': '#3a3a3a'
        }
        
        self.light_colors = {
            'bg': '#f5f5f5', 'sidebar': '#ffffff', 'accent': '#FF033E',
            'text': '#1a1a1a', 'text_secondary': '#666666', 'card_bg': '#ffffff', 'hover': '#e0e0e0'
        }
        
        self.current_theme = 'dark'
        self.colors = self.dark_colors
        self.root.configure(bg=self.colors['bg'])
        
        
        self.song_array = []
        self.song_hash_table = HashTable()
        self.history_stack = []
        self.up_next_queue = deque()
        self.playlist_queue = []  
        
        
        self.db = Database()
        if not self.db.connection:
            messagebox.showerror("Database Error", "Failed to connect to database.")
            self.root.quit()
            return
        
        self.current_user = None
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.total_duration = 0
        self.volume = 0.7
        self.current_playlist_id = None
        self.current_playlist_songs = []  
        self.current_playlist_index = -1  
        
        pygame.mixer.init()
        self.load_songs_into_dsa()
        self.setup_gui()

    def load_songs_into_dsa(self):
        songs = self.db.get_all_songs()
        self.song_array = songs
        for song in songs:
            self.song_hash_table.put(song['id'], song)
            self.song_hash_table.put(song['title'].lower(), song)

    def toggle_theme(self):
        if self.current_theme == 'dark':
            self.colors = self.light_colors
            self.current_theme = 'light'
        else:
            self.colors = self.dark_colors
            self.current_theme = 'dark'
        
        if self.current_user:
            self.main_screen()
        else:
            self.login_screen()

    def setup_gui(self):
        self.login_screen()

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        theme_btn = tk.Button(main_container, text="🌙" if self.current_theme == 'light' else "☀️", 
                              command=self.toggle_theme, bg=self.colors['card_bg'], 
                              fg=self.colors['text'], font=("Segoe UI", 14), relief=tk.FLAT)
        theme_btn.place(x=10, y=10)
        
        center_frame = tk.Frame(main_container, bg=self.colors['bg'])
        center_frame.pack(expand=True)
        
        tk.Label(center_frame, text="AMPIFY", font=("Segoe UI", 48, "bold"), 
                fg=self.colors['accent'], bg=self.colors['bg']).pack(pady=30)
        
        card_frame = tk.Frame(center_frame, bg=self.colors['card_bg'])
        card_frame.pack(pady=20)
        
        card_inner = tk.Frame(card_frame, bg=self.colors['card_bg'])
        card_inner.pack(padx=40, pady=40)
        
        tk.Label(card_inner, text="Login", font=("Segoe UI", 24, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(pady=(0, 20))
        
        tk.Label(card_inner, text="Username", font=("Segoe UI", 12),
                fg=self.colors['text_secondary'], bg=self.colors['card_bg']).pack(anchor="w")
        self.username_entry = ttk.Entry(card_inner, width=30, font=("Segoe UI", 12))
        self.username_entry.pack(pady=(5, 15))
        
        tk.Label(card_inner, text="Password", font=("Segoe UI", 12),
                fg=self.colors['text_secondary'], bg=self.colors['card_bg']).pack(anchor="w")
        self.password_entry = ttk.Entry(card_inner, show="*", width=30, font=("Segoe UI", 12))
        self.password_entry.pack(pady=(5, 20))
        
        btn_frame = tk.Frame(card_inner, bg=self.colors['card_bg'])
        btn_frame.pack()
        
        tk.Button(btn_frame, text="Login", command=self.login, bg=self.colors['accent'],
                 fg=self.colors['text'], font=("Segoe UI", 12, "bold"), padx=30, pady=10,
                 relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Create Account", command=self.register_screen,
                 bg=self.colors['hover'], fg=self.colors['text'], font=("Segoe UI", 12),
                 padx=30, pady=10, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

    def register_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        theme_btn = tk.Button(main_container, text="🌙" if self.current_theme == 'light' else "☀️", 
                              command=self.toggle_theme, bg=self.colors['card_bg'], 
                              fg=self.colors['text'], font=("Segoe UI", 14), relief=tk.FLAT)
        theme_btn.place(x=10, y=10)
        
        center_frame = tk.Frame(main_container, bg=self.colors['bg'])
        center_frame.pack(expand=True)
        
        tk.Label(center_frame, text="Create Account", font=("Segoe UI", 32, "bold"),
                fg=self.colors['accent'], bg=self.colors['bg']).pack(pady=30)
        
        card_frame = tk.Frame(center_frame, bg=self.colors['card_bg'])
        card_frame.pack(pady=20)
        
        card_inner = tk.Frame(card_frame, bg=self.colors['card_bg'])
        card_inner.pack(padx=40, pady=40)
        
        self.reg_entries = {}
        for label in ["Username", "Password", "Email"]:
            tk.Label(card_inner, text=label, font=("Segoe UI", 12),
                    fg=self.colors['text_secondary'], bg=self.colors['card_bg']).pack(anchor="w")
            entry = ttk.Entry(card_inner, width=30, font=("Segoe UI", 12))
            if label == "Password":
                entry.configure(show="*")
            entry.pack(pady=(5, 15))
            self.reg_entries[label.lower()] = entry
        
        btn_frame = tk.Frame(card_inner, bg=self.colors['card_bg'])
        btn_frame.pack()
        
        tk.Button(btn_frame, text="Register", command=self.register, bg=self.colors['accent'],
                 fg=self.colors['text'], font=("Segoe UI", 12, "bold"), padx=30, pady=10,
                 relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Back to Login", command=self.login_screen,
                 bg=self.colors['hover'], fg=self.colors['text'], font=("Segoe UI", 12),
                 padx=30, pady=10, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

    def login(self):
        user = self.db.login_user(self.username_entry.get(), self.password_entry.get())
        if user:
            self.current_user = user
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def register(self):
        if self.db.register_user(self.reg_entries['username'].get(), 
                                  self.reg_entries['password'].get(),
                                  self.reg_entries['email'].get()):
            messagebox.showinfo("Success", "Registration successful!")
            self.login_screen()
        else:
            messagebox.showerror("Error", "Registration failed!")

    def main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        
        tk.Button(main_container, text="🌙" if self.current_theme == 'light' else "☀️", 
                 command=self.toggle_theme, bg=self.colors['card_bg'], 
                 fg=self.colors['text'], font=("Segoe UI", 14), relief=tk.FLAT).place(x=10, y=10)
        
        
        sidebar = tk.Frame(main_container, bg=self.colors['sidebar'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="AMPIFY", font=("Segoe UI", 24, "bold"),
                fg=self.colors['accent'], bg=self.colors['sidebar']).pack(pady=30)
        
        tk.Label(sidebar, text=f"👤 {self.current_user['username']}",
                font=("Segoe UI", 12), fg=self.colors['text'], bg=self.colors['sidebar']).pack(pady=10)
        
        nav_buttons = [
            ("🎵 Library", self.show_library),
            ("📋 Queue", self.show_queue),
            ("📜 History", self.show_history),
            ("📁 Playlists", self.show_playlists),
            ("⭐ Favorites", self.show_favorites),
            ("➕ Add Song", self.upload_song)
        ]
        
        for text, cmd in nav_buttons:
            btn = tk.Button(sidebar, text=text, command=cmd, bg=self.colors['sidebar'],
                           fg=self.colors['text_secondary'], font=("Segoe UI", 11),
                           anchor='w', padx=20, pady=10, relief=tk.FLAT)
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors['hover']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['sidebar']))
        
        tk.Button(sidebar, text="🚪 Logout", command=self.logout, bg=self.colors['sidebar'],
                 fg=self.colors['accent'], font=("Segoe UI", 11), anchor='w', padx=20, pady=10,
                 relief=tk.FLAT).pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        self.main_content = tk.Frame(main_container, bg=self.colors['bg'])
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_now_playing_bar()
        self.show_library()

    def setup_now_playing_bar(self):
        bar_frame = tk.Frame(self.root, bg=self.colors['card_bg'], height=80)
        bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        info_frame = tk.Frame(bar_frame, bg=self.colors['card_bg'])
        info_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.now_playing_label = tk.Label(info_frame, text="No song playing", font=("Segoe UI", 11),
                                          fg=self.colors['text'], bg=self.colors['card_bg'])
        self.now_playing_label.pack()
        
        self.now_playing_artist = tk.Label(info_frame, text="", font=("Segoe UI", 9),
                                           fg=self.colors['text_secondary'], bg=self.colors['card_bg'])
        self.now_playing_artist.pack()
        
        control_frame = tk.Frame(bar_frame, bg=self.colors['card_bg'])
        control_frame.pack(side=tk.LEFT, expand=True)
        
        tk.Button(control_frame, text="⏮", command=self.previous_song, bg=self.colors['card_bg'],
                 fg=self.colors['text'], font=("Segoe UI", 16), relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        
        self.play_pause_btn = tk.Button(control_frame, text="▶", command=self.toggle_play_pause,
                                        bg=self.colors['accent'], fg=self.colors['text'],
                                        font=("Segoe UI", 14), relief=tk.FLAT, width=3)
        self.play_pause_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(control_frame, text="⏭", command=self.next_song, bg=self.colors['card_bg'],
                 fg=self.colors['text'], font=("Segoe UI", 16), relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        
        progress_frame = tk.Frame(bar_frame, bg=self.colors['card_bg'])
        progress_frame.pack(side=tk.RIGHT, padx=20, fill=tk.X, expand=True)
        
        self.current_time_label = tk.Label(progress_frame, text="00:00", font=("Segoe UI", 10),
                                           fg=self.colors['text_secondary'], bg=self.colors['card_bg'])
        self.current_time_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.progress_bar.bind("<Button-1>", self.seek_to_position)
        
        self.total_time_label = tk.Label(progress_frame, text="00:00", font=("Segoe UI", 10),
                                         fg=self.colors['text_secondary'], bg=self.colors['card_bg'])
        self.total_time_label.pack(side=tk.LEFT)
        
        self.fav_btn = tk.Button(bar_frame, text="⭐", command=self.toggle_favorite,
                                 bg=self.colors['card_bg'], fg=self.colors['text_secondary'],
                                 font=("Segoe UI", 16), relief=tk.FLAT)
        self.fav_btn.pack(side=tk.RIGHT, padx=10)
        
        volume_frame = tk.Frame(bar_frame, bg=self.colors['card_bg'])
        volume_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(volume_frame, text="🔊", font=("Segoe UI", 12),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                                       command=self.set_volume, length=100)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(side=tk.LEFT, padx=5)

    def seek_to_position(self, event):
        if not self.current_song or not self.is_playing:
            return
        width = self.progress_bar.winfo_width()
        seek_time = (event.x / width) * self.total_duration
        pygame.mixer.music.play(start=seek_time)
        self.current_time = seek_time
        self.progress_bar["value"] = seek_time
        self.current_time_label.config(text=self.format_time(seek_time))

    def toggle_favorite(self):
        if not self.current_song:
            return
        if self.db.is_favorite(self.current_user['id'], self.current_song['id']):
            self.db.remove_from_favorites(self.current_user['id'], self.current_song['id'])
            self.fav_btn.config(fg=self.colors['text_secondary'])
        else:
            self.db.add_to_favorites(self.current_user['id'], self.current_song['id'])
            self.fav_btn.config(fg="#FFD700")

    def show_library(self):
        self.clear_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Label(header_frame, text="Music Library", font=("Segoe UI", 28, "bold"),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side=tk.LEFT)
        
        control_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, padx=30, pady=10)
        
        search_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        search_frame.pack(side=tk.LEFT)
        
        self.search_entry = ttk.Entry(search_frame, width=30, font=("Segoe UI", 11))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_songs())
        
        tk.Button(search_frame, text="Search", command=self.search_songs, bg=self.colors['accent'],
                 fg=self.colors['text'], font=("Segoe UI", 10), relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        sort_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        sort_frame.pack(side=tk.RIGHT)
        
        for sort_by in ["Title", "Artist", "Year"]:
            tk.Button(sort_frame, text=sort_by, command=lambda s=sort_by: self.sort_songs(s),
                     bg=self.colors['card_bg'], fg=self.colors['text'], font=("Segoe UI", 10),
                     relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        
        tree_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        columns = ("ID", "Title", "Artist", "Year", "Genre")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)
        
        for col, heading, width in zip(columns, ["ID", "Title", "Artist", "Year", "Genre"],
                                       [50, 300, 200, 80, 150]):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<Double-1>", self.play_selected)
        
        action_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        action_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Button(action_frame, text="▶ Play Selected", command=self.play_selected, bg=self.colors['accent'],
                 fg=self.colors['text'], font=("Segoe UI", 11), relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="➕ Add to Queue", command=self.add_to_queue, bg=self.colors['card_bg'],
                 fg=self.colors['text'], font=("Segoe UI", 11), relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="⭐ Add to Favorites", command=self.add_selected_to_favorites, bg=self.colors['card_bg'],
                 fg=self.colors['text'], font=("Segoe UI", 11), relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)
        
        self.load_songs_to_tree()

    def load_songs_to_tree(self, songs=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        songs = songs or self.song_array
        for song in songs:
            self.tree.insert("", tk.END, values=(song['id'], song['title'], song.get('artist', '-'),
                           song.get('year', '-'), song.get('genre', '-')))

    def search_songs(self):
        query = self.search_entry.get().strip()
        if not query:
            self.load_songs_to_tree()
            return
        exact = self.song_hash_table.get(query.lower())
        if exact:
            self.load_songs_to_tree([exact])
        else:
            self.load_songs_to_tree(linear_search(self.song_array, query))

    def sort_songs(self, sort_by):
        key_map = {"Title": "title", "Artist": "artist", "Year": "year"}
        sorted_songs = quick_sort(self.song_array.copy(), key=lambda x: x.get(key_map[sort_by], ''))
        self.load_songs_to_tree(sorted_songs)

    def play_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        song_id = self.tree.item(selected[0])['values'][0]
        song = self.song_hash_table.get(song_id)
        if song:
            
            self.current_playlist_songs = []
            self.current_playlist_index = -1
            self.play_song(song)

    def play_song(self, song):
        try:
            self.current_song = song
            pygame.mixer.music.load(song['filepath'])
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.play_pause_btn.config(text="⏸")
            
            self.now_playing_label.config(text=song['title'])
            self.now_playing_artist.config(text=song.get('artist', ''))
            
            self.history_stack.append(song)
            self.db.update_play_count(song['id'])
            
            is_fav = self.db.is_favorite(self.current_user['id'], song['id'])
            self.fav_btn.config(fg="#FFD700" if is_fav else self.colors['text_secondary'])
            
            try:
                audio = MP3(song['filepath'])
                self.total_duration = int(audio.info.length)
                self.total_time_label.config(text=self.format_time(self.total_duration))
                self.progress_bar["maximum"] = self.total_duration
            except:
                pass
            
            self.update_progress()
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            self.root.bind(pygame.USEREVENT, self.on_song_end)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot play: {e}")
    
    def on_song_end(self, event):
        
        
        if self.current_playlist_songs and self.current_playlist_index < len(self.current_playlist_songs) - 1:
            self.current_playlist_index += 1
            self.play_song(self.current_playlist_songs[self.current_playlist_index])
        
        elif self.up_next_queue:
            self.play_song(self.up_next_queue.popleft())
        
        elif self.current_song and self.song_array:
            idx = next((i for i, s in enumerate(self.song_array) if s['id'] == self.current_song['id']), -1)
            if idx < len(self.song_array) - 1:
                self.play_song(self.song_array[idx + 1])

    def toggle_play_pause(self):
        if not self.current_song:
            return
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_pause_btn.config(text="▶")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_pause_btn.config(text="⏸")

    def next_song(self):
        
        if self.current_playlist_songs and self.current_playlist_index < len(self.current_playlist_songs) - 1:
            self.current_playlist_index += 1
            self.play_song(self.current_playlist_songs[self.current_playlist_index])
        elif self.up_next_queue:
            self.play_song(self.up_next_queue.popleft())
        elif self.current_song and self.song_array:
            idx = next((i for i, s in enumerate(self.song_array) if s['id'] == self.current_song['id']), -1)
            if idx < len(self.song_array) - 1:
                self.play_song(self.song_array[idx + 1])

    def previous_song(self):
        
        if self.current_playlist_songs and self.current_playlist_index > 0:
            self.current_playlist_index -= 1
            self.play_song(self.current_playlist_songs[self.current_playlist_index])
        elif len(self.history_stack) > 1:
            self.history_stack.pop()
            self.play_song(self.history_stack.pop())

    def add_to_queue(self):
        selected = self.tree.selection()
        if not selected:
            return
        song_id = self.tree.item(selected[0])['values'][0]
        song = self.song_hash_table.get(song_id)
        if song:
            self.up_next_queue.append(song)
            messagebox.showinfo("Added", f"Added '{song['title']}' to queue")

    def add_selected_to_favorites(self):
        selected = self.tree.selection()
        if not selected:
            return
        song_id = self.tree.item(selected[0])['values'][0]
        song = self.song_hash_table.get(song_id)
        if song and self.db.add_to_favorites(self.current_user['id'], song_id):
            messagebox.showinfo("Success", f"Added '{song['title']}' to favorites!")

    def show_queue(self):
        self.clear_content()
        tk.Label(self.main_content, text="Up Next Queue", font=("Segoe UI", 28, "bold"),
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=20, padx=30, anchor='w')
        
        queue_box = tk.Listbox(self.main_content, font=("Segoe UI", 11), bg=self.colors['card_bg'],
                               fg=self.colors['text'], selectbackground=self.colors['accent'])
        queue_box.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        for i, s in enumerate(self.up_next_queue, 1):
            queue_box.insert(tk.END, f"{i}. {s['title']} - {s.get('artist', 'Unknown')}")

    def show_history(self):
        self.clear_content()
        tk.Label(self.main_content, text="Recently Played", font=("Segoe UI", 28, "bold"),
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=20, padx=30, anchor='w')
        
        history_box = tk.Listbox(self.main_content, font=("Segoe UI", 11), bg=self.colors['card_bg'],
                                 fg=self.colors['text'], selectbackground=self.colors['accent'])
        history_box.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        for i, s in enumerate(reversed(self.history_stack), 1):
            history_box.insert(tk.END, f"{i}. {s['title']} - {s.get('artist', 'Unknown')}")

    def show_playlists(self):
        self.clear_content()
        
        tk.Label(self.main_content, text="Your Playlists", font=("Segoe UI", 28, "bold"),
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=20, padx=30, anchor='w')
        
        
        create_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        create_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(create_frame, text="Playlist Name:", font=("Segoe UI", 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side=tk.LEFT)
        
        self.playlist_name_entry = ttk.Entry(create_frame, width=30, font=("Segoe UI", 11))
        self.playlist_name_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(create_frame, text="+ Create Playlist", command=self.create_playlist,
                 bg=self.colors['accent'], fg=self.colors['text'], font=("Segoe UI", 11),
                 relief=tk.FLAT).pack(side=tk.LEFT)
        
        
        tk.Label(self.main_content, text="Your Playlists:", font=("Segoe UI", 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(padx=30, anchor='w', pady=(10,0))
        
        self.playlists_listbox = tk.Listbox(self.main_content, font=("Segoe UI", 11),
                                            bg=self.colors['card_bg'], fg=self.colors['text'],
                                            selectbackground=self.colors['accent'], height=6)
        self.playlists_listbox.pack(fill=tk.X, padx=30, pady=5)
        self.playlists_listbox.bind('<<ListboxSelect>>', self.on_playlist_select)
        
        
        self.load_playlists()
        
        
        playlist_actions = tk.Frame(self.main_content, bg=self.colors['bg'])
        playlist_actions.pack(fill=tk.X, padx=30, pady=10)
        
        
        tk.Button(playlist_actions, text="▶ Play Entire Playlist", command=self.play_current_playlist,
                 bg=self.colors['accent'], fg=self.colors['text'], font=("Segoe UI", 11),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)
        
        
        add_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        add_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(add_frame, text="Add Song to Playlist:", font=("Segoe UI", 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side=tk.LEFT)
        
        
        self.song_to_add_var = tk.StringVar()
        self.song_to_add_var.set("Select a song")
        song_names = [f"{s['title']} - {s.get('artist', 'Unknown')}" for s in self.song_array]
        self.song_dropdown = ttk.Combobox(add_frame, textvariable=self.song_to_add_var, 
                                          values=song_names, width=40, state="readonly")
        self.song_dropdown.pack(side=tk.LEFT, padx=10)
        
        tk.Button(add_frame, text="Add to Selected Playlist", command=self.add_song_to_playlist,
                 bg=self.colors['card_bg'], fg=self.colors['text'], font=("Segoe UI", 10),
                 relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        
        tk.Label(self.main_content, text="Playlist Songs:", font=("Segoe UI", 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(padx=30, anchor='w', pady=(10,0))
        
        
        songs_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        songs_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
        
        self.playlist_songs_listbox = tk.Listbox(songs_frame, font=("Segoe UI", 11),
                                                  bg=self.colors['card_bg'], fg=self.colors['text'],
                                                  selectbackground=self.colors['accent'], height=8)
        playlist_scrollbar = ttk.Scrollbar(songs_frame, orient=tk.VERTICAL, command=self.playlist_songs_listbox.yview)
        self.playlist_songs_listbox.configure(yscrollcommand=playlist_scrollbar.set)
        
        self.playlist_songs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        
        self.playlist_songs_listbox.bind("<Double-1>", self.play_selected_playlist_song)
        
        
        remove_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        remove_frame.pack(fill=tk.X, padx=30, pady=5)
        
        tk.Button(remove_frame, text="❌ Remove Selected from Playlist", 
                 command=self.remove_from_playlist, bg=self.colors['card_bg'], fg=self.colors['text'],
                 font=("Segoe UI", 10), relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

    def play_current_playlist(self):
        
        if not self.current_playlist_id:
            messagebox.showwarning("No Playlist", "Please select a playlist first")
            return
        
        playlist_songs = self.db.get_playlist_songs(self.current_playlist_id)
        if not playlist_songs:
            messagebox.showwarning("Empty Playlist", "This playlist has no songs to play")
            return
        
        
        self.current_playlist_songs = playlist_songs
        self.current_playlist_index = 0
        self.play_song(playlist_songs[0])
        
        messagebox.showinfo("Playing Playlist", f"Now playing playlist with {len(playlist_songs)} songs")

    def play_selected_playlist_song(self, event):
        
        selection = self.playlist_songs_listbox.curselection()
        if not selection:
            return
        
        song_text = self.playlist_songs_listbox.get(selection[0])
        if song_text == "📭 No songs in this playlist":
            return
        
        song_title = song_text.replace("🎵 ", "").split(" - ")[0]
        song = next((s for s in self.song_array if s['title'] == song_title), None)
        
        if song:
            
            playlist_songs = self.db.get_playlist_songs(self.current_playlist_id)
            self.current_playlist_songs = playlist_songs
            
            for i, s in enumerate(playlist_songs):
                if s['title'] == song_title:
                    self.current_playlist_index = i
                    break
            self.play_song(song)

    def load_playlists(self):
        
        self.playlists_listbox.delete(0, tk.END)
        self.playlist_ids = {}
        playlists = self.db.get_playlists(self.current_user['id'])
        
        if not playlists:
            self.playlists_listbox.insert(tk.END, "📁 No playlists yet. Create one!")
        else:
            for playlist in playlists:
                self.playlists_listbox.insert(tk.END, f"📁 {playlist['name']}")
                self.playlist_ids[playlist['name']] = playlist['id']

    def on_playlist_select(self, event):
        
        selection = self.playlists_listbox.curselection()
        if not selection:
            return
        
        playlist_text = self.playlists_listbox.get(selection[0])
        if playlist_text == "📁 No playlists yet. Create one!":
            return
        
        playlist_name = playlist_text.replace("📁 ", "")
        playlist_id = self.playlist_ids.get(playlist_name)
        
        if playlist_id:
            self.current_playlist_id = playlist_id
            songs = self.db.get_playlist_songs(playlist_id)
            self.playlist_songs_listbox.delete(0, tk.END)
            if not songs:
                self.playlist_songs_listbox.insert(tk.END, "📭 No songs in this playlist")
            else:
                for song in songs:
                    self.playlist_songs_listbox.insert(tk.END, f"🎵 {song['title']} - {song.get('artist', 'Unknown')}")

    def create_playlist(self):
        
        name = self.playlist_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid", "Please enter a playlist name")
            return
        
        playlist_id = self.db.create_playlist(self.current_user['id'], name)
        if playlist_id:
            messagebox.showinfo("Success", f"Playlist '{name}' created!")
            self.playlist_name_entry.delete(0, tk.END)
            self.load_playlists()
        else:
            messagebox.showerror("Error", "Failed to create playlist")

    def add_song_to_playlist(self):
        
        
        selection = self.playlists_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a playlist first")
            return
        
        playlist_text = self.playlists_listbox.get(selection[0])
        if playlist_text == "📁 No playlists yet. Create one!":
            messagebox.showwarning("No Playlist", "Please create a playlist first")
            return
        
        playlist_name = playlist_text.replace("📁 ", "")
        playlist_id = self.playlist_ids.get(playlist_name)
        
        
        selected_song = self.song_to_add_var.get()
        if selected_song == "Select a song":
            messagebox.showwarning("No Song", "Please select a song")
            return
        
        song_title = selected_song.split(" - ")[0]
        song = next((s for s in self.song_array if s['title'] == song_title), None)
        
        if song and playlist_id:
            if self.db.add_song_to_playlist(playlist_id, song['id']):
                messagebox.showinfo("Success", f"Added '{song['title']}' to '{playlist_name}'")
                if self.current_playlist_id == playlist_id:
                    self.on_playlist_select(None)
            else:
                messagebox.showerror("Error", "Failed to add song")

    def remove_from_playlist(self):
        
        if not self.current_playlist_id:
            messagebox.showwarning("No Playlist", "Please select a playlist first")
            return
        
        selection = self.playlist_songs_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a song to remove")
            return
        
        song_text = self.playlist_songs_listbox.get(selection[0])
        if song_text == "📭 No songs in this playlist":
            return
        
        song_title = song_text.replace("🎵 ", "").split(" - ")[0]
        song = next((s for s in self.song_array if s['title'] == song_title), None)
        
        if song and self.db.remove_song_from_playlist(self.current_playlist_id, song['id']):
            messagebox.showinfo("Success", f"Removed '{song['title']}' from playlist")
            self.on_playlist_select(None)

    def show_favorites(self):
        self.clear_content()
        tk.Label(self.main_content, text="⭐ Favorite Songs", font=("Segoe UI", 28, "bold"),
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=20, padx=30, anchor='w')
        
        favorites = self.db.get_favorites(self.current_user['id'])
        
        fav_frame = tk.Frame(self.main_content, bg=self.colors['bg'])
        fav_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        columns = ("Title", "Artist", "Year", "Genre")
        tree = ttk.Treeview(fav_frame, columns=columns, show="headings", height=15)
        
        for col, heading, width in zip(columns, ["Title", "Artist", "Year", "Genre"], [300, 200, 80, 150]):
            tree.heading(col, text=heading)
            tree.column(col, width=width)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for song in favorites:
            tree.insert("", tk.END, values=(song['title'], song.get('artist', '-'),
                       song.get('year', '-'), song.get('genre', '-')))
        
        tree.bind("<Double-1>", lambda e: self.play_favorite(tree))

    def play_favorite(self, tree):
        selected = tree.selection()
        if selected:
            title = tree.item(selected[0])['values'][0]
            song = next((s for s in self.song_array if s['title'] == title), None)
            if song:
                self.current_playlist_songs = []
                self.current_playlist_index = -1
                self.play_song(song)

    def upload_song(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3")])
        for file in files:
            dialog = tk.Toplevel(self.root)
            dialog.title("Song Details")
            dialog.geometry("400x400")
            dialog.configure(bg=self.colors['bg'])
            
            tk.Label(dialog, text="Add Song Details", font=("Segoe UI", 16, "bold"),
                    fg=self.colors['text'], bg=self.colors['bg']).pack(pady=20)
            
            fields = {}
            for label in ["Title", "Artist", "Year", "Genre"]:
                frame = tk.Frame(dialog, bg=self.colors['bg'])
                frame.pack(pady=10, padx=20, fill=tk.X)
                tk.Label(frame, text=label, font=("Segoe UI", 11), fg=self.colors['text'],
                        bg=self.colors['bg'], width=10, anchor='w').pack(side=tk.LEFT)
                entry = ttk.Entry(frame, width=30)
                entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
                fields[label.lower()] = entry
            
            filename = os.path.basename(file)
            fields['title'].insert(0, os.path.splitext(filename)[0])
            
            def save():
                title = fields['title'].get().strip()
                if title:
                    song_id = self.db.add_song(title, fields['artist'].get(), fields['year'].get(),
                                               file, fields['genre'].get())
                    if song_id:
                        new_song = {'id': song_id, 'title': title, 'artist': fields['artist'].get(),
                                   'year': fields['year'].get(), 'filepath': file, 'genre': fields['genre'].get(),
                                   'play_count': 0}
                        self.song_array.append(new_song)
                        self.song_hash_table.put(song_id, new_song)
                        self.song_hash_table.put(title.lower(), new_song)
                        messagebox.showinfo("Success", f"Song '{title}' added!")
                        dialog.destroy()
                        self.show_library()
            
            tk.Button(dialog, text="Save", command=save, bg=self.colors['accent'],
                     fg=self.colors['text'], font=("Segoe UI", 12), relief=tk.FLAT,
                     padx=20, pady=10).pack(pady=20)

    def set_volume(self, value):
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)

    def update_progress(self):
        if self.is_playing and not self.is_paused:
            self.current_time = pygame.mixer.music.get_pos() / 1000
            if self.current_time >= 0:
                self.progress_bar["value"] = self.current_time
                self.current_time_label.config(text=self.format_time(self.current_time))
            self.root.after(1000, self.update_progress)

    def format_time(self, seconds):
        return f"{int(seconds//60):02}:{int(seconds%60):02}"

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def logout(self):
        self.current_user = None
        self.login_screen()


if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = MusicApp(root)
    root.mainloop()