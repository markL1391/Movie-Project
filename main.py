import random
import statistics
from movie_storage import movie_storage_sql as storage
import requests
import os
from dotenv import load_dotenv
load_dotenv()


OMDB_URL = "https://www.omdbapi.com/"

# === COLORS (ANSI) ====
BOLD = "\033[1m"
BOLD_RED = "\033[1;31m"
BOLD_YELLOW = "\033[1;33m"
BOLD_GREEN = "\033[1;32m"
RESET = "\033[0m"



def fetch_movie_from_omdb(title):
    """
    Return dict with: title(str), year(int), rating(float), poster_url(str|None)
    or None if not found / error.
    """
    api_key = os.getenv("OMDB_API_KEY")

    if not api_key:
        print("⚠️ OMDB_API_KEY is not set.")
        return None

    try:
        response = requests.get(
            OMDB_URL,
            params={"t": title, "apikey": api_key},
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        print("⚠️ Could not reach OMDb API (connection error).")
        return None
    except ValueError:
        print("⚠️ Invalid response from OMDb API.")
        return None

    if data.get("Response") == "False":
        print(f"⚠️ Movie not found: {data.get('Error', 'Unknown error')}")
        return None

    api_title = data.get("Title", "").strip()
    year_raw = str(data.get("Year", "")).strip()
    rating_raw = str(data.get("imdbRating", "")).strip()
    poster_raw = str(data.get("Poster", "")).strip()

    year = int(year_raw[:4]) if year_raw[:4].isdigit() else 0

    if rating_raw == "N/A":
        rating = 0.0
    else:
        try:
            rating = float(rating_raw)
        except ValueError:
            rating = 0.0

    poster_url = None if poster_raw == "N/A" else poster_raw

    return {"title": api_title, "year": year, "rating": rating, "poster_url": poster_url}


# === Helper functions ====
def prompt_non_empty(prompt, error_msg="⚠️ Input cannot be empty. Please try again."):
    while True:
        value = input(prompt).strip()
        if value == "":
            print(error_msg)
            continue
        return value


def prompt_float(prompt, error_msg="⚠️ Invalid input. Rating must be a number."):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print(error_msg)
            continue


def prompt_float_in_range(prompt, min_value, max_value):
    while True:
        value = prompt_float(prompt)
        if value < min_value or value > max_value:
            print(f"⚠️ Value must be between {min_value} and {max_value}.")
            continue
        return value


def prompt_int_positive(prompt):
    while True:
        value = input(prompt).strip()
        try:
            value = int(value)
        except ValueError:
            print("⚠️ Invalid input. Please enter an integer.")
            continue

        if value <= 0:
            print("⚠️ Value must be a positive integer.")
            continue

        return value


def prompt_optional_float(prompt, error_msg="⚠️ Invalid input. Please enter a number."):
    value = input(prompt).strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        print(error_msg)
        return None


def prompt_optional_int(prompt, error_msg="⚠️ Invalid input. Please enter an integer."):
    value = input(prompt).strip()
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        print(error_msg)
        return None


def find_movie_key_case_insensitive(movies, user_title):
    """
    Returns the actual movie title key from the movies dictionary
    if found (case-insensitive), otherwise None
    """
    user_title = user_title.strip().lower()
    for title in movies:
        if title.lower() == user_title:
            return title
    return None


def main_menu():
    """
    Displays the main menu and returns the user's choice.
    """
    print("")
    print("==============================================")
    print("🍿 🍿 🍿 🍿  My Movies Database  🍿 🍿 🍿 🍿")
    print("==============================================")
    print("")
    print("Menu:\n")
    print("0. Exit")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Movies sorted by year")
    print("10. Filter movies")
    print("11. Generate website\n")
    return input("Enter choice (0-11): ").strip()


def list_movies():
    """
    Retrieve and display all movies from the database.
    """
    movies = storage.list_movies()

    if not movies:
        print("No movies in the database yet.")
        return

    print(f"{len(movies)} movies in total\n")
    for title, data in movies.items():
        rating = data["rating"]
        year = data["year"]
        print(f"{BOLD}{title}{RESET} ({year}): {BOLD_GREEN}{rating}{RESET}")


def add_movies():
    """
    Add a movie to the database (fetching data from OMDb by title).
    """
    movies = storage.list_movies()

    # Title input (no empty string).
    title_input = prompt_non_empty(
        "Enter the movie: ",
        "⚠️ Title cannot be empty. Please try again."
    )

    # Early duplicate check (based on current DB titles).
    existing_key = find_movie_key_case_insensitive(movies, title_input)
    if existing_key is not None:
        print(f"⚠️ Movie '{existing_key}' already exists.")
        return

    movie = fetch_movie_from_omdb(title_input)
    if movie is None:
        return

    # Check again using the real API title.
    movies = storage.list_movies()
    existing_key = find_movie_key_case_insensitive(movies, movie["title"])
    if existing_key is not None:
        print(f"⚠️ Movie '{existing_key}' already exists.")
        return

    storage.add_movie(
        movie["title"],
        movie["year"],
        movie["rating"],
        movie["poster_url"]
    )

    print(
        f"Movie {BOLD_YELLOW}{movie['title']}{RESET} ({movie['year']}) "
        f"with rating {BOLD_GREEN}{movie['rating']}{RESET} was added! 🎉")


def delete_movies():
    """
    Deletes a movie from the database.
    """
    movies = storage.list_movies()

    title_input = prompt_non_empty(
        "Enter the movie title you want to delete: ",
        "⚠️ Title cannot be empty. Please try again."
    )

    key = find_movie_key_case_insensitive(movies, title_input)
    if key is None:
        print(f"\n⚠️⚠️⚠️ Error! The movie '{BOLD}{title_input}{RESET}' was not found in the database.")
        return

    success = storage.delete_movie(key)

    if success:
        print(f"\nMovie '{BOLD}{key}{RESET}' was deleted successfully! 🗑️")
    else:
        print(f"\n⚠️ Movie '{BOLD}{key}{RESET}' could not be deleted.")

def update_movies():
    """
    Updates the rating of an existing movie. Year stays unchanged.
    """
    movies = storage.list_movies()

    title_input = prompt_non_empty(
        "Enter the movie you want to update: ",
        "⚠️ Title cannot be empty. Please try again."
    )

    key = find_movie_key_case_insensitive(movies, title_input)
    if key is None:
        print(f"\n⚠️⚠️⚠️ Error! The movie '{BOLD}{title_input}{RESET}' was not found in the database.")
        return

    current_rating = movies[key]["rating"]
    year = movies[key]["year"]
    print(
        f"Current rating for the movie '{BOLD}{key}{RESET}' ({year}) "
          f"is {BOLD}{current_rating}{RESET}"
    )

    updated_rating = prompt_float_in_range(
        "Enter the new rating (1-10): ", 1, 10
    )

    success = storage.update_movie(key, updated_rating)

    if success:
        print("\n ✅ Updated")
        print(f"\n '{BOLD}{key}{RESET}' now has a rating {BOLD}{updated_rating}{RESET} ⭐")
    else:
        print(f"\n⚠️ Movie '{BOLD}{key}{RESET}' could not be updated.")


def get_stats_movies():
    """
    Shows statistics about the movie database.
    """
    movies = storage.list_movies()
    if not movies:
        print(f"📊 {BOLD}Movies statistics:{RESET}")
        print("No movies in the database yet.")
        return

    ratings = [data["rating"] for data in movies.values()]
    total = len(ratings)
    avg_ratings = sum(ratings) / total
    median = statistics.median(ratings)

    best_rating = max(ratings)
    worst_rating = min(ratings)

    best_movies = [title for title, data in movies.items() if data["rating"] == best_rating]
    worst_movies = [title for title, data in movies.items() if data["rating"] == worst_rating]

    print(f"📊 {BOLD}Movies statistics:{RESET}")
    print(f"- Total movies: {total}")
    print(f"- Average rating: {avg_ratings:.1f}")
    print(f"- Median: {median:.1f}")

    print(f"- Best movie(s): 🎖️ 🎖️ 🎖")
    for title in best_movies:
        print(f" '{BOLD_GREEN}{title}{RESET}' with rating {BOLD_GREEN}{best_rating}{RESET}")

    print(f"- Worst movie(s): 💩 💩 💩")
    for title in worst_movies:
        print(f" '{BOLD_RED}{title}{RESET}' with rating {BOLD_RED}{worst_rating}{RESET}")


def get_random_movies():
    """ Prints a random movie suggestion.
    """
    movies = storage.list_movies()

    if not movies:
        print("No movies in the database yet.")
        return

    title = random.choice(list(movies.keys()))
    rating = movies[title]["rating"]
    year = movies[title]["year"]
    print("🎲 Random movie suggestion:")
    print(f"→ {BOLD_YELLOW}{title}{RESET} ({year}) with a rating of {BOLD_YELLOW}{rating}{RESET} ⭐")


def search_movies():
    """
    Searches for movies by partial title (case-insensitive).
    """
    movies = storage.list_movies()

    search_term = prompt_non_empty(
        "Enter part of movie name: ",
        "⚠️ Search term cannot be empty. Please try again."
    ).lower()

    results = []
    for title, data in movies.items():
        if search_term in title.lower():
            results.append((title, data["rating"], data["year"]))

    if not results:
        print(f"\n 🔍 {BOLD_RED}No matching movies found{RESET}")
        return

    print(f"\n 🔍 Search results for {BOLD_YELLOW}{search_term}{RESET}:")
    for title, rating, year in results:
        print(f"→ {BOLD}{title}{RESET} ({year}) (rating: {BOLD_GREEN}{rating}{RESET} ⭐)")


def get_sorted_movies():
    """
    Prints all movies sorted by rating (highest to lowest).
    """
    movies = storage.list_movies()
    sorted_movies = sorted(movies.items(), key=lambda item: item[1]["rating"], reverse=True)

    print(f"📽️ {BOLD}Movies sorted by rating:{RESET}\n")
    for index, (title, data) in enumerate(sorted_movies, start=1):
        print(f"{index}. Movie: {BOLD_YELLOW}{title}{RESET} ({data['year']}) - Rating: {BOLD_YELLOW}{data['rating']}{RESET} ⭐")


def get_sorted_movies_by_year():
    """
    Prints all movies sorted by year (oldest to newest).
    """
    movies = storage.list_movies()
    sorted_movies = sorted(movies.items(), key=lambda item: item[1]["year"])

    print(f"📆️ {BOLD}Movies sorted by year:{RESET}\n")
    for index, (title, data) in enumerate(sorted_movies, start=1):
        print(f"{index}. Movie: {BOLD_YELLOW}{title}{RESET} ({data['year']}) - Rating: {BOLD_YELLOW}{data['rating']}{RESET} ⭐")


def filter_movies():
    """
    Filters movies by optional minimum rating, start year and end year.
    Empty input means no filter for that criterion.
    """
    movies = storage.list_movies()

    if not movies:
        print("No movies in the database yet.")
        return

    # --- Minimum rating ---
    min_rating = prompt_optional_float(
        "Enter minimum rating (leave blank for no minimum rating): ",
        "⚠️ Invalid rating input."
    )

    # --- Start year ---
    start_year = prompt_optional_int(
        "Enter start year (leave blank for no start year): ",
        "⚠️ Invalid start year input."
    )

    # --- End year ---
    end_year = prompt_optional_int(
        "Enter end year (leave blank for no end year): ",
        "⚠️ Invalid end year input."
    )

    # --- Filtering ---
    results = []

    for title, data in movies.items():
        rating = data["rating"]
        year = data["year"]

        if min_rating is not None and rating < min_rating:
            continue
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue

        results.append((title, year, rating))

    # --- Output ---
    if not results:
        print("\nNo movies match your filters.")
        return

    print("\nFiltered Movies:")
    for title, year, rating in results:
        print(f"{BOLD}{title}{RESET} ({year}): {BOLD_GREEN}{rating}{RESET} ⭐")

def generate_website():
    """
    Generates the website from index_template.html and writes _static/index.html.
    """
    movies = storage.list_movies()

    name = input("Enter your name (leave empty for default title): ").strip()
    if name:
        title = f"{name}'s Movies Database"
    else:
        title = "My Movies Database"

    movie_grid = build_movie_grid_html(movies)

    with open("static/index_template.html", "r") as f:
        template = f.read()

    html = template.replace("__TEMPLATE_TITLE__", title)
    html = html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    with open("index.html", "w") as f:
        f.write(html)

    print("Website was generated successfully. 🎉")

def build_movie_grid_html(movies: dict) -> str:
    """
    Builds the HTML string for the movie grid based on the template's structure.
    """
    items = []

    for title, data in movies.items():
        year = data.get("year", "")
        rating = data.get("rating", "")
        poster_url = data.get("poster_url") or ""

        item_html = f"""
        <li>
            <div class="movie">
                <img class="movie-poster" src="{poster_url}" alt="{title}">
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
                <div class="movie-rating">{rating}</div>
            </div>
        </li>
        """
        items.append(item_html.strip())
    return "\n".join(items)




def main():
    """
    Runs the Movie Database CLI application.
    """

    actions = {
        "1": ("List movies",list_movies),
        "2": ("Add movie", add_movies),
        "3": ("Delete movie", delete_movies),
        "4": ("Update movie", update_movies),
        "5": ("Stats", get_stats_movies),
        "6": ("Random movie", get_random_movies),
        "7": ("Search movie", search_movies),
        "8": ("Movies sorted by rating", get_sorted_movies),
        "9": ("Movies sorted by year", get_sorted_movies_by_year),
        "10": ("Filter movies", filter_movies),
        "11": ("Generate website", generate_website),
    }

    # Main loop.
    while True:
        choice = main_menu().strip()

        if choice == "0":
            print("\nExiting program... Goodbye!\n")
            print("\n👋   👋   👋")
            break

        action = actions.get(choice)
        if action:
            label, func = action
            print(f"\nYou've chosen: {label}\n")
            func()
        else:
            print("\nInvalid choice. Please try again.\n")

if __name__ == "__main__":
    main()