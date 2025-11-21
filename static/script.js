document.addEventListener('DOMContentLoaded', () => {
    const movieInput = document.getElementById('movieInput');
    const suggestionsBox = document.getElementById('suggestions');
    const recommendBtn = document.getElementById('recommendBtn');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    let debounceTimer;

    // Autocomplete
    movieInput.addEventListener('input', (e) => {
        const query = e.target.value;
        clearTimeout(debounceTimer);

        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
                const titles = await response.json();
                
                if (titles.length > 0) {
                    suggestionsBox.innerHTML = titles.map(title => 
                        `<div class="suggestion-item">${title}</div>`
                    ).join('');
                    suggestionsBox.style.display = 'block';
                } else {
                    suggestionsBox.style.display = 'none';
                }
            } catch (err) {
                console.error('Search error:', err);
            }
        }, 300);
    });

    // Select suggestion
    suggestionsBox.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-item')) {
            movieInput.value = e.target.textContent;
            suggestionsBox.style.display = 'none';
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            suggestionsBox.style.display = 'none';
        }
    });

    // Get Recommendations
    recommendBtn.addEventListener('click', async () => {
        const movieName = movieInput.value.trim();
        if (!movieName) return;

        // UI Reset
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        suggestionsBox.style.display = 'none';

        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ movie_name: movieName })
            });

            const data = await response.json();

            loadingDiv.classList.add('hidden');

            if (response.ok) {
                displayResults(data);
            } else {
                showError(data.error || 'Something went wrong');
            }
        } catch (err) {
            loadingDiv.classList.add('hidden');
            showError('Failed to connect to server');
        }
    });

    function displayResults(movies) {
        resultsDiv.innerHTML = movies.map(movie => `
            <div class="movie-card">
                <div class="movie-title">${movie.title}</div>
                <div class="similarity-score">${(movie.similarity * 100).toFixed(1)}% Match</div>
            </div>
        `).join('');
        resultsDiv.classList.remove('hidden');
    }

    function showError(msg) {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    }
});
