/**
 * Splunk Dashboard Automator - Main JavaScript
 * ============================================
 * 
 * This file contains all the client-side functionality for the application:
 * - Theme management (light/dark mode switching)
 * - Dashboard and list management
 * - API communication with the Flask backend
 * - User interface interactions
 * - Real-time updates and notifications
 */

class SplunkAutomator {
    constructor() {
        // Initialize application state
        this.dashboards = [];
        this.lists = [];
        this.schedules = [];
        this.currentTheme = 'light';
        this.selectedDashboards = new Set();
        
        // Initialize the application
        this.init();
    }

    /**
     * Initialize the application
     * Sets up event listeners, loads data, and initializes the UI
     */
    async init() {
        // Initialize Feather icons
        feather.replace();
        
        // Load user settings and apply theme
        await this.loadSettings();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadAllData();
        
        // Check if credentials are configured
        await this.checkCredentials();
        
        console.log('Splunk Automator initialized successfully');
    }

    /**
     * Set up all event listeners for the application
     */
    setupEventListeners() {
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Credentials form
        document.getElementById('credentialsForm').addEventListener('submit', (e) => {
            this.handleCredentialsSubmit(e);
        });

        // Add dashboard form
        document.getElementById('addDashboardForm').addEventListener('submit', (e) => {
            this.handleAddDashboard(e);
        });

        // Add list form
        document.getElementById('addListForm').addEventListener('submit', (e) => {
            this.handleAddList(e);
        });

        // Add schedule form
        document.getElementById('addScheduleForm').addEventListener('submit', (e) => {
            this.handleAddSchedule(e);
        });

        // Dashboard management buttons
        document.getElementById('selectAllDashboards').addEventListener('click', () => {
            this.selectAllDashboards();
        });

        document.getElementById('deleteSelectedDashboards').addEventListener('click', () => {
            this.deleteSelectedDashboards();
        });

        // Action buttons
        document.getElementById('captureScreenshots').addEventListener('click', () => {
            this.startScreenshotCapture(true);
        });

        document.getElementById('analyzeWithoutWatermark').addEventListener('click', () => {
            this.startScreenshotCapture(false);
        });

        document.getElementById('scheduleAnalysis').addEventListener('click', () => {
            this.openScheduleModal();
        });

        // Master checkbox for dashboard selection
        document.getElementById('selectAllCheckbox').addEventListener('change', (e) => {
            this.toggleAllDashboards(e.target.checked);
        });

        // Time range preset change
        document.getElementById('timeRangePreset').addEventListener('change', (e) => {
            this.handleTimeRangeChange(e.target.value);
        });

        // List filter
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-filter]')) {
                this.filterDashboards(e.target.dataset.filter);
            }
        });

        // Add new list from dashboard modal
        document.getElementById('addNewList').addEventListener('click', () => {
            this.addNewListFromModal();
        });
    }

    /**
     * Load all application data from the backend
     */
    async loadAllData() {
        try {
            await Promise.all([
                this.loadDashboards(),
                this.loadLists(),
                this.loadSchedules()
            ]);
        } catch (error) {
            console.error('Error loading data:', error);
            this.showNotification('Error loading application data', 'danger');
        }
    }

    /**
     * Load user settings and apply theme
     */
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const settings = await response.json();
            
            this.currentTheme = settings.theme || 'light';
            this.applyTheme(this.currentTheme);
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    /**
     * Toggle between light and dark themes
     */
    async toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.currentTheme = newTheme;
        this.applyTheme(newTheme);
        
        // Save theme preference
        await this.saveSettings({ theme: newTheme });
    }

    /**
     * Apply the specified theme to the application
     * @param {string} theme - Theme name ('light' or 'dark')
     */
    applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        
        // Update theme toggle icon
        const themeIcon = document.querySelector('.theme-icon');
        themeIcon.setAttribute('data-feather', theme === 'light' ? 'moon' : 'sun');
        feather.replace();
        
        console.log(`Applied ${theme} theme`);
    }

    /**
     * Save user settings to the backend
     * @param {Object} settings - Settings object to save
     */
    async saveSettings(settings) {
        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    /**
     * Check if credentials are configured
     */
    async checkCredentials() {
        try {
            const response = await fetch('/api/credentials');
            const data = await response.json();
            
            if (!data.has_credentials) {
                // Show credentials modal if not configured
                const modal = new bootstrap.Modal(document.getElementById('credentialsModal'));
                modal.show();
            } else {
                // Pre-fill username if available
                document.getElementById('username').value = data.username || '';
            }
        } catch (error) {
            console.error('Error checking credentials:', error);
        }
    }

    /**
     * Handle credentials form submission
     * @param {Event} e - Form submit event
     */
    async handleCredentialsSubmit(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if (!username || !password) {
            this.showNotification('Please enter both username and password', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/credentials', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Credentials saved successfully', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('credentialsModal'));
                modal.hide();
                
                // Clear password field for security
                document.getElementById('password').value = '';
            } else {
                this.showNotification(result.error || 'Failed to save credentials', 'danger');
            }
        } catch (error) {
            console.error('Error saving credentials:', error);
            this.showNotification('Error saving credentials', 'danger');
        }
    }

    /**
     * Load dashboards from the backend
     */
    async loadDashboards() {
        try {
            const response = await fetch('/api/dashboards');
            this.dashboards = await response.json();
            this.renderDashboards();
            this.updateDashboardCounts();
        } catch (error) {
            console.error('Error loading dashboards:', error);
            this.showNotification('Error loading dashboards', 'danger');
        }
    }

    /**
     * Load lists from the backend
     */
    async loadLists() {
        try {
            const response = await fetch('/api/lists');
            this.lists = await response.json();
            this.renderLists();
            this.updateListsInModals();
        } catch (error) {
            console.error('Error loading lists:', error);
            this.showNotification('Error loading lists', 'danger');
        }
    }

    /**
     * Load schedules from the backend
     */
    async loadSchedules() {
        try {
            const response = await fetch('/api/schedules');
            this.schedules = await response.json();
            this.renderSchedules();
        } catch (error) {
            console.error('Error loading schedules:', error);
            this.showNotification('Error loading schedules', 'danger');
        }
    }

    /**
     * Render dashboards in the table
     */
    renderDashboards() {
        const tbody = document.getElementById('dashboardTableBody');
        tbody.innerHTML = '';

        this.dashboards.forEach(dashboard => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="form-check-input dashboard-checkbox" 
                           data-dashboard-id="${dashboard.id}" 
                           ${this.selectedDashboards.has(dashboard.id) ? 'checked' : ''}>
                </td>
                <td>
                    <strong>${this.escapeHtml(dashboard.name)}</strong>
                </td>
                <td>
                    <a href="${dashboard.url}" target="_blank" class="text-decoration-none">
                        ${this.truncateUrl(dashboard.url)}
                        <i data-feather="external-link" class="icon-sm ms-1"></i>
                    </a>
                </td>
                <td>
                    ${dashboard.lists.map(list => 
                        `<span class="badge bg-primary me-1">${this.escapeHtml(list)}</span>`
                    ).join('')}
                </td>
                <td>
                    <span class="badge ${this.getStatusClass(dashboard.status)}">
                        ${dashboard.status}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="app.editDashboard('${dashboard.id}')" title="Edit">
                            <i data-feather="edit-2" class="icon-sm"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="app.deleteDashboard('${dashboard.id}')" title="Delete">
                            <i data-feather="trash-2" class="icon-sm"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Re-initialize Feather icons
        feather.replace();

        // Add event listeners for checkboxes
        document.querySelectorAll('.dashboard-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleDashboardSelection(e.target.dataset.dashboardId, e.target.checked);
            });
        });
    }

    /**
     * Render lists in the sidebar
     */
    renderLists() {
        const container = document.getElementById('listFilter');
        
        // Keep the "All Dashboards" item and add other lists
        const allItem = container.querySelector('[data-filter="all"]');
        container.innerHTML = '';
        container.appendChild(allItem);

        this.lists.forEach(list => {
            const listItem = document.createElement('a');
            listItem.href = '#';
            listItem.className = 'list-group-item list-group-item-action';
            listItem.setAttribute('data-filter', list);
            listItem.innerHTML = `
                <i data-feather="folder" class="me-2 icon-sm"></i>
                ${this.escapeHtml(list)}
                <span class="badge bg-primary rounded-pill float-end" id="count-${list}">0</span>
            `;
            container.appendChild(listItem);
        });

        feather.replace();
        this.updateDashboardCounts();
    }

    /**
     * Render schedules in the table
     */
    renderSchedules() {
        const tbody = document.getElementById('scheduleTableBody');
        tbody.innerHTML = '';

        if (this.schedules.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        <i data-feather="calendar" class="me-2"></i>
                        No schedules created yet
                    </td>
                </tr>
            `;
            feather.replace();
            return;
        }

        this.schedules.forEach(schedule => {
            const dashboardNames = schedule.dashboard_ids
                .map(id => {
                    const dashboard = this.dashboards.find(d => d.id === id);
                    return dashboard ? dashboard.name : 'Unknown';
                })
                .join(', ');

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <strong>${this.escapeHtml(schedule.name)}</strong>
                </td>
                <td>
                    <small class="text-muted">${this.truncateText(dashboardNames, 50)}</small>
                </td>
                <td>
                    <span class="badge bg-info">${schedule.schedule_type}</span>
                    <br>
                    <small class="text-muted">${this.formatDateTime(schedule.schedule_time)}</small>
                </td>
                <td>
                    <span class="badge ${schedule.active ? 'bg-success' : 'bg-secondary'}">
                        ${schedule.active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="app.editSchedule('${schedule.id}')" title="Edit">
                            <i data-feather="edit-2" class="icon-sm"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="app.toggleSchedule('${schedule.id}')" 
                                title="${schedule.active ? 'Deactivate' : 'Activate'}">
                            <i data-feather="${schedule.active ? 'pause' : 'play'}" class="icon-sm"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="app.deleteSchedule('${schedule.id}')" title="Delete">
                            <i data-feather="trash-2" class="icon-sm"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        feather.replace();
    }

    /**
     * Update lists in modal dialogs
     */
    updateListsInModals() {
        // Update dashboard modal lists
        const dashboardLists = document.getElementById('dashboardLists');
        dashboardLists.innerHTML = '';

        this.lists.forEach(list => {
            const checkbox = document.createElement('div');
            checkbox.className = 'form-check';
            checkbox.innerHTML = `
                <input class="form-check-input" type="checkbox" value="${list}" id="list-${list}">
                <label class="form-check-label" for="list-${list}">
                    ${this.escapeHtml(list)}
                </label>
            `;
            dashboardLists.appendChild(checkbox);
        });

        // Update schedule modal dashboards
        const scheduleDashboards = document.getElementById('scheduleDashboards');
        scheduleDashboards.innerHTML = '';

        this.dashboards.forEach(dashboard => {
            const checkbox = document.createElement('div');
            checkbox.className = 'form-check';
            checkbox.innerHTML = `
                <input class="form-check-input" type="checkbox" value="${dashboard.id}" id="schedule-dashboard-${dashboard.id}">
                <label class="form-check-label" for="schedule-dashboard-${dashboard.id}">
                    <strong>${this.escapeHtml(dashboard.name)}</strong>
                    <br>
                    <small class="text-muted">${this.truncateUrl(dashboard.url)}</small>
                </label>
            `;
            scheduleDashboards.appendChild(checkbox);
        });
    }

    /**
     * Handle dashboard addition form submission
     * @param {Event} e - Form submit event
     */
    async handleAddDashboard(e) {
        e.preventDefault();
        
        const name = document.getElementById('dashboardName').value.trim();
        const url = document.getElementById('dashboardUrl').value.trim();
        
        // Get selected lists
        const selectedLists = Array.from(document.querySelectorAll('#dashboardLists input:checked'))
            .map(input => input.value);

        if (!name || !url) {
            this.showNotification('Please enter dashboard name and URL', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/dashboards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    url: url,
                    lists: selectedLists
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Dashboard added successfully', 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('addDashboardModal'));
                modal.hide();
                document.getElementById('addDashboardForm').reset();
                
                // Reload dashboards
                await this.loadDashboards();
            } else {
                this.showNotification(result.error || 'Failed to add dashboard', 'danger');
            }
        } catch (error) {
            console.error('Error adding dashboard:', error);
            this.showNotification('Error adding dashboard', 'danger');
        }
    }

    /**
     * Handle list addition form submission
     * @param {Event} e - Form submit event
     */
    async handleAddList(e) {
        e.preventDefault();
        
        const name = document.getElementById('listName').value.trim();
        
        if (!name) {
            this.showNotification('Please enter list name', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/lists', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('List created successfully', 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('addListModal'));
                modal.hide();
                document.getElementById('addListForm').reset();
                
                // Reload lists
                await this.loadLists();
            } else {
                this.showNotification(result.error || 'Failed to create list', 'danger');
            }
        } catch (error) {
            console.error('Error creating list:', error);
            this.showNotification('Error creating list', 'danger');
        }
    }

    /**
     * Handle schedule addition form submission
     * @param {Event} e - Form submit event
     */
    async handleAddSchedule(e) {
        e.preventDefault();
        
        const name = document.getElementById('scheduleName').value.trim();
        const scheduleType = document.getElementById('scheduleType').value;
        const scheduleTime = document.getElementById('scheduleTime').value;
        const includeWatermark = document.getElementById('includeWatermark').checked;
        
        // Get selected dashboards
        const selectedDashboards = Array.from(document.querySelectorAll('#scheduleDashboards input:checked'))
            .map(input => input.value);

        if (!name || !scheduleTime || selectedDashboards.length === 0) {
            this.showNotification('Please fill in all required fields and select at least one dashboard', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/schedules', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    schedule_type: scheduleType,
                    schedule_time: scheduleTime,
                    dashboard_ids: selectedDashboards,
                    include_watermark: includeWatermark,
                    time_range: this.getCurrentTimeRange()
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Schedule created successfully', 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('addScheduleModal'));
                modal.hide();
                document.getElementById('addScheduleForm').reset();
                
                // Reload schedules
                await this.loadSchedules();
            } else {
                this.showNotification(result.error || 'Failed to create schedule', 'danger');
            }
        } catch (error) {
            console.error('Error creating schedule:', error);
            this.showNotification('Error creating schedule', 'danger');
        }
    }

    /**
     * Add new list from dashboard modal
     */
    async addNewListFromModal() {
        const newListName = document.getElementById('newListName').value.trim();
        
        if (!newListName) {
            this.showNotification('Please enter a list name', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/lists', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: newListName })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('List created successfully', 'success');
                document.getElementById('newListName').value = '';
                
                // Reload lists and update modals
                await this.loadLists();
                
                // Auto-select the newly created list
                const newCheckbox = document.querySelector(`#list-${newListName}`);
                if (newCheckbox) {
                    newCheckbox.checked = true;
                }
            } else {
                this.showNotification(result.error || 'Failed to create list', 'danger');
            }
        } catch (error) {
            console.error('Error creating list:', error);
            this.showNotification('Error creating list', 'danger');
        }
    }

    /**
     * Start screenshot capture process
     * @param {boolean} includeWatermark - Whether to include watermark
     */
    async startScreenshotCapture(includeWatermark) {
        const selectedIds = Array.from(this.selectedDashboards);
        
        if (selectedIds.length === 0) {
            this.showNotification('Please select at least one dashboard', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/screenshot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dashboard_ids: selectedIds,
                    include_watermark: includeWatermark,
                    time_range: this.getCurrentTimeRange()
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(
                    `Screenshot capture started for ${selectedIds.length} dashboard(s)`, 
                    'info'
                );
                this.showProgressModal('Screenshot Capture', 'Starting screenshot capture...');
            } else {
                this.showNotification(result.error || 'Failed to start screenshot capture', 'danger');
            }
        } catch (error) {
            console.error('Error starting screenshot capture:', error);
            this.showNotification('Error starting screenshot capture', 'danger');
        }
    }

    /**
     * Toggle dashboard selection
     * @param {string} dashboardId - Dashboard ID
     * @param {boolean} selected - Selection state
     */
    toggleDashboardSelection(dashboardId, selected) {
        if (selected) {
            this.selectedDashboards.add(dashboardId);
        } else {
            this.selectedDashboards.delete(dashboardId);
        }
        
        this.updateSelectionUI();
    }

    /**
     * Select all dashboards
     */
    selectAllDashboards() {
        this.dashboards.forEach(dashboard => {
            this.selectedDashboards.add(dashboard.id);
        });
        
        // Update checkboxes
        document.querySelectorAll('.dashboard-checkbox').forEach(checkbox => {
            checkbox.checked = true;
        });
        
        this.updateSelectionUI();
    }

    /**
     * Toggle all dashboards selection
     * @param {boolean} selectAll - Whether to select all
     */
    toggleAllDashboards(selectAll) {
        if (selectAll) {
            this.selectAllDashboards();
        } else {
            this.selectedDashboards.clear();
            document.querySelectorAll('.dashboard-checkbox').forEach(checkbox => {
                checkbox.checked = false;
            });
        }
        
        this.updateSelectionUI();
    }

    /**
     * Delete selected dashboards
     */
    async deleteSelectedDashboards() {
        const selectedIds = Array.from(this.selectedDashboards);
        
        if (selectedIds.length === 0) {
            this.showNotification('Please select at least one dashboard to delete', 'warning');
            return;
        }

        if (!confirm(`Are you sure you want to delete ${selectedIds.length} dashboard(s)?`)) {
            return;
        }

        try {
            const response = await fetch('/api/dashboards', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ids: selectedIds })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`Deleted ${selectedIds.length} dashboard(s)`, 'success');
                this.selectedDashboards.clear();
                await this.loadDashboards();
            } else {
                this.showNotification(result.error || 'Failed to delete dashboards', 'danger');
            }
        } catch (error) {
            console.error('Error deleting dashboards:', error);
            this.showNotification('Error deleting dashboards', 'danger');
        }
    }

    /**
     * Update selection UI elements
     */
    updateSelectionUI() {
        const selectedCount = this.selectedDashboards.size;
        const totalCount = this.dashboards.length;
        
        // Update master checkbox
        const masterCheckbox = document.getElementById('selectAllCheckbox');
        masterCheckbox.checked = selectedCount === totalCount && totalCount > 0;
        masterCheckbox.indeterminate = selectedCount > 0 && selectedCount < totalCount;
    }

    /**
     * Update dashboard counts for each list
     */
    updateDashboardCounts() {
        // Update "All Dashboards" count
        const allCountElement = document.getElementById('allCount');
        if (allCountElement) {
            allCountElement.textContent = this.dashboards.length;
        }

        // Update individual list counts
        this.lists.forEach(list => {
            const countElement = document.getElementById(`count-${list}`);
            if (countElement) {
                const count = this.dashboards.filter(dashboard => 
                    dashboard.lists.includes(list)
                ).length;
                countElement.textContent = count;
            }
        });
    }

    /**
     * Filter dashboards by list
     * @param {string} filter - Filter criteria
     */
    filterDashboards(filter) {
        // Update active list item
        document.querySelectorAll('[data-filter]').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

        // Filter and render dashboards
        const filteredDashboards = filter === 'all' 
            ? this.dashboards 
            : this.dashboards.filter(dashboard => dashboard.lists.includes(filter));

        this.renderFilteredDashboards(filteredDashboards);
    }

    /**
     * Render filtered dashboards
     * @param {Array} dashboards - Dashboards to render
     */
    renderFilteredDashboards(dashboards) {
        const tbody = document.getElementById('dashboardTableBody');
        tbody.innerHTML = '';

        dashboards.forEach(dashboard => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="form-check-input dashboard-checkbox" 
                           data-dashboard-id="${dashboard.id}" 
                           ${this.selectedDashboards.has(dashboard.id) ? 'checked' : ''}>
                </td>
                <td>
                    <strong>${this.escapeHtml(dashboard.name)}</strong>
                </td>
                <td>
                    <a href="${dashboard.url}" target="_blank" class="text-decoration-none">
                        ${this.truncateUrl(dashboard.url)}
                        <i data-feather="external-link" class="icon-sm ms-1"></i>
                    </a>
                </td>
                <td>
                    ${dashboard.lists.map(list => 
                        `<span class="badge bg-primary me-1">${this.escapeHtml(list)}</span>`
                    ).join('')}
                </td>
                <td>
                    <span class="badge ${this.getStatusClass(dashboard.status)}">
                        ${dashboard.status}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="app.editDashboard('${dashboard.id}')" title="Edit">
                            <i data-feather="edit-2" class="icon-sm"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="app.deleteDashboard('${dashboard.id}')" title="Delete">
                            <i data-feather="trash-2" class="icon-sm"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        feather.replace();

        // Re-add event listeners for checkboxes
        document.querySelectorAll('.dashboard-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleDashboardSelection(e.target.dataset.dashboardId, e.target.checked);
            });
        });
    }

    /**
     * Handle time range selection change
     * @param {string} preset - Selected preset
     */
    handleTimeRangeChange(preset) {
        const customRange = document.getElementById('customTimeRange');
        
        if (preset === 'custom') {
            customRange.style.display = 'block';
        } else {
            customRange.style.display = 'none';
        }
    }

    /**
     * Get current time range settings
     * @returns {Object} Time range configuration
     */
    getCurrentTimeRange() {
        const preset = document.getElementById('timeRangePreset').value;
        
        if (preset === 'custom') {
            return {
                type: 'custom',
                from: document.getElementById('timeFrom').value,
                to: document.getElementById('timeTo').value
            };
        } else {
            return {
                type: 'preset',
                preset: preset
            };
        }
    }

    /**
     * Show progress modal
     * @param {string} title - Modal title
     * @param {string} message - Initial message
     */
    showProgressModal(title, message) {
        document.querySelector('#progressModal .modal-title').textContent = title;
        document.getElementById('progressMessage').textContent = message;
        document.getElementById('progressBar').style.width = '0%';
        
        const modal = new bootstrap.Modal(document.getElementById('progressModal'));
        modal.show();
    }

    /**
     * Update progress modal
     * @param {number} progress - Progress percentage (0-100)
     * @param {string} message - Progress message
     */
    updateProgress(progress, message) {
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('progressMessage').textContent = message;
    }

    /**
     * Show notification toast
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, danger, warning, info)
     */
    showNotification(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
        
        console.log(`Notification: ${message} (${type})`);
    }

    /**
     * Utility function to escape HTML
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Utility function to truncate URL for display
     * @param {string} url - URL to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated URL
     */
    truncateUrl(url, maxLength = 50) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength - 3) + '...';
    }

    /**
     * Utility function to truncate text
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    truncateText(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    /**
     * Get CSS class for status badges
     * @param {string} status - Status string
     * @returns {string} CSS class
     */
    getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'ready': return 'bg-success';
            case 'processing': return 'bg-warning';
            case 'error': return 'bg-danger';
            case 'scheduled': return 'bg-info';
            default: return 'bg-secondary';
        }
    }

    /**
     * Format date/time for display
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date/time
     */
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    /**
     * Open schedule modal (placeholder for future implementation)
     */
    openScheduleModal() {
        const modal = new bootstrap.Modal(document.getElementById('addScheduleModal'));
        modal.show();
    }

    /**
     * Edit dashboard (placeholder for future implementation)
     * @param {string} dashboardId - Dashboard ID
     */
    editDashboard(dashboardId) {
        console.log('Edit dashboard:', dashboardId);
        this.showNotification('Dashboard editing will be implemented in a future version', 'info');
    }

    /**
     * Delete single dashboard
     * @param {string} dashboardId - Dashboard ID
     */
    async deleteDashboard(dashboardId) {
        if (!confirm('Are you sure you want to delete this dashboard?')) {
            return;
        }

        try {
            const response = await fetch('/api/dashboards', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ids: [dashboardId] })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Dashboard deleted successfully', 'success');
                this.selectedDashboards.delete(dashboardId);
                await this.loadDashboards();
            } else {
                this.showNotification(result.error || 'Failed to delete dashboard', 'danger');
            }
        } catch (error) {
            console.error('Error deleting dashboard:', error);
            this.showNotification('Error deleting dashboard', 'danger');
        }
    }

    /**
     * Edit schedule (placeholder for future implementation)
     * @param {string} scheduleId - Schedule ID
     */
    editSchedule(scheduleId) {
        console.log('Edit schedule:', scheduleId);
        this.showNotification('Schedule editing will be implemented in a future version', 'info');
    }

    /**
     * Toggle schedule active state
     * @param {string} scheduleId - Schedule ID
     */
    async toggleSchedule(scheduleId) {
        const schedule = this.schedules.find(s => s.id === scheduleId);
        if (!schedule) return;

        try {
            const response = await fetch('/api/schedules', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: scheduleId,
                    active: !schedule.active
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(
                    `Schedule ${schedule.active ? 'deactivated' : 'activated'}`, 
                    'success'
                );
                await this.loadSchedules();
            } else {
                this.showNotification(result.error || 'Failed to update schedule', 'danger');
            }
        } catch (error) {
            console.error('Error updating schedule:', error);
            this.showNotification('Error updating schedule', 'danger');
        }
    }

    /**
     * Delete schedule
     * @param {string} scheduleId - Schedule ID
     */
    async deleteSchedule(scheduleId) {
        if (!confirm('Are you sure you want to delete this schedule?')) {
            return;
        }

        try {
            const response = await fetch('/api/schedules', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: scheduleId })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Schedule deleted successfully', 'success');
                await this.loadSchedules();
            } else {
                this.showNotification(result.error || 'Failed to delete schedule', 'danger');
            }
        } catch (error) {
            console.error('Error deleting schedule:', error);
            this.showNotification('Error deleting schedule', 'danger');
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SplunkAutomator();
});
