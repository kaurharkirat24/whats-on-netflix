from flask import Flask, render_template, jsonify, request, send_from_directory
import pandas as pd
import json
import os

app = Flask(__name__)
DATA_PATH = 'netflix_titles.csv'

# ─── Data Loading & Cleaning ────────────────────────────────────────────────

def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=['type', 'release_year'])
    df['release_year'] = df['release_year'].astype(int)
    df['rating'] = df['rating'].fillna('Not Rated')

    # Fix date_added
    if 'date_added' in df.columns:
        df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
        df['month_added'] = df['date_added'].dt.month
        df['year_added'] = df['date_added'].dt.year

    # Clean country — take ONLY the first country listed
    df['country_clean'] = df['country'].fillna('Unknown').str.split(',').str[0].str.strip()

    # Clean duration
    movie_mask = df['type'] == 'Movie'
    df.loc[movie_mask, 'duration_min'] = (
        df.loc[movie_mask, 'duration']
        .str.replace(' min', '', regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors='coerce')
    )

    return df

df_global = load_data()

# ─── Helper ─────────────────────────────────────────────────────────────────

def df_to_json(series_or_df):
    """Convert pandas series/df to JSON-safe dict."""
    if isinstance(series_or_df, pd.Series):
        return series_or_df.to_dict()
    return series_or_df.to_dict(orient='records')


# ─── Pages ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html')


# ─── API: Summary KPIs ──────────────────────────────────────────────────────

@app.route('/api/summary')
def api_summary():
    df = df_global
    movies = int((df['type'] == 'Movie').sum())
    shows  = int((df['type'] == 'TV Show').sum())
    countries = int(df['country_clean'].nunique())
    years_span = int(df['release_year'].max() - df['release_year'].min())
    avg_duration = round(df['duration_min'].dropna().mean(), 1)

    return jsonify({
        'total': movies + shows,
        'movies': movies,
        'shows': shows,
        'countries': countries,
        'years_span': years_span,
        'avg_movie_duration': avg_duration,
    })


# ─── API: Content Type Split ─────────────────────────────────────────────────

@app.route('/api/type_split')
def api_type_split():
    counts = df_global['type'].value_counts()
    return jsonify({'labels': list(counts.index), 'values': [int(v) for v in counts.values]})


# ─── API: Titles Per Year ────────────────────────────────────────────────────

@app.route('/api/titles_per_year')
def api_titles_per_year():
    content_type = request.args.get('type', 'all')
    df = df_global
    if content_type != 'all':
        df = df[df['type'] == content_type]

    by_year = df.groupby(['release_year', 'type']).size().unstack(fill_value=0)
    result = {}
    for col in by_year.columns:
        result[col] = {'x': [int(y) for y in by_year.index], 'y': [int(v) for v in by_year[col]]}
    return jsonify(result)


# ─── API: Top Genres ─────────────────────────────────────────────────────────

@app.route('/api/top_genres')
def api_top_genres():
    content_type = request.args.get('type', 'all')
    n = int(request.args.get('n', 15))
    df = df_global if content_type == 'all' else df_global[df_global['type'] == content_type]

    genres = df['listed_in'].dropna().str.split(', ').explode()
    counts = genres.value_counts().head(n)
    return jsonify({'genres': list(counts.index), 'counts': [int(v) for v in counts.values]})


# ─── API: Ratings Distribution ───────────────────────────────────────────────

@app.route('/api/ratings')
def api_ratings():
    content_type = request.args.get('type', 'all')
    df = df_global if content_type == 'all' else df_global[df_global['type'] == content_type]

    counts = df['rating'].value_counts().head(12)
    return jsonify({'ratings': list(counts.index), 'counts': [int(v) for v in counts.values]})


# ─── API: Top Countries ──────────────────────────────────────────────────────

@app.route('/api/top_countries')
def api_top_countries():
    content_type = request.args.get('type', 'all')
    n = int(request.args.get('n', 10))
    df = df_global if content_type == 'all' else df_global[df_global['type'] == content_type]

    df_known = df[df['country_clean'] != 'Unknown']
    counts = df_known['country_clean'].value_counts().head(n)
    return jsonify({'countries': list(counts.index), 'counts': [int(v) for v in counts.values]})


# ─── API: Movie Duration Over Years ──────────────────────────────────────────

