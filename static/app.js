// Tab Management
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // If switching to scheduled jobs, load them and start auto-refresh
    if (tabName === 'scheduled-jobs') {
        startJobsAutoRefresh();
    } else {
        stopJobsAutoRefresh();
    }
}

// Form handling for New Job
const form = document.getElementById('waitlistForm');
const runNowBtn = document.getElementById('runNowBtn');
const scheduleLaterBtn = document.getElementById('scheduleLaterBtn');
const messageDiv = document.getElementById('message');
const datetimeGroup = document.getElementById('datetimeGroup');
const scheduleOptions = document.querySelectorAll('.schedule-option');
const datetimeInput = document.getElementById('scheduleDateTime');

let selectedOption = 'now';

// Handle schedule option selection
scheduleOptions.forEach(option => {
    option.addEventListener('click', () => {
        // Remove active class from all options
        scheduleOptions.forEach(opt => opt.classList.remove('active'));
        
        // Add active class to clicked option
        option.classList.add('active');
        
        // Get selected option
        selectedOption = option.dataset.option;
        
        // Toggle datetime input and buttons
        if (selectedOption === 'later') {
            datetimeGroup.classList.add('show');
            datetimeInput.required = true;
            runNowBtn.style.display = 'none';
            scheduleLaterBtn.style.display = 'block';
        } else {
            datetimeGroup.classList.remove('show');
            datetimeInput.required = false;
            runNowBtn.style.display = 'block';
            scheduleLaterBtn.style.display = 'none';
        }
    });
});

// Handle form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const activeButton = selectedOption === 'now' ? runNowBtn : scheduleLaterBtn;
    const originalText = activeButton.textContent;
    
    // Disable button and show loading state
    activeButton.disabled = true;
    activeButton.textContent = 'Submitting...';
    
    // Get form data
    const formData = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        course: document.getElementById('course').value,
        players: document.getElementById('players').value,
        runType: selectedOption,
        scheduleDateTime: selectedOption === 'later' ? datetimeInput.value : null
    };
    
    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showMessage(result.message, 'success');
            form.reset();
            // Reset to default state
            scheduleOptions[0].click();
        } else {
            showMessage('Something went wrong. Please try again.', 'error');
        }
    } catch (error) {
        showMessage('Error submitting form. Please try again.', 'error');
    } finally {
        activeButton.disabled = false;
        activeButton.textContent = originalText;
    }
});

function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type} show`;
    
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 5000);
}

// Jobs Management
let currentFilter = 'all';
let allJobs = [];

// Filter buttons
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderJobs();
    });
});

async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const result = await response.json();
        
        if (result.status === 'success') {
            allJobs = result.jobs;
            renderJobs();
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function renderJobs() {
    const jobsList = document.getElementById('jobsList');
    
    let filteredJobs = allJobs;
    if (currentFilter !== 'all') {
        filteredJobs = allJobs.filter(job => job.status === currentFilter);
    }
    
    if (filteredJobs.length === 0) {
        jobsList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No ${currentFilter === 'all' ? '' : currentFilter} jobs found</p>
            </div>
        `;
        return;
    }
    
    jobsList.innerHTML = filteredJobs.map(job => `
        <div class="job-card ${job.status}">
            <div class="job-header">
                <div class="job-title">${job.first_name} ${job.last_name}</div>
                <span class="job-status ${job.status}">${job.status.toUpperCase()}</span>
            </div>
            
            <div class="job-details">
                <div class="job-detail">
                    <strong>Email</strong>
                    <span>${job.email}</span>
                </div>
                <div class="job-detail">
                    <strong>Phone</strong>
                    <span>${job.phone}</span>
                </div>
                <div class="job-detail">
                    <strong>Course</strong>
                    <span>${job.course}</span>
                </div>
                <div class="job-detail">
                    <strong>Players</strong>
                    <span>${job.players}</span>
                </div>
                <div class="job-detail">
                    <strong>Type</strong>
                    <span>${job.run_type === 'now' ? 'Immediate' : 'Scheduled'}</span>
                </div>
                <div class="job-detail">
                    <strong>${job.run_type === 'now' ? 'Created' : 'Scheduled'}</strong>
                    <span>${formatDateTime(job.run_type === 'now' ? job.created_at : job.schedule_datetime)}</span>
                </div>
            </div>
            
            ${job.status === 'pending' ? `
                <div class="job-actions">
                    <button class="btn-secondary btn-small" onclick="editJob(${job.id})">
                        ✏️ Edit
                    </button>
                    <button class="btn-danger btn-small" onclick="cancelJob(${job.id})">
                        ❌ Cancel
                    </button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return 'N/A';
    
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
        timeZone: 'America/Los_Angeles',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
        timeZoneName: 'short'
    });
}

async function cancelJob(jobId) {
    if (!confirm('Are you sure you want to cancel this job?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/jobs/${jobId}/cancel`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            loadJobs(); // Reload jobs
        } else {
            alert('Failed to cancel job');
        }
    } catch (error) {
        console.error('Error cancelling job:', error);
        alert('Error cancelling job');
    }
}

async function editJob(jobId) {
    // Find the job
    const job = allJobs.find(j => j.id === jobId);
    if (!job) return;
    
    // Switch to new job tab
    document.querySelectorAll('.tab')[0].click();
    
    // Populate form
    document.getElementById('firstName').value = job.first_name;
    document.getElementById('lastName').value = job.last_name;
    document.getElementById('email').value = job.email;
    document.getElementById('phone').value = job.phone;
    document.getElementById('course').value = job.course;
    document.getElementById('players').value = job.players;
    
    if (job.schedule_datetime) {
        // Click schedule later option
        scheduleOptions[1].click();
        document.getElementById('scheduleDateTime').value = job.schedule_datetime.slice(0, 16);
    }
    
    // Cancel the old job
    await cancelJob(jobId);
}

// Update server time display
async function updateServerTime() {
    try {
        const response = await fetch('/api/time');
        const result = await response.json();
        
        if (result.status === 'success') {
            document.getElementById('serverTime').textContent = result.formatted;
        }
    } catch (error) {
        console.error('Error fetching server time:', error);
    }
}

// Auto-refresh jobs list when on Scheduled Jobs tab
let jobsRefreshInterval = null;

function startJobsAutoRefresh() {
    // Refresh jobs every 5 seconds when on the jobs tab
    if (jobsRefreshInterval) {
        clearInterval(jobsRefreshInterval);
    }
    loadJobs(); // Load immediately
    jobsRefreshInterval = setInterval(loadJobs, 5000);
}

function stopJobsAutoRefresh() {
    if (jobsRefreshInterval) {
        clearInterval(jobsRefreshInterval);
        jobsRefreshInterval = null;
    }
}

async function clearCompletedJobs() {
    if (!confirm('Are you sure you want to clear all completed and cancelled jobs? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/jobs/clear-completed', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert(result.message);
            loadJobs(); // Reload jobs list
        } else {
            alert('Failed to clear jobs: ' + result.message);
        }
    } catch (error) {
        console.error('Error clearing jobs:', error);
        alert('Error clearing jobs');
    }
}

// Load jobs when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    updateServerTime();
    // Update server time every 30 seconds
    setInterval(updateServerTime, 30000);
});

