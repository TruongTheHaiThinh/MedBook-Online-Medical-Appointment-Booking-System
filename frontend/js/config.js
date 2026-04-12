// Base API Configuration
const CONFIG = {
    // Modify this if backend runs on a different port/IP
    API_URL: 'http://localhost:8000',
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
