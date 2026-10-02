// item button
const itembutton = document.getElementById("itembutton");
function handleItemClick() {
    window.location.href = "/items";
}
if (itembutton) {
    itembutton.addEventListener("click", handleItemClick);
}

// storage button
const storagebutton = document.getElementById("storagebutton");
function handleStorageClick() {
    window.location.href = "/storage";
}
if (storagebutton) {
    storagebutton.addEventListener("click", handleStorageClick);
}

// questline button
const questlinebutton = document.getElementById("questlinebutton");
function handleQuestlineClick() {
    window.location.href = "/questlines";
}
if (questlinebutton) {
    questlinebutton.addEventListener("click", handleQuestlineClick);
}

// login button
const loginbutton = document.getElementById("loginbutton");
function handleLoginClick() {
    window.location.href = "/login";
}
if (loginbutton) {
    loginbutton.addEventListener("click", handleLoginClick);
}

async function searchItems() {
    const query = document.getElementById("searchInput").value;

    const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
    const items = await response.json();

    const resultsDiv = document.getElementById("searchResults");
    resultsDiv.innerHTML = "";

    items.forEach(item => {
        resultsDiv.innerHTML += `
            <div class="item-card">
                <img class="item-image" src="/static/images/${item.image}" alt="${item.item_name}">
                <h3>${item.item_name}</h3>
                <p><strong>Category:</strong> ${item.category}</p>
                <p><strong>Type:</strong> ${item.item_type}</p>
                <p><strong>Rarity:</strong> ${item.rarity}</p>
                <p><strong>Effect:</strong> ${item.effect}</p>
                <p><strong>Quest:</strong> ${item.quest}</p>
                <p><strong>Location:</strong> ${item.location}</p>
                <p><strong>DLC:</strong> ${item.dlc}</p>
                <p><strong>Weight:</strong> ${item.item_weight}</p>
                <p><strong>Value:</strong> ${item.item_value}</p>
                <p><strong>Tags:</strong> ${item.tags}</p>
                <small>Match Score: ${item.score.toFixed(2)}</small>
            </div>
        `;
    });
}

function recommendBuild(buildType) {
    const searchInput = document.getElementById("searchInput");

    if (searchInput) {
        searchInput.value = buildType;
        searchItems();
    }
}
// Remove credentials left by the old browser-only login.
['accountUsername', 'accountPassword', 'loggedInUser', 'isLoggedIn'].forEach(key => localStorage.removeItem(key));

async function authRequest(url, data, token) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': token},
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Request failed. Please try again.');
    return result;
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async event => {
        event.preventDefault();
        const button = loginForm.querySelector('button[type="submit"]');
        const message = document.getElementById('login-message');
        button.disabled = true;
        try {
            await authRequest(loginForm.dataset.endpoint, {
                username: document.getElementById('username').value.trim(),
                password: document.getElementById('password').value,
                confirm_password: document.getElementById('confirm-password')?.value,
                remember: document.getElementById('rememberMe').checked
            }, document.getElementById('csrf-token').value);
            window.location.href = '/';
        } catch (error) {
            message.textContent = error.message;
            button.disabled = false;
        }
    });
}

async function initializeAccount() {
    try {
        const response = await fetch('/api/session');
        if (!response.ok) throw new Error('Unable to load your account.');
        const account = await response.json();
        const welcome = document.getElementById('welcome-text');
        if (welcome) welcome.textContent = account.user ? `Welcome, ${account.user.username}!` : 'Log in to save your progress.';
        const login = document.getElementById('loginbutton');
        const logout = document.getElementById('logoutbutton');
        if (login) login.hidden = Boolean(account.user);
        if (logout) {
            logout.hidden = !account.user;
            logout.addEventListener('click', async () => {
                try {
                    await authRequest('/logout', {}, account.csrf_token);
                    window.location.href = '/login';
                } catch (error) { alert(error.message); }
            });
        }
        const buttons = document.querySelectorAll('.collected-button, .quest-complete-button');
        const storageButtons = document.querySelectorAll('.storage-button');
        let progress = {};
        if (account.user && (buttons.length || storageButtons.length)) {
            const saved = await fetch('/api/progress');
            if (!saved.ok) throw new Error('Unable to load saved progress. Refresh to try again.');
            progress = await saved.json();
        }
        function renderProgress() {
            buttons.forEach(button => {
                const quest = button.classList.contains('quest-complete-button');
                const key = quest ? button.dataset.quest : button.dataset.item;
                const active = progress[key] === (quest ? 'completed' : 'collected');
                button.classList.toggle(quest ? 'completed' : 'collected', active);
                if (!quest) button.classList.toggle('not-collected', !active);
                button.textContent = quest ? (active ? 'Completed' : 'Not Completed') : (active ? 'Collected' : 'Not Collected');
            });
        }
        document.querySelectorAll('.storage-location').forEach(label => {
            const name = label.closest('.item-card').querySelector('.item-name').textContent.trim();
            label.textContent = progress[`storage:${name}`] || 'Not stored';
        });
        storageButtons.forEach(button => {
            button.addEventListener('click', async () => {
                if (!account.user) { window.location.href = '/login'; return; }
                const card = button.closest('.item-card');
                const key = `storage:${card.querySelector('.item-name').textContent.trim()}`;
                const location = button.dataset.location;
                storageButtons.forEach(item => { item.disabled = true; });
                try {
                    await authRequest('/api/progress', {[key]: location}, account.csrf_token);
                    card.querySelector('.storage-location').textContent = location;
                } catch (error) { alert(error.message); }
                finally { storageButtons.forEach(item => { item.disabled = false; }); }
            });
        });
        renderProgress();
        buttons.forEach(button => {
            button.addEventListener('click', async () => {
                if (!account.user) { window.location.href = '/login'; return; }
                const quest = button.classList.contains('quest-complete-button');
                const key = quest ? button.dataset.quest : button.dataset.item;
                const active = progress[key] === (quest ? 'completed' : 'collected');
                const changes = {[key]: quest ? (active ? 'not-completed' : 'completed') : (active ? 'not-collected' : 'collected')};
                if (quest && button.dataset.item) changes[button.dataset.item] = active ? 'not-collected' : 'collected';
                buttons.forEach(item => { item.disabled = true; });
                try {
                    await authRequest('/api/progress', changes, account.csrf_token);
                    Object.assign(progress, changes);
                    renderProgress();
                } catch (error) { alert(error.message); }
                finally { buttons.forEach(item => { item.disabled = false; }); }
            });
        });
    } catch (error) {
        document.querySelectorAll('.collected-button, .quest-complete-button, .storage-button').forEach(button => { button.disabled = true; });
        const welcome = document.getElementById('welcome-text');
        if (welcome) welcome.textContent = error.message;
        else if (!loginForm) alert(error.message);
    }
}
initializeAccount();
