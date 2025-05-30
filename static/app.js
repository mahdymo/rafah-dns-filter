/**
 * DNS Filter Dashboard JavaScript
 * Main application logic for the web dashboard
 */

// Global variables
let charts = {};
let toastContainer;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    setupToastContainer();
    setupEventListeners();
    initializeFeatherIcons();
}

/**
 * Setup toast notification container
 */
function setupToastContainer() {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Handle Enter key in quick action inputs
    const quickBlockInput = document.getElementById('quickBlockDomain');
    if (quickBlockInput) {
        quickBlockInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                quickBlockDomain();
            }
        });
    }

    const quickUnblockInput = document.getElementById('quickUnblockDomain');
    if (quickUnblockInput) {
        quickUnblockInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                quickUnblockDomain();
            }
        });
    }

    const domainInput = document.getElementById('domainInput');
    if (domainInput) {
        domainInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                blockDomain();
            }
        });
    }

    // Auto-refresh dashboard every 30 seconds
    setInterval(refreshDashboardData, 30000);
}

/**
 * Initialize Feather icons
 */
function initializeFeatherIcons() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

/**
 * Initialize charts with provided data
 */
function initializeCharts(hourlyStats, stats) {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded');
        return;
    }

    initializeQueryChart(hourlyStats);
    initializePieChart(stats);
}

/**
 * Initialize the query activity chart
 */
