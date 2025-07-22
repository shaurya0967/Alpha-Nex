/**
 * Alpha Nex Main JavaScript
 * Core client-side functionality for the AI training data platform
 * Handles form interactions, validation, and user experience enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload enhancements
    const fileInput = document.getElementById('file');
    const uploadArea = document.querySelector('.upload-area');
    
    if (fileInput && uploadArea) {
        // Drag and drop functionality
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileInfo(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                updateFileInfo(e.target.files[0]);
            }
        });

        function updateFileInfo(file) {
            const fileInfo = document.getElementById('file-info');
            if (fileInfo) {
                const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
                fileInfo.innerHTML = `
                    <strong>Selected file:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${sizeInMB} MB<br>
                    <strong>Type:</strong> ${file.type || 'Unknown'}
                `;
                fileInfo.style.display = 'block';
            }
        }
    }

    // Review rating buttons
    const ratingButtons = document.querySelectorAll('.rating-btn');
    const ratingInput = document.getElementById('rating');
    
    ratingButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            ratingButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Set hidden input value
            if (ratingInput) {
                ratingInput.value = this.getAttribute('data-rating');
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Password confirmation validation
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (passwordInput && confirmPasswordInput) {
        function validatePasswordMatch() {
            if (passwordInput.value !== confirmPasswordInput.value) {
                confirmPasswordInput.setCustomValidity('Passwords do not match');
            } else {
                confirmPasswordInput.setCustomValidity('');
            }
        }
        
        passwordInput.addEventListener('input', validatePasswordMatch);
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }

    // Character counter for review descriptions
    const descriptionTextarea = document.getElementById('description');
    const charCounter = document.getElementById('char-counter');
    
    if (descriptionTextarea && charCounter) {
        function updateCharCounter() {
            const length = descriptionTextarea.value.length;
            charCounter.textContent = `${length}/500 characters (minimum 50)`;
            
            if (length < 50) {
                charCounter.style.color = 'var(--danger-color)';
            } else if (length >= 100) {
                charCounter.style.color = 'var(--success-color)';
            } else {
                charCounter.style.color = 'var(--warning-color)';
            }
        }
        
        descriptionTextarea.addEventListener('input', updateCharCounter);
        updateCharCounter(); // Initialize
    }

    // Consent checkbox validation
    const consentCheckbox = document.getElementById('consent');
    const submitButton = document.getElementById('submit-btn');
    
    if (consentCheckbox && submitButton) {
        function toggleSubmitButton() {
            submitButton.disabled = !consentCheckbox.checked;
        }
        
        consentCheckbox.addEventListener('change', toggleSubmitButton);
        toggleSubmitButton(); // Initialize
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Search functionality
    const searchInput = document.getElementById('search');
    const searchableItems = document.querySelectorAll('.searchable');
    
    if (searchInput && searchableItems.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            searchableItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // File size validation
    function validateFileSize(input, maxSizeMB) {
        const file = input.files[0];
        if (file) {
            const sizeInMB = file.size / (1024 * 1024);
            if (sizeInMB > maxSizeMB) {
                alert(`File size must be less than ${maxSizeMB}MB. Your file is ${sizeInMB.toFixed(2)}MB.`);
                input.value = '';
                return false;
            }
        }
        return true;
    }

    // Apply file size validation to file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateFileSize(this, 500); // 500MB limit
        });
    });

    // Modal handling
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            document.body.style.overflow = 'hidden';
        });
        
        modal.addEventListener('hide.bs.modal', function() {
            document.body.style.overflow = 'auto';
        });
    });

    // Star rating for website feedback
    const starRating = document.querySelectorAll('.star-rating .star');
    const ratingValueInput = document.getElementById('rating-value');
    
    starRating.forEach((star, index) => {
        star.addEventListener('click', function() {
            const rating = index + 1;
            
            // Update visual state
            starRating.forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
            
            // Update hidden input
            if (ratingValueInput) {
                ratingValueInput.value = rating;
            }
        });
        
        star.addEventListener('mouseenter', function() {
            const rating = index + 1;
            starRating.forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('hover');
                } else {
                    s.classList.remove('hover');
                }
            });
        });
    });
    
    const starContainer = document.querySelector('.star-rating');
    if (starContainer) {
        starContainer.addEventListener('mouseleave', function() {
            starRating.forEach(s => s.classList.remove('hover'));
        });
    }

    // Progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('data-width');
        if (targetWidth) {
            setTimeout(() => {
                bar.style.width = targetWidth + '%';
            }, 100);
        }
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const text = targetElement.textContent || targetElement.value;
                navigator.clipboard.writeText(text).then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                });
            }
        });
    });
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    element.appendChild(spinner);
}

function hideLoading(element) {
    const spinner = element.querySelector('.spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // You could send this to a logging service
});

// Page visibility handling
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, pause any ongoing operations
        console.log('Page hidden');
    } else {
        // Page is visible, resume operations
        console.log('Page visible');
    }
});
