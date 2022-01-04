/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function toggleDropdown() {
    // Add show class
    let content = document.querySelector("#dropdown-content")
    content.classList.toggle("show");

    // Flip the carat
    let carat = document.querySelector('.fa-caret-down')
    if (content.classList.contains('show')) {
        carat.style.transform = 'rotate(180deg)'
    } else {
        carat.style.transform = 'rotate(0deg)'
    }
}