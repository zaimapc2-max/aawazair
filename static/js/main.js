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

const profileForm = document.getElementById('profile-form');
const profileNameInput = document.getElementById('profile-name');
const profileAgeGroupInput = document.getElementById('profile-age-group');
const healthConditionsFieldset = document.getElementById('health-conditions');

const advisorySection = document.getElementById('advisory-section');
const advisoryLoading = document.getElementById('advisory-loading');
const advisoryError = document.getElementById('advisory-error');
const advisoryResult = document.getElementById('advisory-result');

function getSelectedConditions() {
    const checkboxes = healthConditionsFieldset.querySelectorAll('input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function showAdvisoryLoading() {
    advisorySection.classList.remove('hidden');
    advisoryLoading.classList.remove('hidden');
    advisoryError.classList.add('hidden');
    advisoryResult.classList.add('hidden');
}

function showAdvisoryError(message) {
    advisoryLoading.classList.add('hidden');
    advisoryError.classList.remove('hidden');
    advisoryResult.classList.add('hidden');
    advisoryError.textContent = message;
}

function showAdvisoryResult(data) {
    advisoryLoading.classList.add('hidden');
    advisoryError.classList.add('hidden');
    advisoryResult.classList.remove('hidden');

    const risk = data.advisory.risk_score;
    const advisories = data.advisory.advisories;

    let html = `<p><strong>Current AQI in ${data.user.city}:</strong> ${data.current_aqi.aqi_us} (${data.current_aqi.category})</p>`;
    html += `<p><strong>Risk level for you:</strong> ${risk} / 5</p>`;
    html += '<ul>';
    advisories.forEach(a => {
        html += `<li><strong>${a.condition}:</strong> ${a.advice}</li>`;
    });
    html += '</ul>';

    advisoryResult.innerHTML = html;
}

async function createUserAndGetAdvisory(name, ageGroup, conditions, city) {
    showAdvisoryLoading();

    try {
        // Step 1: create the user profile
        const createResponse = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                age_group: ageGroup,
                health_conditions: conditions,
                city: city
            })
        });

        const createData = await createResponse.json();

        if (!createResponse.ok) {
            showAdvisoryError(createData.error || 'Could not create your profile.');
            return;
        }

        // Step 2: immediately fetch the personalized advisory using the new user ID
        const advisoryResponse = await fetch(`/api/users/${createData.id}/advisory`);
        const advisoryData = await advisoryResponse.json();

        if (!advisoryResponse.ok) {
            showAdvisoryError(advisoryData.error || 'Could not fetch your advisory.');
            return;
        }

        showAdvisoryResult(advisoryData);

    } catch (err) {
        showAdvisoryError('Could not reach the server. Is Flask running?');
        console.error(err);
    }
}

profileForm.addEventListener('submit', (e) => {
    e.preventDefault();  // stop the form from doing a full page reload

    const name = profileNameInput.value.trim();
    const ageGroup = profileAgeGroupInput.value;
    const conditions = getSelectedConditions();
    const city = cityInput.value.trim();  // reuse the city already entered above

    if (!name || !ageGroup || !city) {
        showAdvisoryError('Please fill in your name, age group, and a city first.');
        return;
    }

    createUserAndGetAdvisory(name, ageGroup, conditions, city);
});