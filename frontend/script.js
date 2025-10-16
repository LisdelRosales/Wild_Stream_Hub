// Wild Stream Hub - Frontend JavaScript
// Handles authentication, WebSocket connections, and UI updates

const API_URL = window.location.protocol + '//' + window.location.hostname + ':8000';
let accessToken = localStorage.getItem('access_token');
let ws = null;
let reconnectInterval = null;

// DOM Elements
const loginModal = document.getElementById('loginModal');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const logoutBtn = document.getElementById('logoutBtn');
const usernameDisplay = document.getElementById('username-display');
const streamForm = document.getElementById('streamForm');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const streamMessage = document.getElementById('streamMessage');

// Stream Lists Elements
const newListName = document.getElementById('newListName');
const createListBtn = document.getElementById('createListBtn');
const streamListSelect = document.getElementById('streamListSelect');
const listVideos = document.getElementById('listVideos');
const videosList = document.getElementById('videosList');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (accessToken) {
        showDashboard();
        connectWebSocket();
    } else {
        showLogin();
    }

    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    loginForm.addEventListener('submit', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);
    streamForm.addEventListener('submit', handleStartStream);
    stopBtn.addEventListener('click', handleStopStream);
    
    // Stream Lists Event Listeners
    createListBtn.addEventListener('click', handleCreateList);
    streamListSelect.addEventListener('change', handleStreamListChange);
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('username', username);
            
            showDashboard();
            connectWebSocket();
        } else {
            showLoginError('Invalid username or password');
        }
    } catch (error) {
        showLoginError('Connection error. Please check if the server is running.');
        console.error('Login error:', error);
    }
}

function handleLogout() {
    accessToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    
    if (ws) {
        ws.close();
    }
    
    showLogin();
}

function showLogin() {
    loginModal.classList.remove('hidden');
    dashboard.classList.add('hidden');
}

function showDashboard() {
    loginModal.classList.add('hidden');
    dashboard.classList.remove('hidden');
    
    const username = localStorage.getItem('username');
    usernameDisplay.textContent = `👤 ${username}`;
    
    // Initialize stream lists
    initializeStreamLists();
}

function showLoginError(message) {
    loginError.textContent = message;
    loginError.classList.add('show');
    setTimeout(() => {
        loginError.classList.remove('show');
    }, 5000);
}

// Stream Control
async function handleStartStream(e) {
    e.preventDefault();
    
    const rtmpUrl = document.getElementById('rtmpUrl').value.trim();
    const streamKey = document.getElementById('streamKey').value.trim();
    const streamListName = streamListSelect.value;
    
    if (!streamListName) {
        showMessage('Please select a stream list', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stream/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                rtmp_url: rtmpUrl,
                stream_key: streamKey,
                stream_list_name: streamListName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Stream started successfully!', 'success');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            updateStreamStatus('active');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Failed to start stream', 'error');
        console.error('Start stream error:', error);
    }
}

