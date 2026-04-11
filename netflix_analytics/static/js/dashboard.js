const THEME = {
    paper_bgcolor: 'transparent',
    plot_bgcolor:  'transparent',
    font: { family: 'DM Sans, sans-serif', color: 'rgba(255,255,255,0.5)', size: 11 },
    gridcolor: 'rgba(255,255,255,0.05)',
    linecolor: 'rgba(255,255,255,0.08)',
    RED: '#E50914',
    BLUE: '#4a9eff',
    colors: ['#E50914','#4a9eff','#f59e0b','#10b981','#8b5cf6','#ec4899'],
};

function baseLayout(extra = {}) {
    return Object.assign({
        paper_bgcolor: THEME.paper_bgcolor,
        plot_bgcolor:  THEME.plot_bgcolor,
        font: THEME.font,
        margin: { l:50, r:20, t:20, b:50 },
        xaxis: { gridcolor: THEME.gridcolor, linecolor: THEME.linecolor, zerolinecolor: THEME.linecolor },
        yaxis: { gridcolor: THEME.gridcolor, linecolor: THEME.linecolor, zerolinecolor: THEME.linecolor },
        showlegend: false,
        hovermode: 'closest',
    }, extra);
}

const CFG = { responsive: true, displayModeBar: false };

/* ── Active filter state ───────────────────────────────── */
let activeType = 'all';

/* ── KPI Loading ───────────────────────────────────────── */
function loadKPIs() {
    fetch('/api/summary').then(r => r.json()).then(d => {
        document.getElementById('s-total').textContent     = d.total.toLocaleString();
        document.getElementById('s-movies').textContent    = d.movies.toLocaleString();
        document.getElementById('s-shows').textContent     = d.shows.toLocaleString();
        document.getElementById('s-countries').textContent = d.countries;
        document.getElementById('s-avg').textContent       = d.avg_movie_duration;
        document.getElementById('filter-summary').textContent =
            `${d.movies.toLocaleString()} movies · ${d.shows.toLocaleString()} TV shows across ${d.countries} countries`;
    });
}

