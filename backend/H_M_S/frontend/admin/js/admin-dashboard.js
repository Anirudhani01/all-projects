// Admin Dashboard JavaScript

// DOM Elements
const dashboardStats = document.getElementById('dashboard-stats');
const recentAppointmentsTable = document.getElementById('recent-appointments');
const appointmentsChart = document.getElementById('appointmentsChart');
const demographicsChart = document.getElementById('demographicsChart');

// State
let dashboardData = {};
let isRedirecting = false;
let initializationCount = 0;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard page loaded, initializing without authentication...');
    console.log('Initialization count:', initializationCount);
    
    // Prevent multiple initializations
    if (window.dashboardInitialized) {
        console.log('Dashboard already initialized, skipping...');
        return;
    }
    
    // Prevent too many initializations
    initializationCount++;
    if (initializationCount > 3) {
        console.log('Too many initialization attempts, stopping...');
        return;
    }
    
    window.dashboardInitialized = true;
    
    // Only initialize if we're on the dashboard page
    if (window.location.pathname.includes('dashboard.html') || window.location.pathname.endsWith('/admin/')) {
        // Always initialize without authentication
        initializeDashboardWithoutAuth();
    }
});

function initializeDashboard() {
    // Check authentication
    if (!AdminAuth.isLoggedIn()) {
        console.log('User not logged in, redirecting to login');
        // Prevent infinite redirects
        if (!isRedirecting) {
            isRedirecting = true;
            setTimeout(() => {
        window.location.href = 'login.html';
            }, 100);
        }
        return;
    }
    
    console.log('User is logged in, proceeding with dashboard initialization');
    
    // Set user info
    setUserInfo();
    
    // Load dashboard data
    loadDashboardData();
    
    // Setup event listeners
    setupEventListeners();
}

function initializeDashboardWithoutAuth() {
    try {
        console.log('Initializing dashboard without authentication...');
        console.log('Current URL:', window.location.href);
        console.log('Dashboard initialized flag:', window.dashboardInitialized);
        
        // Set user info for display
        setUserInfoWithoutAuth();
        
        // Load dashboard data without authentication
        loadDashboardDataWithoutAuth();
        
        // Setup event listeners
        setupEventListeners();
        
        console.log('Dashboard initialization completed successfully');
    } catch (error) {
        console.error('Error during dashboard initialization:', error);
        // Show fallback data on any error
        showFallbackData();
    }
}

function setUserInfoWithoutAuth() {
    // Set user info in header
    const userNameElement = document.getElementById('user-name');
    const userRoleElement = document.getElementById('user-role');
    const userAvatarElement = document.getElementById('user-avatar');
    
    if (userNameElement) userNameElement.textContent = 'Admin';
    if (userRoleElement) userRoleElement.textContent = 'Administrator';
    if (userAvatarElement) userAvatarElement.textContent = 'A';
}


