// API базовый URL
const API_URL = '/api/orders';
const MECHANICS_API_URL = '/api/admin/mechanics';

// Глобальные переменные
let mechanics = [];
let currentSection = 'orders';

// Управление секциями
function showSection(section) {
    currentSection = section;
    document.getElementById('mechanics-section').style.display = section === 'mechanics' ? 'block' : 'none';
    document.getElementById('orders-section').style.display = section === 'orders' ? 'block' : 'none';
    
    if (section === 'mechanics') {
        loadMechanics();
    } else if (section === 'orders') {
        loadOrders();
    }
}

function refreshCurrentSection() {
    if (currentSection === 'mechanics') {
        loadMechanics();
    } else {
        loadOrders();
    }
}

// === Управление механиками ===

async function loadMechanics() {
    try {
        const response = await fetch(MECHANICS_API_URL);
        mechanics = await response.json();
        renderMechanics();
    } catch (error) {
        console.error('Ошибка загрузки механиков:', error);
        document.getElementById('mechanics-list').innerHTML = 
            '<div class="col"><div class="alert alert-danger">Ошибка загрузки механиков</div></div>';
    }
}

function renderMechanics() {
    const container = document.getElementById('mechanics-list');
    
    if (mechanics.length === 0) {
        container.innerHTML = '<div class="col"><div class="alert alert-info">Механиков пока нет. Добавьте первого механика.</div></div>';
        return;
    }
    
    container.innerHTML = mechanics.map(m => `
        <div class="col">
            <div class="card mechanic-card ${m.active ? '' : 'mechanic-inactive'}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${m.name}</h5>
                        <span class="badge ${m.active ? 'bg-success' : 'bg-secondary'}">
                            ${m.active ? 'Активен' : 'Неактивен'}
                        </span>
                    </div>
                    <div class="mechanic-info mb-3">
                        <p class="mb-1"><small><strong>Email:</strong> ${m.email}</small></p>
                        <p class="mb-1"><small><strong>Телефон:</strong> ${m.phone || '-'}</small></p>
                        <p class="mb-1"><small><strong>Специализация:</strong> ${m.specialty || '-'}</small></p>
                    </div>
                    <div class="mechanic-stats mb-3" id="mechanic-stats-${m.id}">
                        <div class="text-center">
                            <div class="spinner-border spinner-border-sm" role="status">
                                <span class="visually-hidden">Загрузка...</span>
                            </div>
                        </div>
                    </div>
                    <div class="d-grid gap-2">
                        <button onclick="editMechanic(${m.id})" class="btn btn-sm btn-outline-primary">
                            ✏️ Редактировать
                        </button>
                        <button onclick="toggleMechanicActive(${m.id})" class="btn btn-sm ${m.active ? 'btn-outline-secondary' : 'btn-outline-success'}">
                            ${m.active ? '🚫 Деактивировать' : '✅ Активировать'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    mechanics.forEach(m => loadMechanicStats(m.id));
}

async function loadMechanicStats(mechanicId) {
    try {
        const response = await fetch(`${MECHANICS_API_URL}/${mechanicId}/stats`);
        const stats = await response.json();
        
        document.getElementById(`mechanic-stats-${mechanicId}`).innerHTML = `
            <div class="row g-2 text-center">
                <div class="col-6">
                    <div class="stat-box">
                        <div class="stat-value">${stats.active_orders}</div>
                        <div class="stat-label">В работе</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="stat-box">
                        <div class="stat-value">${stats.total_completed}</div>
                        <div class="stat-label">Выполнено</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="stat-box">
                        <div class="stat-value">${Math.round(stats.total_time_minutes / 60)}ч</div>
                        <div class="stat-label">Всего времени</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="stat-box">
                        <div class="stat-value">${stats.avg_time_per_order}м</div>
                        <div class="stat-label">Среднее время</div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Ошибка загрузки статистики механика:', error);
        document.getElementById(`mechanic-stats-${mechanicId}`).innerHTML = 
            '<small class="text-danger">Ошибка загрузки статистики</small>';
    }
}

function openMechanicModal(mechanicId = null) {
    const modal = new bootstrap.Modal(document.getElementById('mechanicModal'));
    const form = document.getElementById('mechanic-form');
    form.reset();
    
    if (mechanicId) {
        const mechanic = mechanics.find(m => m.id === mechanicId);
        if (mechanic) {
            document.getElementById('mechanicModalTitle').textContent = 'Редактировать механика';
            document.getElementById('mechanic-id').value = mechanic.id;
            document.getElementById('mechanic-name').value = mechanic.name;
            document.getElementById('mechanic-email').value = mechanic.email;
            document.getElementById('mechanic-phone').value = mechanic.phone || '';
            document.getElementById('mechanic-specialty').value = mechanic.specialty || '';
            document.getElementById('mechanic-password').required = false;
            document.getElementById('password-required-label').style.display = 'none';
        }
    } else {
        document.getElementById('mechanicModalTitle').textContent = 'Новый механик';
        document.getElementById('mechanic-id').value = '';
        document.getElementById('mechanic-password').required = true;
        document.getElementById('password-required-label').style.display = 'inline';
    }
    
    modal.show();
}

function editMechanic(mechanicId) {
    openMechanicModal(mechanicId);
}

