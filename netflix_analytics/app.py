from flask import Flask, render_template, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

app = Flask(__name__)

DATA_PATH = 'netflix_titles.csv'
IMG_DIR = 'static/images'

def generate_charts():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=['type', 'release_year', 'rating', 'country', 'duration'])
    df['release_year'] = df['release_year'].astype(int)

    # Ensure images directory exists
    import os
    os.makedirs(IMG_DIR, exist_ok=True)

    # 1. Movies vs TV Shows
    plt.figure(figsize=(6, 4))
    df['type'].value_counts().plot(kind='bar', color=['skyblue', 'orange'])
    plt.title('Movies vs TV Shows on Netflix')
    plt.xlabel('Type')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/1_movies_vs_tvshows.png')
    plt.close()

    # 2. Growth Over Time
    plt.figure(figsize=(10, 6))
    df.groupby('release_year').size().plot(marker='o', color='teal')
    plt.title('Number of Titles Released Per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Titles')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/2_titles_per_year.png')
    plt.close()

    # 3. Movies vs TV Shows Over Time
    content_by_year = df.groupby(['release_year', 'type']).size().unstack().fillna(0)
    plt.figure(figsize=(10, 6))
    plt.plot(content_by_year.index, content_by_year['Movie'], label='Movies', color='blue')
    plt.plot(content_by_year.index, content_by_year['TV Show'], label='TV Shows', color='orange')
    plt.legend()
    plt.title('Movies vs TV Shows Released Over Years')
    plt.xlabel('Year')
    plt.ylabel('Number of Titles')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/3_movies_vs_tvshows_over_years.png')
    plt.close()

    # 4. Content Ratings by Type
    rating_order = df['rating'].value_counts().index
    rating_type_counts = df.groupby(['rating', 'type']).size().unstack().fillna(0).loc[rating_order]
    rating_type_counts.plot(kind='bar', figsize=(10, 6))
    plt.xticks(rotation=45)
    plt.title('Content Ratings by Type')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/4_content_ratings_by_type.png')
    plt.close()

    # 5. Top Countries by Movies vs TV Shows
    country_type = df.groupby(['country', 'type']).size().unstack().fillna(0).sort_values('Movie', ascending=False).head(10)
    country_type.plot(kind='bar', figsize=(10, 6))
    plt.title('Top 10 Countries by Movies vs TV Shows')
    plt.ylabel('Number of Titles')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/5_top_countries_movies_vs_tvshows.png')
    plt.close()

    # 6. Top Genres
    genres = df['listed_in'].dropna().str.split(', ')
    flat_genres = [genre for sublist in genres for genre in sublist]
    genre_counts = pd.Series(flat_genres).value_counts().head(15)
    plt.figure(figsize=(10, 6))
    plt.barh(genre_counts.index[::-1], genre_counts.values[::-1], color=plt.cm.coolwarm(range(len(genre_counts))))
    plt.title('Top 15 Genres on Netflix')
    plt.xlabel('Number of Titles')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/6_top_genres.png')
    plt.close()

    # 7. Average Movie Duration Over Years
    movie_df = df[df['type'] == 'Movie'].copy()
    movie_df['duration_int'] = movie_df['duration'].str.replace('min', '', regex=False).astype(int)
    avg_duration_per_year = movie_df.groupby('release_year')['duration_int'].mean()
    plt.figure(figsize=(10, 6))
    plt.plot(avg_duration_per_year.index, avg_duration_per_year.values, color='purple')
    plt.title('Average Movie Duration Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Average Duration (minutes)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/7_avg_movie_duration_over_years.png')
    plt.close()

    # 8. Top Directors
    top_directors = df['director'].dropna().value_counts().head(10)
    plt.figure(figsize=(10, 6))
    plt.barh(top_directors.index[::-1], top_directors.values[::-1], color="#c731b3")
    plt.title('Top 10 Directors on Netflix')
    plt.xlabel('Number of Titles')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/8_top_directors.png')
    plt.close()

    # 9. Top Actors
    cast_series = df['cast'].dropna().str.split(', ')
    flat_cast = [actor for sublist in cast_series for actor in sublist]
    top_actors = pd.Series(flat_cast).value_counts().head(10)
    plt.figure(figsize=(10, 6))
    plt.barh(top_actors.index[::-1], top_actors.values[::-1], color="#7D2894")
    plt.title('Top 10 Most Featured Actors on Netflix')
    plt.xlabel('Number of Titles')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/9_top_actors.png')
    plt.close()

    # 10. Seasonal Strategy (Month of Addition)
    if 'date_added' in df.columns:
        df['month_added'] = pd.to_datetime(df['date_added'], errors='coerce').dt.month
        month_counts = df['month_added'].value_counts().sort_index()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.figure(figsize=(10, 6))
        plt.bar(months, month_counts.values, color="#3beb70")  
        plt.title('Netflix Releases by Month')
        plt.xlabel('Month')
        plt.ylabel('Number of Titles Added')
        plt.tight_layout()
        plt.savefig(f'{IMG_DIR}/10_releases_by_month.png')
        plt.close()

    # 11. Rating Trends Over Time
    ratings_per_year = df.groupby(['release_year', 'rating']).size().unstack(fill_value=0)
    ratings_to_plot = [r for r in ['TV-MA', 'R', 'PG-13', 'PG'] if r in ratings_per_year.columns]
    if ratings_to_plot:
        plt.figure(figsize=(12, 6))
        for r in ratings_to_plot:
            plt.plot(ratings_per_year.index, ratings_per_year[r], label=r)
        plt.title('Content Ratings Trends Over the Years')
        plt.xlabel('Year')
        plt.ylabel('Number of Titles')
        plt.legend(title='Rating')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{IMG_DIR}/11_rating_trends_over_time.png')
        plt.close()

    # 12. Average Duration by Country
    avg_duration_by_country = movie_df.groupby('country')['duration_int'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.barh(avg_duration_by_country.index[::-1], avg_duration_by_country.values[::-1], color=plt.cm.viridis(range(len(avg_duration_by_country))))
    plt.title('Average Movie Duration by Country')
    plt.xlabel('Duration (minutes)')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/12_avg_duration_by_country.png')
    plt.close()

    # 13. Wordcloud of Titles
    text = ' '.join(df['title'].dropna())
    wc = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Frequent Words in Netflix Titles')
    plt.tight_layout()
    plt.savefig(f'{IMG_DIR}/13_wordcloud_titles.png')
    plt.close()

INSIGHTS = [
    {
        "file": "1_movies_vs_tvshows.png",
        "title": "Movies vs TV Shows: Who rules the Netflix library?",
        "caption": "Movies still outnumber TV shows on Netflix, but each year the fight gets closer. Netflix’s shift toward binge-worthy series is clear."
    },
    {
        "file": "2_titles_per_year.png",
        "title": "Growth Over Time: The Netflix Explosion",
        "caption": "Since 2015, Netflix's catalog exploded. Hits like 'Stranger Things' and 'Narcos' marked a bold new focus on originals."
    },
    {
        "file": "3_movies_vs_tvshows_over_years.png",
        "title": "Content Evolution: Movies vs Series Year over Year",
        "caption": "Post-2018, TV Show releases surged—series keep viewers hooked episode after episode."
    },
    {
        "file": "4_content_ratings_by_type.png",
        "title": "Who's Watching What? Ratings by Type",
        "caption": "TV Shows on Netflix lean mature (TV-MA) while movies cluster around PG and PG-13."
    },
    {
        "file": "5_top_countries_movies_vs_tvshows.png",
        "title": "Top Countries: Netflix's Global Playbook",
        "caption": "The US leads, followed by India—showcasing Netflix's international expansion strategy."
    },
    {
        "file": "6_top_genres.png",
        "title": "What Genres Captivate Viewers?",
        "caption": "Drama, International Movies, and Documentaries dominate Netflix's global audience."
    },
    {
        "file": "7_avg_movie_duration_over_years.png",
        "title": "Now Streaming Quicker: Movie Durations Shrink",
        "caption": "Average movie lengths have declined, catering to modern viewers' shorter attention spans."
    },
    {
        "file": "8_top_directors.png",
        "title": "Directors Behind the Magic",
        "caption": "Frequent collaborators highlight Netflix's trusted creative partnerships."
    },
    {
        "file": "9_top_actors.png",
        "title": "Star Power: Netflix's Most-Featured Talent",
        "caption": "Popular actors from Bollywood and Hollywood appear repeatedly, driving viewership."
    },
    {
        "file": "10_releases_by_month.png",
        "title": "Seasonal Strategy",
        "caption": "Release peaks in July and December align with holidays and viewer habits."
    },
    {
        "file": "11_rating_trends_over_time.png",
        "title": "Mature Content on the Rise",
        "caption": "A strong rise in TV-MA content reflects Netflix's bold shift toward mature themes."
    },
    {
        "file": "12_avg_duration_by_country.png",
        "title": "Around the World in 120 Minutes",
        "caption": "Longer movies from India and Egypt reveal cultural storytelling traditions."
    },
    {
        "file": "13_wordcloud_titles.png",
        "title": "Netflix Titles: A World of Words",
        "caption": "Frequently used words in titles give a snapshot of popular themes globally."
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', insights=INSIGHTS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/static/images/<filename>')
def image(filename):
    return send_from_directory(IMG_DIR, filename)

if __name__ == '__main__':
    generate_charts()
    app.run(debug=True)
