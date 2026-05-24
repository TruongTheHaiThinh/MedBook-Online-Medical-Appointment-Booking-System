// Base API Configuration
const CONFIG = {
    // Modify this if backend runs on a different port/IP
    API_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:8000'
        : 'https://medbook-backend.onrender.com', // Cấu hình URL Backend Render của bạn tại đây khi deploy
};

// Utils
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN');
}

function formatTime(timeStr) {
    if (!timeStr) return '';
    // timeStr could be "08:30:00"
    return timeStr.substring(0, 5); 
}
