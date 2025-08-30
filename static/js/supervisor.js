// Supervisor Dashboard JavaScript

// Quick Actions
function quickApproveNext() {
    const nextPendingApp = document.querySelector('.application-card .status-pending').closest('.application-card');
    if (nextPendingApp) {
        const appId = nextPendingApp.dataset.applicationId || 'APP-001';
        if (confirm(`Approve application ${appId}?`)) {
            // Simulate approval
            const statusBadge = nextPendingApp.querySelector('.status-pending');
            statusBadge.className = 'application-status status-approved';
            statusBadge.textContent = 'Approved';
            
            // Show success message
            showNotification('Application approved successfully!', 'success');
            
            // Update counters
            updateDashboardCounters();
        }
    } else {
        showNotification('No pending applications to approve', 'info');
    }
}

// Application Management
class ApplicationManager {
    constructor() {
        this.applications = [];
        this.currentFilter = 'all';
        this.currentSort = 'date';
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadApplications();
    }
    
    bindEvents() {
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });
        
        // Sort dropdown
        const sortSelect = document.getElementById('sortApplications');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.setSortOrder(e.target.value);
            });
        }
        
        // Application actions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('approve-btn')) {
                this.approveApplication(e.target.dataset.appId);
            } else if (e.target.classList.contains('reject-btn')) {
                this.rejectApplication(e.target.dataset.appId);
            } else if (e.target.classList.contains('view-btn')) {
                this.viewApplication(e.target.dataset.appId);
            }
        });
    }
    
    loadApplications() {
        // Simulate loading applications
        this.applications = [
            {
                id: 'APP-001',
                name: 'John Doe',
                package: 'Medium Family Basic',
                status: 'pending',
                date: '2024-08-30',
                familySize: 5,
                priority: 'normal'
            },
            {
                id: 'APP-002', 
                name: 'Jane Smith',
                package: 'Small Family Basic',
                status: 'pending',
                date: '2024-08-30',
                familySize: 2,
                priority: 'emergency'
            },
            {
                id: 'APP-003',
                name: 'Michael Johnson',
                package: 'Large Family Basic', 
                status: 'approved',
                date: '2024-08-29',
                familySize: 8,
                priority: 'normal'
            }
        ];
        
        this.renderApplications();
    }
    
    setFilter(filter) {
        this.currentFilter = filter;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        this.renderApplications();
    }
    
    setSortOrder(sortBy) {
        this.currentSort = sortBy;
        this.renderApplications();
    }
    
    renderApplications() {
        const container = document.getElementById('applicationsContainer');
        if (!container) return;
        
        let filteredApps = this.applications.filter(app => {
            if (this.currentFilter === 'all') return true;
            return app.status === this.currentFilter;
        });
        
        // Sort applications
        filteredApps.sort((a, b) => {
            switch (this.currentSort) {
                case 'date':
                    return new Date(b.date) - new Date(a.date);
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'priority':
                    const priorityOrder = { 'emergency': 3, 'normal': 1 };
                    return (priorityOrder[b.priority] || 1) - (priorityOrder[a.priority] || 1);
                default:
                    return 0;
            }
        });
        
        container.innerHTML = filteredApps.map(app => this.renderApplicationCard(app)).join('');
    }
    
    renderApplicationCard(app) {
        const priorityBadge = app.priority === 'emergency' ? 
            '<span class="badge bg-danger ms-2">EMERGENCY</span>' : '';
            
        return `
            <div class="application-card" data-application-id="${app.id}">
                <div class="application-header">
                    <div>
                        <h6 class="mb-1">${app.name} ${priorityBadge}</h6>
                        <small class="text-muted">${app.id} • ${app.date}</small>
                    </div>
                    <div class="btn-group">
                        <button class="action-btn view" data-app-id="${app.id}">View</button>
                        ${app.status === 'pending' ? `
                            <button class="action-btn approve" data-app-id="${app.id}">Approve</button>
                            <button class="action-btn reject" data-app-id="${app.id}">Reject</button>
                        ` : ''}
                    </div>
                </div>
                <div class="application-body">
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Package:</strong> ${app.package}<br>
                            <strong>Family Size:</strong> ${app.familySize} members
                        </div>
                        <div class="col-md-6 text-md-end">
                            <span class="application-status status-${app.status}">${app.status.charAt(0).toUpperCase() + app.status.slice(1)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    approveApplication(appId) {
        if (confirm(`Approve application ${appId}?`)) {
            const app = this.applications.find(a => a.id === appId);
            if (app) {
                app.status = 'approved';
                this.renderApplications();
                showNotification(`Application ${appId} approved successfully!`, 'success');
                updateDashboardCounters();
            }
        }
    }
    
    rejectApplication(appId) {
        const reason = prompt('Please provide a reason for rejection:');
        if (reason && confirm(`Reject application ${appId}?`)) {
            const app = this.applications.find(a => a.id === appId);
            if (app) {
                app.status = 'rejected';
                app.rejectionReason = reason;
                this.renderApplications();
                showNotification(`Application ${appId} rejected.`, 'warning');
                updateDashboardCounters();
            }
        }
    }
    
    viewApplication(appId) {
        // Simulate opening application details modal
        const app = this.applications.find(a => a.id === appId);
        if (app) {
            alert(`Application Details:\n\nID: ${app.id}\nName: ${app.name}\nPackage: ${app.package}\nFamily Size: ${app.familySize}\nStatus: ${app.status}\nDate: ${app.date}`);
        }
    }
}

// Package Management
class PackageManager {
    constructor() {
        this.packages = [];
        this.init();
    }
    
    init() {
        this.loadPackages();
        this.bindEvents();
    }
    
    bindEvents() {
        // Add new package
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-package-btn')) {
                this.showAddPackageForm();
            } else if (e.target.classList.contains('edit-package-btn')) {
                this.editPackage(e.target.dataset.packageId);
            } else if (e.target.classList.contains('delete-package-btn')) {
                this.deletePackage(e.target.dataset.packageId);
            } else if (e.target.classList.contains('update-stock-btn')) {
                this.updateStock(e.target.dataset.packageId);
            }
        });
    }
    
    loadPackages() {
        this.packages = [
            {
                id: 'PKG-001',
                name: 'Small Family Basic',
                items: '5kg Rice, 2kg Beans, 1L Oil, 1kg Salt',
                cashAmount: 5000,
                stock: 25,
                lowStockThreshold: 10,
                familySize: 'small'
            },
            {
                id: 'PKG-002',
                name: 'Medium Family Basic', 
                items: '10kg Rice, 5kg Beans, 2L Oil, 1kg Salt, 1kg Sugar',
                cashAmount: 8000,
                stock: 5,
                lowStockThreshold: 10,
                familySize: 'medium'
            },
            {
                id: 'PKG-003',
                name: 'Large Family Basic',
                items: '25kg Rice, 10kg Beans, 3L Oil, 2kg Salt, 2kg Sugar',
                cashAmount: 15000,
                stock: 0,
                lowStockThreshold: 5,
                familySize: 'large'
            }
        ];
        
        this.renderPackages();
    }
    
    renderPackages() {
        const container = document.getElementById('packagesContainer');
        if (!container) return;
        
        container.innerHTML = this.packages.map(pkg => this.renderPackageCard(pkg)).join('');
    }
    
    renderPackageCard(pkg) {
        let stockClass = 'in-stock';
        let stockBadge = 'In Stock';
        let badgeClass = 'bg-success';
        
        if (pkg.stock === 0) {
            stockClass = 'out-of-stock';
            stockBadge = 'Out of Stock';
            badgeClass = 'bg-danger';
        } else if (pkg.stock <= pkg.lowStockThreshold) {
            stockClass = 'low-stock';
            stockBadge = 'Low Stock';
            badgeClass = 'bg-warning';
        }
        
        return `
            <div class="package-item ${stockClass}">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 class="mb-1">${pkg.name}</h6>
                        <small class="text-muted">${pkg.id}</small>
                    </div>
                    <span class="badge ${badgeClass}">${stockBadge}</span>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-8">
                        <strong>Items:</strong><br>
                        <small>${pkg.items}</small><br>
                        <strong>Cash:</strong> ₦${pkg.cashAmount.toLocaleString()}
                    </div>
                    <div class="col-md-4 text-md-end">
                        <div class="h4 mb-1">${pkg.stock}</div>
                        <small class="text-muted">Available</small>
                    </div>
                </div>
                
                <div class="btn-group w-100">
                    <button class="btn btn-outline-primary update-stock-btn" data-package-id="${pkg.id}">
                        Update Stock
                    </button>
                    <button class="btn btn-outline-secondary edit-package-btn" data-package-id="${pkg.id}">
                        Edit
                    </button>
                    <button class="btn btn-outline-danger delete-package-btn" data-package-id="${pkg.id}">
                        Delete
                    </button>
                </div>
            </div>
        `;
    }
    
    updateStock(packageId) {
        const pkg = this.packages.find(p => p.id === packageId);
        if (pkg) {
            const newStock = prompt(`Current stock: ${pkg.stock}\nEnter new stock quantity:`, pkg.stock);
            if (newStock !== null && !isNaN(newStock)) {
                pkg.stock = parseInt(newStock);
                this.renderPackages();
                showNotification('Stock updated successfully!', 'success');
            }
        }
    }
    
    editPackage(packageId) {
        showNotification('Edit package functionality coming soon!', 'info');
    }
    
    deletePackage(packageId) {
        if (confirm('Are you sure you want to delete this package?')) {
            this.packages = this.packages.filter(p => p.id !== packageId);
            this.renderPackages();
            showNotification('Package deleted successfully!', 'success');
        }
    }
}

// QR Code Scanner Simulation
class QRScanner {
    constructor() {
        this.isScanning = false;
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        const startScanBtn = document.getElementById('startScan');
        const manualEntryBtn = document.getElementById('manualEntry');
        
        if (startScanBtn) {
            startScanBtn.addEventListener('click', () => this.startScanning());
        }
        
        if (manualEntryBtn) {
            manualEntryBtn.addEventListener('click', () => this.showManualEntry());
        }
    }
    
    startScanning() {
        if (this.isScanning) return;
        
        this.isScanning = true;
        const scannerDiv = document.querySelector('.scanner-viewfinder');
        const startBtn = document.getElementById('startScan');
        
        if (scannerDiv && startBtn) {
            scannerDiv.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Scanning...</span></div>';
            startBtn.textContent = 'Scanning...';
            startBtn.disabled = true;
            
            // Simulate scan result after 3 seconds
            setTimeout(() => {
                this.processScannedCode('RELIEF-APP-QR123456789');
            }, 3000);
        }
    }
    
    showManualEntry() {
        const code = prompt('Enter QR code manually:');
        if (code) {
            this.processScannedCode(code);
        }
    }
    
    processScannedCode(code) {
        this.isScanning = false;
        
        // Reset scanner UI
        const scannerDiv = document.querySelector('.scanner-viewfinder');
        const startBtn = document.getElementById('startScan');
        
        if (scannerDiv && startBtn) {
            scannerDiv.innerHTML = '<i class="bi bi-qr-code-scan display-4 text-muted"></i>';
            startBtn.textContent = 'Start Scanning';
            startBtn.disabled = false;
        }
        
        // Simulate lookup
        const mockResult = {
            code: code,
            applicant: 'John Doe',
            package: 'Medium Family Basic',
            status: 'ready_for_pickup',
            reference: 'REF-240830001',
            items: '10kg Rice, 5kg Beans, 2L Oil, ₦8,000 Cash'
        };
        
        this.displayScanResult(mockResult);
    }
    
    displayScanResult(result) {
        const resultDiv = document.getElementById('scanResult');
        if (!resultDiv) return;
        
        resultDiv.innerHTML = `
            <div class="scan-result">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="text-success mb-0">
                        <i class="bi bi-check-circle me-2"></i>Valid QR Code
                    </h5>
                    <span class="badge bg-success">Ready for Pickup</span>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <strong>Applicant:</strong> ${result.applicant}<br>
                        <strong>Reference:</strong> ${result.reference}<br>
                        <strong>Package:</strong> ${result.package}
                    </div>
                    <div class="col-md-6">
                        <strong>Contents:</strong><br>
                        <small>${result.items}</small>
                    </div>
                </div>
                
                <hr>
                
                <div class="text-center">
                    <button class="btn btn-success btn-lg me-2" onclick="confirmPickup('${result.reference}')">
                        <i class="bi bi-check-circle me-2"></i>Confirm Pickup
                    </button>
                    <button class="btn btn-outline-secondary" onclick="clearScanResult()">
                        Scan Another
                    </button>
                </div>
            </div>
        `;
    }
}

// Global Functions
function confirmPickup(reference) {
    if (confirm(`Confirm pickup for ${reference}?`)) {
        showNotification('Pickup confirmed successfully!', 'success');
        clearScanResult();
        updateDashboardCounters();
    }
}

function clearScanResult() {
    const resultDiv = document.getElementById('scanResult');
    if (resultDiv) {
        resultDiv.innerHTML = '';
    }
}

function updateDashboardCounters() {
    // Update various counters throughout the dashboard
    const pendingCount = document.querySelector('.badge.bg-warning');
    if (pendingCount) {
        const current = parseInt(pendingCount.textContent) || 0;
        pendingCount.textContent = Math.max(0, current - 1);
    }
    
    // Update sidebar stats
    const todayPending = document.querySelector('.sidebar .text-primary.fw-bold');
    if (todayPending) {
        const current = parseInt(todayPending.textContent) || 0;
        todayPending.textContent = Math.max(0, current - 1);
    }
    
    const todayPickups = document.querySelector('.sidebar .text-success.fw-bold');
    if (todayPickups) {
        const current = parseInt(todayPickups.textContent) || 0;
        todayPickups.textContent = current + 1;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components based on current page
    const currentPage = document.body.dataset.page;
    
    if (currentPage === 'applications' || document.getElementById('applicationsContainer')) {
        window.applicationManager = new ApplicationManager();
    }
    
    if (currentPage === 'packages' || document.getElementById('packagesContainer')) {
        window.packageManager = new PackageManager();
    }
    
    if (currentPage === 'scanner' || document.querySelector('.scanner-container')) {
        window.qrScanner = new QRScanner();
    }
    
    // Initialize charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
});

// Chart initialization
function initializeCharts() {
    // Applications over time chart
    const applicationsCtx = document.getElementById('applicationsChart');
    if (applicationsCtx) {
        new Chart(applicationsCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Applications',
                    data: [12, 19, 8, 15, 22, 18, 25],
                    borderColor: 'rgb(25, 82, 150)',
                    backgroundColor: 'rgba(25, 82, 150, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Package distribution chart
    const packagesCtx = document.getElementById('packagesChart');
    if (packagesCtx) {
        new Chart(packagesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Small Family', 'Medium Family', 'Large Family', 'Emergency'],
                datasets: [{
                    data: [30, 45, 15, 10],
                    backgroundColor: [
                        'rgb(25, 82, 150)',
                        'rgb(182, 221, 238)', 
                        'rgb(190, 208, 0)',
                        'rgb(161, 218, 248)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}