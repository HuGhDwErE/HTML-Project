// item button
const itembutton = document.getElementById("itembutton");
function handleItemClick() {
    window.location.href = "item_page.html";
}
if (itembutton) {
    itembutton.addEventListener("click", handleItemClick);
}

// storage button
const storagebutton = document.getElementById("storagebutton");
function handleStorageClick() {
    window.location.href = "storage_page.html";
}
if (storagebutton) {
    storagebutton.addEventListener("click", handleStorageClick);
}

// questline button
const questlinebutton = document.getElementById("questlinebutton");
function handleQuestlineClick() {
    window.location.href = "questline_page.html";
}
if (questlinebutton) {
    questlinebutton.addEventListener("click", handleQuestlineClick);
}

// login button
const loginbutton = document.getElementById("loginbutton");
function handleLoginClick() {
    window.location.href = "login_page.html";
}
if (loginbutton) {
    loginbutton.addEventListener("click", handleLoginClick);
}

// collected item buttons
const collectedButtons = document.querySelectorAll(".collected-button");

collectedButtons.forEach(button => {
    const itemName = button.dataset.item;
    const savedState = localStorage.getItem(itemName);

    if (savedState === "collected") {
        button.classList.add("collected");
        button.classList.remove("not-collected");
        button.textContent = "Collected ";
    } else {
        button.classList.add("not-collected");
        button.classList.remove("collected");
        button.textContent = "Not Collected ";
    }

    button.addEventListener("click", () => {
        if (button.classList.contains("not-collected")) {
            button.classList.remove("not-collected");
            button.classList.add("collected");
            button.textContent = "Collected ";
            localStorage.setItem(itemName, "collected");
        } else {
            button.classList.remove("collected");
            button.classList.add("not-collected");
            button.textContent = "Not Collected ";
            localStorage.setItem(itemName, "not-collected");
        }
    });
});

// questline buttons
const questButtons = document.querySelectorAll(".quest-complete-button");

questButtons.forEach(button => {
    const questName = button.dataset.quest;
    const itemName = button.dataset.item;
    const savedQuestState = localStorage.getItem(questName);

    if (savedQuestState === "completed") {
        button.classList.add("completed");
        button.textContent = "Completed ";
    } else {
        button.textContent = "Not Completed ";
    }

    button.addEventListener("click", () => {
        if (button.classList.contains("completed")) {
            button.classList.remove("completed");
            button.textContent = "Not Completed ";
            localStorage.setItem(questName, "not-completed");
            localStorage.setItem(itemName, "not-collected");
        } else {
            button.classList.add("completed");
            button.textContent = "Completed ";
            localStorage.setItem(questName, "completed");
            localStorage.setItem(itemName, "collected");
        }
    });
});

// login system
const loginForm = document.getElementById("login-form");

if (loginForm) {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const rememberMeInput = document.getElementById("rememberMe");
    const loginMessage = document.getElementById("login-message");

    // fill in remembered username if it exists
    const rememberedUsername = localStorage.getItem("rememberedUsername");
    if (rememberedUsername) {
        usernameInput.value = rememberedUsername;
        rememberMeInput.checked = true;
    }

    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (username === "" || password === "") {
            loginMessage.textContent = "Please enter a username and password.";
            return;
        }

        const savedUsername = localStorage.getItem("accountUsername");
        const savedPassword = localStorage.getItem("accountPassword");

        // if no account exists yet, create one
        if (!savedUsername && !savedPassword) {
            localStorage.setItem("accountUsername", username);
            localStorage.setItem("accountPassword", password);
            localStorage.setItem("loggedInUser", username);
            localStorage.setItem("isLoggedIn", "true");

            if (rememberMeInput.checked) {
                localStorage.setItem("rememberedUsername", username);
            } else {
                localStorage.removeItem("rememberedUsername");
            }

            loginMessage.textContent = "Account created successfully!";
            window.location.href = "Html_project.html";
            return;
        }

        // if account exists, check login details
        if (username === savedUsername && password === savedPassword) {
            localStorage.setItem("loggedInUser", username);
            localStorage.setItem("isLoggedIn", "true");

            if (rememberMeInput.checked) {
                localStorage.setItem("rememberedUsername", username);
            } else {
                localStorage.removeItem("rememberedUsername");
            }

            loginMessage.textContent = "Login successful!";
            window.location.href = "Html_project.html";
        } else {
            loginMessage.textContent = "Incorrect username or password.";
        }
    });
}

// logout button
const logoutbutton = document.getElementById("logoutbutton");
if (logoutbutton) {
    logoutbutton.addEventListener("click", () => {
        localStorage.removeItem("isLoggedIn");
        localStorage.removeItem("loggedInUser");
        window.location.href = "login_page.html";
    });
}

// welcome text
const welcomeText = document.getElementById("welcome-text");
if (welcomeText) {
    const loggedInUser = localStorage.getItem("loggedInUser");
    if (loggedInUser) {
        welcomeText.textContent = "Welcome, " + loggedInUser + "!";
    } else {
        welcomeText.textContent = "You are not logged in.";
    }
}