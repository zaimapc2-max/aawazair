const checkAqiBtn = document.getElementById('check-aqi-btn');
const cityInput = document.getElementById('city-input');

const aqiLoading = document.getElementById('aqi-loading');
const aqiError = document.getElementById('aqi-error');
const aqiResult = document.getElementById('aqi-result');
const aqiNumber = document.getElementById('aqi-number');
const aqiCategory = document.getElementById('aqi-category');
const aqiCityLabel = document.getElementById('aqi-city-label');

// Keep the latest AQI data in memory so other features (advisory, chart)
// can reuse it without re-fetching
let currentAqiData = null;

function showAqiLoading() {
    aqiLoading.classList.remove('hidden');
    aqiError.classList.add('hidden');
    aqiResult.classList.add('hidden');
}

function showAqiError(message) {
    aqiLoading.classList.add('hidden');
    aqiError.classList.remove('hidden');
    aqiResult.classList.add('hidden');
    aqiError.textContent = message;
}

function showAqiResult(data) {
    aqiLoading.classList.add('hidden');
    aqiError.classList.add('hidden');
    aqiResult.classList.remove('hidden');

    aqiNumber.textContent = data.aqi_us;
    aqiCategory.textContent = data.category;
    aqiCityLabel.textContent = `${data.city}, ${data.country}`;
}

async function fetchAqi(city) {
    showAqiLoading();

    try {
        const response = await fetch(`/api/aqi?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok) {
            showAqiError(data.error || 'Something went wrong fetching AQI data.');
            return;
        }

        currentAqiData = data;
        showAqiResult(data);

    } catch (err) {
        showAqiError('Could not reach the server. Is Flask running?');
        console.error(err);
    }
}

checkAqiBtn.addEventListener('click', () => {
    const city = cityInput.value.trim();
    if (!city) {
        showAqiError('Please enter a city name.');
        return;
    }
    fetchAqi(city);
});

// Auto-load Lahore on page load, since it's pre-filled in the input
fetchAqi(cityInput.value.trim());