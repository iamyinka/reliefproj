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

// Application Management - DISABLED (replaced by page-specific implementation)
class ApplicationManagerOld {
    constructor() {
        this.applications = [];
        this.currentFilter = 'all';
        this.currentSort = 'date';
        // Disabled to use real backend implementation
        // this.init();
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
    
    async loadApplications() {
        try {
            const response = await fetch('/api/applications/list/');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            const applications = Array.isArray(data) ? data : data.results || [];
            
            // Transform API data to match expected format
            this.applications = applications.map(app => ({
                id: app.id,
                name: `${app.first_name} ${app.last_name}`,
                package: this.getPackageName(app.selected_package),
                status: app.status.toLowerCase(),
                date: app.created_at.split('T')[0],
                familySize: app.family_size,
                priority: app.employment_status === 'unemployed' ? 'emergency' : 'normal'
            }));
            
            this.renderApplications();
            console.log(`Loaded ${this.applications.length} applications from API`);
            
        } catch (error) {
            console.error('Error loading applications:', error);
            this.applications = [];
            this.renderApplications();
        }
    }
    
    getPackageName(packageType) {
        const packageNames = {
            'small_basic': 'Small Family Basic',
            'medium_basic': 'Medium Family Basic',
            'large_basic': 'Large Family Basic',
            'emergency': 'Emergency Relief',
            'senior': 'Senior Citizen Special'
        };
        return packageNames[packageType] || packageType;
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
    
    async loadPackages() {
        try {
            const response = await fetch('/api/packages/manage/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) {
                throw new Error('Failed to load packages');
            }
            
            const data = await response.json();
            
            // Handle different response structures
            let packages = [];
            if (Array.isArray(data)) {
                packages = data;
            } else if (data.results && Array.isArray(data.results)) {
                // Paginated response
                packages = data.results;
            } else if (data.packages && Array.isArray(data.packages)) {
                packages = data.packages;
            } else {
                console.warn('Unexpected API response structure:', data);
                showNotification('No package data available', 'warning');
                this.packages = [];
                this.renderPackages();
                return;
            }
            
            this.packages = packages.map(pkg => ({
                id: pkg.id,
                name: pkg.name,
                items: this.formatPackageItems(pkg.package_items || []),
                cashAmount: pkg.cash_amount || 0,
                stock: pkg.available_quantity || 0,
                totalQuantity: pkg.total_quantity || 0,
                lowStockThreshold: 10, // Default threshold
                packageType: pkg.package_type,
                isActive: pkg.is_active,
                isAvailable: pkg.is_available,
                isLowStock: pkg.is_low_stock,
                description: pkg.description || ''
            }));
            
            this.renderPackages();
            this.updateStatistics();
        } catch (error) {
            console.error('Error loading packages:', error);
            showNotification('Error loading packages. Using fallback display.', 'warning');
            
            // Fallback to empty array
            this.packages = [];
            this.renderPackages();
        }
    }
    
    formatPackageItems(packageItems) {
        if (!packageItems || packageItems.length === 0) {
            return 'No items specified';
        }
        
        return packageItems
            .sort((a, b) => (a.order || 0) - (b.order || 0))
            .map(item => item.item_name)
            .join(', ');
    }
    
    updateStatistics() {
        const activePackages = this.packages.filter(pkg => pkg.isActive).length;
        const totalStock = this.packages.reduce((sum, pkg) => sum + pkg.stock, 0);
        const lowStockCount = this.packages.filter(pkg => pkg.isLowStock).length;
        const outOfStockCount = this.packages.filter(pkg => pkg.stock === 0).length;
        
        // Update statistics cards if they exist
        this.updateStatCard('.stat-card.primary .stat-number', activePackages);
        this.updateStatCard('.stat-card.success .stat-number', totalStock);
        this.updateStatCard('.stat-card.warning .stat-number', lowStockCount);
        this.updateStatCard('.stat-card.info .stat-number', outOfStockCount);
    }
    
    updateStatCard(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
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
        } else if (pkg.isLowStock) {
            stockClass = 'low-stock';
            stockBadge = 'Low Stock';
            badgeClass = 'bg-warning';
        }
        
        // Add inactive badge if not active
        const inactiveClass = !pkg.isActive ? ' inactive-package' : '';
        const statusBadges = [];
        
        if (!pkg.isActive) {
            statusBadges.push('<span class="badge bg-secondary ms-1">Inactive</span>');
        }
        if (!pkg.isAvailable) {
            statusBadges.push('<span class="badge bg-warning ms-1">Unavailable</span>');
        }
        
        return `
            <div class="package-item ${stockClass}${inactiveClass}">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 class="mb-1">
                            ${pkg.name}
                            ${statusBadges.join('')}
                        </h6>
                        <small class="text-muted">ID: ${pkg.id} • ${pkg.packageType}</small>
                    </div>
                    <span class="badge ${badgeClass}">${stockBadge}</span>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-8">
                        <strong>Items:</strong><br>
                        <small class="text-wrap">${pkg.items}</small><br><br>
                        <strong>Cash Support:</strong> ₦${pkg.cashAmount.toLocaleString()}
                        ${pkg.description ? `<br><small class="text-muted">${pkg.description}</small>` : ''}
                    </div>
                    <div class="col-md-4 text-md-end">
                        <div class="h4 mb-1">${pkg.stock}</div>
                        <small class="text-muted">Available</small>
                        ${pkg.totalQuantity ? `<br><small class="text-muted">of ${pkg.totalQuantity} total</small>` : ''}
                    </div>
                </div>
                
                <div class="btn-group w-100">
                    <button class="btn btn-outline-primary update-stock-btn" data-package-id="${pkg.id}" 
                            onclick="showStockUpdateModal(${pkg.id}, ${pkg.stock})">
                        Restock
                    </button>
                    <button class="btn btn-outline-info" onclick="viewPackageDetails(${pkg.id})">
                        View Details
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
    
    async updateStock(packageId, newQuantity) {
        try {
            const response = await fetch(`/api/packages/${packageId}/restock/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ quantity: newQuantity })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showNotification(result.message || 'Stock updated successfully!', 'success');
                // Reload packages to get updated data
                this.loadPackages();
            } else {
                throw new Error(result.message || 'Failed to update stock');
            }
        } catch (error) {
            console.error('Error updating stock:', error);
            showNotification('Error updating stock: ' + error.message, 'danger');
        }
    }
    
    getCSRFToken() {
        // First try to get from meta tag (most reliable)
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // Fallback: try to get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Final fallback: try Django's default CSRF input
        const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        console.warn('CSRF token not found');
        return '';
    }
    
    editPackage(packageId) {
        showNotification('Edit package functionality coming soon!', 'info');
    }
    
    async deletePackage(packageId) {
        if (!confirm('Are you sure you want to delete this package? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/packages/manage/${packageId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                showNotification('Package deleted successfully!', 'success');
                // Reload packages to get updated data
                this.loadPackages();
            } else {
                const result = await response.json().catch(() => ({}));
                throw new Error(result.detail || 'Failed to delete package');
            }
        } catch (error) {
            console.error('Error deleting package:', error);
            showNotification('Error deleting package: ' + error.message, 'danger');
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
                // Generate a realistic test QR code or fetch from real scan
                const testCode = `RELIEF-APP-QR${Date.now()}`;
                this.processScannedCode(testCode);
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
        // This function is deprecated - the new ReliefQRScanner handles all QR processing
        console.warn('Old QRScanner.processScannedCode called - this should not happen');
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
        // ApplicationManager is now initialized in the specific page template
        // window.applicationManager = new ApplicationManager();
    }
    
    if (currentPage === 'packages' || document.getElementById('packagesContainer')) {
        window.packageManager = new PackageManager();
    }
    
    if (currentPage === 'scanner' || document.querySelector('.scanner-container')) {
        // Old QRScanner disabled - using new ReliefQRScanner instead
        console.log('Scanner page detected - ReliefQRScanner will be initialized from scanner.html');
    }
    
    // Charts are now initialized in individual page templates to avoid conflicts
    // No longer initializing charts globally from supervisor.js
});

// Chart initialization moved to individual page templates to prevent conflicts