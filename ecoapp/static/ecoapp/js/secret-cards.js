let currentIndex = 1; // Индекс текущей картинки

// Список картинок и их описаний
const images = [
    "/static/ecoapp/images/secret1.png",
    "/static/ecoapp/images/secret2.png",
    "/static/ecoapp/images/secret3.png",
    "/static/ecoapp/images/secret4.png",
    "/static/ecoapp/images/secret5.png",
    "/static/ecoapp/images/secret6.png",
    "/static/ecoapp/images/secret7.png"
];

const descriptions = [
    "Из-за географического расположения на Камчатке выпадает много осадков.",
    "На Камчатке расположено более 300 вулканов, около 30 действующих.",
    "Песок образуется из-за разрушения вулканических пород.",
    "Около 20 000 бурых медведей живут на Камчатке.",
    "Озеро образовалось благодаря вулканической активности.",
    "Рыбные ресурсы поддерживают популяцию медведей.",
    "Традиционные танцы и обряды коренных народов Камчатки уникальны!"
];

function changeImage(n) {
    currentIndex += n;
    if (currentIndex > images.length) {
        currentIndex = 1;
    } else if (currentIndex < 1) {
        currentIndex = images.length;
    }
    showImage(currentIndex);
}

function showImage(index) {
    const img = document.querySelector('.secrets-slider img');
    const description = document.querySelector('.secret-description');
    
    img.src = images[index - 1];
    description.textContent = descriptions[index - 1];  // Обновляем описание

    // Обновить активную точку
    const dots = document.querySelectorAll('.dot');
    dots.forEach(dot => dot.classList.remove('active'));
    dots[index - 1].classList.add('active');
}

function setImage(index) {
    currentIndex = index + 1;
    showImage(currentIndex);
}

// Инициализация первого изображения и описания
showImage(currentIndex);