/* ── Chart: Content Growth Over Time ──────────────────── */
function loadTrend(type) {
    const url = type === 'all' ? '/api/titles_per_year' : `/api/titles_per_year?type=${encodeURIComponent(type)}`;
    fetch(url).then(r => r.json()).then(d => {
        const traces = [];
        const colorMap = { 'Movie': THEME.RED, 'TV Show': THEME.BLUE };
        for (const [name, vals] of Object.entries(d)) {
            traces.push({
                type: 'scatter', mode: 'lines', fill: 'tozeroy',
                name, x: vals.x, y: vals.y,
                line: { color: colorMap[name] || THEME.RED, width: 2 },
                fillcolor: `${(colorMap[name] || THEME.RED)}18`,
                hovertemplate: `%{x}: %{y} titles<extra>${name}</extra>`,
            });
        }
        const layout = baseLayout({
            margin: { l:50, r:20, t:10, b:40 },
            showlegend: true,
            legend: { x: 0.02, y: 0.95, font: { size: 11 }, bgcolor: 'transparent' },
            xaxis: { gridcolor: THEME.gridcolor, range: [1990, 2022] },
            yaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-trend', traces, layout, CFG);
    });
}

/* ── Chart: Type Donut ──────────────────────────────────── */
function loadType() {
    fetch('/api/type_split').then(r => r.json()).then(d => {
        const trace = {
            type: 'pie', hole: 0.6,
            labels: d.labels, values: d.values,
            marker: { colors: [THEME.RED, THEME.BLUE] },
            textinfo: 'label+percent',
            textfont: { color: 'rgba(255,255,255,0.7)', size: 12 },
            hovertemplate: '%{label}: %{value} titles<extra></extra>',
        };
        const layout = baseLayout({ margin: { l:20, r:20, t:10, b:10 } });
        Plotly.react('chart-type', [trace], layout, CFG);
    });
}

/* ── Chart: Ratings Bar ──────────────────────────────────── */
function loadRatings(type) {
    const url = type === 'all' ? '/api/ratings' : `/api/ratings?type=${encodeURIComponent(type)}`;
    fetch(url).then(r => r.json()).then(d => {
        const trace = {
            type: 'bar', x: d.ratings, y: d.counts,
            marker: {
                color: d.counts,
                colorscale: [[0,'rgba(229,9,20,0.2)'], [1, THEME.RED]],
                showscale: false,
            },
            hovertemplate: '%{x}: %{y} titles<extra></extra>',
        };
        const layout = baseLayout({
            xaxis: { gridcolor: THEME.gridcolor, tickangle: -30 },
            yaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-ratings', [trace], layout, CFG);
    });
}

/* ── Chart: Top Genres ──────────────────────────────────── */
function loadGenres(type) {
    const url = type === 'all' ? '/api/top_genres' : `/api/top_genres?type=${encodeURIComponent(type)}`;
    fetch(url).then(r => r.json()).then(d => {
        const trace = {
            type: 'bar', orientation: 'h',
            y: d.genres, x: d.counts,
            marker: {
                color: d.counts,
                colorscale: [[0,'rgba(229,9,20,0.25)'], [1, THEME.RED]],
                showscale: false,
            },
            hovertemplate: '%{y}: %{x} titles<extra></extra>',
        };
        const layout = baseLayout({
            margin: { l:160, r:20, t:10, b:40 },
            yaxis: { gridcolor: THEME.gridcolor, autorange: 'reversed', tickfont: { size: 11 } },
            xaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-genres', [trace], layout, CFG);
    });
}

/* ── Chart: Top Countries ───────────────────────────────── */
function loadCountries(type) {
    const url = type === 'all' ? '/api/top_countries' : `/api/top_countries?type=${encodeURIComponent(type)}`;
    fetch(url).then(r => r.json()).then(d => {
        const trace = {
            type: 'bar',
            x: d.countries, y: d.counts,
            marker: {
                color: d.counts,
                colorscale: [[0,'rgba(229,9,20,0.2)'], [1, THEME.RED]],
                showscale: false,
            },
            hovertemplate: '%{x}: %{y} titles<extra></extra>',
        };
        const layout = baseLayout({
            xaxis: { gridcolor: THEME.gridcolor, tickangle: -25 },
            yaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-countries', [trace], layout, CFG);
    });
}

/* ── Chart: Duration Trend ──────────────────────────────── */
function loadDurationTrend() {
    fetch('/api/duration_trend').then(r => r.json()).then(d => {
        const trace = {
            type: 'scatter', mode: 'lines+markers',
            x: d.years, y: d.avg_duration,
            line: { color: THEME.RED, width: 2 },
            marker: { color: THEME.RED, size: 4 },
            fill: 'tozeroy',
            fillcolor: `${THEME.RED}12`,
            hovertemplate: '%{x}: %{y} min avg<extra></extra>',
        };
        const layout = baseLayout({
            yaxis: { gridcolor: THEME.gridcolor, title: { text: 'Minutes', font: { size: 11 } } },
            xaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-duration', [trace], layout, CFG);
    });
}

/* ── Chart: Seasonal ───────────────────────────────────── */
function loadSeasonal() {
    fetch('/api/seasonal').then(r => r.json()).then(d => {
        if (d.error) return;
        const trace = {
            type: 'bar',
            x: d.months, y: d.counts,
            marker: {
                color: d.counts,
                colorscale: [[0,'rgba(229,9,20,0.2)'],[1,THEME.RED]],
                showscale: false,
            },
            hovertemplate: '%{x}: %{y} titles<extra></extra>',
        };
        const layout = baseLayout({
            xaxis: { gridcolor: THEME.gridcolor },
            yaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-seasonal', [trace], layout, CFG);
    });
}

/* ── Chart: Top Directors ───────────────────────────────── */
function loadDirectors() {
    fetch('/api/top_directors').then(r => r.json()).then(d => {
        const trace = {
            type: 'bar', orientation: 'h',
            y: d.directors, x: d.counts,
            marker: { color: THEME.BLUE },
            hovertemplate: '%{y}: %{x} titles<extra></extra>',
        };
        const layout = baseLayout({
            margin: { l:150, r:20, t:10, b:40 },
            yaxis: { gridcolor: THEME.gridcolor, autorange:'reversed', tickfont:{size:10} },
            xaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-directors', [trace], layout, CFG);
    });
}

/* ── Chart: Rating Trends ───────────────────────────────── */
function loadRatingTrends() {
    fetch('/api/rating_trends').then(r => r.json()).then(d => {
        const ratings = Object.keys(d).filter(k => k !== 'years');
        const colors = { 'TV-MA': THEME.RED, 'R':'#f97316', 'PG-13':'#eab308', 'PG':'#22c55e','TV-PG':'#06b6d4','TV-14':'#a855f7' };
        const traces = ratings.map(r => ({
            type: 'scatter', mode: 'lines', name: r,
            x: d.years, y: d[r],
            line: { color: colors[r] || '#888', width: 2 },
            hovertemplate: `%{x}: %{y} titles<extra>${r}</extra>`,
        }));
        const layout = baseLayout({
            showlegend: true,
            legend: { x: 0.02, y: 0.95, bgcolor: 'transparent', font: { size: 11 } },
            xaxis: { gridcolor: THEME.gridcolor, range:[1990,2022] },
            yaxis: { gridcolor: THEME.gridcolor },
        });
        Plotly.react('chart-rating-trends', traces, layout, CFG);
    });
}

/* ── Chart: Duration by Country ─────────────────────────── */
function loadDurationByCountry() {
    fetch('/api/duration_by_country').then(r => r.json()).then(d => {
        const trace = {
            type: 'bar', orientation: 'h',
            y: d.countries, x: d.avg_duration,
            marker: {
                color: d.avg_duration,
                colorscale: [[0,'rgba(74,158,255,0.2)'],[1,THEME.BLUE]],
                showscale: false,
            },
            hovertemplate: '%{y}: %{x} min avg<extra></extra>',
        };
        const layout = baseLayout({
            margin: { l:150, r:20, t:10, b:50 },
            yaxis: { gridcolor: THEME.gridcolor, autorange:'reversed', tickfont:{size:11} },
            xaxis: { gridcolor: THEME.gridcolor, title:{ text:'Avg minutes', font:{size:11} } },
        });
        Plotly.react('chart-dur-country', [trace], layout, CFG);
    });
}

/* ── Load all charts ───────────────────────────────────── */
function loadAllCharts(type) {
    loadTrend(type);
    loadType();              // type split doesn't filter
    loadRatings(type);
    loadGenres(type);
    loadCountries(type);
    loadDurationTrend();     // movies only, no type filter needed
    loadSeasonal();          // aggregate, no filter
    loadDirectors();
    loadRatingTrends();
    loadDurationByCountry();
}

/* ── Filter buttons ────────────────────────────────────── */
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeType = btn.dataset.type;
        loadAllCharts(activeType);
    });
});

/* ── Search ────────────────────────────────────────────── */
function populateFilterOptions() {
    fetch('/api/filter_options').then(r => r.json()).then(d => {
        const genreSelect = document.getElementById('search-genre');
        genreSelect.innerHTML = '<option value="">All Genres</option>';
        d.genres.forEach(g => {
            const o = document.createElement('option');
            o.value = g; o.textContent = g;
            genreSelect.appendChild(o);
        });

        const ratingSelect = document.getElementById('search-rating');
        ratingSelect.innerHTML = '<option value="">All Ratings</option>';
        d.ratings.forEach(r => {
            const o = document.createElement('option');
            o.value = r; o.textContent = r;
            ratingSelect.appendChild(o);
        });

        const years = d.years;
        document.getElementById('year-from').min = years[0];
        document.getElementById('year-from').max = years[years.length-1];
        document.getElementById('year-to').min   = years[0];
        document.getElementById('year-to').max   = years[years.length-1];
    });
}

function runSearch() {
    const q        = document.getElementById('search-q').value.trim();
    const genre    = document.getElementById('search-genre').value;
    const type     = document.getElementById('search-type').value;
    const rating   = document.getElementById('search-rating').value;
    const yearFrom = document.getElementById('year-from').value;
    const yearTo   = document.getElementById('year-to').value;

    const params = new URLSearchParams();
    if (q)        params.set('q', q);
    if (genre)    params.set('genre', genre);
    if (type)     params.set('type', type);
    if (rating)   params.set('rating', rating);
    if (yearFrom) params.set('year_from', yearFrom);
    if (yearTo)   params.set('year_to', yearTo);

    document.getElementById('search-meta').textContent = 'Searching…';

    fetch('/api/search?' + params.toString())
        .then(r => r.json())
        .then(d => {
            const meta = document.getElementById('search-meta');
            const body = document.getElementById('results-body');
            const empty = document.getElementById('empty-state');
            const table = document.getElementById('results-table');

            meta.textContent = d.count > 0
                ? `${d.count.toLocaleString()} result${d.count !== 1 ? 's' : ''} found${d.count > 50 ? ' (showing first 50)' : ''}`
                : 'No results found.';

            if (d.results.length === 0) {
                body.innerHTML = '';
                table.style.display = 'none';
                empty.textContent = 'No titles match your search. Try different filters.';
                empty.style.display = 'block';
                return;
            }

            table.style.display = 'table';
            empty.style.display = 'none';
            body.innerHTML = d.results.map(r => `
                <tr>
                    <td>${escHtml(r.title)}</td>
                    <td><span class="badge ${r.type === 'Movie' ? 'badge-movie' : 'badge-show'}">${escHtml(r.type)}</span></td>
                    <td>${r.release_year}</td>
                    <td>${escHtml(r.rating)}</td>
                    <td>${escHtml(r.country)}</td>
                    <td style="max-width:200px;font-size:11px;color:rgba(255,255,255,0.4)">${escHtml(r.listed_in)}</td>
                    <td>${escHtml(r.duration)}</td>
                </tr>
            `).join('');
        });
}

function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function clearSearch() {
    document.getElementById('search-q').value = '';
    document.getElementById('search-genre').value = '';
    document.getElementById('search-type').value = '';
    document.getElementById('search-rating').value = '';
    document.getElementById('year-from').value = '';
    document.getElementById('year-to').value = '';
    document.getElementById('search-meta').textContent = '';
    document.getElementById('results-body').innerHTML = '';
    document.getElementById('results-table').style.display = 'none';
    document.getElementById('empty-state').textContent = 'Enter a search query above to explore Netflix titles.';
    document.getElementById('empty-state').style.display = 'block';
}

document.getElementById('btn-search').addEventListener('click', runSearch);
document.getElementById('btn-clear').addEventListener('click', clearSearch);
document.getElementById('search-q').addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });

/* ── Init ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('results-table').style.display = 'none';
    loadKPIs();
    loadAllCharts('all');
    populateFilterOptions();
});