async function saveMechanic() {
    const form = document.getElementById('mechanic-form');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const mechanicId = document.getElementById('mechanic-id').value;
    const data = {
        name: document.getElementById('mechanic-name').value,
        email: document.getElementById('mechanic-email').value,
        phone: document.getElementById('mechanic-phone').value,
        specialty: document.getElementById('mechanic-specialty').value
    };
    
    const password = document.getElementById('mechanic-password').value;
    if (password) {
        if (password.length < 6) {
            alert('Пароль должен содержать минимум 6 символов');
            return;
        }
        data.password = password;
    } else if (!mechanicId) {
        alert('Пароль обязателен для нового механика');
        return;
    }
    
    try {
        const url = mechanicId ? `${MECHANICS_API_URL}/${mechanicId}` : MECHANICS_API_URL;
        const method = mechanicId ? 'PATCH' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('mechanicModal'));
            modal.hide();
            loadMechanics();
            showNotification(mechanicId ? 'Механик обновлён' : 'Механик создан', 'success');
        } else {
            const error = await response.json();
            alert(error.error || 'Ошибка сохранения механика');
        }
    } catch (error) {
        console.error('Ошибка сохранения механика:', error);
        alert('Ошибка сохранения механика');
    }
}

async function toggleMechanicActive(mechanicId) {
    const mechanic = mechanics.find(m => m.id === mechanicId);
    const action = mechanic.active ? 'деактивировать' : 'активировать';
    
    if (!confirm(`Вы уверены, что хотите ${action} механика ${mechanic.name}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${MECHANICS_API_URL}/${mechanicId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active: !mechanic.active })
        });
        
        if (response.ok) {
            loadMechanics();
            showNotification(`Механик ${mechanic.active ? 'деактивирован' : 'активирован'}`, 'success');
        } else {
            throw new Error('Ошибка обновления');
        }
    } catch (error) {
        console.error('Ошибка обновления механика:', error);
        alert('Ошибка обновления механика');
    }
}

// === Назначение заказов ===

async function assignOrderModal(orderId) {
    if (mechanics.length === 0) {
        await loadMechanics();
    }
    
    const order = await getOrderById(orderId);
    if (!order) {
        alert('Заказ не найден');
        return;
    }
    
    document.getElementById('assign-order-id').value = orderId;
    
    const select = document.getElementById('assign-mechanic-select');
    select.innerHTML = '<option value="">Выберите механика...</option>' + 
        mechanics.filter(m => m.active).map(m => `
            <option value="${m.id}" ${order.assigned_mechanic_id === m.id ? 'selected' : ''}>
                ${m.name}${m.specialty ? ' - ' + m.specialty : ''}
            </option>
        `).join('');
    
    document.getElementById('assign-notes').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('assignModal'));
    modal.show();
}

async function getOrderById(orderId) {
    try {
        const response = await fetch(`${API_URL}/${orderId}`);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Ошибка получения заказа:', error);
    }
    return null;
}

async function confirmAssignOrder() {
    const orderId = document.getElementById('assign-order-id').value;
    const mechanicId = document.getElementById('assign-mechanic-select').value;
    const notes = document.getElementById('assign-notes').value;
    
    if (!mechanicId) {
        alert('Выберите механика');
        return;
    }
    
    try {
        const order = await getOrderById(orderId);
        const isReassign = order && order.assigned_mechanic_id;
        
        const endpoint = isReassign ? 
            `${API_URL}/${orderId}/reassign` : 
            `${API_URL}/${orderId}/assign`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                mechanic_id: parseInt(mechanicId), 
                notes: notes 
            })
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignModal'));
            modal.hide();
            loadOrders();
            showNotification(isReassign ? 'Заказ переназначен' : 'Заказ назначен', 'success');
        } else {
            const error = await response.json();
            alert(error.error || 'Ошибка назначения заказа');
        }
    } catch (error) {
        console.error('Ошибка назначения заказа:', error);
        alert('Ошибка назначения заказа');
    }
}

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
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-info" onclick="assignOrderModal(${order.id})" title="${order.assigned_mechanic_id ? 'Переназначить' : 'Назначить механика'}">
                        ${order.assigned_mechanic_id ? '👨‍🔧' : '➕👨‍🔧'}
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="printOrder(${order.id})" title="Печать">
                        🖨️
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteOrder(${order.id})" title="Удалить">
                        🗑️
                    </button>
                </div>
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
        
        const assignedMechanic = order.assigned_mechanic_id 
            ? mechanics.find(m => m.id === order.assigned_mechanic_id) 
            : null;
        
        document.getElementById('order-details').innerHTML = `
            <dl class="row">
                <dt class="col-sm-3">ID заказа:</dt>
                <dd class="col-sm-9">#${order.id}</dd>
                
                <dt class="col-sm-3">Дата создания:</dt>
                <dd class="col-sm-9">${new Date(order.created_at).toLocaleString('ru-RU')}</dd>
                
                <dt class="col-sm-3">Механик (отправитель):</dt>
                <dd class="col-sm-9">${order.mechanic_name}</dd>
                
                <dt class="col-sm-3">Назначен на:</dt>
                <dd class="col-sm-9">${assignedMechanic ? `${assignedMechanic.name} (${assignedMechanic.specialty || 'нет специализации'})` : '<span class="text-muted">Не назначен</span>'}</dd>
                
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
    loadMechanics();
    loadOrders();
    
    // Автообновление каждые 30 секунд
    setInterval(() => {
        if (currentSection === 'orders') {
            loadOrders();
        }
    }, 30000);
});
