let currentCategoryId = null;
let categoryModal = null;
let partModal = null;

document.addEventListener('DOMContentLoaded', () => {
    categoryModal = new bootstrap.Modal(document.getElementById('categoryModal'));
    partModal = new bootstrap.Modal(document.getElementById('partModal'));
    loadCategories();
});

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        
        const listContainer = document.getElementById('categories-list');
        
        if (categories.length === 0) {
            listContainer.innerHTML = '<p class="text-muted text-center">Категорий пока нет</p>';
            return;
        }
        
        listContainer.innerHTML = categories.map(cat => `
            <div class="list-group-item list-group-item-action" 
                 onclick="selectCategory(${cat.id})"
                 style="cursor: pointer;">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span style="font-size: 1.2em;">${cat.icon}</span>
                        <strong>${cat.name_ru}</strong>
                        <span class="badge bg-secondary">${cat.parts_count}</span>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showEditCategoryModal(${cat.id})">
                            ✏️
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); deleteCategory(${cat.id})">
                            🗑️
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
        alert('Ошибка загрузки категорий');
    }
}

async function selectCategory(categoryId) {
    currentCategoryId = categoryId;
    
    const items = document.querySelectorAll('#categories-list .list-group-item');
    items.forEach(item => item.classList.remove('active'));
    event.currentTarget.classList.add('active');
    
    await loadParts(categoryId);
    
    document.getElementById('add-part-btn').style.display = 'block';
}

async function loadParts(categoryId) {
    try {
        const [categoryResponse, partsResponse] = await Promise.all([
            fetch(`/api/categories/${categoryId}`),
            fetch(`/api/parts?category_id=${categoryId}`)
        ]);
        
        const category = await categoryResponse.json();
        const parts = await partsResponse.json();
        
        document.getElementById('parts-title').textContent = `${category.icon} ${category.name_ru}`;
        
        const partsContainer = document.getElementById('parts-list');
        
        if (parts.length === 0) {
            partsContainer.innerHTML = '<p class="text-muted">Деталей в этой категории пока нет</p>';
            return;
        }
        
        partsContainer.innerHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Название (RU)</th>
                        <th>עברית</th>
                        <th>English</th>
                        <th>Часто используемая</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    ${parts.map(part => `
                        <tr>
                            <td><strong>${part.name_ru}</strong></td>
                            <td dir="rtl">${part.name_he || '-'}</td>
                            <td>${part.name_en || '-'}</td>
                            <td>${part.is_common ? '✅' : '❌'}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="showEditPartModal(${part.id})">
                                    ✏️
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deletePart(${part.id})">
                                    🗑️
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading parts:', error);
        alert('Ошибка загрузки деталей');
    }
}

function showCreateCategoryModal() {
    document.getElementById('categoryModalTitle').textContent = 'Создать категорию';
    document.getElementById('category-id').value = '';
    document.getElementById('category-name-ru').value = '';
    document.getElementById('category-name-he').value = '';
    document.getElementById('category-name-en').value = '';
    document.getElementById('category-icon').value = '';
    categoryModal.show();
}

async function showEditCategoryModal(categoryId) {
    try {
        const response = await fetch(`/api/categories/${categoryId}`);
        const category = await response.json();
        
        document.getElementById('categoryModalTitle').textContent = 'Редактировать категорию';
        document.getElementById('category-id').value = category.id;
        document.getElementById('category-name-ru').value = category.name_ru;
        document.getElementById('category-name-he').value = category.name_he || '';
        document.getElementById('category-name-en').value = category.name_en || '';
        document.getElementById('category-icon').value = category.icon;
        
        categoryModal.show();
    } catch (error) {
        console.error('Error loading category:', error);
        alert('Ошибка загрузки категории');
    }
}

