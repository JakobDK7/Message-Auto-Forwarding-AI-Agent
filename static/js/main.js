// main.js - JavaScript for Message Auto-Forwarding System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Platform credential fields toggle based on platform type
    const platformTypeSelect = document.getElementById('platform-type');
    if (platformTypeSelect) {
        platformTypeSelect.addEventListener('change', function() {
            const credentialsField = document.getElementById('credentials-helper');
            const credentialsExample = document.getElementById('credentials-example');
            const selectedType = this.value;
            
            let exampleJson = '{}';
            let helperText = 'Enter credentials in JSON format';
            
            switch(selectedType) {
                case 'telegram':
                    exampleJson = '{\n  "phone": "+1234567890"\n}';
                    helperText = 'Enter your Telegram phone number';
                    break;
                case 'whatsapp':
                    exampleJson = '{\n  "name": "Your Name"\n}';
                    helperText = 'Will require QR code scan on first use';
                    break;
                case 'slack':
                    exampleJson = '{\n  "email": "your@email.com",\n  "password": "your_password"\n}';
                    helperText = 'Enter your Slack email and password';
                    break;
                case 'discord':
                    exampleJson = '{\n  "email": "your@email.com",\n  "password": "your_password"\n}';
                    helperText = 'Enter your Discord email and password';
                    break;
            }
            
            if (credentialsField) credentialsField.textContent = helperText;
            if (credentialsExample) credentialsExample.textContent = exampleJson;
        });
    }

    // Rule form handling - show/hide fields based on rule type
    const ruleSourceSelect = document.getElementById('source_id');
    const ruleDestSelect = document.getElementById('destination_id');
    
    if (ruleSourceSelect && ruleDestSelect) {
        const updateFilterFields = function() {
            const sourceId = ruleSourceSelect.value;
            const destId = ruleDestSelect.value;
            
            if (sourceId && destId) {
                document.getElementById('rule-config-section').classList.remove('d-none');
            } else {
                document.getElementById('rule-config-section').classList.add('d-none');
            }
        };
        
        ruleSourceSelect.addEventListener('change', updateFilterFields);
        ruleDestSelect.addEventListener('change', updateFilterFields);
    }

    // Copy example credentials to clipboard
    const copyCredentialsBtn = document.getElementById('copy-credentials');
    if (copyCredentialsBtn) {
        copyCredentialsBtn.addEventListener('click', function() {
            const credentialsExample = document.getElementById('credentials-example');
            if (credentialsExample) {
                navigator.clipboard.writeText(credentialsExample.textContent).then(function() {
                    // Success feedback
                    const originalText = copyCredentialsBtn.textContent;
                    copyCredentialsBtn.textContent = 'Copied!';
                    setTimeout(function() {
                        copyCredentialsBtn.textContent = originalText;
                    }, 2000);
                });
            }
        });
    }

    // Confirm deletion of platforms and rules
    const confirmDeletionForms = document.querySelectorAll('.confirm-deletion');
    if (confirmDeletionForms) {
        confirmDeletionForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }

    // Log auto-refresh
    const autoRefreshCheckbox = document.getElementById('auto-refresh');
    if (autoRefreshCheckbox) {
        let refreshInterval;
        
        autoRefreshCheckbox.addEventListener('change', function() {
            if (this.checked) {
                refreshInterval = setInterval(function() {
                    location.reload();
                }, 30000); // Refresh every 30 seconds
            } else {
                clearInterval(refreshInterval);
            }
        });
    }

    // JSON validator for filters field
    const filtersField = document.getElementById('filters');
    const filtersValidation = document.getElementById('filters-validation');
    
    if (filtersField && filtersValidation) {
        filtersField.addEventListener('blur', function() {
            try {
                if (this.value.trim()) {
                    JSON.parse(this.value);
                    filtersValidation.textContent = 'Valid JSON';
                    filtersValidation.className = 'text-success';
                } else {
                    filtersValidation.textContent = '';
                }
            } catch (e) {
                filtersValidation.textContent = 'Invalid JSON: ' + e.message;
                filtersValidation.className = 'text-danger';
            }
        });
    }
});
