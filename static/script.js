// Utility functions for UI state management
let currentProcess = null;

function showHome() {
    document.getElementById('homeScreen').classList.remove('hidden');
    document.getElementById('reportScreen').classList.add('hidden');
}

function showReport() {
    document.getElementById('homeScreen').classList.add('hidden');
    document.getElementById('reportScreen').classList.remove('hidden');
}

// Sprint Review Modal Functions
function showSprintReviewModal() {
    document.getElementById('sprintReviewModal').classList.remove('hidden');
    // Set default dates
    const today = new Date();
    const twoWeeksAgo = new Date(today.getTime() - (14 * 24 * 60 * 60 * 1000));
    
    document.getElementById('startDate').value = formatDate(twoWeeksAgo);
    document.getElementById('endDate').value = formatDate(today);
}

function hideSprintReviewModal() {
    document.getElementById('sprintReviewModal').classList.add('hidden');
    resetSprintReviewForm();
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function resetSprintReviewForm() {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    const ticketList = document.getElementById('ticketList');
    ticketList.innerHTML = `
        <div class="flex gap-2">
            <input type="text" class="ticket-input flex-grow px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary focus:border-primary" placeholder="Enter ticket">
            <button onclick="removeTicket(this)" class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors">✕</button>
        </div>
    `;
}

function addTicket() {
    const ticketList = document.getElementById('ticketList');
    const newTicket = document.createElement('div');
    newTicket.className = 'flex gap-2';
    newTicket.innerHTML = `
        <input type="text" class="ticket-input flex-grow px-3 py-2 border rounded-md focus:ring-2 focus:ring-primary focus:border-primary" placeholder="Enter ticket">
        <button onclick="removeTicket(this)" class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors">✕</button>
    `;
    ticketList.appendChild(newTicket);
}

function removeTicket(button) {
    const ticketInputs = document.querySelectorAll('.ticket-input');
    if (ticketInputs.length > 1) {
        button.parentElement.remove();
    }
}

function getTickets() {
    const tickets = [];
    document.querySelectorAll('.ticket-input').forEach(input => {
        if (input.value.trim()) {
            tickets.push(input.value.trim());
        }
    });
    return tickets;
}

async function copyResponse() {
    const response = document.getElementById('response').textContent;
    await navigator.clipboard.writeText(response);
    
    const button = document.querySelector('button[onclick="copyResponse()"]');
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    setTimeout(() => {
        button.textContent = originalText;
    }, 2000);
}

function updateLogs(message) {
    const logsElement = document.getElementById('logs');
    logsElement.textContent += message + '\n';
    logsElement.scrollTop = logsElement.scrollHeight;
}

let accumulatedResponse = '';
let isCollectingResponse = false;

function updateResponse(text) {
    const responseElement = document.getElementById('response');
    responseElement.style.whiteSpace = 'pre-wrap';
    responseElement.style.wordBreak = 'break-word';
    responseElement.textContent = text;
}

function clearPanels() {
    document.getElementById('logs').textContent = '';
    document.getElementById('response').textContent = '';
    accumulatedResponse = '';
    isCollectingResponse = false;
}

// Navigation handlers
function goHome() {
    if (currentProcess) {
        if (confirm('Are you sure you want to cancel the current process?')) {
            currentProcess.abort();
            currentProcess = null;
        } else {
            return;
        }
    }
    showHome();
}

function quit() {
    if (currentProcess) {
        if (confirm('Are you sure you want to quit? Current process will be terminated.')) {
            currentProcess.abort();
            window.close();
        }
    } else {
        window.close();
    }
}

// Stream handling
function handleStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    return reader.read().then(function processText({ done, value }) {
        if (done) {
            if (buffer) {
                handleStreamChunk(buffer);
            }
            return;
        }

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n');
        buffer = lines.pop();

        lines.forEach(line => {
            if (line.trim()) {
                handleStreamChunk(line);
            }
        });

        return reader.read().then(processText);
    });
}

function handleStreamChunk(text) {
    if (text.includes('RESPONSE_START')) {
        isCollectingResponse = true;
        accumulatedResponse = '';
        return;
    }
    
    if (text.includes('RESPONSE_END')) {
        isCollectingResponse = false;
        updateResponse(accumulatedResponse.trim());
        return;
    }
    
    if (isCollectingResponse) {
        accumulatedResponse += text + '\n';
        // Update response in real-time as we receive chunks
        updateResponse(accumulatedResponse.trim());
        return;
    }
    
    if (text.includes('Error:')) {
        updateLogs(text);
    } else if (!text.includes('RESPONSE')) {
        updateLogs(text);
    }
}

// Main process handlers
async function handleEOD() {
    showReport();
    clearPanels();
    updateLogs('Starting EOD Generator...\n');
    
    try {
        const controller = new AbortController();
        currentProcess = controller;
        
        const response = await fetch('http://localhost:5001/run-eod', { 
            method: 'POST',
            signal: controller.signal
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        await handleStream(response);
    } catch (error) {
        if (error.name === 'AbortError') {
            updateLogs('Process cancelled.\n');
        } else {
            updateLogs('Error: ' + error.message + '\n');
            updateResponse('Failed to generate EOD report.');
        }
    } finally {
        currentProcess = null;
    }
}

async function handleSprintReviewSubmit() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const tickets = getTickets();

    if (!startDate || !endDate) {
        alert('Please select both start and end dates');
        return;
    }

    if (!tickets.length) {
        alert('Please enter at least one ticket');
        return;
    }

    hideSprintReviewModal();
    showReport();
    clearPanels();
    updateLogs('Starting Sprint Review Generator...\n');
    
    try {
        const controller = new AbortController();
        currentProcess = controller;
        
        const response = await fetch('http://localhost:5001/run-sprint-review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ startDate, endDate, tickets }),
            signal: controller.signal
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        await handleStream(response);
    } catch (error) {
        if (error.name === 'AbortError') {
            updateLogs('Process cancelled.\n');
        } else {
            updateLogs('Error: ' + error.message + '\n');
            updateResponse('Failed to generate Sprint Review report.');
        }
    } finally {
        currentProcess = null;
    }
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    showHome();
});