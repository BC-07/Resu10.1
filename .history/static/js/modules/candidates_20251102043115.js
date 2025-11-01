// Candidates Module
const CandidatesModule = {
    candidatesContent: null,
    modal: null,
    searchInput: null,
    sortSelect: null,
    filterSelect: null,
    candidatesData: null,
    selectedCandidates: new Set(),
    isLoading: false,

    // Initialize candidates functionality
    init() {
        this.setupElements();
        this.setupEventListeners();
        this.initializeFilters();
    },

    // Setup DOM elements
    setupElements() {
        this.candidatesContent = document.getElementById('candidatesContent');
        this.searchInput = document.getElementById('candidateSearch');
        this.sortSelect = document.getElementById('candidateSort');
        this.filterSelect = document.getElementById('candidateFilter');
        
        if (document.getElementById('candidateDetailsModal')) {
            this.modal = new bootstrap.Modal(document.getElementById('candidateDetailsModal'));
        }
    },

    // Setup event listeners
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshCandidates');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadCandidates();
            });
        }

        // Export button
        const exportBtn = document.getElementById('exportCandidates');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportCandidates();
            });
        }

        // Search functionality
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(() => {
                this.filterAndDisplayCandidates();
            }, 300));
        }

        // Sort functionality
        if (this.sortSelect) {
            this.sortSelect.addEventListener('change', () => {
                this.filterAndDisplayCandidates();
            });
        }

        // Filter functionality
        if (this.filterSelect) {
            this.filterSelect.addEventListener('change', () => {
                this.filterAndDisplayCandidates();
            });
        }

        // Clear filters
        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Bulk actions
        const bulkActionsBtn = document.getElementById('bulkActions');
        if (bulkActionsBtn) {
            bulkActionsBtn.addEventListener('click', () => {
                this.showBulkActionsMenu();
            });
        }

        // Modal action buttons
        this.setupModalActions();
    },

    // Initialize filters and controls
    initializeFilters() {
        // Set default values if elements exist
        if (this.sortSelect) {
            this.sortSelect.value = 'score-desc';
        }
        if (this.filterSelect) {
            this.filterSelect.value = 'all';
        }
    },

    // Debounce utility for search
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Load candidates from API
    async loadCandidates() {
        if (!this.candidatesContent) return;

        this.setLoadingState(true);

        try {
            const data = await APIService.candidates.getAll();
            
            if (data.success) {
                this.candidatesData = data.candidates_by_job;
                this.totalCandidates = data.total_candidates;
                this.filterAndDisplayCandidates();
                this.updateCandidateStats();
            } else {
                ToastUtils.showError('Failed to load candidates');
            }
        } catch (error) {
            console.error('Error loading candidates:', error);
            ToastUtils.showError('Error loading candidates');
        } finally {
            this.setLoadingState(false);
        }
    },

    // Filter and display candidates based on search, sort, and filter criteria
    filterAndDisplayCandidates() {
        if (!this.candidatesData) return;

        let filteredData = { ...this.candidatesData };
        const searchTerm = this.searchInput ? this.searchInput.value.toLowerCase().trim() : '';
        const sortBy = this.sortSelect ? this.sortSelect.value : 'score-desc';
        const statusFilter = this.filterSelect ? this.filterSelect.value : 'all';

        // Apply filters to each job category
        Object.keys(filteredData).forEach(jobId => {
            let candidates = filteredData[jobId].candidates;

            // Apply search filter
            if (searchTerm) {
                candidates = candidates.filter(candidate => 
                    candidate.name.toLowerCase().includes(searchTerm) ||
                    candidate.email.toLowerCase().includes(searchTerm) ||
                    candidate.predicted_category.toLowerCase().includes(searchTerm) ||
                    (candidate.all_skills || []).some(skill => 
                        skill.toLowerCase().includes(searchTerm)
                    )
                );
            }

            // Apply status filter
            if (statusFilter !== 'all') {
                candidates = candidates.filter(candidate => 
                    candidate.status.toLowerCase() === statusFilter
                );
            }

            // Apply sorting
            candidates = this.sortCandidates(candidates, sortBy);

            filteredData[jobId].candidates = candidates;
        });

        this.displayCandidatesByJob(filteredData, this.totalCandidates);
        this.setupCandidateActionListeners();
    },

    // Sort candidates based on criteria
    sortCandidates(candidates, sortBy) {
        return [...candidates].sort((a, b) => {
            switch (sortBy) {
                case 'name-asc':
                    return a.name.localeCompare(b.name);
                case 'name-desc':
                    return b.name.localeCompare(a.name);
                case 'score-asc':
                    return a.score - b.score;
                case 'score-desc':
                    return b.score - a.score;
                case 'category-asc':
                    return a.predicted_category.localeCompare(b.predicted_category);
                case 'category-desc':
                    return b.predicted_category.localeCompare(a.predicted_category);
                case 'status-asc':
                    return a.status.localeCompare(b.status);
                case 'status-desc':
                    return b.status.localeCompare(a.status);
                default:
                    return b.score - a.score; // Default to score desc
            }
        });
    },

    // Set loading state
    setLoadingState(isLoading) {
        this.isLoading = isLoading;
        const refreshBtn = document.getElementById('refreshCandidates');
        
        if (refreshBtn) {
            if (isLoading) {
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            } else {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync me-2"></i>Refresh';
            }
        }

        if (isLoading && this.candidatesContent) {
            this.candidatesContent.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin"></i>
                    </div>
                    <p>Loading candidates...</p>
                </div>
            `;
        }
    },

    // Update candidate statistics
    updateCandidateStats() {
        const statsContainer = document.getElementById('candidateStats');
        if (!statsContainer || !this.candidatesData) return;

        const totalCandidates = Object.values(this.candidatesData)
            .reduce((sum, job) => sum + job.candidates.length, 0);
        
        const statusCounts = {};
        Object.values(this.candidatesData).forEach(job => {
            job.candidates.forEach(candidate => {
                statusCounts[candidate.status] = (statusCounts[candidate.status] || 0) + 1;
            });
        });

        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">${totalCandidates}</div>
                    <div class="stat-label">Total Candidates</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${statusCounts.pending || 0}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${statusCounts.shortlisted || 0}</div>
                    <div class="stat-label">Shortlisted</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${statusCounts.rejected || 0}</div>
                    <div class="stat-label">Rejected</div>
                </div>
            </div>
        `;
    },

    // Display candidates grouped by job
    displayCandidatesByJob(candidatesByJob, totalCandidates) {
        this.candidatesContent.innerHTML = '';
        
        if (totalCandidates === 0) {
            this.candidatesContent.innerHTML = `
                <div class="no-candidates-message">
                    <div class="no-candidates-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h4>No Candidates Found</h4>
                    <p>Upload some PDS files in the "Upload Documents" section to see candidates here.</p>
                    <a href="#upload" class="btn btn-primary" onclick="NavigationModule.showSection('upload')">
                        <i class="fas fa-upload me-2"></i>Upload PDS Files
                    </a>
                </div>
            `;
            return;
        }
        
        // Create content for each job category
        Object.entries(candidatesByJob).forEach(([jobId, jobData]) => {
            if (jobData.candidates.length === 0) return;
            
            const jobSection = this.createJobSection(jobData);
            this.candidatesContent.appendChild(jobSection);
        });
    },

    // Create job section element
    createJobSection(jobData) {
        const jobSection = document.createElement('div');
        jobSection.className = 'job-section';
        
        // Handle LSPU job structure vs legacy/unassigned
        const isLSPUJob = jobData.position_title && jobData.campus_name;
        const jobTitle = isLSPUJob ? jobData.position_title : (jobData.job_title || 'Unassigned Candidates');
        const jobCategory = isLSPUJob ? jobData.position_category : (jobData.job_category || 'General');
        
        jobSection.innerHTML = `
            <div class="job-header">
                <h3 class="job-title">
                    <i class="fas fa-briefcase me-2"></i>
                    ${DOMUtils.escapeHtml(jobTitle)}
                </h3>
                <div class="job-meta">
                    <span class="badge bg-primary">${DOMUtils.escapeHtml(jobCategory)}</span>
                    ${isLSPUJob ? `<span class="badge bg-info">${DOMUtils.escapeHtml(jobData.campus_name)}</span>` : ''}
                    <span class="candidate-count">${jobData.candidates.length} candidate${jobData.candidates.length !== 1 ? 's' : ''}</span>
                </div>
            </div>
            ${isLSPUJob ? this.renderLSPUJobDetails(jobData) : this.renderBasicJobDetails(jobData)}
            <div class="candidates-table-container">
                <div class="table-responsive">
                    <table class="table table-hover candidates-table-compact">
                        <thead class="table-dark">
                            <tr>
                                <th class="checkbox-header">
                                    <input type="checkbox" class="select-all-candidates" title="Select All">
                                </th>
                                <th class="candidate-header">Candidate</th>
                                <th class="gov-ids-header">Government IDs</th>
                                <th class="education-level-header">Education Level</th>
                                <th class="civil-service-header">Civil Service Eligibility</th>
                                <th class="score-header">Assessment Score</th>
                                <th class="status-header">Status</th>
                                <th class="actions-header">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.renderCandidateRows(jobData.candidates)}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        return jobSection;
    },

    // Render LSPU job details with enhanced information
    renderLSPUJobDetails(jobData) {
        return `
            <div class="job-description lspu-job-details">
                <div class="row">
                    <div class="col-md-6">
                        <div class="job-detail-item">
                            <strong><i class="fas fa-building me-2"></i>Department:</strong> 
                            ${DOMUtils.escapeHtml(jobData.department_office || 'Not specified')}
                        </div>
                        <div class="job-detail-item">
                            <strong><i class="fas fa-map-marker-alt me-2"></i>Campus:</strong> 
                            ${DOMUtils.escapeHtml(jobData.campus_name)}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="job-detail-item">
                            <strong><i class="fas fa-money-bill-wave me-2"></i>Salary Grade:</strong> 
                            ${DOMUtils.escapeHtml(jobData.salary_grade || 'Not specified')}
                        </div>
                        <div class="job-detail-item">
                            <strong><i class="fas fa-tag me-2"></i>Position Type:</strong> 
                            ${DOMUtils.escapeHtml(jobData.position_category)}
                        </div>
                    </div>
                </div>
                ${jobData.job_description ? `
                    <div class="job-description-text mt-3">
                        <strong><i class="fas fa-info-circle me-2"></i>Description:</strong>
                        <p>${FormatUtils.truncateText(jobData.job_description, 300)}</p>
                    </div>
                ` : ''}
                ${jobData.job_requirements ? `
                    <div class="job-requirements mt-2">
                        <strong><i class="fas fa-list-check me-2"></i>Required Skills:</strong> 
                        ${DOMUtils.escapeHtml(jobData.job_requirements)}
                    </div>
                ` : ''}
            </div>
        `;
    },

    // Render basic job details for legacy/unassigned categories
    renderBasicJobDetails(jobData) {
        if (!jobData.job_description && !jobData.job_requirements) {
            return `
                <div class="job-description">
                    <p class="text-muted"><i class="fas fa-info-circle me-2"></i>Candidates not yet assigned to a specific LSPU job posting.</p>
                </div>
            `;
        }
        
        return `
            <div class="job-description">
                ${jobData.job_description ? `<p>${FormatUtils.truncateText(jobData.job_description, 200)}</p>` : ''}
                ${jobData.job_requirements ? `
                    <div class="job-requirements">
                        <strong>Required Skills:</strong> ${DOMUtils.escapeHtml(jobData.job_requirements)}
                    </div>
                ` : ''}
            </div>
        `;
    },

    // Render candidate table rows
    renderCandidateRows(candidates) {
        return candidates.map(candidate => {
            const assessmentScore = candidate.assessment_score || candidate.score || 0;
            const scoreClass = this.getScoreColorClass(assessmentScore);
            const statusClass = `status-${candidate.status.toLowerCase()}`;
            const isSelected = this.selectedCandidates.has(candidate.id);
            const processingTypeLabel = this.getProcessingTypeLabel(candidate.processing_type, candidate.ocr_confidence);
            
            // Extract PDS-specific data with fallbacks
            const governmentIds = this.formatGovernmentIds(candidate);
            const educationLevel = this.getHighestEducationLevel(candidate);
            const civilServiceEligibility = this.formatCivilServiceEligibility(candidate);
            const assessmentScoreFormatted = this.formatAssessmentScore(candidate);
            
            return `
                <tr data-candidate-id="${candidate.id}" class="candidate-row ${isSelected ? 'selected' : ''}" onclick="CandidatesModule.showCandidateDetails('${candidate.id}')">
                    <td class="checkbox-column">
                        <input type="checkbox" class="candidate-checkbox" 
                               ${isSelected ? 'checked' : ''} 
                               data-candidate-id="${candidate.id}"
                               onclick="event.stopPropagation()">
                    </td>
                    <td class="candidate-column">
                        <div class="candidate-compact">
                            <div class="candidate-avatar">
                                <i class="fas fa-user-circle"></i>
                            </div>
                            <div class="candidate-info">
                                <div class="candidate-name">${DOMUtils.escapeHtml(candidate.name)}</div>
                                <div class="candidate-meta">
                                    <span class="candidate-email">${DOMUtils.escapeHtml(candidate.email)}</span>
                                    <span class="candidate-phone">${DOMUtils.escapeHtml(candidate.phone || 'No phone')}</span>
                                </div>
                                <div class="candidate-education">
                                    ${FormatUtils.truncateText(candidate.education, 60)}
                                </div>
                                <div class="processing-type-label">
                                    ${processingTypeLabel}
                                </div>
                            </div>
                        </div>
                    </td>
                    <td class="gov-ids-column">
                        <div class="gov-ids-compact">
                            ${governmentIds}
                        </div>
                    </td>
                    <td class="education-level-column">
                        <div class="education-level-compact">
                            <span class="education-badge">${educationLevel}</span>
                        </div>
                    </td>
                    <td class="civil-service-column">
                        <div class="civil-service-compact">
                            ${civilServiceEligibility}
                        </div>
                    </td>
                    <td class="score-column">
                        <div class="score-compact">
                            <span class="score-badge ${scoreClass}">${assessmentScoreFormatted}</span>
                            <div class="score-bar-mini">
                                <div class="score-fill ${scoreClass}" style="width: ${assessmentScore}%"></div>
                            </div>
                        </div>
                    </td>
                    <td class="status-column">
                        <span class="status-badge ${statusClass}">${candidate.status}</span>
                    </td>
                    <td class="actions-column">
                        <div class="action-buttons-compact">
                            <button class="btn btn-sm btn-outline-success shortlist-candidate" 
                                    title="Shortlist" onclick="event.stopPropagation(); CandidatesModule.updateCandidateStatus('${candidate.id}', 'shortlisted')">
                                <i class="fas fa-star"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger reject-candidate" 
                                    title="Reject" onclick="event.stopPropagation(); CandidatesModule.updateCandidateStatus('${candidate.id}', 'rejected')">
                                <i class="fas fa-times"></i>
                            </button>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                        data-bs-toggle="dropdown" title="More" onclick="event.stopPropagation()">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    <li><button class="dropdown-item view-candidate" onclick="CandidatesModule.showCandidateDetails('${candidate.id}')">
                                        <i class="fas fa-eye me-2"></i>View Details</button></li>
                                    <li><button class="dropdown-item shortlist-candidate" onclick="CandidatesModule.updateCandidateStatus('${candidate.id}', 'pending')">
                                        <i class="fas fa-clock me-2"></i>Set Pending</button></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><button class="dropdown-item remove-candidate text-danger" onclick="CandidatesModule.handleRemoveCandidate('${candidate.id}')">
                                        <i class="fas fa-trash me-2"></i>Remove</button></li>
                                </ul>
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },

    // Setup candidate action listeners
    setupCandidateActionListeners() {
        if (!this.candidatesContent) return;

        // Individual candidate checkboxes
        this.candidatesContent.addEventListener('change', (e) => {
            if (e.target.classList.contains('candidate-checkbox')) {
                const candidateId = e.target.dataset.candidateId;
                const candidateRow = e.target.closest('.candidate-row');
                
                if (e.target.checked) {
                    this.selectedCandidates.add(candidateId);
                    candidateRow.classList.add('selected');
                } else {
                    this.selectedCandidates.delete(candidateId);
                    candidateRow.classList.remove('selected');
                }
                
                this.updateBulkActionsVisibility();
                this.updateSelectAllState();
            }
        });

        // Select all checkboxes
        this.candidatesContent.addEventListener('change', (e) => {
            if (e.target.classList.contains('select-all-candidates')) {
                const table = e.target.closest('table');
                const checkboxes = table.querySelectorAll('.candidate-checkbox');
                const isChecked = e.target.checked;
                
                checkboxes.forEach(checkbox => {
                    const candidateId = checkbox.dataset.candidateId;
                    const candidateRow = checkbox.closest('.candidate-row');
                    
                    checkbox.checked = isChecked;
                    
                    if (isChecked) {
                        this.selectedCandidates.add(candidateId);
                        candidateRow.classList.add('selected');
                    } else {
                        this.selectedCandidates.delete(candidateId);
                        candidateRow.classList.remove('selected');
                    }
                });
                
                this.updateBulkActionsVisibility();
            }
        });

        // Candidate actions
        this.candidatesContent.addEventListener('click', async (e) => {
            const candidateRow = e.target.closest('.candidate-row');
            if (!candidateRow) return;
            
            const candidateId = candidateRow.dataset.candidateId;
            
            // Prevent row click when interacting with controls
            if (e.target.closest('.candidate-checkbox') || 
                e.target.closest('.action-buttons-compact') ||
                e.target.closest('.dropdown-menu')) {
                return;
            }
            
            // Handle button clicks
            if (e.target.closest('.view-candidate')) {
                e.stopPropagation();
                await this.showCandidateDetails(candidateId);
            } else if (e.target.closest('.shortlist-candidate')) {
                e.stopPropagation();
                await this.updateCandidateStatus(candidateId, 'shortlisted');
            } else if (e.target.closest('.reject-candidate')) {
                e.stopPropagation();
                await this.updateCandidateStatus(candidateId, 'rejected');
            } else if (e.target.closest('.remove-candidate')) {
                e.stopPropagation();
                const confirmed = await confirmRemove('this candidate');
                if (confirmed) {
                    await this.removeCandidate(candidateId);
                }
            }
            // Row click is handled by onclick attribute in the HTML for better performance
        });
    },

    // Update bulk actions visibility
    updateBulkActionsVisibility() {
        const bulkActionsContainer = document.getElementById('bulkActionsContainer');
        const selectedCount = this.selectedCandidates.size;
        
        if (bulkActionsContainer) {
            if (selectedCount > 0) {
                bulkActionsContainer.style.display = 'block';
                bulkActionsContainer.querySelector('.selected-count').textContent = selectedCount;
            } else {
                bulkActionsContainer.style.display = 'none';
            }
        }
    },

    // Update select all checkbox state
    updateSelectAllState() {
        const selectAllCheckboxes = this.candidatesContent.querySelectorAll('.select-all-candidates');
        
        selectAllCheckboxes.forEach(selectAll => {
            const table = selectAll.closest('table');
            const allCheckboxes = table.querySelectorAll('.candidate-checkbox');
            const checkedCheckboxes = table.querySelectorAll('.candidate-checkbox:checked');
            
            if (checkedCheckboxes.length === 0) {
                selectAll.indeterminate = false;
                selectAll.checked = false;
            } else if (checkedCheckboxes.length === allCheckboxes.length) {
                selectAll.indeterminate = false;
                selectAll.checked = true;
            } else {
                selectAll.indeterminate = true;
                selectAll.checked = false;
            }
        });
    },

    // Show bulk actions menu
    showBulkActionsMenu() {
        if (this.selectedCandidates.size === 0) {
            ToastUtils.showWarning('Please select candidates first');
            return;
        }

        // Create bulk actions modal or dropdown
        const actions = [
            { id: 'bulk-shortlist', label: 'Shortlist Selected', icon: 'fas fa-star', action: () => this.bulkUpdateStatus('shortlisted') },
            { id: 'bulk-reject', label: 'Reject Selected', icon: 'fas fa-times', action: () => this.bulkUpdateStatus('rejected') },
            { id: 'bulk-pending', label: 'Set as Pending', icon: 'fas fa-clock', action: () => this.bulkUpdateStatus('pending') },
            { id: 'bulk-remove', label: 'Remove Selected', icon: 'fas fa-trash', action: () => this.bulkRemoveCandidates(), className: 'text-danger' }
        ];

        // You can implement a proper modal here or use a simple confirm approach
        this.showBulkActionsDialog(actions);
    },

    // Show bulk actions dialog
    showBulkActionsDialog(actions) {
        const selectedCount = this.selectedCandidates.size;
        let actionsHtml = actions.map(action => 
            `<button class="dropdown-item ${action.className || ''}" data-action="${action.id}">
                <i class="${action.icon} me-2"></i>${action.label}
            </button>`
        ).join('');

        // Simple implementation using browser confirm - you can enhance this with a proper modal
        const actionChoice = prompt(`Selected ${selectedCount} candidates. Choose action:\n1. Shortlist\n2. Reject\n3. Set as Pending\n4. Remove\n\nEnter number (1-4):`);
        
        switch(actionChoice) {
            case '1':
                this.bulkUpdateStatus('shortlisted');
                break;
            case '2':
                this.bulkUpdateStatus('rejected');
                break;
            case '3':
                this.bulkUpdateStatus('pending');
                break;
            case '4':
                this.bulkRemoveCandidates();
                break;
        }
    },

    // Bulk update candidate status
    async bulkUpdateStatus(status) {
        const selectedIds = Array.from(this.selectedCandidates);
        const updatePromises = selectedIds.map(id => this.updateCandidateStatus(id, status, false));
        
        try {
            await Promise.all(updatePromises);
            ToastUtils.showSuccess(`${selectedIds.length} candidates updated to ${status}`);
            this.selectedCandidates.clear();
            this.updateBulkActionsVisibility();
            await this.loadCandidates();
        } catch (error) {
            ToastUtils.showError('Some candidates could not be updated');
        }
    },

    // Bulk remove candidates
    async bulkRemoveCandidates() {
        const selectedIds = Array.from(this.selectedCandidates);
        const confirmed = await confirmRemove(`${selectedIds.length} candidates`);
        
        if (!confirmed) return;

        const removePromises = selectedIds.map(id => this.removeCandidate(id, false));
        
        try {
            await Promise.all(removePromises);
            ToastUtils.showSuccess(`${selectedIds.length} candidates removed`);
            this.selectedCandidates.clear();
            this.updateBulkActionsVisibility();
            await this.loadCandidates();
        } catch (error) {
            ToastUtils.showError('Some candidates could not be removed');
        }
    },

    // Export candidates
    async exportCandidates() {
        try {
            ToastUtils.showInfo('Preparing export...');
            
            // Prepare export data
            const exportData = [];
            Object.values(this.candidatesData || {}).forEach(jobData => {
                jobData.candidates.forEach(candidate => {
                    // Handle LSPU job structure vs legacy/unassigned
                    const isLSPUJob = jobData.position_title && jobData.campus_name;
                    
                    const exportRow = {
                        name: candidate.name,
                        email: candidate.email,
                        phone: candidate.phone || '',
                        education: candidate.education,
                        skills: candidate.all_skills.join(', '),
                        predicted_category: candidate.predicted_category,
                        match_score: candidate.score,
                        status: candidate.status
                    };
                    
                    // Add LSPU-specific fields or legacy fields
                    if (isLSPUJob) {
                        exportRow.position_title = jobData.position_title;
                        exportRow.position_category = jobData.position_category;
                        exportRow.campus_name = jobData.campus_name;
                        exportRow.department_office = jobData.department_office || '';
                        exportRow.salary_grade = jobData.salary_grade || '';
                    } else {
                        exportRow.job_title = jobData.job_title || 'Unassigned';
                        exportRow.job_category = jobData.job_category || 'General';
                        exportRow.campus_name = '';
                        exportRow.department_office = '';
                        exportRow.salary_grade = '';
                    }
                    
                    exportData.push(exportRow);
                });
            });

            // Convert to CSV
            const csvContent = this.arrayToCSV(exportData);
            
            // Download file
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `candidates_export_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            ToastUtils.showSuccess('Candidates exported successfully');
        } catch (error) {
            console.error('Export error:', error);
            ToastUtils.showError('Failed to export candidates');
        }
    },

    // Clear all filters
    clearFilters() {
        if (this.searchInput) this.searchInput.value = '';
        if (this.sortSelect) this.sortSelect.value = 'score-desc';
        if (this.filterSelect) this.filterSelect.value = 'all';
        this.selectedCandidates.clear();
        this.updateBulkActionsVisibility();
        this.filterAndDisplayCandidates();
    },

    // Convert array to CSV
    arrayToCSV(data) {
        if (!data.length) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [];
        
        // Add header row
        csvRows.push(headers.map(header => `"${header}"`).join(','));
        
        // Add data rows
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header] || '';
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    },

    // Show candidate details modal
    async showCandidateDetails(candidateId) {
        if (!this.modal) return;

        try {
            const data = await APIService.candidates.getById(candidateId);
            
            if (data.success) {
                const candidate = data.candidate;
                this.populateModal(candidate);
                this.modal.show();
            } else {
                ToastUtils.showError('Failed to load candidate details');
            }
        } catch (error) {
            console.error('Error loading candidate details:', error);
            ToastUtils.showError('Error loading candidate details');
        }
    },

    // Populate modal with candidate data
    populateModal(candidate) {
        console.log('🎯 Populating modal for candidate:', candidate);
        
        // Enhanced basic info with fallbacks
        let candidateName = candidate.name || 'Unknown';
        let candidateEmail = candidate.email || '';
        let candidatePhone = candidate.phone || '';
        
        // If we have PDS data, try to get better information
        if (candidate.pds_data && candidate.pds_data.personal_info) {
            const personalInfo = candidate.pds_data.personal_info;
            
            // Better name extraction
            if (personalInfo.full_name && 
                personalInfo.full_name.trim() !== '' && 
                personalInfo.full_name.toLowerCase() !== 'n/a') {
                candidateName = personalInfo.full_name.replace(/\s+N\/a$/i, '').trim();
            } else {
                const nameParts = [
                    personalInfo.first_name,
                    personalInfo.middle_name,
                    personalInfo.surname,
                    personalInfo.name_extension
                ].filter(part => part && 
                          part.trim() !== '' && 
                          part.toLowerCase() !== 'n/a');
                
                if (nameParts.length > 0) {
                    candidateName = nameParts.join(' ');
                }
            }
            
            // Better email extraction
            if (personalInfo.email && 
                personalInfo.email.trim() !== '' && 
                personalInfo.email.toLowerCase() !== 'n/a') {
                candidateEmail = personalInfo.email;
            }
            
            // Better phone extraction
            if (personalInfo.mobile_no && 
                personalInfo.mobile_no.trim() !== '' && 
                personalInfo.mobile_no.toLowerCase() !== 'n/a') {
                candidatePhone = personalInfo.mobile_no;
            } else if (personalInfo.telephone_no && 
                       personalInfo.telephone_no.trim() !== '' && 
                       personalInfo.telephone_no.toLowerCase() !== 'n/a') {
                candidatePhone = personalInfo.telephone_no;
            }
        }
        
        console.log('👤 Final header info:', {
            name: candidateName,
            email: candidateEmail,
            phone: candidatePhone
        });
        
        // Set header information
        document.querySelector('#candidateDetailsModal .candidate-name').textContent = candidateName;
        document.querySelector('#candidateDetailsModal .email').textContent = candidateEmail || 'N/A';
        document.querySelector('#candidateDetailsModal .phone').textContent = candidatePhone || 'N/A';
        
        // Initialize score circle with loading state
        const scoreCircle = document.querySelector('#candidateDetailsModal .score-circle');
        scoreCircle.className = `score-circle score-loading`;
        scoreCircle.querySelector('.score-value').textContent = '...';
        
        // Fetch assessment data to show actual assessment score instead of match score
        this.fetchAssessmentData(candidate.id).then(assessmentData => {
            if (assessmentData) {
                const overallTotal = assessmentData.overall_total || 0;
                scoreCircle.className = `score-circle ${this.getScoreColorClass(overallTotal)}`;
                scoreCircle.querySelector('.score-value').textContent = `${overallTotal}`;
            } else {
                // Fallback to match score if assessment not available
                scoreCircle.className = `score-circle ${this.getScoreColorClass(candidate.matchScore)}`;
                scoreCircle.querySelector('.score-value').textContent = `${candidate.matchScore}%`;
            }
        }).catch(error => {
            console.error('Error fetching assessment score:', error);
            // Fallback to match score if error
            scoreCircle.className = `score-circle ${this.getScoreColorClass(candidate.matchScore)}`;
            scoreCircle.querySelector('.score-value').textContent = `${candidate.matchScore}%`;
        });
        
        // Check if this is a PDS candidate (legacy or new comprehensive system)
        console.log('Candidate data:', candidate); // Debug log
        console.log('Processing type:', candidate.processing_type); // Debug log
        console.log('PDS data exists:', !!candidate.pds_data); // Debug log
        
        const isPDS = candidate.processing_type === 'pds' || 
                     candidate.processing_type === 'comprehensive_pds_extraction' ||
                     candidate.processing_type === 'pds_extraction_fallback' ||
                     (candidate.pds_data && Object.keys(candidate.pds_data).length > 0);
        const pdsSection = document.querySelector('#candidateDetailsModal .pds-sections');
        
        console.log('Is PDS candidate:', isPDS); // Debug log
        
        // Hide/show sections based on candidate type
        if (isPDS) {
            pdsSection.style.display = 'block';
            this.populatePDSData(candidate);
            
            // Hide legacy resume sections for PDS candidates
            this.hideLegacySections();
        } else {
            pdsSection.style.display = 'none';
            
            // Show legacy resume sections for regular candidates
            this.showLegacySections();
            
            // Populate legacy sections
            this.populateLegacySections(candidate);
        }
        
        // Set up action buttons (common for both types)
        this.setupActionButtons(candidate);
    },

    // Hide legacy resume sections for PDS candidates
    hideLegacySections() {
        const legacySections = [
            '.skills-section',
            '.education-section', 
            '.experience-section',
            '.certifications-section',
            '.scoring-section',
            '.matched-skills-section',
            '.missing-skills-section'
        ];
        
        legacySections.forEach(selector => {
            const section = document.querySelector(`#candidateDetailsModal ${selector}`);
            if (section) {
                section.style.display = 'none';
            }
        });
    },

    // Show legacy resume sections for regular candidates
    showLegacySections() {
        const legacySections = [
            '.skills-section',
            '.education-section', 
            '.experience-section',
            '.certifications-section',
            '.scoring-section',
            '.matched-skills-section',
            '.missing-skills-section'
        ];
        
        legacySections.forEach(selector => {
            const section = document.querySelector(`#candidateDetailsModal ${selector}`);
            if (section) {
                section.style.display = 'block';
            }
        });
    },

    // Populate legacy sections for regular candidates
    populateLegacySections(candidate) {
        const skillsContainer = document.querySelector('#candidateDetailsModal .skills-container');
        if (candidate.skills && candidate.skills.length > 0) {
            skillsContainer.innerHTML = candidate.skills.map(skill => 
                `<span class="skill-badge">${DOMUtils.escapeHtml(skill)}</span>`
            ).join('');
        } else {
            skillsContainer.innerHTML = '<p>No skills information available</p>';
        }
        
        // Education (for non-PDS candidates or additional education info)
        const educationContainer = document.querySelector('#candidateDetailsModal .education-container');
        if (candidate.education && candidate.education.length > 0) {
            educationContainer.innerHTML = candidate.education.map(edu => `
                <div class="education-item">
                    <h6>${DOMUtils.escapeHtml(edu.degree || 'Unknown Degree')}</h6>
                    <p class="text-muted">${DOMUtils.escapeHtml(edu.year || 'Year not specified')}</p>
                    <p>${DOMUtils.escapeHtml(edu.details || '')}</p>
                </div>
            `).join('');
        } else {
            educationContainer.innerHTML = '<p>No education information available</p>';
        }
        
        // Matched skills
        const matchedSkillsContainer = document.querySelector('#candidateDetailsModal .matched-skills-container');
        if (candidate.matched_skills && candidate.matched_skills.length > 0) {
            matchedSkillsContainer.innerHTML = candidate.matched_skills.map(skill => 
                `<span class="skill-badge bg-success">${DOMUtils.escapeHtml(skill)}</span>`
            ).join('');
        } else {
            matchedSkillsContainer.innerHTML = '<p>No matched skills</p>';
        }
        
        // Missing skills
        const missingSkillsContainer = document.querySelector('#candidateDetailsModal .missing-skills-container');
        if (candidate.missing_skills && candidate.missing_skills.length > 0) {
            missingSkillsContainer.innerHTML = candidate.missing_skills.map(skill => 
                `<span class="skill-badge bg-danger">${DOMUtils.escapeHtml(skill)}</span>`
            ).join('');
        } else {
            missingSkillsContainer.innerHTML = '<p>No missing skills</p>';
        }
    },

    // Set up modal action buttons (common for both PDS and regular candidates)
    setupActionButtons(candidate) {
        const candidateId = candidate.id;
        document.getElementById('removeCandidate').dataset.candidateId = candidateId;
        document.getElementById('shortlistCandidate').dataset.candidateId = candidateId;
        document.getElementById('rejectCandidate').dataset.candidateId = candidateId;
    },

    // Populate PDS-specific data sections
    populatePDSData(candidate) {
        console.log('Starting PDS data population for candidate:', candidate);
        const pdsData = candidate.pds_data || {};
        console.log('PDS Data:', pdsData);
        
        // Personal Information
        this.populatePersonalInfo(pdsData);
        
        // Educational Background (new PDS section)
        this.populateEducationalBackground(candidate, pdsData);
        
        // Government IDs
        const govIdsContainer = document.querySelector('#candidateDetailsModal .government-ids-container');
        let govIds = candidate.government_ids || {};
        
        // If government_ids is empty, try to extract from PDS data
        if (Object.keys(govIds).length === 0 && pdsData.personal_info) {
            const personalInfo = pdsData.personal_info;
            govIds = {
                gsis_id: personalInfo.gsis_id,
                pagibig_id: personalInfo.pagibig_id,
                philhealth_no: personalInfo.philhealth_no,
                sss_no: personalInfo.sss_no,
                tin_no: personalInfo.tin_no
            };
        }
        
        const validGovIds = Object.entries(govIds)
            .filter(([key, value]) => value && value.trim() !== '' && value.toLowerCase() !== 'n/a');
            
        if (validGovIds.length > 0) {
            govIdsContainer.innerHTML = validGovIds.map(([key, value]) => `
                <div class="id-item">
                    <strong>${this.formatIDLabel(key)}:</strong> ${DOMUtils.escapeHtml(value)}
                </div>
            `).join('');
        } else {
            govIdsContainer.innerHTML = '<p>No government ID information available</p>';
        }
        
        // Civil Service Eligibility
        const eligibilityContainer = document.querySelector('#candidateDetailsModal .eligibility-container');
        const eligibility = candidate.eligibility || [];
        if (eligibility.length > 0) {
            const validEligibility = eligibility.filter(elig => 
                elig.eligibility && 
                elig.eligibility.trim() !== '' && 
                !elig.eligibility.includes('WORK EXPERIENCE') &&
                !elig.eligibility.includes('Continue on separate')
            );
            
            if (validEligibility.length > 0) {
                eligibilityContainer.innerHTML = validEligibility.map(elig => `
                    <div class="eligibility-item">
                        <h6>${DOMUtils.escapeHtml(elig.eligibility)}</h6>
                        <p class="text-muted">
                            ${elig.rating ? `Rating: ${elig.rating}` : ''} 
                            ${elig.date_exam ? `| Date: ${elig.date_exam}` : ''} 
                            ${elig.place_exam ? `| Place: ${elig.place_exam}` : ''}
                        </p>
                        ${elig.license_no ? `<p>License: ${DOMUtils.escapeHtml(elig.license_no)}</p>` : ''}
                        ${elig.validity ? `<p>Validity: ${DOMUtils.escapeHtml(elig.validity)}</p>` : ''}
                    </div>
                `).join('');
            } else {
                eligibilityContainer.innerHTML = '<p>No civil service eligibility information available</p>';
            }
        } else {
            eligibilityContainer.innerHTML = '<p>No civil service eligibility information available</p>';
        }
        
        // Work Experience (PDS)
        const workExpContainer = document.querySelector('#candidateDetailsModal .work-experience-container');
        const workExperience = candidate.work_experience || candidate.experience || [];
        if (workExperience.length > 0) {
            const validWorkExp = workExperience.filter(work => 
                work.position && 
                work.position.trim() !== '' && 
                work.position !== 'To' &&
                work.company && 
                work.company.trim() !== ''
            );
            
            if (validWorkExp.length > 0) {
                workExpContainer.innerHTML = validWorkExp.map(work => `
                    <div class="work-experience-item">
                        <h6>${DOMUtils.escapeHtml(work.position)}</h6>
                        <div class="company">${DOMUtils.escapeHtml(work.company)}</div>
                        <div class="date-range">
                            ${work.date_from ? new Date(work.date_from).toLocaleDateString() : 'N/A'} - 
                            ${work.date_to ? new Date(work.date_to).toLocaleDateString() : 'Present'}
                        </div>
                        ${work.status ? `<div class="description">${DOMUtils.escapeHtml(work.status)}</div>` : ''}
                        ${work.salary ? `<div class="text-muted">Salary: ${DOMUtils.escapeHtml(work.salary)}</div>` : ''}
                        ${work.govt_service ? `<div class="text-muted">Government Service: ${work.govt_service}</div>` : ''}
                    </div>
                `).join('');
            } else {
                workExpContainer.innerHTML = '<p>No work experience information available</p>';
            }
        } else {
            workExpContainer.innerHTML = '<p>No work experience information available</p>';
        }
        
        // Training and Development
        const trainingContainer = document.querySelector('#candidateDetailsModal .training-container');
        const training = candidate.training || [];
        if (training.length > 0) {
            const validTraining = training.filter(train => 
                train.title && 
                train.title.trim() !== '' && 
                train.title !== 'From'
            );
            
            if (validTraining.length > 0) {
                trainingContainer.innerHTML = validTraining.map(train => `
                    <div class="training-item">
                        <h6>${DOMUtils.escapeHtml(train.title)}</h6>
                        <p class="text-muted">
                            ${train.date_from || train.type ? 
                                `${train.type || train.date_from || ''} ${train.conductor ? `to ${train.conductor}` : ''}` : 
                                'Dates not specified'
                            }
                            ${train.hours ? `| ${train.hours} hours` : ''}
                        </p>
                    </div>
                `).join('');
            } else {
                trainingContainer.innerHTML = '<p>No training information available</p>';
            }
        } else {
            trainingContainer.innerHTML = '<p>No training information available</p>';
        }
        
        // Volunteer Work
        const volunteerContainer = document.querySelector('#candidateDetailsModal .volunteer-container');
        const volunteerWork = candidate.voluntary_work || candidate.volunteer_work || [];
        console.log('Volunteer work data:', volunteerWork); // Debug log
        
        if (volunteerWork.length > 0) {
            const validVolunteerWork = volunteerWork.filter(vol => 
                vol.organization && 
                vol.organization.trim() !== '' &&
                vol.organization !== 'From'
            );
            
            if (validVolunteerWork.length > 0) {
                volunteerContainer.innerHTML = validVolunteerWork.map(vol => `
                    <div class="volunteer-item">
                        <h6>${DOMUtils.escapeHtml(vol.organization)}</h6>
                        <p class="text-muted">
                            ${vol.date_from || vol.position ? 
                                `${vol.position || vol.date_from || ''}` : 
                                'Dates not specified'
                            }
                            ${vol.hours ? `| ${vol.hours} hours` : ''}
                        </p>
                    </div>
                `).join('');
            } else {
                volunteerContainer.innerHTML = '<p>No volunteer work information available</p>';
            }
        } else {
            volunteerContainer.innerHTML = '<p>No volunteer work information available</p>';
        }
        
        // Personal References
        const referencesContainer = document.querySelector('#candidateDetailsModal .references-container');
        const references = candidate.personal_references || (pdsData.other_info && pdsData.other_info.references) || [];
        if (references.length > 0) {
            const validReferences = references.filter(ref => 
                ref.name && 
                ref.name.trim() !== '' &&
                !ref.name.includes('42.') &&
                !ref.name.includes('declare under oath')
            );
            
            if (validReferences.length > 0) {
                referencesContainer.innerHTML = validReferences.map(ref => `
                    <div class="reference-item">
                        <h6>${DOMUtils.escapeHtml(ref.name)}</h6>
                        <p class="text-muted">
                            ${ref.address || 'N/A'} 
                            ${ref.telephone_no || ref.tel_no ? `| ${ref.telephone_no || ref.tel_no}` : ''}
                        </p>
                    </div>
                `).join('');
            } else {
                referencesContainer.innerHTML = '<p>No personal references available</p>';
            }
        } else {
            referencesContainer.innerHTML = '<p>No personal references available</p>';
        }
        
        // Assessment Results (new PDS section)
        this.populateAssessmentResults(candidate);
    },

    // Populate Educational Background section for PDS candidates
    populateEducationalBackground(candidate, pdsData) {
        const educationContainer = document.querySelector('#candidateDetailsModal .educational-background-container');
        const education = candidate.education || pdsData.educational_background || [];
        
        if (education.length > 0) {
            const validEducation = education.filter(edu => 
                edu.school && 
                edu.school.trim() !== '' &&
                edu.school !== 'From' &&
                !edu.school.includes('GRADUATE STUDIES') &&
                !edu.school.includes('VOCATIONAL')
            );
            
            if (validEducation.length > 0) {
                educationContainer.innerHTML = validEducation.map(edu => `
                    <div class="education-item">
                        <h6>${DOMUtils.escapeHtml(edu.level || 'Unknown Level')}</h6>
                        <div class="school">${DOMUtils.escapeHtml(edu.school)}</div>
                        <div class="degree">${DOMUtils.escapeHtml(edu.degree_course || edu.degree || '')}</div>
                        <div class="date-range text-muted">
                            ${edu.period_from ? edu.period_from : 'N/A'} - 
                            ${edu.period_to ? edu.period_to : (edu.year_graduated || 'N/A')}
                        </div>
                        ${edu.honors ? `<div class="honors"><i class="fas fa-award text-warning"></i> ${DOMUtils.escapeHtml(edu.honors)}</div>` : ''}
                        ${edu.highest_level_units ? `<div class="text-muted">Units: ${DOMUtils.escapeHtml(edu.highest_level_units)}</div>` : ''}
                    </div>
                `).join('');
            } else {
                educationContainer.innerHTML = '<p>No educational background information available</p>';
            }
        } else {
            educationContainer.innerHTML = '<p>No educational background information available</p>';
        }
    },

    // Populate Assessment Results section for PDS candidates
    populateAssessmentResults(candidate) {
        const assessmentContainer = document.querySelector('#candidateDetailsModal .assessment-results-container');
        
        // Show loading state
        assessmentContainer.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading assessment...</span>
                </div>
                <p class="mt-2">Calculating assessment results...</p>
            </div>
        `;
        
        // Fetch assessment data from API
        this.fetchAssessmentData(candidate.id).then(assessmentData => {
            if (assessmentData) {
                this.renderAssessmentResults(candidate, assessmentData);
                
                // Now populate hybrid scoring sections
                this.populateHybridScoring(candidate);
                this.populateSemanticAnalysis(candidate);
                this.populateAssessmentComparison(candidate);
            } else {
                this.renderNoAssessmentData();
            }
        }).catch(error => {
            console.error('Error fetching assessment data:', error);
            this.renderAssessmentError();
        });
    },

    // NEW: Populate Hybrid Scoring Analysis section
    async populateHybridScoring(candidate) {
        const hybridContainer = document.querySelector('#candidateDetailsModal .hybrid-scoring-container');
        
        if (!hybridContainer) {
            console.warn('Hybrid scoring container not found');
            return;
        }
        
        // Show loading state
        hybridContainer.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading hybrid analysis...</span>
                </div>
                <p class="mt-2 mb-0">Analyzing hybrid scoring...</p>
            </div>
        `;
        
        try {
            // Fetch hybrid assessment data for specific job
            const jobId = this.getJobIdForCandidate(candidate);
            if (jobId) {
                const response = await fetch(`/api/candidates/${candidate.id}/assessment/${jobId}`);
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        this.renderHybridScoringResults(result.assessment);
                    } else {
                        this.renderHybridScoringError('Failed to load hybrid scoring data');
                    }
                } else {
                    this.renderHybridScoringError('Network error loading hybrid scoring');
                }
            } else {
                this.renderHybridScoringError('No job assignment found for hybrid scoring');
            }
        } catch (error) {
            console.error('Error fetching hybrid scoring data:', error);
            this.renderHybridScoringError('Error loading hybrid scoring data');
        }
    },

    // NEW: Render hybrid scoring results
    renderHybridScoringResults(hybridData) {
        const hybridContainer = document.querySelector('#candidateDetailsModal .hybrid-scoring-container');
        
        const universityScores = hybridData.university_assessment || {};
        const semanticScores = hybridData.semantic_analysis || {};
        const enhancedScores = hybridData.enhanced_assessment || {};
        
        hybridContainer.innerHTML = `
            <div class="hybrid-scoring-display">
                <div class="scoring-methods-comparison">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="scoring-method-card university-method">
                                <div class="method-header">
                                    <div class="method-icon">
                                        <i class="fas fa-university"></i>
                                    </div>
                                    <div class="method-info">
                                        <h5>University Assessment</h5>
                                        <p class="text-muted">Official LSPU Criteria</p>
                                    </div>
                                    <div class="method-score">
                                        <span class="score-value">${universityScores.total_score || 0}</span>
                                        <span class="score-label">/100</span>
                                    </div>
                                </div>
                                <div class="method-breakdown">
                                    ${this.renderUniversityBreakdown(universityScores)}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="scoring-method-card semantic-method">
                                <div class="method-header">
                                    <div class="method-icon">
                                        <i class="fas fa-brain"></i>
                                    </div>
                                    <div class="method-info">
                                        <h5>Semantic Analysis</h5>
                                        <p class="text-muted">AI-Powered Relevance</p>
                                    </div>
                                    <div class="method-score">
                                        <span class="score-value">${semanticScores.overall_score || 0}</span>
                                        <span class="score-label">%</span>
                                    </div>
                                </div>
                                <div class="method-breakdown">
                                    ${this.renderSemanticBreakdown(semanticScores)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="hybrid-results-summary">
                    <div class="hybrid-score-card">
                        <div class="hybrid-header">
                            <h6><i class="fas fa-balance-scale"></i> Hybrid Assessment Result</h6>
                        </div>
                        <div class="hybrid-scores">
                            <div class="hybrid-score-item">
                                <span class="label">University Compliance:</span>
                                <span class="value">${universityScores.total_score || 0}/100</span>
                                <div class="score-bar">
                                    <div class="score-fill university" style="width: ${universityScores.total_score || 0}%"></div>
                                </div>
                            </div>
                            <div class="hybrid-score-item">
                                <span class="label">Semantic Relevance:</span>
                                <span class="value">${semanticScores.overall_score || 0}%</span>
                                <div class="score-bar">
                                    <div class="score-fill semantic" style="width: ${semanticScores.overall_score || 0}%"></div>
                                </div>
                            </div>
                            <div class="hybrid-score-item total">
                                <span class="label">Enhanced Assessment:</span>
                                <span class="value">${enhancedScores.recommended_score || 0}</span>
                                <div class="score-bar">
                                    <div class="score-fill hybrid" style="width: ${(enhancedScores.recommended_score || 0)}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // NEW: Render university scoring breakdown
    renderUniversityBreakdown(universityScores) {
        const detailed = universityScores.detailed_scores || {};
        return `
            <div class="university-breakdown">
                <div class="breakdown-item">
                    <span class="item-label">Education (40%):</span>
                    <span class="item-score">${detailed.education || 0}/40</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Experience (20%):</span>
                    <span class="item-score">${detailed.experience || 0}/20</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Training (10%):</span>
                    <span class="item-score">${detailed.training || 0}/10</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Eligibility (10%):</span>
                    <span class="item-score">${detailed.eligibility || 0}/10</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Performance (5%):</span>
                    <span class="item-score">${detailed.performance || 0}/5</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Potential (15%):</span>
                    <span class="item-score">${detailed.potential || 0}/15</span>
                </div>
            </div>
        `;
    },

    // NEW: Render semantic analysis breakdown
    renderSemanticBreakdown(semanticScores) {
        return `
            <div class="semantic-breakdown">
                <div class="breakdown-item">
                    <span class="item-label">Education Relevance:</span>
                    <span class="item-score">${(semanticScores.education_relevance || 0).toFixed(1)}%</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Experience Match:</span>
                    <span class="item-score">${(semanticScores.experience_relevance || 0).toFixed(1)}%</span>
                </div>
                <div class="breakdown-item">
                    <span class="item-label">Training Relevance:</span>
                    <span class="item-score">${(semanticScores.training_relevance || 0).toFixed(1)}%</span>
                </div>
                <div class="breakdown-item total">
                    <span class="item-label">Overall Relevance:</span>
                    <span class="item-score">${(semanticScores.overall_score || 0).toFixed(1)}%</span>
                </div>
            </div>
        `;
    },

    // NEW: Populate Semantic Analysis section
    async populateSemanticAnalysis(candidate) {
        const semanticContainer = document.querySelector('#candidateDetailsModal .semantic-analysis-container');
        
        if (!semanticContainer) {
            console.warn('Semantic analysis container not found');
            return;
        }

        // Show loading state
        semanticContainer.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading semantic analysis...</span>
                </div>
                <p class="mt-2 mb-0">Analyzing semantic relevance...</p>
            </div>
        `;

        try {
            const jobId = this.getJobIdForCandidate(candidate);
            if (jobId) {
                // Use the same endpoint as hybrid scoring since it includes semantic analysis
                const response = await fetch(`/api/candidates/${candidate.id}/assessment/${jobId}`);
                if (response.ok) {
                    const result = await response.json();
                    if (result.success && result.assessment && result.assessment.semantic_analysis) {
                        this.renderSemanticAnalysisResults(result.assessment.semantic_analysis);
                    } else {
                        this.renderSemanticAnalysisError('Semantic analysis data not available');
                    }
                } else {
                    this.renderSemanticAnalysisError('Network error loading semantic analysis');
                }
            } else {
                this.renderSemanticAnalysisError('No job assignment found for semantic analysis');
            }
        } catch (error) {
            console.error('Error fetching semantic analysis:', error);
            this.renderSemanticAnalysisError('Error loading semantic analysis');
        }
    },

    // NEW: Render semantic analysis results
    renderSemanticAnalysisResults(semanticData) {
        const semanticContainer = document.querySelector('#candidateDetailsModal .semantic-analysis-container');
        
        // Handle both direct semantic data and nested structure
        const analysis = semanticData.semantic_analysis || semanticData || {};
        const insights = semanticData.insights || analysis.insights || [];
        const recommendations = semanticData.recommendations || analysis.recommendations || [];
        
        // Handle different field names between endpoints - fixed to match backend structure
        const overallScore = analysis.overall_score || analysis.overall_relevance_score || 0;
        const educationRelevance = analysis.education_relevance || 0;
        const experienceRelevance = analysis.experience_relevance || 0;
        const trainingRelevance = analysis.training_relevance || 0;
        
        semanticContainer.innerHTML = `
            <div class="semantic-analysis-display">
                <div class="semantic-overview">
                    <div class="relevance-score-display">
                        <div class="relevance-circle">
                            <div class="circle-chart" data-percentage="${overallScore}">
                                <span class="percentage">${(overallScore).toFixed(1)}%</span>
                                <span class="label">Overall Relevance</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="semantic-breakdown-detailed">
                    <h6>Detailed Relevance Analysis</h6>
                    <div class="relevance-categories">
                        <div class="relevance-category">
                            <div class="category-header">
                                <span class="category-name">Educational Background</span>
                                <span class="category-score">${(educationRelevance).toFixed(1)}%</span>
                            </div>
                            <div class="category-bar">
                                <div class="bar-fill education" style="width: ${educationRelevance}%"></div>
                            </div>
                            <div class="category-insights">
                                ${analysis.education_insights ? `<p class="insight">${analysis.education_insights}</p>` : ''}
                            </div>
                        </div>
                        
                        <div class="relevance-category">
                            <div class="category-header">
                                <span class="category-name">Work Experience</span>
                                <span class="category-score">${(experienceRelevance).toFixed(1)}%</span>
                            </div>
                            <div class="category-bar">
                                <div class="bar-fill experience" style="width: ${experienceRelevance}%"></div>
                            </div>
                            <div class="category-insights">
                                ${analysis.experience_insights ? `<p class="insight">${analysis.experience_insights}</p>` : ''}
                            </div>
                        </div>
                        
                        <div class="relevance-category">
                            <div class="category-header">
                                <span class="category-name">Training & Development</span>
                                <span class="category-score">${(trainingRelevance).toFixed(1)}%</span>
                            </div>
                            <div class="category-bar">
                                <div class="bar-fill skills" style="width: ${trainingRelevance}%"></div>
                            </div>
                            <div class="category-insights">
                                ${analysis.training_insights ? `<p class="insight">${analysis.training_insights}</p>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                ${insights.length > 0 ? `
                    <div class="ai-insights">
                        <h6><i class="fas fa-lightbulb"></i> AI Insights</h6>
                        <div class="insights-list">
                            ${insights.map(insight => `<div class="insight-item">${insight}</div>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${recommendations.length > 0 ? `
                    <div class="ai-recommendations">
                        <h6><i class="fas fa-robot"></i> AI Recommendations</h6>
                        <div class="recommendations-list">
                            ${recommendations.map(rec => `<div class="recommendation-item">${rec}</div>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Initialize circle chart animation
        this.animateCircleChart();
    },

    // NEW: Populate Assessment Comparison section
    async populateAssessmentComparison(candidate) {
        const comparisonContainer = document.querySelector('#candidateDetailsModal .assessment-comparison-container');
        
        if (!comparisonContainer) {
            console.warn('Assessment comparison container not found');
            return;
        }
        
        // Show loading state
        comparisonContainer.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading comparison data...</span>
                </div>
                <p class="mt-2 mb-0">Comparing assessment methods...</p>
            </div>
        `;
        
        try {
            // Use the dedicated assessment comparison endpoint
            const response = await fetch(`/api/candidates/${candidate.id}/assessment/comparison`);
            if (response.ok) {
                const result = await response.json();
                if (result.success && result.data) {
                    this.renderAssessmentComparisonResults(result.data);
                } else {
                    this.renderAssessmentComparisonError('Assessment comparison data not available');
                }
            } else {
                this.renderAssessmentComparisonError('Network error loading comparison');
            }
        } catch (error) {
            console.error('Error fetching assessment comparison:', error);
            this.renderAssessmentComparisonError('Error loading comparison data');
        }
    },

    // NEW: Render assessment comparison results
    renderAssessmentComparisonResults(comparisonData) {
        const comparisonContainer = document.querySelector('#candidateDetailsModal .assessment-comparison-container');
        
        const traditional = comparisonData.traditional_assessment || {};
        const enhanced = comparisonData.enhanced_assessment || {};
        const differences = comparisonData.differences || {};
        
        comparisonContainer.innerHTML = `
            <div class="assessment-comparison-display">
                <div class="comparison-methods">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="method-comparison-card traditional">
                                <div class="card-header">
                                    <h6><i class="fas fa-file-alt"></i> Traditional Assessment</h6>
                                    <span class="method-badge traditional">Basic</span>
                                </div>
                                <div class="card-body">
                                    <div class="score-display">
                                        <span class="score-value">${traditional.total_score || 0}</span>
                                        <span class="score-label">/100</span>
                                    </div>
                                    <div class="method-details">
                                        <p class="text-muted">Standard university criteria evaluation</p>
                                        <div class="score-breakdown">
                                            ${this.renderTraditionalBreakdown(traditional)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="method-comparison-card enhanced">
                                <div class="card-header">
                                    <h6><i class="fas fa-brain"></i> Enhanced Assessment</h6>
                                    <span class="method-badge enhanced">AI-Powered</span>
                                </div>
                                <div class="card-body">
                                    <div class="score-display">
                                        <span class="score-value">${enhanced.total_score || 0}</span>
                                        <span class="score-label">/100</span>
                                    </div>
                                    <div class="method-details">
                                        <p class="text-muted">University criteria + semantic analysis</p>
                                        <div class="score-breakdown">
                                            ${this.renderEnhancedBreakdown(enhanced)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="comparison-insights">
                    <div class="insights-header">
                        <h6><i class="fas fa-chart-line"></i> Assessment Comparison Insights</h6>
                    </div>
                    <div class="insights-content">
                        <div class="difference-indicator">
                            <span class="difference-label">Score Difference:</span>
                            <span class="difference-value ${differences.improvement > 0 ? 'positive' : differences.improvement < 0 ? 'negative' : 'neutral'}">
                                ${differences.improvement > 0 ? '+' : ''}${differences.improvement || 0} points
                            </span>
                        </div>
                        <div class="improvement-areas">
                            ${differences.improvements && differences.improvements.length > 0 ? `
                                <div class="improvements">
                                    <h6>Improvements Identified:</h6>
                                    <ul>
                                        ${differences.improvements.map(imp => `<li>${imp}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                        <div class="method-advantages">
                            ${differences.method_advantages && differences.method_advantages.length > 0 ? `
                                <div class="advantages">
                                    <h6>Enhanced Assessment Advantages:</h6>
                                    <ul>
                                        ${differences.method_advantages.map(adv => `
                                            <li><i class="fas fa-check text-success"></i> ${adv}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            ` : `
                                <div class="ai-advantages">
                                    <div class="advantage-item">
                                        <i class="fas fa-check text-success"></i>
                                        <span>Contextual understanding of job requirements</span>
                                    </div>
                                    <div class="advantage-item">
                                        <i class="fas fa-check text-success"></i>
                                        <span>Semantic analysis of qualifications relevance</span>
                                    </div>
                                    <div class="advantage-item">
                                        <i class="fas fa-check text-success"></i>
                                        <span>Comprehensive skills and experience matching</span>
                                    </div>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // NEW: Render traditional assessment breakdown
    renderTraditionalBreakdown(traditional) {
        return `
            <div class="traditional-breakdown">
                <div class="breakdown-item">
                    <span>Education:</span>
                    <span>${traditional.education || 0}/40</span>
                </div>
                <div class="breakdown-item">
                    <span>Experience:</span>
                    <span>${traditional.experience || 0}/20</span>
                </div>
                <div class="breakdown-item">
                    <span>Training:</span>
                    <span>${traditional.training || 0}/10</span>
                </div>
                <div class="breakdown-item">
                    <span>Eligibility:</span>
                    <span>${traditional.eligibility || 0}/10</span>
                </div>
            </div>
        `;
    },

    // NEW: Render enhanced assessment breakdown
    renderEnhancedBreakdown(enhanced) {
        return `
            <div class="enhanced-breakdown">
                <div class="breakdown-item">
                    <span>University Score:</span>
                    <span>${enhanced.university_score || 0}/85</span>
                </div>
                <div class="breakdown-item">
                    <span>Semantic Enhancement:</span>
                    <span>${enhanced.semantic_bonus || 0}</span>
                </div>
                <div class="breakdown-item">
                    <span>AI Improvement:</span>
                    <span>${enhanced.ai_enhancement || 0}%</span>
                </div>
                <div class="breakdown-item">
                    <span>Education Relevance:</span>
                    <span>${enhanced.education_relevance || 0}%</span>
                </div>
                <div class="breakdown-item">
                    <span>Experience Relevance:</span>
                    <span>${enhanced.experience_relevance || 0}%</span>
                </div>
                <div class="breakdown-item">
                    <span>Training Relevance:</span>
                    <span>${enhanced.training_relevance || 0}%</span>
                </div>
            </div>
        `;
    },

    // NEW: Helper method to get job ID for candidate
    getJobIdForCandidate(candidate) {
        console.log('🔍 getJobIdForCandidate called with candidate:', candidate);
        
        // Try multiple possible job ID fields
        const possibleJobIds = [
            candidate.job_id,
            candidate.position_id,
            candidate.lspu_job_id,
            candidate.target_job_id,
            candidate.job_posting_id
        ];
        
        console.log('🎯 Possible job IDs found:', possibleJobIds);
        
        // Find first valid job ID
        for (const jobId of possibleJobIds) {
            if (jobId && jobId !== null && jobId !== undefined && jobId !== 0) {
                console.log('✅ Using job ID:', jobId);
                return jobId;
            }
        }
        
        // If no direct job ID, try to get from context or URL
        const urlParams = new URLSearchParams(window.location.search);
        const urlJobId = urlParams.get('jobId') || urlParams.get('job_id');
        if (urlJobId) {
            console.log('🌐 Using job ID from URL:', urlJobId);
            return urlJobId;
        }
        
        // Try to get from currently selected job in upload module
        if (window.uploadModuleInstance && window.uploadModuleInstance.selectedJobId) {
            console.log('📤 Using job ID from upload module:', window.uploadModuleInstance.selectedJobId);
            return window.uploadModuleInstance.selectedJobId;
        }
        
        // Last resort: try to get from candidate's associated job data
        if (candidate.job_data && candidate.job_data.id) {
            console.log('📋 Using job ID from job_data:', candidate.job_data.id);
            return candidate.job_data.id;
        }
        
        console.warn('❌ No job ID found for candidate. Available fields:', Object.keys(candidate));
        return null;
    },

    // NEW: Animate circle chart
    animateCircleChart() {
        const circleChart = document.querySelector('.circle-chart');
        if (circleChart) {
            const percentage = circleChart.dataset.percentage;
            const circumference = 2 * Math.PI * 45; // radius = 45
            const strokeDashoffset = circumference - (percentage / 100) * circumference;
            
            // Add SVG circle if not exists
            if (!circleChart.querySelector('svg')) {
                circleChart.innerHTML = `
                    <svg width="120" height="120" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="45" fill="none" stroke="#e0e0e0" stroke-width="8"/>
                        <circle cx="60" cy="60" r="45" fill="none" stroke="#007bff" stroke-width="8"
                                stroke-dasharray="${circumference}" stroke-dashoffset="${strokeDashoffset}"
                                stroke-linecap="round" transform="rotate(-90 60 60)" 
                                style="transition: stroke-dashoffset 1s ease-in-out"/>
                    </svg>
                    <div class="chart-content">
                        <span class="percentage">${percentage}%</span>
                        <span class="label">Overall Relevance</span>
                    </div>
                `;
            }
        }
    },

    // NEW: Error rendering methods
    renderHybridScoringError(message) {
        const hybridContainer = document.querySelector('#candidateDetailsModal .hybrid-scoring-container');
        hybridContainer.innerHTML = `
            <div class="text-center p-3">
                <p class="text-muted">${message}</p>
                <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">Retry</button>
            </div>
        `;
    },

    renderSemanticAnalysisError(message) {
        const semanticContainer = document.querySelector('#candidateDetailsModal .semantic-analysis-container');
        semanticContainer.innerHTML = `
            <div class="text-center p-3">
                <p class="text-muted">${message}</p>
                <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">Retry</button>
            </div>
        `;
    },

    renderAssessmentComparisonError(message) {
        const comparisonContainer = document.querySelector('#candidateDetailsModal .assessment-comparison-container');
        comparisonContainer.innerHTML = `
            <div class="text-center p-3">
                <p class="text-muted">${message}</p>
                <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">Retry</button>
            </div>
        `;
    },

    async fetchAssessmentData(candidateId) {
        try {
            const response = await fetch(`/api/candidates/${candidateId}/assessment`);
            if (response.ok) {
                const result = await response.json();
                return result.success ? result.assessment : null;
            }
            return null;
        } catch (error) {
            console.error('Error fetching assessment data:', error);
            return null;
        }
    },

    renderAssessmentResults(candidate, assessmentData) {
        const assessmentContainer = document.querySelector('#candidateDetailsModal .assessment-results-container');
        
        // Extract scores from assessment data - handle both old and new structures
        const detailedScores = assessmentData.university_assessment?.detailed_scores || {};
        const breakdown = {
            education: detailedScores.education || assessmentData.education_score || 0,
            experience: detailedScores.experience || assessmentData.experience_score || 0,
            training: detailedScores.training || assessmentData.training_score || 0,
            eligibility: detailedScores.eligibility || assessmentData.eligibility_score || 0,
            accomplishments: detailedScores.performance || assessmentData.accomplishments_score || 0,
            potential: assessmentData.potential_score || 0
        };
        
        const automatedTotal = assessmentData.automated_total || 0;
        const overallTotal = assessmentData.overall_total || 0;
        const percentageScore = (overallTotal / 100) * 100;
        
        assessmentContainer.innerHTML = `
            <div class="assessment-overview">
                <div class="assessment-scores-row">
                    <div class="score-section">
                        <div class="score-circle-large ${this.getScoreColorClass(automatedTotal)}">
                            <span class="score-value">${automatedTotal}</span>
                            <span class="score-label">Automated</span>
                        </div>
                        <p class="score-description">85 points maximum</p>
                    </div>
                    <div class="score-section">
                        <div class="score-circle-large ${this.getScoreColorClass(overallTotal)}">
                            <span class="score-value">${overallTotal}</span>
                            <span class="score-label">Overall</span>
                        </div>
                        <p class="score-description">100 points total</p>
                    </div>
                </div>
            </div>
            
            <div class="assessment-breakdown">
                <div class="criteria-header">
                    <h6>University Assessment Criteria</h6>
                    <small class="text-muted">Based on LSPU Standards</small>
                </div>
                
                <div class="criteria-list">
                    <div class="criteria-item">
                        <span class="criteria-label">I. Potential (15%) - Manual Entry</span>
                        <div class="criteria-controls">
                            <div class="potential-input-group">
                                <input type="number" 
                                       id="potentialScore" 
                                       class="form-control form-control-sm potential-input" 
                                       value="${breakdown.potential}" 
                                       min="0" 
                                       max="15" 
                                       step="0.1"
                                       data-candidate-id="${candidate.id}">
                                <span class="input-label">/ 15</span>
                                <button class="btn btn-sm btn-primary update-potential-btn" 
                                        onclick="CandidatesModule.updatePotentialScore(${candidate.id})">
                                    Update
                                </button>
                            </div>
                            <small class="text-muted">Interview (10%) + Aptitude Test (5%)</small>
                        </div>
                    </div>
                    
                    <div class="criteria-item automated">
                        <span class="criteria-label">II. Education (40%)</span>
                        <div class="criteria-bar">
                            <div class="criteria-fill education" style="width: ${(breakdown.education/40)*100}%"></div>
                        </div>
                        <span class="criteria-score">${breakdown.education}/40</span>
                    </div>
                    
                    <div class="criteria-item automated">
                        <span class="criteria-label">III. Experience (20%)</span>
                        <div class="criteria-bar">
                            <div class="criteria-fill experience" style="width: ${(breakdown.experience/20)*100}%"></div>
                        </div>
                        <span class="criteria-score">${breakdown.experience}/20</span>
                    </div>
                    
                    <div class="criteria-item automated">
                        <span class="criteria-label">IV. Training (10%)</span>
                        <div class="criteria-bar">
                            <div class="criteria-fill training" style="width: ${(breakdown.training/10)*100}%"></div>
                        </div>
                        <span class="criteria-score">${breakdown.training}/10</span>
                    </div>
                    
                    <div class="criteria-item automated">
                        <span class="criteria-label">V. Eligibility (10%)</span>
                        <div class="criteria-bar">
                            <div class="criteria-fill eligibility" style="width: ${(breakdown.eligibility/10)*100}%"></div>
                        </div>
                        <span class="criteria-score">${breakdown.eligibility}/10</span>
                    </div>
                    
                    <div class="criteria-item automated">
                        <span class="criteria-label">VI. Outstanding Accomplishments (5%)</span>
                        <div class="criteria-bar">
                            <div class="criteria-fill accomplishments" style="width: ${(breakdown.accomplishments/5)*100}%"></div>
                        </div>
                        <span class="criteria-score">${breakdown.accomplishments}/5</span>
                    </div>
                </div>
                
                <div class="assessment-summary">
                    <div class="summary-row">
                        <span class="summary-label">Automated Score (85%):</span>
                        <span class="summary-value">${automatedTotal}/85 points</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Manual Score (15%):</span>
                        <span class="summary-value">${breakdown.potential}/15 points</span>
                    </div>
                    <div class="summary-row total">
                        <span class="summary-label">Total Score (100%):</span>
                        <span class="summary-value">${overallTotal}/100 points</span>
                    </div>
                    <div class="summary-row percentage">
                        <span class="summary-label">Percentage:</span>
                        <span class="summary-value">${percentageScore.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
    },

    renderNoAssessmentData() {
        const assessmentContainer = document.querySelector('#candidateDetailsModal .assessment-results-container');
        assessmentContainer.innerHTML = `
            <div class="text-center p-4">
                <p class="text-muted">No assessment data available for this candidate.</p>
                <p class="small">Assessment requires PDS data.</p>
            </div>
        `;
    },

    renderAssessmentError() {
        const assessmentContainer = document.querySelector('#candidateDetailsModal .assessment-results-container');
        assessmentContainer.innerHTML = `
            <div class="text-center p-4">
                <p class="text-danger">Error loading assessment data.</p>
                <button class="btn btn-sm btn-secondary" onclick="location.reload()">Refresh Page</button>
            </div>
        `;
    },
    // Update potential score via AJAX
    async updatePotentialScore(candidateId) {
        const input = document.getElementById('potentialScore');
        const updateBtn = document.querySelector('.update-potential-btn');
        const newScore = parseFloat(input.value) || 0;
        
        if (newScore < 0 || newScore > 15) {
            this.showNotification('Potential score must be between 0 and 15', 'error');
            input.focus();
            return;
        }
        
        // Show loading state
        const originalBtnText = updateBtn.textContent;
        updateBtn.disabled = true;
        updateBtn.textContent = 'Updating...';
        
        try {
            const response = await fetch('/api/update_potential_score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    candidate_id: candidateId,
                    potential_score: newScore
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.success) {
                    // Update the assessment display immediately
                    this.updateAssessmentDisplay(candidateId, newScore);
                    
                    // Show success message
                    this.showNotification('Potential score updated successfully', 'success');
                    
                    // Note: We no longer need to call loadCandidates() since we update the row directly
                    // This provides faster feedback and better user experience
                } else {
                    throw new Error(result.error || 'Failed to update potential score');
                }
            } else {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error updating potential score:', error);
            this.showNotification(`Failed to update potential score: ${error.message}`, 'error');
        } finally {
            // Restore button state
            updateBtn.disabled = false;
            updateBtn.textContent = originalBtnText;
        }
    },
    
    // Update assessment display with new potential score
    updateAssessmentDisplay(candidateId, newPotentialScore) {
        // Refresh the assessment data directly from the API
        this.fetchAssessmentData(candidateId).then(assessmentData => {
            if (assessmentData) {
                // Update the assessment breakdown
                const candidate = { id: candidateId };
                this.renderAssessmentResults(candidate, assessmentData);
                
                // Update the top score circle with new overall score
                const overallTotal = assessmentData.overall_total || 0;
                const scoreCircle = document.querySelector('#candidateDetailsModal .score-circle');
                const scoreValue = scoreCircle.querySelector('.score-value');
                if (scoreValue) {
                    scoreValue.textContent = `${overallTotal}`;
                    scoreCircle.className = `score-circle ${this.getScoreColorClass(overallTotal)}`;
                }
                
                // Update the candidate's score in the main table
                this.updateCandidateRowScore(candidateId, overallTotal);
                
                // Update the hybrid scoring display if it exists
                this.updateHybridScoringDisplay(candidateId, assessmentData);
                
                // Update the assessment comparison display if it exists  
                this.updateAssessmentComparisonDisplay(candidateId);
            }
        }).catch(error => {
            console.error('Error updating assessment display:', error);
        });
    },
    
    // Update candidate row score in the main table
    updateCandidateRowScore(candidateId, newAssessmentScore) {
        // Find the candidate row in the table
        const candidateRow = document.querySelector(`tr[data-candidate-id="${candidateId}"]`);
        if (candidateRow) {
            // Update the score column
            const scoreColumn = candidateRow.querySelector('.score-column');
            if (scoreColumn) {
                const scoreClass = this.getScoreColorClass(newAssessmentScore);
                scoreColumn.innerHTML = `
                    <div class="score-compact">
                        <span class="score-badge ${scoreClass}">${newAssessmentScore}/100</span>
                        <div class="score-bar-mini">
                            <div class="score-fill ${scoreClass}" style="width: ${newAssessmentScore}%"></div>
                        </div>
                    </div>
                `;
            }
        }
        
        // Also update the cached candidate data if it exists
        if (this.candidatesData) {
            // Find the candidate in the grouped data structure
            Object.values(this.candidatesData).forEach(jobData => {
                if (jobData.candidates) {
                    const candidate = jobData.candidates.find(c => c.id == candidateId);
                    if (candidate) {
                        candidate.assessment_score = newAssessmentScore;
                        candidate.score = newAssessmentScore;
                    }
                }
            });
        }
    },
    
    // Update hybrid scoring display with new assessment data
    async updateHybridScoringDisplay(candidateId, assessmentData) {
        const hybridContainer = document.querySelector('#candidateDetailsModal .hybrid-scoring-container');
        
        if (!hybridContainer) {
            // Hybrid scoring section not currently visible
            return;
        }
        
        try {
            // Get the job ID for this candidate to fetch hybrid data
            const jobId = this.getJobIdForCandidate({ id: candidateId });
            if (jobId) {
                // Fetch fresh hybrid assessment data using the existing endpoint
                const response = await fetch(`/api/candidates/${candidateId}/assessment/${jobId}`);
                if (response.ok) {
                    const result = await response.json();
                    if (result.success && result.assessment) {
                        // Re-render the hybrid scoring with updated data
                        this.renderHybridScoringResults(result.assessment);
                        
                        // Highlight the updated sections briefly
                        this.highlightUpdatedElements();
                    }
                }
            }
        } catch (error) {
            console.error('Error updating hybrid scoring display:', error);
        }
    },
    
    // Highlight updated elements to show user what changed
    highlightUpdatedElements() {
        // Highlight the potential score in university assessment
        const potentialElements = document.querySelectorAll('.university-breakdown .breakdown-item:last-child');
        potentialElements.forEach(element => {
            element.style.transition = 'background-color 0.3s ease';
            element.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                element.style.backgroundColor = '';
            }, 2000);
        });
        
        // Highlight the overall university score
        const universityScoreElements = document.querySelectorAll('.university-method .score-value');
        universityScoreElements.forEach(element => {
            element.style.transition = 'color 0.3s ease';
            element.style.color = '#28a745';
            setTimeout(() => {
                element.style.color = '';
            }, 2000);
        });
        
        // Highlight the enhanced assessment total
        const enhancedScoreElements = document.querySelectorAll('.hybrid-score-item.total .value');
        enhancedScoreElements.forEach(element => {
            element.style.transition = 'color 0.3s ease';
            element.style.color = '#007bff';
            setTimeout(() => {
                element.style.color = '';
            }, 2000);
        });
    },
    
    // Show notification message
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    },

    // Populate personal information section
    populatePersonalInfo(pdsData) {
        console.log('🔍 Populating personal info with PDS data:', pdsData);
        const personalInfo = pdsData.personal_info || {};
        console.log('📋 Personal info extracted:', personalInfo);
        
        // Enhanced debugging: log all available keys
        console.log('🔑 Available personal info keys:', Object.keys(personalInfo));
        console.log('👤 Individual fields:');
        console.log('  - first_name:', personalInfo.first_name);
        console.log('  - middle_name:', personalInfo.middle_name);
        console.log('  - surname:', personalInfo.surname);
        console.log('  - name_extension:', personalInfo.name_extension);
        console.log('  - full_name:', personalInfo.full_name);
        console.log('  - mobile_no:', personalInfo.mobile_no);
        console.log('  - telephone_no:', personalInfo.telephone_no);
        console.log('  - email:', personalInfo.email);
        
        // Full Name - Enhanced logic with multiple fallbacks
        let fullName = '';
        
        // Method 1: Use existing full_name field if available
        if (personalInfo.full_name && 
            personalInfo.full_name.trim() !== '' && 
            personalInfo.full_name.toLowerCase() !== 'n/a' &&
            !personalInfo.full_name.includes('N/a')) {
            fullName = personalInfo.full_name.replace(/\s+N\/a$/i, '').trim();
        }
        
        // Method 2: Construct from name parts if full_name is not good
        if (!fullName || fullName === '') {
            const nameParts = [
                personalInfo.first_name,
                personalInfo.middle_name,
                personalInfo.surname,
                personalInfo.name_extension
            ].filter(part => part && 
                      part.trim() !== '' && 
                      part.toLowerCase() !== 'n/a' &&
                      part.toLowerCase() !== 'none');
            
            if (nameParts.length > 0) {
                fullName = nameParts.join(' ');
            }
        }
        
        // Method 3: Try alternative field names
        if (!fullName || fullName === '') {
            const altNameFields = ['name', 'candidate_name', 'applicant_name'];
            for (const field of altNameFields) {
                if (personalInfo[field] && 
                    personalInfo[field].trim() !== '' && 
                    personalInfo[field].toLowerCase() !== 'n/a') {
                    fullName = personalInfo[field];
                    break;
                }
            }
        }
        
        console.log('✅ Final full name:', fullName);
        
        // Enhanced safe element access with better logging
        const setTextContent = (id, value, label = id) => {
            const element = document.getElementById(id);
            if (element) {
                const displayValue = (value && value.toString().trim() !== '' && 
                                   value.toString().toLowerCase() !== 'n/a' && 
                                   value.toString().toLowerCase() !== 'none') ? value.toString() : 'N/A';
                element.textContent = displayValue;
                console.log(`📝 Set ${label}:`, displayValue);
            } else {
                console.warn(`❌ Element with ID '${id}' not found`);
            }
        };
        
        // Set all personal information fields
        setTextContent('fullName', fullName, 'Full Name');
        setTextContent('dateOfBirth', personalInfo.date_of_birth, 'Date of Birth');
        setTextContent('placeOfBirth', personalInfo.place_of_birth, 'Place of Birth');
        setTextContent('gender', personalInfo.sex, 'Gender');
        setTextContent('civilStatus', personalInfo.civil_status, 'Civil Status');
        setTextContent('citizenship', personalInfo.citizenship, 'Citizenship');
        
        // Physical Information
        setTextContent('height', personalInfo.height ? `${personalInfo.height} m` : null, 'Height');
        setTextContent('weight', personalInfo.weight ? `${personalInfo.weight} kg` : null, 'Weight');
        setTextContent('bloodType', personalInfo.blood_type, 'Blood Type');
        
        // Contact Information - Enhanced with multiple fallbacks
        let mobileNo = personalInfo.mobile_no || personalInfo.phone || personalInfo.mobile;
        let telephoneNo = personalInfo.telephone_no || personalInfo.tel_no || personalInfo.telephone;
        let email = personalInfo.email || personalInfo.email_address;
        
        console.log('📞 Contact info processing:');
        console.log('  - mobile options:', {
            mobile_no: personalInfo.mobile_no,
            phone: personalInfo.phone,
            mobile: personalInfo.mobile,
            final: mobileNo
        });
        
        //setTextContent('mobileNo', mobileNo, 'Mobile Number');
        //setTextContent('telephoneNo', telephoneNo, 'Telephone Number');
        //setTextContent('emailAddress', email, 'Email Address');
        
        // Addresses - Enhanced handling
        let residentialAddr = '';
        let permanentAddr = '';
        
        if (personalInfo.residential_address) {
            if (typeof personalInfo.residential_address === 'string') {
                residentialAddr = personalInfo.residential_address;
            } else if (personalInfo.residential_address.full_address) {
                residentialAddr = personalInfo.residential_address.full_address;
            } else {
                // Try to construct from parts
                const addrParts = [
                    personalInfo.residential_address.house_block_lot_no,
                    personalInfo.residential_address.street,
                    personalInfo.residential_address.subdivision_village,
                    personalInfo.residential_address.barangay,
                    personalInfo.residential_address.city_municipality,
                    personalInfo.residential_address.province,
                    personalInfo.residential_address.zip_code
                ].filter(part => part && part.trim() !== '');
                
                if (addrParts.length > 0) {
                    residentialAddr = addrParts.join(', ');
                }
            }
        }
        
        if (personalInfo.permanent_address) {
            if (typeof personalInfo.permanent_address === 'string') {
                permanentAddr = personalInfo.permanent_address;
            } else if (personalInfo.permanent_address.full_address) {
                permanentAddr = personalInfo.permanent_address.full_address;
            } else {
                // Try to construct from parts
                const addrParts = [
                    personalInfo.permanent_address.house_block_lot_no,
                    personalInfo.permanent_address.street,
                    personalInfo.permanent_address.subdivision_village,
                    personalInfo.permanent_address.barangay,
                    personalInfo.permanent_address.city_municipality,
                    personalInfo.permanent_address.province,
                    personalInfo.permanent_address.zip_code
                ].filter(part => part && part.trim() !== '');
                
                if (addrParts.length > 0) {
                    permanentAddr = addrParts.join(', ');
                }
            }
        }
        
        setTextContent('residentialAddress', residentialAddr, 'Residential Address');
        setTextContent('permanentAddress', permanentAddr, 'Permanent Address');
        
        console.log('✅ Personal information population completed');
    },

    // Format ID labels for display
    formatIDLabel(key) {
        const labels = {
            'gsis_id': 'GSIS ID',
            'pagibig_id': 'Pag-IBIG ID',
            'philhealth_no': 'PhilHealth No.',
            'sss_no': 'SSS No.',
            'tin_no': 'TIN No.'
        };
        return labels[key] || key.replace('_', ' ').toUpperCase();
    },

    // Setup modal action buttons
    setupModalActions() {
        const removeBtn = document.getElementById('removeCandidate');
        const shortlistBtn = document.getElementById('shortlistCandidate');
        const rejectBtn = document.getElementById('rejectCandidate');
        
        if (removeBtn) {
            removeBtn.addEventListener('click', async () => {
                const candidateId = removeBtn.dataset.candidateId;
                const confirmed = await confirmRemove('this candidate');
                if (confirmed) {
                    await this.removeCandidate(candidateId);
                    this.modal.hide();
                }
            });
        }
        
        if (shortlistBtn) {
            shortlistBtn.addEventListener('click', async () => {
                const candidateId = shortlistBtn.dataset.candidateId;
                await this.updateCandidateStatus(candidateId, 'shortlisted');
                this.modal.hide();
            });
        }
        
        if (rejectBtn) {
            rejectBtn.addEventListener('click', async () => {
                const candidateId = rejectBtn.dataset.candidateId;
                await this.updateCandidateStatus(candidateId, 'rejected');
                this.modal.hide();
            });
        }
    },

    // Remove candidate
    async removeCandidate(candidateId, showToast = true) {
        try {
            const result = await APIService.candidates.delete(candidateId);
            
            if (result.success) {
                if (showToast) {
                    ToastUtils.showSuccess('Candidate removed successfully');
                    await this.loadCandidates();
                }
                return true;
            } else {
                if (showToast) {
                    ToastUtils.showError('Failed to remove candidate');
                }
                return false;
            }
        } catch (error) {
            console.error('Error removing candidate:', error);
            if (showToast) {
                ToastUtils.showError('Error removing candidate');
            }
            return false;
        }
    },

    // Update candidate status
    async updateCandidateStatus(candidateId, status, showToast = true) {
        try {
            const result = await APIService.candidates.updateStatus(candidateId, status);
            
            if (result.success) {
                if (showToast) {
                    ToastUtils.showSuccess(`Candidate ${status} successfully`);
                    await this.loadCandidates();
                }
                return true;
            } else {
                if (showToast) {
                    ToastUtils.showError('Failed to update candidate status');
                }
                return false;
            }
        } catch (error) {
            console.error('Error updating candidate status:', error);
            if (showToast) {
                ToastUtils.showError('Error updating candidate status');
            }
            return false;
        }
    },

    // Handle remove candidate with confirmation
    async handleRemoveCandidate(candidateId) {
        const confirmed = await confirmRemove('this candidate');
        if (confirmed) {
            await this.removeCandidate(candidateId);
        }
    },

    // Get processing type label with appropriate styling
    getProcessingTypeLabel(processingType, ocrConfidence = null) {
        const typeConfig = {
            'resume': {
                label: 'Resume',
                icon: 'fas fa-file-alt',
                class: 'processing-type-resume'
            },
            'pds': {
                label: 'PDS Excel',
                icon: 'fas fa-file-excel',
                class: 'processing-type-pds'
            },
            'pds_text': {
                label: 'PDS Text',
                icon: 'fas fa-file-text',
                class: 'processing-type-pds-text'
            },
            'pds_only': {
                label: 'PDS Only',
                icon: 'fas fa-id-card',
                class: 'processing-type-pds-only'
            },
            'ocr_scanned': {
                label: 'OCR Scanned',
                icon: 'fas fa-scanner',
                class: 'processing-type-ocr'
            }
        };

        const config = typeConfig[processingType] || {
            label: 'Unknown',
            icon: 'fas fa-question',
            class: 'processing-type-unknown'
        };

        // Add OCR confidence if available
        let confidenceDisplay = '';
        if (processingType === 'ocr_scanned' && ocrConfidence !== null && ocrConfidence !== undefined) {
            const confidenceClass = this.getConfidenceColorClass(ocrConfidence);
            confidenceDisplay = ` <span class="ocr-confidence-badge ${confidenceClass}" title="OCR Confidence: ${ocrConfidence}%">${Math.round(ocrConfidence)}%</span>`;
        }

        return `<span class="processing-type-badge ${config.class}" title="Processed using ${config.label}">
                    <i class="${config.icon}"></i> ${config.label}${confidenceDisplay}
                </span>`;
    },

    // Get score color class
    getScoreColorClass(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        if (score >= 40) return 'score-fair';
        return 'score-poor';
    },

    // PDS-specific formatting methods for Phase 2 frontend modernization
    
    // Format government IDs for display
    formatGovernmentIds(candidate) {
        let govIds = candidate.government_ids || {};
        
        // If government_ids is empty, try to extract from PDS data
        if (Object.keys(govIds).length === 0 && candidate.pds_data && candidate.pds_data.personal_info) {
            const personalInfo = candidate.pds_data.personal_info;
            govIds = {
                gsis_id: personalInfo.gsis_id,
                pagibig_id: personalInfo.pagibig_id,
                philhealth_no: personalInfo.philhealth_no,
                sss_no: personalInfo.sss_no,
                tin_no: personalInfo.tin_no
            };
        }
        
        const ids = [];
        
        // Priority order for display - Updated to match actual PDS field names
        const idTypes = [
            { key: 'tin_no', label: 'TIN', icon: 'fa-id-card' },
            { key: 'sss_no', label: 'SSS', icon: 'fa-shield-alt' },
            { key: 'philhealth_no', label: 'PhilHealth', icon: 'fa-heartbeat' },
            { key: 'pagibig_id', label: 'Pag-IBIG', icon: 'fa-home' },
            { key: 'gsis_id', label: 'GSIS', icon: 'fa-university' }
        ];
        
        idTypes.forEach(idType => {
            const value = govIds[idType.key];
            if (value && 
                value.toString().trim() !== '' && 
                value.toString().toLowerCase() !== 'n/a' &&
                value.toString().toLowerCase() !== 'none' &&
                value.toString() !== 'null') {
                ids.push(`<span class="gov-id-item" title="${idType.label}: ${value}">
                    <i class="fas ${idType.icon}"></i> ${idType.label}
                </span>`);
            }
        });
        
        if (ids.length === 0) {
            return '<span class="text-muted"><i class="fas fa-id-card-alt"></i> Not provided</span>';
        }
        
        // Show max 2 IDs, with count if more
        const displayed = ids.slice(0, 2);
        const additional = ids.length > 2 ? `<span class="ids-count">+${ids.length - 2}</span>` : '';
        
        return displayed.join(' ') + additional;
    },
    
    // Get highest education level
    getHighestEducationLevel(candidate) {
        const education = candidate.education || [];
        if (!Array.isArray(education) || education.length === 0) {
            return '<span class="text-muted">Not specified</span>';
        }
        
        // Education level priority (highest to lowest) - Updated for PDS structure
        const levelPriority = {
            'graduate': 5,
            'doctoral': 5,
            'doctorate': 5,
            'phd': 5,
            'masters': 4,
            'master': 4,
            'college': 3,
            'bachelor': 3,
            'undergraduate': 3,
            'vocational': 2,
            'technical': 2,
            'trade': 2,
            'secondary': 1,
            'high school': 1,
            'elementary': 0
        };
        
        let highest = null;
        let highestPriority = -1;
        
        education.forEach(edu => {
            const level = (edu.level || '').toLowerCase();
            const degree = (edu.degree || edu.course || '').toLowerCase();
            const school = edu.school || edu.institution || '';
            
            // Check level first, then degree content
            let priority = levelPriority[level] || -1;
            
            if (priority === -1) {
                // Check degree content for keywords
                for (const [keyword, prio] of Object.entries(levelPriority)) {
                    if (degree.includes(keyword) && prio > priority) {
                        priority = prio;
                    }
                }
            }
            
            if (priority > highestPriority) {
                highest = edu;
                highestPriority = priority;
            }
        });
        
        if (highest) {
            const level = highest.level || 'Unknown';
            const school = highest.school || highest.institution || '';
            const displayText = level.charAt(0).toUpperCase() + level.slice(1);
            
            return `<span class="education-level" title="${displayText} - ${school}">
                <i class="fas fa-graduation-cap"></i> ${displayText}
            </span>`;
        }
        
        return '<span class="text-muted">Not classified</span>';
    },
    
    // Format civil service eligibility
    formatCivilServiceEligibility(candidate) {
        const eligibility = candidate.eligibility || [];
        if (!Array.isArray(eligibility) || eligibility.length === 0) {
            return '<span class="text-muted"><i class="fas fa-certificate"></i> None</span>';
        }
        
        // Filter out invalid entries and find the best eligibility
        const validEligibility = eligibility.filter(elig => 
            elig.eligibility && 
            elig.eligibility.trim() !== '' && 
            !elig.eligibility.includes('WORK EXPERIENCE') &&
            !elig.eligibility.includes('Continue on separate') &&
            !elig.eligibility.includes('28.') &&
            !elig.eligibility.includes('From') &&
            !elig.eligibility.includes('To')
        );
        
        if (validEligibility.length === 0) {
            return '<span class="text-muted"><i class="fas fa-certificate"></i> None</span>';
        }
        
        // Find the best eligibility (with rating or most recent)
        let best = null;
        let bestRating = 0;
        
        validEligibility.forEach(elig => {
            const rating = parseFloat(elig.rating || 0);
            const examName = elig.eligibility || '';
            
            if (examName && rating > bestRating) {
                best = elig;
                bestRating = rating;
            } else if (examName && !best) {
                best = elig; // Take first valid entry if no ratings found
            }
        });
        
        if (best) {
            const examType = best.eligibility || 'Civil Service';
            const rating = best.rating || '';
            
            let badgeClass = 'badge bg-secondary';
            if (rating && parseFloat(rating) >= 80) {
                badgeClass = 'badge bg-success';
            } else if (rating && parseFloat(rating) >= 70) {
                badgeClass = 'badge bg-warning';
            }
            
            const ratingText = rating ? ` (${rating}%)` : '';
            const title = `${examType}${ratingText}${best.date_exam ? ` - ${best.date_exam}` : ''}`;
            
            // Show count if multiple eligibilities
            const countText = validEligibility.length > 1 ? ` +${validEligibility.length - 1}` : '';
            
            return `<span class="${badgeClass}" title="${title}">
                <i class="fas fa-certificate"></i> ${FormatUtils.truncateText(examType, 12)}${ratingText}${countText}
            </span>`;
        }
        
        // Fallback: show count of eligibilities
        return `<span class="badge bg-info" title="${validEligibility.length} eligibility entries">
            <i class="fas fa-certificate"></i> ${validEligibility.length} entries
        </span>`;
    },
    
    // Format assessment score with breakdown
    formatAssessmentScore(candidate) {
        const assessmentScore = candidate.assessment_score || candidate.score || 0;
        
        // Show assessment score out of 100
        return `${assessmentScore}/100`;
    },

    // Get confidence color class for OCR confidence scores
    getConfidenceColorClass(confidence) {
        if (confidence >= 85) return 'confidence-high';
        if (confidence >= 70) return 'confidence-medium';
        if (confidence >= 50) return 'confidence-low';
        return 'confidence-very-low';
    }
};

// Make globally available
window.CandidatesModule = CandidatesModule;

// Backward compatibility
window.loadCandidatesSection = CandidatesModule.loadCandidates.bind(CandidatesModule);
