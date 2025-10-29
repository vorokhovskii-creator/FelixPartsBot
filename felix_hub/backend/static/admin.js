// API базовый URL
const API_URL = '/api/orders';

// Загрузка статистики
async function loadStats() {
    try {
        const response = await fetch('/api/orders/stats');
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-today').textContent = stats.today;
        document.getElementById('stat-working').textContent = stats.by_status['в работе'] || 0;
        document.getElementById('stat-ready').textContent = stats.by_status['готов'] || 0;
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// Загрузка заказов
async function loadOrders() {
    const status = document.getElementById('filter-status').value;
    const mechanic = document.getElementById('filter-mechanic').value;
    const search = document.getElementById('search').value;
    
    let url = API_URL + '?';
    if (status) url += `status=${status}&`;
    if (mechanic) url += `mechanic=${mechanic}&`;
    
    try {
        const response = await fetch(url);
        const orders = await response.json();
        
        // Фильтрация по поиску на клиенте
        const filtered = search 
            ? orders.filter(o => 
                o.vin.toLowerCase().includes(search.toLowerCase()) || 
                o.id.toString().includes(search)
              )
            : orders;
        
        renderOrders(filtered);
        loadStats();
    } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
        document.getElementById('orders-table').innerHTML = 
            '<tr><td colspan="9" class="text-center text-danger">Ошибка загрузки данных</td></tr>';
    }
}

// Отрисовка таблицы заказов
function renderOrders(orders) {
    const tbody = document.getElementById('orders-table');
    
    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">Заказов не найдено</td></tr>';
        return;
    }
    
    tbody.innerHTML = orders.map(order => `
        <tr>
            <td><strong>#${order.id}</strong></td>
            <td>${new Date(order.created_at).toLocaleString('ru-RU')}</td>
            <td>${order.mechanic_name}</td>
            <td>${order.category}</td>
            <td><code>${order.vin}</code></td>
            <td>
                <button class="btn btn-sm btn-link" onclick="showOrderDetails(${order.id})">
                    ${order.selected_parts.length} шт.
                </button>
            </td>
            <td>${order.is_original ? '✨ Да' : '🔧 Нет'}</td>
            <td>
                <select class="form-select form-select-sm status-select" 
                        onchange="updateStatus(${order.id}, this.value)"
                        data-current="${order.status}">
                    <option value="новый" ${order.status === 'новый' ? 'selected' : ''}>🆕 Новый</option>
                    <option value="в работе" ${order.status === 'в работе' ? 'selected' : ''}>⏳ В работе</option>
                    <option value="готов" ${order.status === 'готов' ? 'selected' : ''}>✅ Готов</option>
                    <option value="выдан" ${order.status === 'выдан' ? 'selected' : ''}>📦 Выдан</option>
                </select>
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="printOrder(${order.id})" title="Печать">
                    🖨️
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteOrder(${order.id})" title="Удалить">
                    🗑️
                </button>
            </td>
        </tr>
    `).join('');
}

// Обновление статуса заказа
async function updateStatus(orderId, newStatus) {
    try {
        const response = await fetch(`${API_URL}/${orderId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            showNotification(`Статус заказа #${orderId} изменён на "${newStatus}"`, 'success');
            loadOrders();
        } else {
            throw new Error('Ошибка обновления');
        }
    } catch (error) {
        console.error('Ошибка обновления статуса:', error);
        showNotification('Ошибка обновления статуса', 'danger');
        loadOrders();
    }
}

// Показ деталей заказа
async function showOrderDetails(orderId) {
    try {
        const response = await fetch(`${API_URL}/${orderId}`);
        const order = await response.json();
        
        const parts = order.selected_parts.map(p => `<li>${p}</li>`).join('');
        const photo = order.photo_url 
            ? `<img src="${order.photo_url}" class="img-fluid mt-2" alt="Фото детали">`
            : '<p class="text-muted">Фото не загружено</p>';
        
        document.getElementById('order-details').innerHTML = `
            <dl class="row">
                <dt class="col-sm-3">ID заказа:</dt>
                <dd class="col-sm-9">#${order.id}</dd>
                
                <dt class="col-sm-3">Дата создания:</dt>
                <dd class="col-sm-9">${new Date(order.created_at).toLocaleString('ru-RU')}</dd>
                
                <dt class="col-sm-3">Механик:</dt>
                <dd class="col-sm-9">${order.mechanic_name}</dd>
                
                <dt class="col-sm-3">Telegram ID:</dt>
                <dd class="col-sm-9"><code>${order.telegram_id}</code></dd>
                
                <dt class="col-sm-3">Категория:</dt>
                <dd class="col-sm-9">${order.category}</dd>
                
                <dt class="col-sm-3">VIN:</dt>
                <dd class="col-sm-9"><code>${order.vin}</code></dd>
                
                <dt class="col-sm-3">Детали:</dt>
                <dd class="col-sm-9"><ul>${parts}</ul></dd>
                
                <dt class="col-sm-3">Тип:</dt>
                <dd class="col-sm-9">${order.is_original ? '✨ Оригинал' : '🔧 Не оригинал'}</dd>
                
                <dt class="col-sm-3">Статус:</dt>
                <dd class="col-sm-9"><span class="badge bg-primary">${order.status}</span></dd>
                
                <dt class="col-sm-3">Напечатан:</dt>
                <dd class="col-sm-9">${order.printed ? '✅ Да' : '❌ Нет'}</dd>
                
                <dt class="col-sm-3">Фото:</dt>
                <dd class="col-sm-9">${photo}</dd>
            </dl>
        `;
        
        new bootstrap.Modal(document.getElementById('orderModal')).show();
    } catch (error) {
        console.error('Ошибка загрузки деталей:', error);
        showNotification('Ошибка загрузки деталей заказа', 'danger');
    }
}

// Печать чека
async function printOrder(orderId) {
    if (!confirm('Отправить заказ на печать?')) return;
    
    try {
        const response = await fetch(`${API_URL}/${orderId}/print`, { method: 'POST' });
        if (response.ok) {
            showNotification(`Заказ #${orderId} отправлен на печать`, 'success');
        }
    } catch (error) {
        console.error('Ошибка печати:', error);
        showNotification('Ошибка печати', 'danger');
    }
}

// Удаление заказа
async function deleteOrder(orderId) {
    if (!confirm('Удалить заказ? Это действие нельзя отменить.')) return;
    
    try {
        const response = await fetch(`${API_URL}/${orderId}`, { method: 'DELETE' });
        if (response.ok) {
            showNotification(`Заказ #${orderId} удалён`, 'success');
            loadOrders();
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        showNotification('Ошибка удаления заказа', 'danger');
    }
}

// Экспорт в Excel
function exportOrders() {
    const days = prompt('За сколько дней экспортировать заказы?', '30');
    if (days) {
        window.location.href = `/export?days=${days}`;
    }
}

// Сброс фильтров
function resetFilters() {
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-mechanic').value = '';
    document.getElementById('search').value = '';
    loadOrders();
}

// Уведомления
function showNotification(message, type = 'info') {
    // Можно использовать toast или alert
    alert(message);
}

// Загрузка при старте
document.addEventListener('DOMContentLoaded', () => {
    loadOrders();
    
    // Автообновление каждые 30 секунд
    setInterval(loadOrders, 30000);
});
