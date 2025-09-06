// Application Form Handler
class ApplicationFormHandler {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        this.currentStep = 1;
        this.totalSteps = 5;
        this.formData = {};
        
        if (this.form) {
            this.init();
        }
    }
    
    init() {
        this.setupStepNavigation();
        this.setupFormValidation();
        this.loadPackages();
        this.bindEvents();
    }
    
    setupStepNavigation() {
        const nextBtns = document.querySelectorAll('.next-btn');
        const prevBtns = document.querySelectorAll('.prev-btn');
        const submitBtn = document.querySelector('.submit-btn');
        
        nextBtns.forEach(btn => {
            btn.addEventListener('click', () => this.nextStep());
        });
        
        prevBtns.forEach(btn => {
            btn.addEventListener('click', () => this.prevStep());
        });
        
        if (submitBtn) {
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.submitApplication();
            });
        }
    }
    
    setupFormValidation() {
        // Phone number validation
        const phoneInput = document.getElementById('phone');
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => {
                this.validatePhoneNumber(e.target);
            });
        }
        
        // Form step validation
        this.form.addEventListener('input', (e) => {
            this.updateFormData();
        });
        
        this.form.addEventListener('change', (e) => {
            this.updateFormData();
        });
    }
    
    async loadPackages() {
        try {
            const response = await fetch('/api/packages/available/');
            if (response.ok) {
                const packages = await response.json();
                this.updatePackageOptions(packages);
            }
        } catch (error) {
            console.warn('Could not load packages from API, using defaults');
        }
    }
    
    updatePackageOptions(packages) {
        const packageContainer = document.querySelector('.row.g-3');
        if (!packageContainer || packages.length === 0) return;
        
        // Clear existing options except the recommendation div
        const packageOptions = packageContainer.querySelectorAll('.col-lg-6');
        packageOptions.forEach(option => option.remove());
        
        // Add packages from API
        packages.forEach(package => {
            if (package.is_available) {
                const packageHtml = `
                    <div class="col-lg-6">
                        <div class="card package-option">
                            <div class="card-body">
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="selected_package" 
                                           id="${package.package_type}" value="${package.package_type}" required>
                                    <label class="form-check-label w-100" for="${package.package_type}">
                                        <h6>${package.name} - ₦${parseFloat(package.cash_amount).toLocaleString()}</h6>
                                        <small class="text-muted">${package.description}</small>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                packageContainer.insertAdjacentHTML('beforeend', packageHtml);
            }
        });
    }
    
    validatePhoneNumber(input) {
        const phoneRegex = /^(\+?234|0)[789][01]\d{8}$/;
        const isValid = phoneRegex.test(input.value.replace(/\s/g, ''));
        
        if (input.value && !isValid) {
            input.setCustomValidity('Please enter a valid Nigerian phone number (e.g., 08012345678)');
        } else {
            input.setCustomValidity('');
        }
    }
    
    updateFormData() {
        const formData = new FormData(this.form);
        this.formData = {};
        
        for (let [key, value] of formData.entries()) {
            if (this.form.elements[key] && this.form.elements[key].type === 'checkbox') {
                this.formData[key] = this.form.elements[key].checked;
            } else {
                this.formData[key] = value;
            }
        }
        
        // Update summary if on final step
        if (this.currentStep === 5) {
            this.updateSummary();
        }
    }
    
    updateSummary() {
        const summaryDiv = document.getElementById('application-summary');
        if (!summaryDiv) return;
        
        const summary = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Personal Information</h6>
                    <p><strong>Name:</strong> ${this.formData.first_name || ''} ${this.formData.last_name || ''}</p>
                    <p><strong>Phone:</strong> ${this.formData.phone || ''}</p>
                    <p><strong>Email:</strong> ${this.formData.email || 'Not provided'}</p>
                </div>
                <div class="col-md-6">
                    <h6>Family Details</h6>
                    <p><strong>Family Size:</strong> ${this.formData.family_size || ''} people</p>
                    <p><strong>Children:</strong> ${this.formData.children_count || '0'}</p>
                    <p><strong>Employment:</strong> ${this.formData.employment_status || ''}</p>
                </div>
                <div class="col-md-6">
                    <h6>Package Selection</h6>
                    <p><strong>Selected Package:</strong> ${this.getPackageName(this.formData.selected_package)}</p>
                    <p><strong>Flexible:</strong> ${this.formData.package_flexibility ? 'Yes' : 'No'}</p>
                </div>
                <div class="col-md-6">
                    <h6>Pickup Schedule</h6>
                    <p><strong>Preferred Date:</strong> ${this.formData.preferred_date || ''}</p>
                    <p><strong>Preferred Time:</strong> ${this.getTimeSlotName(this.formData.preferred_time)}</p>
                    ${this.formData.transportation_help ? '<p><strong>Transportation Help:</strong> Requested</p>' : ''}
                    ${this.formData.delivery_request ? '<p><strong>Delivery:</strong> Requested</p>' : ''}
                </div>
            </div>
        `;
        
        summaryDiv.innerHTML = summary;
    }
    
    getPackageName(packageType) {
        const packageNames = {
            'small_basic': 'Small Family Basic',
            'medium_basic': 'Medium Family Basic',
            'emergency': 'Emergency Relief',
            'senior': 'Senior Citizen Special'
        };
        return packageNames[packageType] || packageType;
    }
    
    getTimeSlotName(timeSlot) {
        const timeSlots = {
            'morning': 'Morning (9:00 AM - 12:00 PM)',
            'afternoon': 'Afternoon (12:00 PM - 3:00 PM)',
            'evening': 'Evening (3:00 PM - 6:00 PM)'
        };
        return timeSlots[timeSlot] || timeSlot;
    }
    
    nextStep() {
        if (this.validateCurrentStep() && this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateStepDisplay();
            this.updateFormData();
        }
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
        }
    }
    
    validateCurrentStep() {
        const currentStepDiv = document.querySelector(`.form-step:nth-child(${this.currentStep})`);
        if (!currentStepDiv) return true;
        
        const requiredFields = currentStepDiv.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.checkValidity()) {
                field.reportValidity();
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    updateStepDisplay() {
        // Update step indicators
        const stepIndicators = document.querySelectorAll('.step');
        stepIndicators.forEach((step, index) => {
            if (index + 1 <= this.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        // Update form steps
        const formSteps = document.querySelectorAll('.form-step');
        formSteps.forEach((step, index) => {
            if (index + 1 === this.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        // Update navigation buttons
        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        const submitBtn = document.querySelector('.submit-btn');
        
        if (prevBtn) {
            prevBtn.style.display = this.currentStep === 1 ? 'none' : 'inline-block';
        }
        
        if (nextBtn && submitBtn) {
            if (this.currentStep === this.totalSteps) {
                nextBtn.style.display = 'none';
                submitBtn.style.display = 'inline-block';
            } else {
                nextBtn.style.display = 'inline-block';
                submitBtn.style.display = 'none';
            }
        }
    }
    
    bindEvents() {
        // Update package recommendations based on family size
        const familySizeSelect = document.getElementById('family_size');
        if (familySizeSelect) {
            familySizeSelect.addEventListener('change', (e) => {
                this.updatePackageRecommendations(e.target.value);
            });
        }
    }
    
    updatePackageRecommendations(familySize) {
        const recommendedDiv = document.getElementById('recommended-packages');
        if (!recommendedDiv) return;
        
        const size = parseInt(familySize) || 1;
        let recommendation = '';
        
        if (size <= 3) {
            recommendation = 'Based on your family size, we recommend the <strong>Small Family Basic</strong> package.';
        } else if (size <= 6) {
            recommendation = 'Based on your family size, we recommend the <strong>Medium Family Basic</strong> package.';
        } else {
            recommendation = 'Based on your family size, we recommend the <strong>Medium Family Basic</strong> or consider multiple packages.';
        }
        
        recommendedDiv.innerHTML = `
            <i class="bi bi-lightbulb me-2"></i>
            <strong>Recommended for you:</strong> ${recommendation}
        `;
    }
    
    async submitApplication() {
        if (!this.validateCurrentStep()) {
            return;
        }
        
        this.updateFormData();
        
        // Show loading state
        const submitBtn = document.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Submitting...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/applications/submit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(this.formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccessMessage(result);
            } else {
                this.showErrorMessage(result);
            }
            
        } catch (error) {
            console.error('Submission error:', error);
            this.showErrorMessage({
                message: 'Network error. Please check your connection and try again.',
                errors: {}
            });
        } finally {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    getCSRFToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
    
    showSuccessMessage(result) {
        const successHtml = `
            <div class="alert alert-success" role="alert">
                <h4 class="alert-heading">Application Submitted Successfully! 🎉</h4>
                <p class="mb-3">${result.message}</p>
                <hr>
                <div class="row">
                    <div class="col-md-6">
                        <p class="mb-1"><strong>Reference Number:</strong></p>
                        <h5 class="text-primary">${result.reference_number}</h5>
                        <small class="text-muted">Please save this reference number</small>
                    </div>
                    <div class="col-md-6">
                        <p class="mb-1"><strong>Status:</strong> ${result.data.status}</p>
                        <p class="mb-1"><strong>Package:</strong> ${this.getPackageName(result.data.selected_package)}</p>
                        <p class="mb-0"><strong>Contact:</strong> ${result.data.phone}</p>
                    </div>
                </div>
                <hr>
                <p class="mb-0">
                    <small>
                        📱 You will receive an SMS/email notification when your application is reviewed.<br>
                        🎫 If approved, you'll get a QR code for pickup.
                    </small>
                </p>
            </div>
        `;
        
        // Replace form with success message
        const formContainer = document.querySelector('.form-container');
        if (formContainer) {
            formContainer.innerHTML = successHtml;
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    showErrorMessage(result) {
        let errorHtml = `
            <div class="alert alert-danger" role="alert">
                <h5 class="alert-heading">Submission Failed</h5>
                <p>${result.message || 'Please correct the errors below and try again.'}</p>
        `;
        
        if (result.errors && Object.keys(result.errors).length > 0) {
            errorHtml += '<ul class="mb-0">';
            for (const [field, errors] of Object.entries(result.errors)) {
                if (Array.isArray(errors)) {
                    errors.forEach(error => {
                        errorHtml += `<li>${field}: ${error}</li>`;
                    });
                } else {
                    errorHtml += `<li>${field}: ${errors}</li>`;
                }
            }
            errorHtml += '</ul>';
        }
        
        errorHtml += '</div>';
        
        // Show error message at top of form
        const formContainer = document.querySelector('.form-container');
        if (formContainer) {
            const existingAlert = formContainer.querySelector('.alert');
            if (existingAlert) {
                existingAlert.remove();
            }
            formContainer.insertAdjacentHTML('afterbegin', errorHtml);
        }
        
        // Scroll to error
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date to tomorrow
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.min = tomorrow.toISOString().split('T')[0];
    });
    
    // Initialize application form
    new ApplicationFormHandler('#application-form');
});