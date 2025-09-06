// Community Relief - Main JavaScript

// Multi-step form functionality
class MultiStepForm {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (!this.form) return;
        
        this.steps = this.form.querySelectorAll('.form-step');
        this.currentStep = 0;
        this.nextBtn = this.form.querySelector('.next-btn');
        this.prevBtn = this.form.querySelector('.prev-btn');
        this.submitBtn = this.form.querySelector('.submit-btn');
        
        this.init();
    }
    
    init() {
        this.showStep(0);
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextStep());
        }
        
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevStep());
        }
        
        // Form validation on step change
        this.form.addEventListener('input', (e) => this.validateCurrentStep());
    }
    
    showStep(stepIndex) {
        // Hide all steps
        this.steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
        });
        
        // Update step indicators
        const stepIndicators = document.querySelectorAll('.step');
        stepIndicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === stepIndex);
            indicator.classList.toggle('completed', index < stepIndex);
        });
        
        // Update buttons
        if (this.prevBtn) {
            this.prevBtn.style.display = stepIndex === 0 ? 'none' : 'inline-block';
        }
        
        if (this.nextBtn && this.submitBtn) {
            if (stepIndex === this.steps.length - 1) {
                this.nextBtn.style.display = 'none';
                this.submitBtn.style.display = 'inline-block';
            } else {
                this.nextBtn.style.display = 'inline-block';
                this.submitBtn.style.display = 'none';
            }
        }
        
        this.currentStep = stepIndex;
        this.validateCurrentStep();
    }
    
    nextStep() {
        if (this.validateCurrentStep() && this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        }
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    validateCurrentStep() {
        const currentStepElement = this.steps[this.currentStep];
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;
        
        // Track radio button groups to avoid duplicate validation
        const radioGroups = new Set();
        
        requiredFields.forEach(field => {
            if (field.type === 'radio') {
                // Handle radio button groups
                if (!radioGroups.has(field.name)) {
                    radioGroups.add(field.name);
                    const radioGroup = currentStepElement.querySelectorAll(`input[name="${field.name}"]`);
                    const isRadioGroupValid = Array.from(radioGroup).some(radio => radio.checked);
                    
                    radioGroup.forEach(radio => {
                        if (isRadioGroupValid) {
                            radio.classList.remove('is-invalid');
                            // Remove invalid class from parent as well
                            radio.closest('.form-check')?.classList.remove('is-invalid');
                        } else {
                            radio.classList.add('is-invalid');
                            // Add invalid class to parent for visual feedback
                            radio.closest('.form-check')?.classList.add('is-invalid');
                            isValid = false;
                        }
                    });
                }
            } else {
                // Handle other field types
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            }
        });
        
        // Enable/disable next button
        if (this.nextBtn) {
            this.nextBtn.disabled = !isValid;
        }
        
        return isValid;
    }
}

// Package filtering functionality
class PackageFilter {
    constructor() {
        this.filterForm = document.querySelector('.filter-form');
        this.packageContainer = document.querySelector('.packages-container');
        
        if (this.filterForm && this.packageContainer) {
            this.init();
        }
    }
    
    init() {
        const filterInputs = this.filterForm.querySelectorAll('input, select');
        
        filterInputs.forEach(input => {
            input.addEventListener('change', () => this.applyFilters());
        });
        
        // Search input with debounce
        const searchInput = this.filterForm.querySelector('input[type="search"]');
        if (searchInput) {
            let timeout;
            searchInput.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => this.applyFilters(), 300);
            });
        }
    }
    
    applyFilters() {
        const formData = new FormData(this.filterForm);
        const filters = Object.fromEntries(formData.entries());
        
        const packages = this.packageContainer.querySelectorAll('.package-card');
        
        packages.forEach(packageCard => {
            let shouldShow = true;
            
            // Apply search filter
            if (filters.search) {
                const title = packageCard.querySelector('.card-title').textContent.toLowerCase();
                const description = packageCard.querySelector('.card-text').textContent.toLowerCase();
                const searchTerm = filters.search.toLowerCase();
                
                if (!title.includes(searchTerm) && !description.includes(searchTerm)) {
                    shouldShow = false;
                }
            }
            
            // Apply family size filter
            if (filters.family_size && filters.family_size !== 'all') {
                const packageFamilySize = packageCard.dataset.familySize;
                if (packageFamilySize !== filters.family_size) {
                    shouldShow = false;
                }
            }
            
            // Apply availability filter
            if (filters.availability && filters.availability !== 'all') {
                const isAvailable = packageCard.dataset.available === 'true';
                if (filters.availability === 'available' && !isAvailable) {
                    shouldShow = false;
                } else if (filters.availability === 'unavailable' && isAvailable) {
                    shouldShow = false;
                }
            }
            
            // Show/hide package with animation
            if (shouldShow) {
                packageCard.style.display = 'block';
                packageCard.classList.add('fade-in');
            } else {
                packageCard.style.display = 'none';
                packageCard.classList.remove('fade-in');
            }
        });
        
        // Show no results message
        const visiblePackages = Array.from(packages).filter(p => p.style.display !== 'none');
        this.toggleNoResults(visiblePackages.length === 0);
    }
    
    toggleNoResults(show) {
        let noResultsMsg = this.packageContainer.querySelector('.no-results');
        
        if (show && !noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.className = 'no-results text-center py-5';
            noResultsMsg.innerHTML = `
                <div class="mb-3">
                    <i class="bi bi-search display-4 text-muted"></i>
                </div>
                <h4 class="text-muted">No packages found</h4>
                <p class="text-muted">Try adjusting your search criteria</p>
            `;
            this.packageContainer.appendChild(noResultsMsg);
        } else if (!show && noResultsMsg) {
            noResultsMsg.remove();
        }
    }
}

