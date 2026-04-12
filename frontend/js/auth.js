// Auth State Management
function isAuthenticated() {
    return !!localStorage.getItem('medbook_token');
}

function getUser() {
    const userStr = localStorage.getItem('medbook_user');
    return userStr ? JSON.parse(userStr) : null;
}

function logout() {
    localStorage.removeItem('medbook_token');
    localStorage.removeItem('medbook_user');
    // Redirect to index page
    window.location.href = window.location.pathname.includes('/frontend/') 
        ? window.location.pathname.split('/frontend/')[0] + '/frontend/index.html'
        : '/index.html';
}

// Ensure correct page access based on roles
function guardRoute(requiredRole) {
    if (!isAuthenticated()) {
        window.location.href = '../index.html';
        return false;
    }
    const user = getUser();
    if (requiredRole && user.role !== requiredRole) {
        alert("Bạn không có quyền truy cập trang này!");
        window.location.href = '../index.html';
        return false;
    }
    
    // Auto-update UI with user info
    setTimeout(() => {
        const nameEls = document.querySelectorAll('.user-name-display');
        nameEls.forEach(el => el.textContent = user.full_name);
    }, 100);
    
    return true;
}

// UI Helpers for Index Page
function initAuthUI() {
    const authContainer = document.getElementById('nav-auth');
    if (!authContainer) return;

    if (isAuthenticated()) {
        const user = getUser();
        authContainer.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="text-sm font-bold text-gray"><i class="fa-solid fa-user-circle mr-2"></i>${user.full_name}</span>
                <button class="btn btn-primary btn-sm" onclick="goToDashboard()">Dashboard</button>
                <button class="btn btn-outline btn-sm" onclick="logout()">Đăng xuất</button>
            </div>
        `;
    }
}

function openLoginModal() {
    document.getElementById('auth-modal').style.display = 'flex';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('login-error').style.display = 'none';
}

function openRegisterModal() {
    document.getElementById('auth-modal').style.display = 'flex';
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'block';
    document.getElementById('reg-error').style.display = 'none';
}

function closeAuthModal() {
    document.getElementById('auth-modal').style.display = 'none';
}

function toggleAuthForms() {
    const login = document.getElementById('login-section');
    const register = document.getElementById('register-section');
    if (login.style.display === 'none') {
        login.style.display = 'block';
        register.style.display = 'none';
    } else {
        login.style.display = 'none';
        register.style.display = 'block';
    }
}

// Form Handlers
async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const err = document.getElementById('login-error');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
    err.style.display = 'none';

    try {
        const res = await api.post('/auth/login', {
            identifier: document.getElementById('login-email').value,
            password: document.getElementById('login-password').value
        });
        
        localStorage.setItem('medbook_token', res.access_token);
        localStorage.setItem('medbook_user', JSON.stringify(res.user));
        
        // Redirect
        goToDashboard();
    } catch (error) {
        err.textContent = error.message;
        err.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Đăng Nhập';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const btn = document.getElementById('reg-btn');
    const err = document.getElementById('reg-error');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
    err.style.display = 'none';

    try {
        const emailVal = document.getElementById('reg-email').value;
        await api.post('/auth/register', {
            email: emailVal || null,
            password: document.getElementById('reg-password').value,
            full_name: document.getElementById('reg-name').value,
            phone: document.getElementById('reg-phone').value,
            address: document.getElementById('reg-address').value,
            role: document.getElementById('reg-role').value
        });
        
        alert("Đăng ký thành công! Vui lòng đăng nhập.");
        toggleAuthForms(); // Switch to login
    } catch (error) {
        err.textContent = error.message;
        err.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Tạo Tài Khoản';
    }
}
