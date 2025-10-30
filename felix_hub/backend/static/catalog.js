let selectedCategoryId = null;
let categoryModal, partModal;

document.addEventListener('DOMContentLoaded', () => {
    categoryModal = new bootstrap.Modal(document.getElementById('categoryModal'));
    partModal = new bootstrap.Modal(document.getElementById('partModal'));
    
    loadCategories();
});

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) throw new Error('Failed to load categories');
        
        const categories = await response.json();
        const container = document.getElementById('categories-list');
        
        if (categories.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Нет категорий. Добавьте первую!</div>';
            return;
        }
        
        container.innerHTML = categories.map(cat => `
            <div class="list-group-item ${selectedCategoryId === cat.id ? 'active' : ''}" 
                 style="cursor: pointer;" 
                 onclick="selectCategory(${cat.id})">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span style="font-size: 1.2em;">${cat.icon}</span>
                        <strong class="ms-2">${cat.name_ru}</strong>
                        ${cat.name_he ? `<br><small class="text-muted ms-4">${cat.name_he}</small>` : ''}
                        ${cat.name_en ? `<br><small class="text-muted ms-4">${cat.name_en}</small>` : ''}
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="event.stopPropagation(); editCategory(${cat.id})" title="Редактировать">
                            ✏️
                        </button>
                        <button class="btn btn-outline-danger" onclick="event.stopPropagation(); deleteCategory(${cat.id})" title="Удалить">
                            🗑️
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading categories:', error);
        showError('Ошибка загрузки категорий');
    }
}

async function selectCategory(categoryId) {
    selectedCategoryId = categoryId;
    document.getElementById('add-part-btn').disabled = false;
    
    await loadCategories();
    await loadParts(categoryId);
}

async function loadParts(categoryId) {
    try {
        const response = await fetch(`/api/parts?category_id=${categoryId}`);
        if (!response.ok) throw new Error('Failed to load parts');
        
        const parts = await response.json();
        const container = document.getElementById('parts-list');
        
        const categoryResponse = await fetch(`/api/categories/${categoryId}`);
        const category = await categoryResponse.json();
        document.getElementById('parts-title').textContent = `Детали: ${category.name_ru}`;
        
        if (parts.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Нет деталей в этой категории</div>';
            return;
        }
        
        container.innerHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Название (RU)</th>
                        <th>HE / EN</th>
                        <th style="width: 120px;">Чек-лист</th>
                        <th style="width: 100px;">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${parts.map(part => `
                        <tr>
                            <td><strong>${part.name_ru}</strong></td>
                            <td>
                                ${part.name_he ? `<small class="d-block">${part.name_he}</small>` : ''}
                                ${part.name_en ? `<small class="d-block text-muted">${part.name_en}</small>` : ''}
                            </td>
                            <td>
                                ${part.is_common ? '<span class="badge bg-success">Да</span>' : '<span class="badge bg-secondary">Нет</span>'}
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary" onclick="editPart(${part.id})" title="Редактировать">✏️</button>
                                    <button class="btn btn-outline-danger" onclick="deletePart(${part.id})" title="Удалить">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
    } catch (error) {
        console.error('Error loading parts:', error);
        showError('Ошибка загрузки деталей');
    }
}

function showCategoryModal() {
    document.getElementById('categoryForm').reset();
    document.getElementById('category-id').value = '';
    document.getElementById('categoryModalTitle').textContent = 'Добавить категорию';
    categoryModal.show();
}

async function editCategory(id) {
    try {
        const response = await fetch(`/api/categories/${id}`);
        if (!response.ok) throw new Error('Failed to load category');
        
        const category = await response.json();
        
        document.getElementById('category-id').value = category.id;
        document.getElementById('category-icon').value = category.icon || '';
        document.getElementById('category-name-ru').value = category.name_ru || '';
        document.getElementById('category-name-he').value = category.name_he || '';
        document.getElementById('category-name-en').value = category.name_en || '';
        document.getElementById('category-sort').value = category.sort_order || 0;
        
        document.getElementById('categoryModalTitle').textContent = 'Редактировать категорию';
        categoryModal.show();
        
    } catch (error) {
        console.error('Error loading category:', error);
        showError('Ошибка загрузки категории');
    }
}

