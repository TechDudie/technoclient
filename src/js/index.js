const _version = "1.0.0";

screens = [
    "_main",
    "_multiplayer"
];

function e(id) {
    return document.getElementById(id);
}

function view(screen) {
    screens.forEach(function (id) {
        if (id != screen) {
            e(id).style.display = "none";
        }
    });
    e(screen).style.display = "block";
}

document.getElementById("subheader").innerText = _version;

e("servers").addEventListener('click', () => {
    view("_multiplayer");
});

Array.from(document.getElementsByClassName("back")).forEach(function (element) {
    element.addEventListener('click', () => {
        view("_main");
    });
});