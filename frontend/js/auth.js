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
    window.location.href = window.location.pathname.includes('/frontend/') 
        ? window.location.pathname.split('/frontend/')[0] + '/frontend/index.html'
        : '/index.html';
}

// Support multiple roles in guard
function guardRoute(requiredRoles) {
    if (!isAuthenticated()) {
        window.location.href = '../index.html';
        return false;
    }
    
    const user = getUser();
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
    
    if (requiredRoles && !roles.includes(user.role)) {
        alert("Bạn không có quyền truy cập trang này!");
        window.location.href = '../index.html';
        return false;
    }
    
    // Auto-update UI with user info
    setTimeout(() => {
        const nameEls = document.querySelectorAll('.user-name-display');
        nameEls.forEach(el => el.textContent = user.full_name);
        
        const roleEls = document.querySelectorAll('.user-role-display');
        const roleLabels = {
            'hr_admin': 'Quản lý nhân sự',
            'cashier_admin': 'Thu ngân',
            'doctor': 'Bác sĩ',
            'patient': 'Bệnh nhân'
        };
        roleEls.forEach(el => el.textContent = roleLabels[user.role] || user.role);
    }, 100);
    
    return true;
}

function initAuthUI() {
    const authContainer = document.getElementById('nav-auth');
    if (!authContainer) return;

    if (isAuthenticated()) {
        const user = getUser();
        if (!user) return;
        
        const roleLabels = {
            'patient': 'BỆNH NHÂN',
            'doctor': 'BÁC SĨ',
            'hr_admin': 'QUẢN LÝ NHÂN SỰ',
            'cashier_admin': 'THU NGÂN'
        };
        authContainer.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="text-right d-none d-md-block" style="line-height: 1.2">
                    <p class="text-sm font-bold mb-0">${user.full_name}</p>
                    <p class="text-xs text-primary mb-0">${roleLabels[user.role] || user.role.toUpperCase()}</p>
                </div>
                <button class="btn btn-primary btn-sm" onclick="goToDashboard()">Dashboard</button>
                <button class="btn btn-outline btn-sm" onclick="logout()">Đăng xuất</button>
            </div>
        `;
    }
}

async function handleLogin(e) {
    if (e) e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const err = document.getElementById('login-error');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Đang xác thực...';
    err.style.display = 'none';

    try {
        const res = await api.post('/auth/login', {
            identifier: document.getElementById('login-email').value,
            password: document.getElementById('login-password').value
        });
        
        localStorage.setItem('medbook_token', res.access_token);
        localStorage.setItem('medbook_user', JSON.stringify(res.user));
        
        // Redirect using main page logic
        if (typeof goToDashboard === 'function') goToDashboard();
        else {
             const user = res.user;
             if (user.role === 'patient') window.location.href = 'patient/dashboard.html';
             else if (user.role === 'doctor') window.location.href = 'doctor/dashboard.html';
             else if (user.role === 'hr_admin') window.location.href = 'admin/hr_dashboard.html';
             else if (user.role === 'cashier_admin') window.location.href = 'admin/cashier_main.html';
        }
        
    } catch (error) {
        err.textContent = error.message;
        err.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function handleRegister(e) {
    if (e) e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const err = document.getElementById('reg-error');
    const originalText = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Đang khởi tạo...';
    err.style.display = 'none';

    try {
        const emailInput = document.getElementById('reg-email');
        await api.post('/auth/register', {
            full_name: document.getElementById('reg-name').value,
            phone: document.getElementById('reg-phone').value,
            password: document.getElementById('reg-password').value,
            role: 'patient', 
            address: 'Chưa cập nhật',
            email: emailInput && emailInput.value ? emailInput.value.trim() : null,
            date_of_birth: document.getElementById('reg-dob') && document.getElementById('reg-dob').value ? new Date(document.getElementById('reg-dob').value).toISOString() : null,
            gender: document.getElementById('reg-gender') ? document.getElementById('reg-gender').value : null,
            blood_type: document.getElementById('reg-blood') ? document.getElementById('reg-blood').value : null
        });
        
        alert("Đăng ký thành công! Bạn có thể đăng nhập ngay.");
        if (typeof toggleAuthForms === 'function') toggleAuthForms();
    } catch (error) {
        err.textContent = error.message;
        err.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function handleForgotPassword(e) {
    if (e) e.preventDefault();
    const btn = document.getElementById('forgot-submit-btn');
    const err = document.getElementById('forgot-error');
    const success = document.getElementById('forgot-success');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Đang gửi...';
    err.style.display = 'none';
    success.style.display = 'none';

    try {
        const res = await api.post('/auth/forgot-password', {
            email: document.getElementById('forgot-email').value
        });
        
        success.textContent = res.message || "Đã gửi link đặt lại mật khẩu thành công!";
        success.style.display = 'flex';
        document.getElementById('forgot-email').value = '';
    } catch (error) {
        err.textContent = error.message;
        err.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}
