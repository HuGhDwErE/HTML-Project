// item button
const itembutton = document.getElementById("itembutton")
function handleItemClick() {
    window.location.href = "item_page.html"
}
itembutton.addEventListener("click", handleItemClick);

// storage button
const storagebutton = document.getElementById("storagebutton")
function handleStorageClick() {
    window.location.href = "storage_page.html"
}
storagebutton.addEventListener("click", handleStorageClick);

// questline button
const questlinebutton = document.getElementById("questlinebutton")
function handleQuestlineClick() {
    window.location.href = "questline_page.html"
}
questlinebutton.addEventListener("click", handleQuestlineClick)

// login button
const loginbutton = document.getElementById("loginbutton")
function handleLoginClick() {
    window.location.href = "login_page"
}
loginbutton.addEventListener("click", handleLoginClick)