from flask import Flask, render_template, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

DATA_PATH = 'netflix_titles.csv'
IMG_PATH = 'static/images'

def generate_charts():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=['type', 'release_year', 'rating', 'country', 'duration'])

    # Chart 1: Movies vs TV Shows
    type_counts = df['type'].value_counts()
    plt.bar(type_counts.index, type_counts.values, color=['skyblue','orange'])
    plt.title('Number of movies vs TV shows on Netflix')
    plt.xlabel('Type')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'{IMG_PATH}/movies_vs_tvshows.png')
    plt.close()

    # Chart 2: Content Ratings
    rating_counts = df['rating'].value_counts()
    plt.pie(rating_counts, labels= rating_counts.index, autopct="%1.1f%%", startangle=90)
    plt.title('Percentage of Content Ratings')
    plt.tight_layout()
    plt.savefig(f'{IMG_PATH}/content_ratings_pie.png')
    plt.close()

    # Chart 3: Movie Durations
    movie_df = df[df['type'] == 'Movie'].copy()
    movie_df['duration_int'] = movie_df['duration'].str.replace('min','').astype(int)
    plt.hist(movie_df['duration_int'], bins=30, color='purple', edgecolor='black')
    plt.title('Distribution of Movie Duration')
    plt.xlabel('Duration (minutes)')
    plt.ylabel('Number of Movies')
    plt.tight_layout()
    plt.savefig(f'{IMG_PATH}/movie_duration_histogram.png')
    plt.close()

    # Chart 4: Release Year vs Number of Shows
    release_counts = df['release_year'].value_counts().sort_index()
    plt.scatter(release_counts.index, release_counts.values, color='red')
    plt.title('Release Year vs Number of Shows')
    plt.xlabel('Release Year')
    plt.ylabel('Number of Shows')
    plt.tight_layout()
    plt.savefig(f'{IMG_PATH}/release_year_scatter.png')
    plt.close()

    # Chart 5: Top 10 Countries
    country_counts = df['country'].value_counts().head(10)
    plt.barh(country_counts.index, country_counts.values, color='teal')
    plt.title('Top 10 Countries by Number of Shows')
    plt.xlabel('Number of Shows')
    plt.ylabel('Country')
    plt.tight_layout()
    plt.savefig(f'{IMG_PATH}/top10_countries.png')
    plt.close()

    # Chart 6: Movies vs TV Shows Over Years
    content_by_year = df.groupby(['release_year', 'type']).size().unstack().fillna(0)
    fig, ax = plt.subplots(1,2, figsize=(12,5))
    ax[0].plot(content_by_year.index, content_by_year['Movie'], color='blue')
    ax[0].set_title('Movies Released Per Year')
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Number of Movies')
    ax[1].plot(content_by_year.index, content_by_year['TV Show'], color='orange')
    ax[1].set_title('TV Shows Released Per Year')
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('Number of TV Shows')
    fig.suptitle('Comparison of Movies and TV Shows Released Over Years')
    plt.tight_layout()
    plt.savefig(f'{IMG_PATH}/movies_tv_shows_comparision.png')
    plt.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    charts = [
        'movies_vs_tvshows.png',
        'content_ratings_pie.png',
        'movie_duration_histogram.png',
        'release_year_scatter.png',
        'top10_countries.png',
        'movies_tv_shows_comparision.png'
    ]
    return render_template('dashboard.html', charts=charts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/static/images/<filename>')
def image(filename):
    return send_from_directory(IMG_PATH, filename)

if __name__ == '__main__':
    os.makedirs(IMG_PATH, exist_ok=True)
    generate_charts()
    app.run(debug=True)
