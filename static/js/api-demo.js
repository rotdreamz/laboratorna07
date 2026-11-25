// ============================================
// НАЛАШТУВАННЯ
// ============================================
const API_URL = '/api/products';

// ============================================
// ДОПОМІЖНІ ФУНКЦІЇ
// ============================================

function showLoading(show) {
    document.getElementById('loading').classList.toggle('show', show);
}

function showMessage(text, type) {
    const box = document.getElementById('message');
    box.textContent = text;
    box.className = type + ' show';
    setTimeout(() => box.classList.remove('show'), 5000);
}

// Дістає текст помилки з відповіді API ({"error": "..."})
async function getErrorText(response) {
    try {
        const body = await response.json();
        let text = body.error || `HTTP помилка! Статус: ${response.status}`;
        if (body.details) {
            text += ': ' + JSON.stringify(body.details);
        }
        return text;
    } catch {
        return `HTTP помилка! Статус: ${response.status}`;
    }
}

// ============================================
// РОБОТА З API
// ============================================

async function loadData() {
    try {
        showLoading(true);
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(await getErrorText(response));
        }
        const data = await response.json();
        displayData(data);
    } catch (error) {
        showMessage('❌ Помилка завантаження: ' + error.message, 'error');
        console.error('Помилка:', error);
    } finally {
        showLoading(false);
    }
}

async function addItem(itemData) {
    try {
        showLoading(true);
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(itemData)
        });
        if (!response.ok) {
            throw new Error(await getErrorText(response));
        }
        showMessage('✅ Товар успішно додано!', 'success');
        await loadData();
        return true;
    } catch (error) {
        showMessage('❌ Помилка додавання: ' + error.message, 'error');
        console.error('Помилка:', error);
        return false;
    } finally {
        showLoading(false);
    }
}

// ============================================
// ВІДОБРАЖЕННЯ ДАНИХ
// ============================================

function displayData(items) {
    const container = document.getElementById('dataList');
    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = '<div class="empty-state">📭 Товарів поки немає. Додайте перший!</div>';
        return;
    }

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';

        if (item.image) {
            const img = document.createElement('img');
            img.src = item.image;
            img.alt = item.name;
            div.appendChild(img);
        }

        const title = document.createElement('h3');
        title.textContent = item.name || 'Без назви';

        const price = document.createElement('p');
        price.className = 'price';
        price.textContent = item.price + ' ₴';

        const stock = document.createElement('p');
        stock.textContent = 'На складі: ' + item.stock;

        div.append(title, price, stock);

        if (item.description) {
            const desc = document.createElement('p');
            desc.textContent = item.description;
            div.appendChild(desc);
        }

        container.appendChild(div);
    });
}

// ============================================
// ОБРОБКА ФОРМИ
// ============================================

document.getElementById('addForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('name').value.trim();
    const description = document.getElementById('description').value.trim();
    const priceRaw = document.getElementById('price').value.trim();
    const stockRaw = document.getElementById('stock').value.trim();
    const image = document.getElementById('image').value.trim();

    // Валідація
    if (name.length < 2) {
        showMessage('❌ Назва повинна містити мінімум 2 символи', 'error');
        return;
    }
    const price = Number(priceRaw);
    if (priceRaw === '' || isNaN(price) || price < 0) {
        showMessage('❌ Ціна повинна бути числом не менше 0', 'error');
        return;
    }
    const stock = stockRaw === '' ? 0 : Number(stockRaw);
    if (!Number.isInteger(stock) || stock < 0) {
        showMessage('❌ Кількість повинна бути цілим числом не менше 0', 'error');
        return;
    }

    const itemData = { name, description, price, stock };
    if (image) {
        itemData.image = image;
    }

    const ok = await addItem(itemData);
    if (ok) {
        event.target.reset();
    }
});

// ============================================
// ІНІЦІАЛІЗАЦІЯ
// ============================================
loadData();