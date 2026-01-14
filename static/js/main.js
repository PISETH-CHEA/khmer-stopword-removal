// main.js - Interactive features for Khmer NLP System

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const textForm = document.getElementById('textForm');
    const textInput = document.getElementById('textInput');
    const clearBtn = document.getElementById('clearBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const exportJsonBtn = document.getElementById('exportJson');
    const exportCsvBtn = document.getElementById('exportCsv');
    const exportTxtBtn = document.getElementById('exportTxt');
    
    // Language switcher
    const languageSwitchers = document.querySelectorAll('.language-switch');

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Language switching
    languageSwitchers.forEach(switcher => {
        switcher.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('data-lang');
            switchLanguage(lang);
        });
    });

    // Clear button functionality
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            textInput.value = '';
            textInput.focus();
            updateCharCount();
        });
    }

    // Form submission with loading state
    if (textForm) {
        textForm.addEventListener('submit', function(e) {
            if (!textInput.value.trim()) {
                e.preventDefault();
                showAlert(window.languageStrings?.enter_text || 'Please enter text before analyzing', 'danger');
                return;
            }
            
            // Show loading state
            if (analyzeBtn && loadingSpinner) {
                analyzeBtn.disabled = true;
                loadingSpinner.classList.remove('d-none');
                analyzeBtn.innerHTML = `<i class="bi bi-gear me-1"></i>${window.languageStrings?.loading || 'Analyzing...'}`;
            }
        });
    }

    // Export functionality
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', function() {
            exportResults('json');
        });
    }

    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            exportResults('csv');
        });
    }

    if (exportTxtBtn) {
        exportTxtBtn.addEventListener('click', function() {
            exportResults('txt');
        });
    }

    // Real-time character count
    if (textInput) {
        textInput.addEventListener('input', function() {
            updateCharCount();
        });
        
        // Initial count
        updateCharCount();
    }

    // Token click functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('token')) {
            const token = e.target.textContent;
            copyToClipboard(token);
            const message = window.languageStrings?.copy_token || 'Copied word to clipboard';
            showAlert(message.replace('${token}', token), 'success');
        }
    });

    // Function to update character count
    function updateCharCount() {
        const charCount = textInput.value.length;
        const wordCount = textInput.value.trim().split(/\s+/).filter(word => word.length > 0).length;
        
        const charCounter = document.getElementById('charCounter');
        if (charCounter) {
            charCounter.innerHTML = `
                <i class="bi bi-info-circle me-1"></i>
                ${charCount} ${window.languageStrings?.chars || 'Characters'} | ${wordCount} ${window.languageStrings?.words || 'Words'}
            `;
        }
    }

    // Function to switch language
    async function switchLanguage(lang) {
        try {
            const response = await fetch('/set_language/' + lang, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            if (data.success) {
                location.reload();
            }
        } catch (error) {
            console.error('Error switching language:', error);
            showAlert('Failed to switch language', 'danger');
        }
    }

    // Function to export results
    function exportResults(format) {
        const results = window.resultsData || getResultsFromPage();
        
        if (!results) {
            showAlert(window.languageStrings?.no_data || 'No data available for export', 'warning');
            return;
        }

        let content, mimeType, filename;

        switch(format) {
            case 'json':
                content = JSON.stringify(results, null, 2);
                mimeType = 'application/json';
                filename = 'khmer_nlp_analysis.json';
                break;
                
            case 'csv':
                content = convertToCSV(results);
                mimeType = 'text/csv';
                filename = 'khmer_nlp_analysis.csv';
                break;
                
            case 'txt':
                content = convertToTXT(results);
                mimeType = 'text/plain';
                filename = 'khmer_nlp_analysis.txt';
                break;
        }

        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        const message = `${window.languageStrings?.exported || 'Exported as format'} ${format.toUpperCase()}`;
        showAlert(message, 'success');
    }

    // Function to convert results to CSV
    function convertToCSV(results) {
        const headers = [window.languageStrings?.word || 'Word', window.languageStrings?.frequency || 'Frequency', 'Type'];
        const rows = [];
        
        // Add filtered tokens
        if (results.filtered_tokens) {
            results.filtered_tokens.forEach(token => {
                rows.push([token, '1', window.languageStrings?.filtered_tokens || 'Filtered']);
            });
        }
        
        // Add removed tokens
        if (results.removed_tokens) {
            results.removed_tokens.forEach(token => {
                rows.push([token, '1', window.languageStrings?.removed_tokens || 'Removed']);
            });
        }
        
        // Add frequency data
        if (results.frequency_tokens) {
            Object.entries(results.frequency_tokens).forEach(([token, freq]) => {
                rows.push([token, freq, window.languageStrings?.filtered_tokens || 'Filtered']);
            });
        }
        
        return [headers, ...rows].map(row => 
            row.map(cell => `"${cell}"`).join(',')
        ).join('\n');
    }

    // Function to convert results to TXT
    function convertToTXT(results) {
        let text = `${window.languageStrings?.app_name || 'Khmer NLP Analysis Results'}\n`;
        text += '='.repeat(50) + '\n\n';
        
        if (results.stats) {
            text += `${window.languageStrings?.statistics || 'Statistics'}:\n`;
            Object.entries(results.stats).forEach(([key, value]) => {
                text += `  ${key}: ${value}\n`;
            });
            text += '\n';
        }
        
        if (results.filtered_tokens) {
            text += `${window.languageStrings?.filtered_tokens || 'Filtered Tokens'}:\n`;
            text += results.filtered_tokens.join(', ') + '\n\n';
        }
        
        if (results.removed_tokens) {
            text += `${window.languageStrings?.removed_tokens || 'Removed Tokens'}:\n`;
            text += results.removed_tokens.join(', ') + '\n\n';
        }
        
        return text;
    }

    // Function to get results from page
    function getResultsFromPage() {
        const results = {};
        
        // Get filtered tokens
        const filteredTokens = [];
        document.querySelectorAll('#filtered .token').forEach(token => {
            filteredTokens.push(token.textContent);
        });
        results.filtered_tokens = filteredTokens;
        
        // Get removed tokens
        const removedTokens = [];
        document.querySelectorAll('#removed .token').forEach(token => {
            removedTokens.push(token.textContent);
        });
        results.removed_tokens = removedTokens;
        
        // Get frequency data
        const frequencyTokens = {};
        document.querySelectorAll('#frequency tbody tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                frequencyTokens[cells[0].textContent] = parseInt(cells[1].textContent);
            }
        });
        results.frequency_tokens = frequencyTokens;
        
        // Get stats
        const statsCards = document.querySelectorAll('.stats-card h3');
        if (statsCards.length >= 4) {
            results.stats = {
                original_tokens: parseInt(statsCards[0]?.textContent || '0'),
                filtered_tokens: parseInt(statsCards[1]?.textContent || '0'),
                removed_tokens: parseInt(statsCards[2]?.textContent || '0')
            };
        }
        
        return results;
    }

    // Function to copy text to clipboard
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).catch(err => {
            console.error('Failed to copy: ', err);
        });
    }

    // Function to show alerts
    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-dismissible');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '1050';
        alertDiv.style.minWidth = '300px';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto dismiss after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 3000);
    }

    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
});

// Function to initialize charts
function initializeCharts() {
    const ctx = document.getElementById('frequencyChart');
    if (ctx) {
        const frequencyData = window.frequencyData || getFrequencyData();
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(frequencyData).slice(0, 10),
                datasets: [{
                    label: window.languageStrings?.word_frequency || 'Word Frequency',
                    data: Object.values(frequencyData).slice(0, 10),
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            font: {
                                family: 'Battambang'
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            font: {
                                family: 'Battambang'
                            }
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                family: 'Battambang'
                            }
                        }
                    }
                }
            }
        });
    }
}

// Function to get frequency data from page
function getFrequencyData() {
    const data = {};
    const rows = document.querySelectorAll('#frequency tbody tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
            const word = cells[0].textContent.trim();
            const frequency = parseInt(cells[1].textContent);
            if (word && !isNaN(frequency)) {
                data[word] = frequency;
            }
        }
    });
    
    return data;
}