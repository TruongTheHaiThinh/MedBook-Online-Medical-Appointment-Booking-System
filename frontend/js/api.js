// Centralized API handler to inject JWT automatically
const api = {
    _headers: function() {
        const headers = {
            'Content-Type': 'application/json'
        };
        const token = localStorage.getItem('medbook_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    },

    _handleResponse: async function(response) {
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('medbook_token');
            localStorage.removeItem('medbook_user');
            // Redirect to index only if not already on index
            if (!window.location.pathname.endsWith('index.html') && window.location.pathname !== '/') {
                window.location.href = '../index.html';
            }
            throw new Error('Phiên đăng nhập đã hết hạn');
        }

        const data = await response.json().catch(() => null);
        
        if (!response.ok) {
            let errorMsg = 'Có lỗi xảy ra từ máy chủ';
            if (data && data.detail) {
                if (typeof data.detail === 'string') errorMsg = data.detail;
                else if (Array.isArray(data.detail)) errorMsg = data.detail[0].msg;
            }
            throw new Error(errorMsg);
        }
        return data;
    },

    get: async function(endpoint) {
        const res = await fetch(`${CONFIG.API_URL}${endpoint}`, {
            method: 'GET',
            headers: this._headers()
        });
        return this._handleResponse(res);
    },

    post: async function(endpoint, body) {
        const res = await fetch(`${CONFIG.API_URL}${endpoint}`, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(body)
        });
        return this._handleResponse(res);
    },

    patch: async function(endpoint, body) {
        const res = await fetch(`${CONFIG.API_URL}${endpoint}`, {
            method: 'PATCH',
            headers: this._headers(),
            body: JSON.stringify(body)
        });
        return this._handleResponse(res);
    },

    put: async function(endpoint, body) {
        const res = await fetch(`${CONFIG.API_URL}${endpoint}`, {
            method: 'PUT',
            headers: this._headers(),
            body: JSON.stringify(body)
        });
        return this._handleResponse(res);
    },

    delete: async function(endpoint) {
        const res = await fetch(`${CONFIG.API_URL}${endpoint}`, {
            method: 'DELETE',
            headers: this._headers()
        });
        if (!res.ok) return this._handleResponse(res);
        return true; // 204 No Content typically doesn't have JSON body
    }
};
const showToast = (message, type = 'success') => {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';
    if (type === 'info') icon = 'fa-info-circle';

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <div class="toast-content">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};