async function saveCategory() {
    const id = document.getElementById('category-id').value;
    const data = {
        icon: document.getElementById('category-icon').value || '🔧',
        name_ru: document.getElementById('category-name-ru').value,
        name_he: document.getElementById('category-name-he').value,
        name_en: document.getElementById('category-name-en').value,
        sort_order: parseInt(document.getElementById('category-sort').value) || 0
    };
    
    if (!data.name_ru) {
        showError('Название (RU) обязательно');
        return;
    }
    
    try {
        const url = id ? `/api/categories/${id}` : '/api/categories';
        const method = id ? 'PATCH' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save category');
        }
        
        categoryModal.hide();
        showSuccess(id ? 'Категория обновлена' : 'Категория создана');
        await loadCategories();
        
    } catch (error) {
        console.error('Error saving category:', error);
        showError(error.message);
    }
}

async function deleteCategory(id) {
    if (!confirm('Удалить категорию? Все связанные детали также будут удалены.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/categories/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete category');
        }
        
        showSuccess('Категория удалена');
        
        if (selectedCategoryId === id) {
            selectedCategoryId = null;
            document.getElementById('parts-title').textContent = 'Выберите категорию';
            document.getElementById('parts-list').innerHTML = '<div class="alert alert-info">Выберите категорию для просмотра деталей</div>';
            document.getElementById('add-part-btn').disabled = true;
        }
        
        await loadCategories();
        
    } catch (error) {
        console.error('Error deleting category:', error);
        showError(error.message);
    }
}

function showPartModal() {
    if (!selectedCategoryId) {
        showError('Сначала выберите категорию');
        return;
    }
    
    document.getElementById('partForm').reset();
    document.getElementById('part-id').value = '';
    document.getElementById('part-category-id').value = selectedCategoryId;
    document.getElementById('part-is-common').checked = true;
    document.getElementById('partModalTitle').textContent = 'Добавить деталь';
    partModal.show();
}

async function editPart(id) {
    try {
        const response = await fetch(`/api/parts/${id}`);
        if (!response.ok) throw new Error('Failed to load part');
        
        const part = await response.json();
        
        document.getElementById('part-id').value = part.id;
        document.getElementById('part-category-id').value = part.category_id;
        document.getElementById('part-name-ru').value = part.name_ru || '';
        document.getElementById('part-name-he').value = part.name_he || '';
        document.getElementById('part-name-en').value = part.name_en || '';
        document.getElementById('part-is-common').checked = part.is_common;
        document.getElementById('part-sort').value = part.sort_order || 0;
        
        document.getElementById('partModalTitle').textContent = 'Редактировать деталь';
        partModal.show();
        
    } catch (error) {
        console.error('Error loading part:', error);
        showError('Ошибка загрузки детали');
    }
}

async function savePart() {
    const id = document.getElementById('part-id').value;
    const data = {
        category_id: parseInt(document.getElementById('part-category-id').value),
        name_ru: document.getElementById('part-name-ru').value,
        name_he: document.getElementById('part-name-he').value,
        name_en: document.getElementById('part-name-en').value,
        is_common: document.getElementById('part-is-common').checked,
        sort_order: parseInt(document.getElementById('part-sort').value) || 0
    };
    
    if (!data.name_ru) {
        showError('Название (RU) обязательно');
        return;
    }
    
    try {
        const url = id ? `/api/parts/${id}` : '/api/parts';
        const method = id ? 'PATCH' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save part');
        }
        
        partModal.hide();
        showSuccess(id ? 'Деталь обновлена' : 'Деталь создана');
        await loadParts(selectedCategoryId);
        
    } catch (error) {
        console.error('Error saving part:', error);
        showError(error.message);
    }
}

async function deletePart(id) {
    if (!confirm('Удалить деталь?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/parts/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete part');
        }
        
        showSuccess('Деталь удалена');
        await loadParts(selectedCategoryId);
        
    } catch (error) {
        console.error('Error deleting part:', error);
        showError(error.message);
    }
}

function showError(message) {
    alert('❌ ' + message);
}

function showSuccess(message) {
    alert('✅ ' + message);
}