@app.route('/api/duration_trend')
def api_duration_trend():
    movies = df_global[(df_global['type'] == 'Movie') & df_global['duration_min'].notna()]
    avg = movies.groupby('release_year')['duration_min'].mean().round(1)
    # only years with enough samples
    counts = movies.groupby('release_year').size()
    avg = avg[counts >= 5]
    return jsonify({'years': [int(y) for y in avg.index], 'avg_duration': list(avg.values)})


# ─── API: Seasonal Additions ─────────────────────────────────────────────────

@app.route('/api/seasonal')
def api_seasonal():
    if 'month_added' not in df_global.columns:
        return jsonify({'error': 'date_added not available'})
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    df = df_global.dropna(subset=['month_added'])
    counts = df.groupby('month_added').size().reindex(range(1, 13), fill_value=0)
    return jsonify({'months': months, 'counts': [int(v) for v in counts.values]})


# ─── API: Rating Trends Over Time ────────────────────────────────────────────

@app.route('/api/rating_trends')
def api_rating_trends():
    key_ratings = ['TV-MA', 'R', 'PG-13', 'PG', 'TV-PG', 'TV-14']
    df = df_global[df_global['rating'].isin(key_ratings)]
    pivot = df.groupby(['release_year', 'rating']).size().unstack(fill_value=0)
    result = {'years': [int(y) for y in pivot.index]}
    for r in key_ratings:
        if r in pivot.columns:
            result[r] = [int(v) for v in pivot[r]]
    return jsonify(result)


# ─── API: Top Directors ───────────────────────────────────────────────────────

@app.route('/api/top_directors')
def api_top_directors():
    n = int(request.args.get('n', 10))
    counts = df_global['director'].dropna().value_counts().head(n)
    return jsonify({'directors': list(counts.index), 'counts': [int(v) for v in counts.values]})


# ─── API: Avg Duration by Country ────────────────────────────────────────────

@app.route('/api/duration_by_country')
def api_duration_by_country():
    movies = df_global[
        (df_global['type'] == 'Movie') &
        df_global['duration_min'].notna() &
        (df_global['country_clean'] != 'Unknown')
    ]
    # require at least 10 movies per country for meaningful avg
    grouped = movies.groupby('country_clean').filter(lambda x: len(x) >= 10)
    avg = grouped.groupby('country_clean')['duration_min'].mean().round(1).sort_values(ascending=False).head(12)
    return jsonify({'countries': list(avg.index), 'avg_duration': list(avg.values)})


# ─── API: Search / Filter titles ─────────────────────────────────────────────

@app.route('/api/search')
def api_search():
    query   = request.args.get('q', '').strip().lower()
    genre   = request.args.get('genre', '')
    ctype   = request.args.get('type', '')
    rating  = request.args.get('rating', '')
    year_from = request.args.get('year_from', '')
    year_to   = request.args.get('year_to', '')

    df = df_global.copy()

    if query:
        mask = (
            df['title'].str.lower().str.contains(query, na=False) |
            df['director'].str.lower().str.contains(query, na=False) |
            df['cast'].str.lower().str.contains(query, na=False) |
            df['description'].str.lower().str.contains(query, na=False)
        )
        df = df[mask]

    if genre:
        df = df[df['listed_in'].str.contains(genre, na=False, case=False)]
    if ctype:
        df = df[df['type'] == ctype]
    if rating:
        df = df[df['rating'] == rating]
    if year_from:
        df = df[df['release_year'] >= int(year_from)]
    if year_to:
        df = df[df['release_year'] <= int(year_to)]

    cols = ['title', 'type', 'release_year', 'rating', 'country_clean', 'listed_in', 'duration', 'description']
    results = df[cols].head(50).fillna('—').rename(columns={'country_clean': 'country'})
    return jsonify({'count': len(df), 'results': results.to_dict(orient='records')})


# ─── API: Filter options ──────────────────────────────────────────────────────

@app.route('/api/filter_options')
def api_filter_options():
    genres = sorted(df_global['listed_in'].dropna().str.split(', ').explode().unique().tolist())
    ratings = sorted(df_global['rating'].dropna().unique().tolist())
    years = sorted(df_global['release_year'].dropna().unique().astype(int).tolist())
    return jsonify({'genres': genres, 'ratings': ratings, 'years': years})


if __name__ == '__main__':
    app.run(debug=True)
