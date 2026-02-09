# 🎬 Movie Database CLI App

A Python-based Movie Database application with user profiles, ratings, and website generation.  
Each user has their own personal movie collection, fetched automatically from the OMDb API.

---

## ✨ Features

### Core Features
- Add, list, update, and delete movies
- Fetch movie data automatically from OMDb (title, year, rating, poster)
- Persistent storage using SQLite
- Clean and user-friendly CLI interface

### 👤 User Profiles (Bonus)
- Multiple users supported
- Each user has their **own movie collection**
- Users can be created and switched at runtime
- Movies are linked to users via a foreign key

### ⭐ Ratings (Bonus)
- Each movie includes a rating
- Ratings are displayed:
  - in the CLI
  - on the generated website
- Movies can be sorted and filtered by rating

### 🌐 Website Generation
- Generate a static HTML website per user
- Each user gets their own file (e.g. `John.html`)
- Responsive grid layout for many movies
- Movie cards with poster, title, year, and rating

---

## 📁 Project Structure

```
Movie-Project/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│ ├── main.py # CLI application
│ └── movie_storage/
│   └── movie_storage_sql.py # SQLite storage layer
│
├── data/
│   └── movies.db
│
└── static/
    ├── index_template.html
    └── style.css
```
## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
```
```bash
cd <your-project-folder>
```
### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```
```bash
source .venv/bin/activate   # macOS / Linux
```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up OMDb API Key
Create a .env file in the project root:

```bash
env
OMDB_API_KEY=your_api_key_here
```

You can get a free API key from:

👉 https://www.omdbapi.com/

## ▶️ Running the App

```bash
python src/main.py
```

## 🧭 How It Works

### User Selection

When the app starts, you select or create a user:

```bash
Welcome to the Movie App! 🎬

Select a user:
1. John
2. Sara
3. Create new user
```

All actions (add, list, update, delete) apply only to the active user.

### Movie Storage
- Movies are stored in SQLite
- Each movie belongs to exactly one user
- Duplicate movie titles per user are prevented

### Website Generation

- Generates a static HTML page for the active user
- Uses a responsive grid layout for large movie collections
- Includes poster images and ratings

Example:
```bash
11. Generate website
```
Result:
```bash
static/John.html
```

---

## 🧪 Bonus Features Implemented
- ✅ User Profiles
- ✅ Ratings
- ✅ Many Movies (responsive layout)
- ✅ Website generation per user

---

## 📌 Notes
- The database is created automatically on first run
- Foreign keys ensure clean deletion of user-related movies
- The app is designed to be easily extensible

---

## 💡 Possible Improvements
- Search by genre or year range
- Star-based rating visualization on the website
- Notes/comments per movie
- Export movie lists (CSV / JSON)

---

## 👋 Author

Created by Mark.

Built with ❤️ as a learning project for Python, SQL, and clean application design.