// Status checking functionality - DISABLED (replaced by page-specific implementation)
class StatusCheckerOld {
    constructor() {
        this.statusForm = document.querySelector('#status-form');
        this.statusResult = document.querySelector('#status-result');
        
        // Disabled to prevent conflicts with new implementation
        // if (this.statusForm && this.statusResult) {
        //     this.init();
        // }
    }
    
    init() {
        this.statusForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.checkStatus();
        });
    }
    
    async checkStatus() {
        const formData = new FormData(this.statusForm);
        const phone = formData.get('phone');
        const reference = formData.get('reference');
        
        // Show loading state
        this.statusResult.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Checking your application status...</p>
            </div>
        `;
        
        // This would be replaced with an actual API call to check status
        // For now, this is handled by the status.html template
    }
    
    displayStatus(data) {
        const statusClass = this.getStatusClass(data.status);
        const statusText = this.getStatusText(data.status);
        
        let html = `
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <div class="text-center mb-4">
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Package Details</h6>
                            <p class="text-muted">${data.package}</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Pickup Information</h6>
                            <p class="text-muted">
                                <i class="bi bi-calendar me-2"></i>${data.pickup_date}<br>
                                <i class="bi bi-clock me-2"></i>${data.pickup_time}<br>
                                <i class="bi bi-geo-alt me-2"></i>${data.pickup_location}
                            </p>
                        </div>
                    </div>
        `;
        
        if (data.status === 'approved' && data.qr_code) {
            html += `
                <div class="text-center mt-4">
                    <h6>Your QR Code</h6>
                    <div class="qr-code">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${data.qr_code}" 
                             alt="QR Code" class="img-fluid">
                    </div>
                    <p class="small text-muted mt-2">Present this QR code during pickup</p>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        this.statusResult.innerHTML = html;
    }
    
    getStatusClass(status) {
        const classes = {
            'pending': 'status-pending',
            'approved': 'status-approved',
            'ready': 'status-ready',
            'collected': 'status-collected'
        };
        return classes[status] || 'status-pending';
    }
    
    getStatusText(status) {
        const texts = {
            'pending': 'Under Review',
            'approved': 'Approved - Ready for Pickup',
            'ready': 'Ready for Pickup',
            'collected': 'Collected'
        };
        return texts[status] || 'Unknown Status';
    }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            // Skip if href is just "#" or empty
            if (!href || href === '#' || href.length <= 1) {
                return;
            }
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize multi-step form
    new MultiStepForm('#application-form');
    
    // Initialize package filter
    new PackageFilter();
    
    // Initialize status checker - DISABLED (page-specific implementation used instead)
    // new StatusChecker();
    
    // Initialize smooth scrolling
    initSmoothScrolling();
    
    // Add fade-in animation to cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    document.querySelectorAll('.card, .package-card').forEach(card => {
        observer.observe(card);
    });
});

// Form validation utilities
function validatePhone(phone) {
    const phoneRegex = /^(\+234|234|0)[789][01][0-9]{8}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Export for use in other scripts
window.CommunityRelief = {
    MultiStepForm,
    PackageFilter,
    StatusCheckerOld,  // Renamed to avoid conflicts
    validatePhone,
    validateEmail
};