async function saveCategory() {
    const categoryId = document.getElementById('category-id').value;
    const nameRu = document.getElementById('category-name-ru').value.trim();
    
    if (!nameRu) {
        alert('Название (Русский) обязательно');
        return;
    }
    
    const data = {
        name_ru: nameRu,
        name_he: document.getElementById('category-name-he').value.trim() || null,
        name_en: document.getElementById('category-name-en').value.trim() || null,
        icon: document.getElementById('category-icon').value.trim() || '🔧'
    };
    
    try {
        let response;
        if (categoryId) {
            response = await fetch(`/api/categories/${categoryId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch('/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
        
        if (response.ok) {
            categoryModal.hide();
            await loadCategories();
            if (categoryId && currentCategoryId == categoryId) {
                await loadParts(categoryId);
            }
        } else {
            const error = await response.json();
            alert(error.error || 'Ошибка сохранения категории');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        alert('Ошибка сохранения категории');
    }
}

async function deleteCategory(categoryId) {
    if (!confirm('Вы уверены, что хотите удалить эту категорию? Все детали в ней также будут удалены.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            if (currentCategoryId === categoryId) {
                currentCategoryId = null;
                document.getElementById('parts-title').textContent = 'Выберите категорию';
                document.getElementById('parts-list').innerHTML = '<p class="text-muted">Выберите категорию слева для просмотра деталей</p>';
                document.getElementById('add-part-btn').style.display = 'none';
            }
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.error || 'Ошибка удаления категории');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('Ошибка удаления категории');
    }
}

function showCreatePartModal() {
    if (!currentCategoryId) {
        alert('Сначала выберите категорию');
        return;
    }
    
    document.getElementById('partModalTitle').textContent = 'Создать деталь';
    document.getElementById('part-id').value = '';
    document.getElementById('part-category-id').value = currentCategoryId;
    document.getElementById('part-name-ru').value = '';
    document.getElementById('part-name-he').value = '';
    document.getElementById('part-name-en').value = '';
    document.getElementById('part-is-common').checked = true;
    
    partModal.show();
}

async function showEditPartModal(partId) {
    try {
        const response = await fetch(`/api/parts?category_id=${currentCategoryId}`);
        const parts = await response.json();
        const part = parts.find(p => p.id === partId);
        
        if (!part) {
            alert('Деталь не найдена');
            return;
        }
        
        document.getElementById('partModalTitle').textContent = 'Редактировать деталь';
        document.getElementById('part-id').value = part.id;
        document.getElementById('part-category-id').value = part.category_id;
        document.getElementById('part-name-ru').value = part.name_ru;
        document.getElementById('part-name-he').value = part.name_he || '';
        document.getElementById('part-name-en').value = part.name_en || '';
        document.getElementById('part-is-common').checked = part.is_common;
        
        partModal.show();
    } catch (error) {
        console.error('Error loading part:', error);
        alert('Ошибка загрузки детали');
    }
}

async function savePart() {
    const partId = document.getElementById('part-id').value;
    const nameRu = document.getElementById('part-name-ru').value.trim();
    const categoryId = document.getElementById('part-category-id').value;
    
    if (!nameRu) {
        alert('Название (Русский) обязательно');
        return;
    }
    
    const data = {
        category_id: parseInt(categoryId),
        name_ru: nameRu,
        name_he: document.getElementById('part-name-he').value.trim() || null,
        name_en: document.getElementById('part-name-en').value.trim() || null,
        is_common: document.getElementById('part-is-common').checked
    };
    
    try {
        let response;
        if (partId) {
            response = await fetch(`/api/parts/${partId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch('/api/parts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
        
        if (response.ok) {
            partModal.hide();
            await loadParts(currentCategoryId);
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.error || 'Ошибка сохранения детали');
        }
    } catch (error) {
        console.error('Error saving part:', error);
        alert('Ошибка сохранения детали');
    }
}

async function deletePart(partId) {
    if (!confirm('Вы уверены, что хотите удалить эту деталь?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/parts/${partId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadParts(currentCategoryId);
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.error || 'Ошибка удаления детали');
        }
    } catch (error) {
        console.error('Error deleting part:', error);
        alert('Ошибка удаления детали');
    }
}