function initializeQueryChart(hourlyStats) {
    const ctx = document.getElementById('queryChart');
    if (!ctx) return;

    const labels = hourlyStats.map(stat => stat.hour);
    const totalData = hourlyStats.map(stat => stat.total);
    const blockedData = hourlyStats.map(stat => stat.blocked);
    const allowedData = hourlyStats.map(stat => stat.allowed);

    charts.queryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Queries',
                    data: totalData,
                    borderColor: 'rgb(74, 144, 226)',
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Blocked',
                    data: blockedData,
                    borderColor: 'rgb(220, 53, 69)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Allowed',
                    data: allowedData,
                    borderColor: 'rgb(40, 167, 69)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Initialize the pie chart for query distribution
 */
function initializePieChart(stats) {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;

    const allowedQueries = stats.total_queries - stats.blocked_queries;
    
    charts.pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Allowed', 'Blocked', 'Cached'],
            datasets: [{
                data: [allowedQueries, stats.blocked_queries, stats.cached_queries],
                backgroundColor: [
                    'rgb(40, 167, 69)',
                    'rgb(220, 53, 69)',
                    'rgb(23, 162, 184)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: false
                }
            }
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info'
    };

    const backgroundMap = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    };

    const toast = document.createElement('div');
    toast.className = `toast fade-in ${backgroundMap[type]} text-white`;
    toast.id = toastId;
    toast.innerHTML = `
        <div class="toast-header">
            <i data-feather="${iconMap[type]}" class="me-2"></i>
            <strong class="me-auto">DNS Filter</strong>
            <button type="button" class="btn-close btn-close-white" onclick="closeToast('${toastId}')"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    toastContainer.appendChild(toast);
    
    // Initialize Feather icons in the new toast
    feather.replace();

    // Auto-remove toast after duration
    setTimeout(() => {
        closeToast(toastId);
    }, duration);
}

/**
 * Close toast notification
 */
function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

/**
 * Block a domain
 */
function blockDomain(domain) {
    const domainToBlock = domain || document.getElementById('domainInput')?.value?.trim();
    
    if (!domainToBlock) {
        showToast('Please enter a domain name', 'warning');
        return;
    }

    if (!isValidDomain(domainToBlock)) {
        showToast('Please enter a valid domain name', 'warning');
        return;
    }

    fetch('/api/domain/block', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain: domainToBlock })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            
            // Clear input if it exists
            const input = document.getElementById('domainInput');
            if (input) input.value = '';
            
            // Close modal if open
            const modal = document.getElementById('quickActionModal');
            if (modal) {
                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                if (bootstrapModal) bootstrapModal.hide();
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error blocking domain:', error);
        showToast('Error blocking domain', 'error');
    });
}

/**
 * Unblock a domain
 */
function unblockDomain(domain) {
    const domainToUnblock = domain || document.getElementById('domainInput')?.value?.trim();
    
    if (!domainToUnblock) {
        showToast('Please enter a domain name', 'warning');
        return;
    }

    fetch('/api/domain/unblock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain: domainToUnblock })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            
            // Clear input if it exists
            const input = document.getElementById('domainInput');
            if (input) input.value = '';
            
            // Close modal if open
            const modal = document.getElementById('quickActionModal');
            if (modal) {
                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                if (bootstrapModal) bootstrapModal.hide();
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error unblocking domain:', error);
        showToast('Error unblocking domain', 'error');
    });
}

/**
 * Validate domain name format
 */
function isValidDomain(domain) {
    const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
    return domainRegex.test(domain) && domain.length <= 253;
}

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            updateStatCards(stats);
            
            // Fetch hourly stats
            return fetch('/api/hourly-stats');
        })
        .then(response => response.json())
        .then(hourlyStats => {
            updateCharts(hourlyStats);
        })
        .catch(error => {
            console.error('Error refreshing dashboard data:', error);
        });
}

/**
 * Update statistics cards
 */
function updateStatCards(stats) {
    const elements = {
        totalQueries: document.querySelector('.card.bg-primary h4'),
        blockedQueries: document.querySelector('.card.bg-danger h4'),
        cachedQueries: document.querySelector('.card.bg-success h4'),
        uniqueDomains: document.querySelector('.card.bg-info h4'),
        blockRate: document.querySelector('.card.bg-danger p'),
        cacheRate: document.querySelector('.card.bg-success p'),
        bandwidthSaved: document.getElementById('bandwidthSaved'),
        savingsPercent: document.getElementById('savingsPercent'),
        totalBandwidth: document.getElementById('totalBandwidth')
    };

    if (elements.totalQueries) elements.totalQueries.textContent = stats.total_queries;
    if (elements.blockedQueries) elements.blockedQueries.textContent = stats.blocked_queries;
    if (elements.cachedQueries) elements.cachedQueries.textContent = stats.cached_queries;
    if (elements.uniqueDomains) elements.uniqueDomains.textContent = stats.unique_domains;
    if (elements.blockRate) elements.blockRate.textContent = `Blocked (${stats.block_rate}%)`;
    if (elements.cacheRate) elements.cacheRate.textContent = `Cached (${stats.cache_rate}%)`;
    
    // Update bandwidth statistics
    if (elements.bandwidthSaved) {
        elements.bandwidthSaved.textContent = formatBandwidth(stats.bandwidth_saved);
    }
    if (elements.savingsPercent) {
        elements.savingsPercent.textContent = `${stats.bandwidth_savings_percent}%`;
    }
    if (elements.totalBandwidth) {
        elements.totalBandwidth.textContent = formatBandwidth(stats.estimated_total_bandwidth);
    }
}

/**
 * Update charts with new data
 */
function updateCharts(hourlyStats) {
    if (charts.queryChart) {
        const labels = hourlyStats.map(stat => stat.hour);
        const totalData = hourlyStats.map(stat => stat.total);
        const blockedData = hourlyStats.map(stat => stat.blocked);
        const allowedData = hourlyStats.map(stat => stat.allowed);

        charts.queryChart.data.labels = labels;
        charts.queryChart.data.datasets[0].data = totalData;
        charts.queryChart.data.datasets[1].data = blockedData;
        charts.queryChart.data.datasets[2].data = allowedData;
        charts.queryChart.update('none');
    }
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
}

/**
 * Format bandwidth for display
 */
function formatBandwidth(bytes) {
    if (bytes === 0) return '0 B';
    
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const formattedValue = (bytes / Math.pow(1024, i)).toFixed(2);
    
    return `${formattedValue} ${sizes[i]}`;
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy to clipboard for older browsers
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard', 'success');
    } catch (err) {
        showToast('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show loading state for an element
 */
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border spinner-border-sm me-2';
        spinner.setAttribute('role', 'status');
        element.insertBefore(spinner, element.firstChild);
    }
}

/**
 * Hide loading state for an element
 */
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        const spinner = element.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Get query parameter from URL
 */
function getQueryParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Set query parameter in URL
 */
function setQueryParameter(name, value) {
    const url = new URL(window.location);
    url.searchParams.set(name, value);
    window.history.pushState({}, '', url);
}

// Export functions for global access
window.showToast = showToast;
window.blockDomain = blockDomain;
window.unblockDomain = unblockDomain;
window.copyToClipboard = copyToClipboard;
window.initializeCharts = initializeCharts;
window.refreshDashboardData = refreshDashboardData;
