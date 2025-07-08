/**
 * Demo Mode JavaScript - Shows database operations from db_logs table
 */

class DatabaseDemo {
    constructor() {
        this.isVisible = false;
        this.queries = [];
        this.storageKey = 'app_database_queries';
        this.visibilityKey = 'databaseDemo_visible';
        this.apiUrl = 'http://localhost:5001/api/db-logs';
        this.init();
    }

    init() {
        this.loadFromStorage();
        this.createDemoPanel();
        this.setupToggleButton();
        this.restoreVisibility();
        this.refreshQueries(); // Load initial data
    }

    saveToStorage() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.queries));
            localStorage.setItem(this.visibilityKey, this.isVisible.toString());
        } catch (e) {
            console.log('Demo panel: localStorage not available');
        }
    }

    loadFromStorage() {
        try {
            const savedQueries = localStorage.getItem(this.storageKey);
            const savedVisibility = localStorage.getItem(this.visibilityKey);
            
            if (savedQueries) {
                this.queries = JSON.parse(savedQueries);
            }
            
            if (savedVisibility) {
                this.isVisible = savedVisibility === 'true';
            }
        } catch (e) {
            console.log('Demo panel: Could not load from localStorage');
        }
    }

    restoreVisibility() {
        if (this.isVisible) {
            // Delay to ensure DOM is ready
            setTimeout(() => {
                const panel = document.getElementById('demo-panel');
                const toggle = document.getElementById('demo-toggle');
                const body = document.body;
                
                if (panel && toggle) {
                    panel.classList.add('visible');
                    body.classList.add('demo-panel-open');
                    toggle.innerHTML = '<i class="fas fa-eye-slash"></i> Hide';
                }
                this.renderQueries();
                this.updateStats();
            }, 100);
        } else {
            // Even if not visible, render queries in case user opens panel
            setTimeout(() => {
                this.renderQueries();
                this.updateStats();
            }, 100);
        }
    }

    createDemoPanel() {
        // Create demo panel HTML
        const demoPanel = document.createElement('div');
        demoPanel.id = 'demo-panel';
        demoPanel.className = 'demo-panel';
        demoPanel.innerHTML = `
            <div class="demo-header">
                <h5><i class="fas fa-database"></i> Database Operations Log</h5>
                <div class="demo-controls">
                    <button class="btn btn-sm btn-outline-light" onclick="databaseDemo.refreshQueries()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    <button class="btn btn-sm btn-outline-light" onclick="databaseDemo.clearQueries()">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                    <button class="btn btn-sm btn-outline-light" onclick="databaseDemo.togglePanel()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="demo-content">
                <div class="demo-stats">
                    <span class="stat-item">
                        <i class="fas fa-database"></i> 
                        <span id="demo-total-queries">0</span> queries
                    </span>
                    <span class="stat-item">
                        <i class="fas fa-stopwatch"></i> 
                        <span id="demo-avg-time">0</span>ms avg
                    </span>
                </div>
                <div class="demo-queries" id="demo-queries">
                    <div class="no-queries">
                        <i class="fas fa-info-circle"></i>
                        Interact with the app to see database queries
                        <br><br>
                        <small>💡 Shows actual SQL queries with execution times - persists across page reloads</small>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(demoPanel);
    }

    setupToggleButton() {
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'demo-toggle';
        toggleBtn.className = 'demo-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-database"></i> DB Log';
        toggleBtn.onclick = () => this.togglePanel();
        document.body.appendChild(toggleBtn);
    }

    togglePanel() {
        const panel = document.getElementById('demo-panel');
        const toggle = document.getElementById('demo-toggle');
        const body = document.body;
        
        if (this.isVisible) {
            panel.classList.remove('visible');
            body.classList.remove('demo-panel-open');
            toggle.innerHTML = '<i class="fas fa-database"></i> DB Log';
            this.isVisible = false;
        } else {
            panel.classList.add('visible');
            body.classList.add('demo-panel-open');
            toggle.innerHTML = '<i class="fas fa-eye-slash"></i> Hide';
            this.isVisible = true;
            // Refresh data when panel is opened
            this.refreshQueries();
        }
        
        this.saveToStorage();
    }

    async refreshQueries() {
        try {
            // Show loading state
            const refreshBtn = document.querySelector('.demo-controls .btn:first-child');
            if (refreshBtn) {
                const originalHTML = refreshBtn.innerHTML;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                refreshBtn.disabled = true;
                
                // Restore button after delay
                setTimeout(() => {
                    refreshBtn.innerHTML = originalHTML;
                    refreshBtn.disabled = false;
                }, 1000);
            }

            const response = await fetch(this.apiUrl);
            const data = await response.json();
            
            if (data.success && data.data) {
                this.queries = data.data.logs || [];
                this.renderQueries();
                this.updateStats();
                this.saveToStorage();
            } else {
                console.error('Failed to fetch logs:', data.message);
            }
        } catch (error) {
            console.error('Failed to refresh queries:', error);
        }
    }

    async clearQueries() {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'DELETE'
            });
            const data = await response.json();
            
            if (data.success) {
                this.queries = [];
                this.renderQueries();
                this.updateStats();
                this.saveToStorage();
            } else {
                console.error('Failed to clear logs:', data.message);
            }
        } catch (error) {
            console.error('Failed to clear queries:', error);
        }
    }

    renderQueries() {
        const container = document.getElementById('demo-queries');
        
        if (this.queries.length === 0) {
            container.innerHTML = `
                <div class="no-queries">
                    <i class="fas fa-info-circle"></i>
                    Interact with the app to see database queries
                    <br><br>
                    <small>💡 Shows actual SQL queries with execution times - persists across page reloads</small>
                </div>
            `;
            return;
        }
        
        // Show queries (already sorted by timestamp desc from API)
        container.innerHTML = this.queries.map(query => {
            const operationParts = query.operation.split(':');
            const queryType = operationParts[0];
            const queryText = operationParts.slice(1).join(':').trim();
            
            return `
                <div class="query-item">
                    <div class="query-header">
                        <span class="query-type ${queryType.toLowerCase()}">${queryType}</span>
                        <span class="query-time">${query.timestamp}</span>
                        <span class="query-duration">${query.time_taken_ms}ms</span>
                    </div>
                    <div class="query-text">${queryText}</div>
                    <div class="query-meta">
                        <span class="query-results">${query.response_count} rows</span>
                    </div>
                </div>
            `;
        }).join('');
        
        // Auto-scroll to top for newest queries
        container.scrollTop = 0;
    }

    updateStats() {
        const totalQueries = this.queries.length;
        const avgTime = totalQueries > 0 ? 
            (this.queries.reduce((sum, q) => sum + (q.time_taken_ms || 0), 0) / totalQueries).toFixed(1) : 0;
        
        const totalElement = document.getElementById('demo-total-queries');
        const timeElement = document.getElementById('demo-avg-time');
        
        if (totalElement) totalElement.textContent = totalQueries;
        if (timeElement) timeElement.textContent = avgTime;
    }
}

// Initialize demo when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.databaseDemo = new DatabaseDemo();
}); 