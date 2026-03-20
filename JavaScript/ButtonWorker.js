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

// collected buttons
const collectedButtons = document.querySelectorAll('.collected-button');

collectedButtons.forEach(button => {
    button.classList.add('not-collected');
    button.textContent = 'Not Collected ❌';

    button.addEventListener('click', () => {
        if (button.classList.contains('not-collected')) {
            button.classList.remove('not-collected');
            button.classList.add('collected');
            button.textContent = 'Collected ✅';
        } else {
            button.classList.remove('collected');
            button.classList.add('not-collected');
            button.textContent = 'Not Collected ❌';
        }
    });
});