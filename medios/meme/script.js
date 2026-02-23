let memes = [];
let index = 0;
let lock = false;

// Cargar memes
fetch('memes.json')
    .then(r => r.json())
    .then(data => {
        memes = data;
        if (memes.length > 0) {
            render();
        }
    })
    .catch(err => {
        console.error('Error cargando memes.json', err);
    });

function render(intentos = 0) {
    const viewer = document.getElementById('meme-viewer');
    const indicator = document.getElementById('indicator');

    viewer.innerHTML = '';
    indicator.textContent = '';

    if (!memes.length || intentos >= memes.length) {
        return; // No hay nada válido
    }

    // Índice circular
    index = (index + memes.length) % memes.length;

    const meme = memes[index];
    let el;

    if (meme.type === 'image') {
        el = document.createElement('img');
        el.src = 'media/memes/' + meme.file;
    }

    if (meme.type === 'video') {
        el = document.createElement('video');
        el.src = 'media/memes/' + meme.file;
        el.controls = true;
        el.autoplay = true;
        el.loop = true;
    }

    if (!el) return;

    // Manejo de error REAL
    el.onerror = () => {
        index++;
        render(intentos + 1);
    };

    viewer.appendChild(el);
    indicator.textContent = `Meme ${index + 1} de ${memes.length}`;
}

// Navegación
function siguiente() {
    index++;
    render();
}

function anterior() {
    index--;
    render();
}

// Scroll
window.addEventListener('wheel', e => {
    if (lock || memes.length <= 1) return;
    lock = true;

    e.deltaY > 0 ? siguiente() : anterior();

    setTimeout(() => lock = false, 400);
});

// Swipe
let startY = 0;

window.addEventListener('touchstart', e => {
    startY = e.touches[0].clientY;
});

window.addEventListener('touchend', e => {
    if (memes.length <= 1) return;

    const diff = startY - e.changedTouches[0].clientY;
    if (Math.abs(diff) > 50) {
        diff > 0 ? siguiente() : anterior();
    }
});