async function handleStopStream() {
    try {
        const response = await fetch(`${API_URL}/stream/stop`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Stream stopped successfully', 'success');
            startBtn.disabled = false;
            stopBtn.disabled = true;
            updateStreamStatus('inactive');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Failed to stop stream', 'error');
        console.error('Stop stream error:', error);
    }
}

// WebSocket Connection
function connectWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/monitor`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected');
        
        // Clear reconnect interval if it exists
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        } catch (error) {
            console.error('WebSocket message error:', error);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('error');
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus('disconnected');
        
        // Attempt to reconnect every 5 seconds
        if (!reconnectInterval) {
            reconnectInterval = setInterval(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 5000);
        }
    };
}

// UI Updates
function updateDashboard(data) {
    // Update last update time
    const now = new Date().toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = `Last update: ${now}`;
    
    // Update stream status
    const stream = data.stream;
    document.getElementById('currentVideo').textContent = stream.current_video || '-';
    document.getElementById('bitrate').textContent = stream.bitrate;
    document.getElementById('uptime').textContent = stream.uptime;
    
    if (stream.active) {
        updateStreamStatus('active');
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        updateStreamStatus('inactive');
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
    
    // Update system metrics
    const system = data.system;
    updateProgressBar('cpu', system.cpu);
    updateProgressBar('ram', system.ram.percent);
    updateProgressBar('gpu', system.gpu.utilization);
    updateProgressBar('disk', system.disk.percent);
    
    document.getElementById('cpuPercent').textContent = `${system.cpu.toFixed(1)}%`;
    document.getElementById('ramPercent').textContent = `${system.ram.percent.toFixed(1)}%`;
    document.getElementById('ramDetails').textContent = 
        `${system.ram.used_gb} GB / ${system.ram.total_gb} GB`;
    
    if (system.gpu.available) {
        document.getElementById('gpuPercent').textContent = `${system.gpu.utilization.toFixed(1)}%`;
        document.getElementById('gpuDetails').textContent = `Temp: ${system.gpu.temperature}°C`;
    } else {
        document.getElementById('gpuPercent').textContent = 'N/A';
        document.getElementById('gpuDetails').textContent = 'GPU not available';
    }
    
    document.getElementById('diskPercent').textContent = `${system.disk.percent.toFixed(1)}%`;
    document.getElementById('diskDetails').textContent = 
        `${system.disk.used_gb} GB / ${system.disk.total_gb} GB`;
    
    // Update FFmpeg process status
    const ffmpeg = data.ffmpeg;
    if (ffmpeg.running) {
        document.getElementById('processStatus').textContent = 'Running';
        document.getElementById('processCpu').textContent = `${ffmpeg.cpu_percent.toFixed(1)}%`;
        document.getElementById('processMemory').textContent = `${ffmpeg.memory_mb} MB`;
        document.getElementById('ffmpegStatus').textContent = 'Running';
    } else {
        document.getElementById('processStatus').textContent = 'Not Running';
        document.getElementById('processCpu').textContent = '0%';
        document.getElementById('processMemory').textContent = '0 MB';
        document.getElementById('ffmpegStatus').textContent = 'Not Running';
    }
}

function updateProgressBar(id, percentage) {
    const bar = document.getElementById(`${id}Bar`);
    bar.style.width = `${percentage}%`;
    
    // Change color based on usage
    bar.classList.remove('warning', 'danger');
    if (percentage > 80) {
        bar.classList.add('danger');
    } else if (percentage > 60) {
        bar.classList.add('warning');
    }
}

function updateStreamStatus(status) {
    const badge = document.getElementById('streamStatusBadge');
    badge.classList.remove('status-active', 'status-inactive');
    
    if (status === 'active') {
        badge.classList.add('status-active');
        badge.textContent = 'Active';
    } else {
        badge.classList.add('status-inactive');
        badge.textContent = 'Inactive';
    }
}

function updateConnectionStatus(status) {
    const wsStatus = document.getElementById('wsStatus');
    wsStatus.classList.remove('status-active', 'status-inactive');
    
    if (status === 'connected') {
        wsStatus.classList.add('status-active');
        wsStatus.textContent = 'Connected';
    } else {
        wsStatus.classList.add('status-inactive');
        wsStatus.textContent = status === 'error' ? 'Error' : 'Disconnected';
    }
}

function showMessage(message, type) {
    streamMessage.textContent = message;
    streamMessage.className = `message ${type}`;
    
    setTimeout(() => {
        streamMessage.className = 'message';
    }, 5000);
}

// Stream Lists Management
async function loadStreamLists() {
    try {
        const response = await fetch(`${API_URL}/stream-lists`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateStreamListSelect(data.data);
        }
    } catch (error) {
        console.error('Error loading stream lists:', error);
    }
}

function updateStreamListSelect(lists) {
    streamListSelect.innerHTML = '<option value="">Choose a stream list...</option>';
    
    lists.forEach(list => {
        const option = document.createElement('option');
        option.value = list.name;
        option.textContent = `${list.name} (${list.video_count} videos)`;
        streamListSelect.appendChild(option);
    });
}

async function handleCreateList() {
    const listName = newListName.value.trim();
    
    if (!listName) {
        showMessage('Please enter a list name', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stream-lists`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                list_name: listName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(`Stream list '${listName}' created successfully!`, 'success');
            newListName.value = '';
            loadStreamLists(); // Reload the list
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Failed to create stream list', 'error');
        console.error('Create list error:', error);
    }
}

async function handleStreamListChange() {
    const selectedList = streamListSelect.value;
    
    if (!selectedList) {
        listVideos.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stream-lists/${selectedList}/videos`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayVideos(data.data);
            listVideos.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        showMessage('Failed to load videos', 'error');
    }
}

function displayVideos(videos) {
    if (videos.length === 0) {
        videosList.innerHTML = `
            <div class="empty-state">
                <div class="icon">📁</div>
                <p>No videos in this list</p>
                <small>Upload videos to this list to start streaming</small>
            </div>
        `;
        return;
    }
    
    videosList.innerHTML = videos.map(video => `
        <div class="video-item">
            <div class="video-info">
                <div class="video-name">${video.filename}</div>
                <div class="video-details">
                    ${video.size_mb} MB • ${video.extension.toUpperCase()}
                </div>
            </div>
            <div class="video-actions">
                <button class="btn btn-danger-small btn-small" onclick="deleteVideo('${video.filename}')">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

async function deleteVideo(filename) {
    const selectedList = streamListSelect.value;
    
    if (!confirm(`Are you sure you want to delete '${filename}'?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stream-lists/${selectedList}/videos/${filename}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(`Video '${filename}' deleted successfully`, 'success');
            handleStreamListChange(); // Reload videos
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Failed to delete video', 'error');
        console.error('Delete video error:', error);
    }
}

// Initialize stream lists when dashboard loads
function initializeStreamLists() {
    loadStreamLists();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
});