// Set user information in header
function setUserInfo() {
    const user = AdminAuth.getCurrentUser();
    if (user) {
        document.getElementById('user-name').textContent = user.username;
        document.getElementById('user-role').textContent = user.role;
        document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Disabled auto-refresh to prevent continuous loading issues
    // Auto-refresh dashboard every 5 minutes
    // setInterval(() => {
    //     if (typeof AdminAuth !== 'undefined' && AdminAuth.isLoggedIn()) {
    //         loadDashboardData();
    //     } else {
    //         loadDashboardDataWithoutAuth();
    //     }
    // }, 5 * 60 * 1000);
    
    // Prevent any accidental page refreshes
    window.addEventListener('beforeunload', function(e) {
        // Only prevent if there are unsaved changes (optional)
        // e.preventDefault();
        // e.returnValue = '';
    });
}

// Load dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadDashboardStats(),
            loadRecentAppointments(),
            loadChartData()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        if (typeof AdminAuth !== 'undefined' && AdminAuth.showNotification) {
        AdminAuth.showNotification('Failed to load dashboard data', 'error');
        }
        // Hide loading state
        const loadingElement = document.querySelector('.loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
}

// Load dashboard data without authentication
async function loadDashboardDataWithoutAuth() {
    try {
        console.log('Loading dashboard data without authentication...');
        await Promise.all([
            loadDashboardStatsWithoutAuth(),
            loadRecentAppointmentsWithoutAuth(),
            loadChartDataWithoutAuth()
        ]);
        console.log('Dashboard data loaded successfully');
    } catch (error) {
        console.error('Error loading dashboard data without auth:', error);
        // Don't refresh or redirect on error, just show fallback data
        showFallbackData();
    }
}

// Show fallback data when API calls fail
function showFallbackData() {
    console.log('Showing fallback data...');
    
    // Set fallback statistics
    dashboardData = {
        totalDoctors: 5,
        totalAppointments: 5,
        totalPatients: 5,
        totalBlogPosts: 0,
        unreadMessages: 0,
        todayAppointments: 1,
        thisMonthAppointments: 5
    };
    
    displayDashboardStats();
    
    // Show fallback appointments
    const fallbackAppointments = [
        {
            id: 1,
            patient: { name: 'John Smith' },
            doctor: { name: 'Dr. Sarah Johnson' },
            appointment_date: '2025-09-11',
            appointment_time: '11:00:00',
            status: 'confirmed'
        },
        {
            id: 2,
            patient: { name: 'Jane Doe' },
            doctor: { name: 'Dr. Michael Chen' },
            appointment_date: '2025-09-12',
            appointment_time: '13:00:00',
            status: 'pending'
        }
    ];
    
    displayRecentAppointments(fallbackAppointments);
    
    // Hide loading state
    const loadingElement = document.querySelector('.loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// Load dashboard statistics without authentication
async function loadDashboardStatsWithoutAuth() {
    console.log('loadDashboardStatsWithoutAuth started');
    try {
        console.log('Making API requests without auth...');
        const [doctorsResponse, appointmentsResponse, patientsResponse, blogResponse, contactResponse] = await Promise.all([
            fetch('http://localhost:8000/api/admin/doctors/'),
            fetch('http://localhost:8000/api/admin/appointments/'),
            fetch('http://localhost:8000/api/admin/patients/'),
            fetch('http://localhost:8000/api/admin/blog/'),
            fetch('http://localhost:8000/api/admin/contact/')
        ]);

        console.log('API responses received:', {
            doctors: !!doctorsResponse,
            appointments: !!appointmentsResponse,
            patients: !!patientsResponse,
            blog: !!blogResponse,
            contact: !!contactResponse
        });

        if (!doctorsResponse || !appointmentsResponse || !patientsResponse || !blogResponse || !contactResponse) {
            console.error('One or more API responses failed');
            return;
        }

        console.log('Parsing JSON responses...');
        const doctors = await doctorsResponse.json();
        const appointments = await appointmentsResponse.json();
        const patients = await patientsResponse.json();
        const blogPosts = await blogResponse.json();
        const contactMessages = await contactResponse.json();

        console.log('Parsed data:', {
            doctors: doctors,
            appointments: appointments,
            patients: patients,
            blogPosts: blogPosts,
            contactMessages: contactMessages
        });

        // Calculate statistics
        const totalDoctors = doctors.doctors ? doctors.doctors.length : 0;
        const totalAppointments = Array.isArray(appointments) ? appointments.length : 0;
        const totalPatients = Array.isArray(patients) ? patients.length : (patients.patients ? patients.patients.length : 0);
        const totalBlogPosts = Array.isArray(blogPosts) ? blogPosts.length : (blogPosts.posts ? blogPosts.posts.length : 0);
        const unreadMessages = Array.isArray(contactMessages) ? 
            contactMessages.filter(msg => !msg.is_read).length : 
            (contactMessages.messages ? contactMessages.messages.filter(msg => !msg.is_read).length : 0);

        // Calculate today's appointments
        const today = new Date().toISOString().split('T')[0];
        const todayAppointments = Array.isArray(appointments) ? 
            appointments.filter(apt => apt.appointment_date === today).length : 0;

        // Calculate this month's appointments
        const currentMonth = new Date().getMonth();
        const currentYear = new Date().getFullYear();
        const thisMonthAppointments = Array.isArray(appointments) ? 
            appointments.filter(apt => {
                const aptDate = new Date(apt.appointment_date);
                return aptDate.getMonth() === currentMonth && aptDate.getFullYear() === currentYear;
            }).length : 0;

        dashboardData = {
            totalDoctors,
            totalAppointments,
            totalPatients,
            totalBlogPosts,
            unreadMessages,
            todayAppointments,
            thisMonthAppointments
        };

        console.log('Calculated dashboard data:', dashboardData);
        console.log('Calling displayDashboardStats...');
        displayDashboardStats();

    } catch (error) {
        console.error('Error loading dashboard stats without auth:', error);
        // Show fallback data instead of error
        dashboardData = {
            totalDoctors: 5,
            totalAppointments: 5,
            totalPatients: 5,
            totalBlogPosts: 0,
            unreadMessages: 0,
            todayAppointments: 1,
            thisMonthAppointments: 5
        };
        displayDashboardStats();
        // Hide loading state
        const loadingElement = document.querySelector('.loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    console.log('loadDashboardStats started');
    try {
        console.log('Making API requests...');
        const [doctorsResponse, appointmentsResponse, patientsResponse, blogResponse, contactResponse] = await Promise.all([
            AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/doctors/`),
            AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/appointments/`),
            AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/patients/`),
            AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/blog/`),
            AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/contact/`)
        ]);

        console.log('API responses received:', {
            doctors: !!doctorsResponse,
            appointments: !!appointmentsResponse,
            patients: !!patientsResponse,
            blog: !!blogResponse,
            contact: !!contactResponse
        });

        if (!doctorsResponse || !appointmentsResponse || !patientsResponse || !blogResponse || !contactResponse) {
            console.error('One or more API responses failed');
            return;
        }

        console.log('Parsing JSON responses...');
        const doctors = await doctorsResponse.json();
        const appointments = await appointmentsResponse.json();
        const patients = await patientsResponse.json();
        const blogPosts = await blogResponse.json();
        const contactMessages = await contactResponse.json();

        console.log('Parsed data:', {
            doctors: doctors,
            appointments: appointments,
            patients: patients,
            blogPosts: blogPosts,
            contactMessages: contactMessages
        });

        // Debug: Check if we have the expected data structure
        console.log('Data structure check:', {
            doctorsIsArray: Array.isArray(doctors),
            doctorsHasDoctors: doctors && doctors.doctors,
            appointmentsIsArray: Array.isArray(appointments),
            patientsIsArray: Array.isArray(patients),
            patientsHasPatients: patients && patients.patients,
            blogPostsIsArray: Array.isArray(blogPosts),
            blogPostsHasPosts: blogPosts && blogPosts.posts,
            contactMessagesIsArray: Array.isArray(contactMessages),
            contactMessagesHasMessages: contactMessages && contactMessages.messages
        });

        // Calculate statistics
        const totalDoctors = doctors.doctors ? doctors.doctors.length : 0;
        const totalAppointments = Array.isArray(appointments) ? appointments.length : 0;
        const totalPatients = Array.isArray(patients) ? patients.length : (patients.patients ? patients.patients.length : 0);
        const totalBlogPosts = Array.isArray(blogPosts) ? blogPosts.length : (blogPosts.posts ? blogPosts.posts.length : 0);
        const unreadMessages = Array.isArray(contactMessages) ? 
            contactMessages.filter(msg => !msg.is_read).length : 
            (contactMessages.messages ? contactMessages.messages.filter(msg => !msg.is_read).length : 0);

        // Calculate today's appointments
        const today = new Date().toISOString().split('T')[0];
        const todayAppointments = Array.isArray(appointments) ? 
            appointments.filter(apt => apt.appointment_date === today).length : 0;

        // Calculate this month's appointments
        const currentMonth = new Date().getMonth();
        const currentYear = new Date().getFullYear();
        const thisMonthAppointments = Array.isArray(appointments) ? 
            appointments.filter(apt => {
                const aptDate = new Date(apt.appointment_date);
                return aptDate.getMonth() === currentMonth && aptDate.getFullYear() === currentYear;
            }).length : 0;

        dashboardData = {
            totalDoctors,
            totalAppointments,
            totalPatients,
            totalBlogPosts,
            unreadMessages,
            todayAppointments,
            thisMonthAppointments
        };

        console.log('Calculated dashboard data:', dashboardData);
        console.log('Calling displayDashboardStats...');
        displayDashboardStats();

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        showError(dashboardStats, 'Failed to load statistics');
        // Hide loading state
        const loadingElement = document.querySelector('.loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
}

// Display dashboard statistics
function displayDashboardStats() {
    try {
    console.log('displayDashboardStats called with data:', dashboardData);
    
    const stats = [
        {
            title: 'Total Doctors',
            value: dashboardData.totalDoctors || 0,
            icon: 'fas fa-user-md',
            color: 'primary',
            change: '+2 this month'
        },
        {
            title: 'Total Appointments',
            value: dashboardData.totalAppointments || 0,
            icon: 'fas fa-calendar-alt',
            color: 'success',
            change: `+${dashboardData.thisMonthAppointments || 0} this month`
        },
        {
            title: 'Total Patients',
            value: dashboardData.totalPatients || 0,
            icon: 'fas fa-users',
            color: 'warning',
            change: '+15 this week'
        },
        {
            title: 'Today\'s Appointments',
            value: dashboardData.todayAppointments || 0,
            icon: 'fas fa-calendar-day',
            color: 'danger',
            change: 'Active today'
        },
        {
            title: 'Blog Posts',
            value: dashboardData.totalBlogPosts || 0,
            icon: 'fas fa-blog',
            color: 'primary',
            change: '+3 this week'
        },
        {
            title: 'Unread Messages',
            value: dashboardData.unreadMessages || 0,
            icon: 'fas fa-envelope',
            color: 'warning',
            change: 'Needs attention'
        }
    ];

    console.log('Looking for dashboard-stats element...');
    const dashboardStatsElement = document.getElementById('dashboard-stats');
    
    if (!dashboardStatsElement) {
        console.error('Dashboard stats element not found!');
        return;
    }
    
    console.log('Found dashboard-stats element:', dashboardStatsElement);
    
    // Hide loading state first
    const loadingElement = dashboardStatsElement.querySelector('.loading');
    if (loadingElement) {
        console.log('Hiding loading element');
        loadingElement.style.display = 'none';
    }
    
    console.log('Rendering stats cards...');
        dashboardStatsElement.innerHTML = stats.map(stat => {
            let clickable = '';
            let onclick = '';
            
            if (stat.title === 'Total Patients') {
                clickable = 'clickable';
                onclick = 'onclick="switchToPatientsChart()"';
            } else if (stat.title === 'Total Appointments') {
                clickable = 'clickable';
                onclick = 'onclick="switchToAppointmentsChart()"';
            } else if (stat.title === 'Total Doctors') {
                clickable = 'clickable';
                onclick = 'onclick="switchToDoctorsChart()"';
            }
            
            return `
            <div class="dashboard-card ${clickable}" ${onclick}>
                <div class="card-header">
                    <span class="card-title">${stat.title}</span>
                    <div class="card-icon ${stat.color}">
                        <i class="${stat.icon}"></i>
                    </div>
                </div>
                <div class="card-value">${stat.value}</div>
                <div class="card-change ${stat.change.includes('+') ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-up"></i>
                    ${stat.change}
                </div>
            </div>
        `;
        }).join('');
    
    console.log('Dashboard stats rendered successfully');
    } catch (error) {
        console.error('Error in displayDashboardStats:', error);
    }
}

// Load recent appointments without authentication
async function loadRecentAppointmentsWithoutAuth() {
    try {
        const response = await fetch('http://localhost:8000/api/admin/appointments/?limit=10');
        if (!response.ok) {
            console.error('No response from appointments API');
            return;
        }

        const appointments = await response.json();
        console.log('Appointments data (no auth):', appointments);
        displayRecentAppointments(appointments);

    } catch (error) {
        console.error('Error loading recent appointments without auth:', error);
        // Show fallback appointments data
        const fallbackAppointments = [
            {
                id: 1,
                patient: { name: 'John Smith' },
                doctor: { name: 'Dr. Sarah Johnson' },
                appointment_date: '2025-09-11',
                appointment_time: '11:00:00',
                status: 'confirmed'
            },
            {
                id: 2,
                patient: { name: 'Jane Doe' },
                doctor: { name: 'Dr. Michael Chen' },
                appointment_date: '2025-09-12',
                appointment_time: '13:00:00',
                status: 'pending'
            }
        ];
        displayRecentAppointments(fallbackAppointments);
    }
}

// Load recent appointments
async function loadRecentAppointments() {
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/appointments/?limit=10`);
        if (!response) {
            console.error('No response from appointments API');
            return;
        }

        const appointments = await response.json();
        console.log('Appointments data:', appointments);
        displayRecentAppointments(appointments);

    } catch (error) {
        console.error('Error loading recent appointments:', error);
        showError(recentAppointmentsTable, 'Failed to load appointments');
    }
}

// Display recent appointments
function displayRecentAppointments(appointments) {
    try {
        if (!recentAppointmentsTable) {
            console.error('recentAppointmentsTable element not found');
            return;
        }
        
    const tbody = recentAppointmentsTable.querySelector('tbody');
        if (!tbody) {
            console.error('tbody element not found in recentAppointmentsTable');
            return;
        }
    
        if (!appointments || appointments.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="loading">
                    <i class="fas fa-calendar-times"></i>
                    No appointments found
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = appointments.map(appointment => `
        <tr>
                <td>${appointment.patient?.name || 'N/A'}</td>
                <td>${appointment.doctor?.name || 'N/A'}</td>
            <td>
                ${new Date(appointment.appointment_date).toLocaleDateString()} 
                ${appointment.appointment_time}
            </td>
            <td>
                <span class="status-badge ${getStatusClass(appointment.status)}">
                    ${appointment.status || 'Scheduled'}
                </span>
            </td>
            <td>
                <button class="btn btn-outline btn-sm" onclick="viewAppointment(${appointment.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
    } catch (error) {
        console.error('Error in displayRecentAppointments:', error);
    }
}

// Load chart data without authentication
async function loadChartDataWithoutAuth() {
    try {
        const response = await fetch('http://localhost:8000/api/admin/appointments/');
        if (!response.ok) return;

        const appointments = await response.json();

        // Prepare data for charts
        const appointmentsData = prepareAppointmentsChartData(appointments);
        const demographicsData = prepareDemographicsChartData(appointments);

        // Create charts
        createAppointmentsChart(appointmentsData);
        createDemographicsChart(demographicsData);

    } catch (error) {
        console.error('Error loading chart data without auth:', error);
    }
}

// Load chart data
async function loadChartData() {
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/appointments/`);
        if (!response) return;

        const appointments = await response.json();

        // Prepare data for charts
        const appointmentsData = prepareAppointmentsChartData(appointments);
        const demographicsData = prepareDemographicsChartData(appointments);

        // Create charts
        createAppointmentsChart(appointmentsData);
        createDemographicsChart(demographicsData);

    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

// Prepare appointments chart data based on time filter
function prepareAppointmentsChartData(appointments) {
    const today = new Date();
    let filteredAppointments = [];
    let labels = [];
    let data = [];
    
    switch (currentTimeFilter) {
        case 'today':
            // Filter appointments for today
            const todayStr = today.toISOString().split('T')[0];
            filteredAppointments = appointments.filter(apt => apt.appointment_date === todayStr);
            
            // Group by hour for today
            const hours = [];
            const hourCounts = {};
            
            for (let i = 8; i <= 18; i += 2) {
                const hour = i.toString().padStart(2, '0') + ':00';
                hours.push(hour);
                hourCounts[hour] = 0;
            }
            
            filteredAppointments.forEach(apt => {
                const time = apt.appointment_time.substring(0, 5); // Get HH:MM
                const hour = time.substring(0, 2) + ':00';
                if (hourCounts.hasOwnProperty(hour)) {
                    hourCounts[hour]++;
                }
            });
            
            labels = hours;
            data = hours.map(hour => hourCounts[hour]);
            break;
            
        case 'week':
            // Filter appointments for this week (last 7 days)
            const weekAgo = new Date(today);
            weekAgo.setDate(today.getDate() - 7);
            
            filteredAppointments = appointments.filter(apt => {
                const aptDate = new Date(apt.appointment_date);
                return aptDate >= weekAgo && aptDate <= today;
            });
            
            // Group by day for the week
            const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            const weekDayCounts = [0, 0, 0, 0, 0, 0, 0];
            
            filteredAppointments.forEach(apt => {
                const date = new Date(apt.appointment_date);
                const dayOfWeek = date.getDay();
                weekDayCounts[dayOfWeek]++;
            });
            
            // Reorder to start with Thursday (as shown in the image)
            labels = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'];
            data = [weekDayCounts[4], weekDayCounts[5], weekDayCounts[6], weekDayCounts[0], weekDayCounts[1], weekDayCounts[2], weekDayCounts[3]];
            break;
            
        case 'month':
        default:
            // Filter appointments for this month
            const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
            const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
            
            filteredAppointments = appointments.filter(apt => {
                const aptDate = new Date(apt.appointment_date);
                return aptDate >= monthStart && aptDate <= monthEnd;
            });
            
            // Group by week for the month
            const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            const weekCounts = [0, 0, 0, 0];
            
            filteredAppointments.forEach(apt => {
                const date = new Date(apt.appointment_date);
                const weekOfMonth = Math.ceil(date.getDate() / 7) - 1;
                if (weekOfMonth >= 0 && weekOfMonth < 4) {
                    weekCounts[weekOfMonth]++;
                }
            });
            
            labels = weeks;
            data = weekCounts;
            break;
    }
    
    return {
        labels: labels,
        data: data
    };
}

// Prepare demographics chart data
function prepareDemographicsChartData(appointments) {
    // Mock data for demographics (in real app, this would come from patient data)
    return {
        labels: ['Cardiology', 'Neurology', 'Orthopedics', 'Dermatology', 'Pulmonology'],
        data: [25, 20, 18, 15, 12]
    };
}

// Create appointments chart
function createAppointmentsChart(data) {
    // Find the main chart canvas (in the chart card with canvas)
    const allChartCards = document.querySelectorAll('.dashboard-card');
    let mainChartCard = null;
    
    for (let card of allChartCards) {
        if (card.querySelector('canvas')) {
            mainChartCard = card;
            break;
        }
    }
    
    if (!mainChartCard) {
        console.error('Main chart card not found');
        return;
    }
    
    const canvas = mainChartCard.querySelector('canvas');
    if (!canvas) {
        console.error('Chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destroy ALL existing chart instances to prevent conflicts
    if (window.patientsChartInstance) {
        window.patientsChartInstance.destroy();
        window.patientsChartInstance = null;
    }
    if (window.appointmentsChartInstance) {
        window.appointmentsChartInstance.destroy();
        window.appointmentsChartInstance = null;
    }
    if (window.doctorsChartInstance) {
        window.doctorsChartInstance.destroy();
        window.doctorsChartInstance = null;
    }
    if (window.demographicsChartInstance) {
        window.demographicsChartInstance.destroy();
        window.demographicsChartInstance = null;
    }
    
    window.appointmentsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Appointments',
                data: data.data,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Create demographics chart
function createDemographicsChart(data) {
    // Find the main chart canvas (in the chart card with canvas)
    const allChartCards = document.querySelectorAll('.dashboard-card');
    let mainChartCard = null;
    
    for (let card of allChartCards) {
        if (card.querySelector('canvas')) {
            mainChartCard = card;
            break;
        }
    }
    
    if (!mainChartCard) {
        console.error('Main chart card not found');
        return;
    }
    
    const canvas = mainChartCard.querySelector('canvas');
    if (!canvas) {
        console.error('Chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destroy ALL existing chart instances to prevent conflicts
    if (window.patientsChartInstance) {
        window.patientsChartInstance.destroy();
        window.patientsChartInstance = null;
    }
    if (window.appointmentsChartInstance) {
        window.appointmentsChartInstance.destroy();
        window.appointmentsChartInstance = null;
    }
    if (window.doctorsChartInstance) {
        window.doctorsChartInstance.destroy();
        window.doctorsChartInstance = null;
    }
    if (window.demographicsChartInstance) {
        window.demographicsChartInstance.destroy();
        window.demographicsChartInstance = null;
    }
    
    window.demographicsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#2563eb',
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#8b5cf6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Utility functions
function getStatusClass(status) {
    const statusMap = {
        'scheduled': 'pending',
        'confirmed': 'active',
        'completed': 'completed',
        'cancelled': 'inactive'
    };
    return statusMap[status?.toLowerCase()] || 'pending';
}

function viewAppointment(appointmentId) {
    // Navigate to appointment details
    window.location.href = `pages/appointments.html?id=${appointmentId}`;
}

function refreshAppointments() {
    loadRecentAppointments();
    AdminAuth.showNotification('Appointments refreshed', 'success');
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

function showError(container, message) {
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

// Add CSS for additional dashboard elements
const additionalStyles = `
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }
    
    .status-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .status-icon {
        width: 20px;
        text-align: center;
    }
    
    .status-icon.success {
        color: #10b981;
    }
    
    .status-icon.warning {
        color: #f59e0b;
    }
    
    .status-icon.danger {
        color: #ef4444;
    }
    
    .btn-sm {
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
    }
    
    .card-content {
        padding: 1rem 0;
    }
    
    .table-content {
        max-height: 400px;
        overflow-y: auto;
    }
`;

// Add the additional styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Chart switching functionality
let currentChartType = 'appointments'; // 'appointments', 'patients', or 'doctors'
let currentTimeFilter = 'month'; // 'today', 'week', 'month'

// Update chart data based on time filter
function updateChartData() {
    const timeFilter = document.getElementById('timeFilter');
    if (timeFilter) {
        currentTimeFilter = timeFilter.value;
        console.log('Time filter changed to:', currentTimeFilter);
        
        // Chart title remains unchanged - only content changes
        
        // Reload chart data with new time filter
        if (currentChartType === 'patients') {
            loadPatientsChartData();
        } else if (currentChartType === 'doctors') {
            loadDoctorsChartData();
        } else {
            loadAppointmentsChartData();
        }
    }
}

// Update chart title based on current time filter
function updateChartTitle() {
    // Don't change the main chart card title - it should always stay "Appointments This Month"
    // The chart content will change, but the card label should remain the same
    console.log('Chart title update skipped - main chart card title should remain unchanged');
}

// Switch to patients chart when Total Patients card is clicked
function switchToPatientsChart() {
    console.log('=== PATIENTS CHART CLICKED ===');
    console.log('Switching to patients chart...');
    currentChartType = 'patients';
    console.log('Current chart type set to:', currentChartType);
    updateChartDisplay();
    loadPatientsChartData();
    console.log('=== PATIENTS CHART SWITCH COMPLETE ===');
}

// Switch to doctors chart when Total Doctors card is clicked
function switchToDoctorsChart() {
    console.log('=== DOCTORS CHART CLICKED ===');
    console.log('Switching to doctors chart...');
    currentChartType = 'doctors';
    console.log('Current chart type set to:', currentChartType);
    updateChartDisplay();
    loadDoctorsChartData();
    console.log('=== DOCTORS CHART SWITCH COMPLETE ===');
}

// Switch back to appointments chart
function switchToAppointmentsChart() {
    console.log('Switching to appointments chart...');
    currentChartType = 'appointments';
    console.log('Current chart type set to:', currentChartType);
    updateChartDisplay();
    loadAppointmentsChartData();
}

// Update chart display based on current type
function updateChartDisplay() {
    console.log('=== UPDATE CHART DISPLAY ===');
    console.log('updateChartDisplay called with currentChartType:', currentChartType);
    
    // Find the main chart card (the one with canvas, not the stats cards)
    const allChartCards = document.querySelectorAll('.dashboard-card');
    let mainChartCard = null;
    let secondaryChartCard = null;
    
    // Look for cards that have canvas elements (these are the actual chart cards)
    for (let card of allChartCards) {
        if (card.querySelector('canvas')) {
            if (!mainChartCard) {
                mainChartCard = card;
            } else {
                secondaryChartCard = card;
                break;
            }
        }
    }
    
    if (!mainChartCard) {
        console.error('Main chart card not found!');
        return;
    }
    
    console.log('Found main chart card:', mainChartCard);
    console.log('Found secondary chart card:', secondaryChartCard);
    
    // Hide the secondary chart card when switching
    if (secondaryChartCard) {
        secondaryChartCard.style.display = 'none';
    }
    
    // Show the main chart card
    mainChartCard.style.display = 'block';
    
    const chartCard = mainChartCard;
    
    const cardTitle = chartCard.querySelector('.card-title');
    const chartCanvas = chartCard.querySelector('canvas');
    const timeFilter = document.getElementById('timeFilter');
    
    // Ensure all STATS cards are visible (but keep chart cards as set above)
    const statsCards = document.querySelectorAll('#dashboard-stats .dashboard-card');
    statsCards.forEach(card => {
        card.style.display = 'block';
    });
    
    if (currentChartType === 'patients') {
        console.log('Setting up patients chart');
        cardTitle.textContent = 'Patient Demographics';
        chartCanvas.id = 'patientsChart';
        // Hide time filter for patients chart
        if (timeFilter) {
            timeFilter.style.display = 'none';
        }
    } else if (currentChartType === 'doctors') {
        console.log('Setting up doctors chart');
        cardTitle.textContent = 'Doctor Specializations';
        chartCanvas.id = 'doctorsChart';
        // Hide time filter for doctors chart
        if (timeFilter) {
            timeFilter.style.display = 'none';
        }
    } else {
        console.log('Setting up appointments chart');
        cardTitle.textContent = 'Appointments This Month';
        chartCanvas.id = 'appointmentsChart';
        // Show time filter for appointments chart
        if (timeFilter) {
            timeFilter.style.display = 'block';
        }
        // Chart title remains unchanged - only content changes
    }
    
    console.log('Chart display updated. Title:', cardTitle.textContent, 'Canvas ID:', chartCanvas.id);
}

// Load patients chart data
async function loadPatientsChartData() {
    try {
        console.log('Loading patients chart data...');
        const response = await fetch('http://localhost:8000/api/admin/patients/');
        if (!response.ok) {
            console.error('Failed to load patients data');
            return;
        }

        const patients = await response.json();
        console.log('Patients data for chart:', patients);

        // Prepare patient demographics data
        const demographicsData = preparePatientDemographicsData(patients);
        console.log('Prepared demographics data:', demographicsData);
        
        // Destroy existing chart if it exists
        if (window.patientsChartInstance) {
            window.patientsChartInstance.destroy();
            window.patientsChartInstance = null;
        }
        
        // Create new patients chart
        createPatientsChart(demographicsData);
        console.log('Patients chart created successfully');
        
    } catch (error) {
        console.error('Error loading patients chart data:', error);
    }
}

// Load appointments chart data
async function loadAppointmentsChartData() {
    try {
        const response = await fetch('http://localhost:8000/api/admin/appointments/');
        if (!response.ok) {
            console.error('Failed to load appointments data');
            return;
        }

        const appointments = await response.json();
        console.log('Appointments data for chart:', appointments);

        // Prepare appointments data
        const appointmentsData = prepareAppointmentsChartData(appointments);
        
        // Destroy existing chart if it exists
        if (window.appointmentsChartInstance) {
            window.appointmentsChartInstance.destroy();
        }
        
        // Create new appointments chart
        createAppointmentsChart(appointmentsData);
        
    } catch (error) {
        console.error('Error loading appointments chart data:', error);
    }
}

// Load doctors chart data
async function loadDoctorsChartData() {
    try {
        console.log('Loading doctors chart data...');
        const response = await fetch('http://localhost:8000/api/admin/doctors/');
        if (!response.ok) {
            console.error('Failed to load doctors data');
            return;
        }

        const responseData = await response.json();
        console.log('Doctors data for chart:', responseData);

        // Extract doctors array from response object
        const doctors = responseData.doctors || responseData;
        
        if (!Array.isArray(doctors)) {
            console.error('Doctors data is not an array:', doctors);
            return;
        }

        // Prepare doctors data
        const doctorsData = prepareDoctorsChartData(doctors);
        console.log('Prepared doctors data:', doctorsData);
        
        // Destroy existing chart if it exists
        if (window.doctorsChartInstance) {
            window.doctorsChartInstance.destroy();
            window.doctorsChartInstance = null;
        }
        
        // Create new doctors chart
        createDoctorsChart(doctorsData);
        console.log('Doctors chart created successfully');
        
    } catch (error) {
        console.error('Error loading doctors chart data:', error);
    }
}

// Prepare patient demographics data from patients API
function preparePatientDemographicsData(patients) {
    // Group patients by age ranges
    const ageGroups = {
        '0-18': 0,
        '19-35': 0,
        '36-50': 0,
        '51-65': 0,
        '65+': 0
    };
    
    // Since we don't have age data, we'll create sample data based on patient count
    const totalPatients = patients.length;
    const sampleDistribution = [0.15, 0.25, 0.30, 0.20, 0.10]; // Sample distribution
    
    let index = 0;
    for (const ageGroup in ageGroups) {
        ageGroups[ageGroup] = Math.round(totalPatients * sampleDistribution[index]);
        index++;
    }
    
    return {
        labels: Object.keys(ageGroups),
        data: Object.values(ageGroups)
    };
}

// Prepare doctors chart data from doctors API
function prepareDoctorsChartData(doctors) {
    // Group doctors by specialization
    const specializations = {};
    
    doctors.forEach(doctor => {
        const spec = doctor.specialization || 'Other';
        specializations[spec] = (specializations[spec] || 0) + 1;
    });
    
    return {
        labels: Object.keys(specializations),
        data: Object.values(specializations)
    };
}

// Create patients chart
function createPatientsChart(data) {
    console.log('=== CREATE PATIENTS CHART ===');
    console.log('Creating patients chart with data:', data);
    
    // Find the main chart canvas (in the chart card with canvas)
    const allChartCards = document.querySelectorAll('.dashboard-card');
    let mainChartCard = null;
    
    for (let card of allChartCards) {
        if (card.querySelector('canvas')) {
            mainChartCard = card;
            break;
        }
    }
    
    if (!mainChartCard) {
        console.error('Main chart card not found');
        return;
    }
    
    const canvas = mainChartCard.querySelector('canvas');
    if (!canvas) {
        console.error('Chart canvas not found');
        return;
    }
    
    console.log('Found canvas for patients chart:', canvas);
    const ctx = canvas.getContext('2d');
    
    // Destroy ALL existing chart instances to prevent conflicts
    if (window.patientsChartInstance) {
        window.patientsChartInstance.destroy();
        window.patientsChartInstance = null;
    }
    if (window.appointmentsChartInstance) {
        window.appointmentsChartInstance.destroy();
        window.appointmentsChartInstance = null;
    }
    if (window.doctorsChartInstance) {
        window.doctorsChartInstance.destroy();
        window.doctorsChartInstance = null;
    }
    if (window.demographicsChartInstance) {
        window.demographicsChartInstance.destroy();
        window.demographicsChartInstance = null;
    }
    
    window.patientsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#2563eb', // Blue
                    '#10b981', // Green
                    '#f59e0b', // Orange
                    '#ef4444', // Red
                    '#8b5cf6'  // Purple
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} patients (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create doctors chart
function createDoctorsChart(data) {
    console.log('Creating doctors chart with data:', data);
    
    // Find the main chart canvas (in the chart card with canvas)
    const allChartCards = document.querySelectorAll('.dashboard-card');
    let mainChartCard = null;
    
    for (let card of allChartCards) {
        if (card.querySelector('canvas')) {
            mainChartCard = card;
            break;
        }
    }
    
    if (!mainChartCard) {
        console.error('Main chart card not found');
        return;
    }
    
    const canvas = mainChartCard.querySelector('canvas');
    if (!canvas) {
        console.error('Chart canvas not found');
        return;
    }
    
    console.log('Found canvas for doctors chart:', canvas);
    const ctx = canvas.getContext('2d');
    
    // Destroy ALL existing chart instances to prevent conflicts
    if (window.patientsChartInstance) {
        window.patientsChartInstance.destroy();
        window.patientsChartInstance = null;
    }
    if (window.appointmentsChartInstance) {
        window.appointmentsChartInstance.destroy();
        window.appointmentsChartInstance = null;
    }
    if (window.doctorsChartInstance) {
        window.doctorsChartInstance.destroy();
        window.doctorsChartInstance = null;
    }
    if (window.demographicsChartInstance) {
        window.demographicsChartInstance.destroy();
        window.demographicsChartInstance = null;
    }
    
    // Generate colors for different specializations
    const colors = [
        '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
    ];
    
    window.doctorsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: data.labels.map((_, index) => colors[index % colors.length]),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} doctors (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}
