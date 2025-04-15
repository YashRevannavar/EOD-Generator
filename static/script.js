// Utility functions for UI state management
let currentProcess = null;
let lastEODContext = null;
let lastSprintReviewContext = null;

function showHome() {
    document.getElementById('homeScreen').classList.remove('hidden');
    document.getElementById('reportScreen').classList.add('hidden');
}

function showReport() {
    document.getElementById('homeScreen').classList.add('hidden');
    document.getElementById('reportScreen').classList.remove('hidden');
}

// Sprint Review Modal Functions
function showSprintReviewModal(context = null) {
    document.getElementById('sprintReviewModal').classList.remove('hidden');
    // Set default dates or use context
    if (context) {
        document.getElementById('startDate').value = context.startDate;
        document.getElementById('endDate').value = context.endDate;
        // Restore tickets
        const ticketList = document.getElementById('ticketList');
        ticketList.innerHTML = '';
        context.tickets.forEach(ticket => {
            const ticketDiv = document.createElement('div');
            ticketDiv.className = 'flex gap-2';
            ticketDiv.innerHTML = `
                <input type="text" class="ticket-input flex-grow px-3 py-2 bg-dark-400 border border-dark-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary text-gray-200" placeholder="Enter ticket" value="${ticket}">
                <button onclick="removeTicket(this)" class="btn-3d px-3 py-2 bg-gradient-to-b from-red-500/90 to-red-600 text-white rounded-md">✕</button>
            `;
            ticketList.appendChild(ticketDiv);
        });
    } else {
        // Set default dates
        const today = new Date();
        const twoWeeksAgo = new Date(today.getTime() - (14 * 24 * 60 * 60 * 1000));
        document.getElementById('startDate').value = formatDate(twoWeeksAgo);
        document.getElementById('endDate').value = formatDate(today);
        resetTicketList();
    }
}

function hideSprintReviewModal() {
    document.getElementById('sprintReviewModal').classList.add('hidden');
    if (!lastSprintReviewContext) {
        resetSprintReviewForm();
    }
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function resetSprintReviewForm() {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    resetTicketList();
}

function resetTicketList() {
    const ticketList = document.getElementById('ticketList');
    ticketList.innerHTML = `
        <div class="flex gap-2">
            <input type="text" class="ticket-input flex-grow px-3 py-2 bg-dark-400 border border-dark-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary text-gray-200" placeholder="Enter ticket">
            <button onclick="removeTicket(this)" class="btn-3d px-3 py-2 bg-gradient-to-b from-red-500/90 to-red-600 text-white rounded-md">✕</button>
        </div>
    `;
}

function addTicket() {
    const ticketList = document.getElementById('ticketList');
    const newTicket = document.createElement('div');
    newTicket.className = 'flex gap-2';
    newTicket.innerHTML = `
        <input type="text" class="ticket-input flex-grow px-3 py-2 bg-dark-400 border border-dark-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary text-gray-200" placeholder="Enter ticket">
        <button onclick="removeTicket(this)" class="btn-3d px-3 py-2 bg-gradient-to-b from-red-500/90 to-red-600 text-white rounded-md">✕</button>
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

function showErrorModal(message) {
    const errorModal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorModal.classList.remove('hidden');
}

function hideErrorModal() {
    document.getElementById('errorModal').classList.add('hidden');
    // Clear last error context if user cancels
    if (!document.getElementById('sprintReviewModal').classList.contains('hidden')) {
        lastSprintReviewContext = null;
        resetSprintReviewForm();
    }
}

function retryOperation() {
    hideErrorModal();
    if (lastSprintReviewContext) {
        handleSprintReviewSubmit(lastSprintReviewContext);
    } else if (lastEODContext) {
        handleEOD(true);
    }
}

function handleError(error) {
    let errorMessage = 'An unexpected error occurred.';
    
    if (error.name === 'AbortError') {
        errorMessage = 'Process was cancelled.';
    } else if (error.message.includes('HTTP error')) {
        errorMessage = 'Failed to connect to the server. Please check your connection and try again.';
    } else if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Could not reach the server. Please ensure the service is running.';
    } else {
        errorMessage = `Error: ${error.message}`;
    }
    
    updateLogs(errorMessage);
    updateResponse('Operation failed. Please try again.');
    showErrorModal(errorMessage);
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
    // Hide error modal if it's showing
    document.getElementById('errorModal').classList.add('hidden');
}

// Navigation handlers
function goHome() {
    if (currentProcess) {
        if (confirm('Are you sure you want to cancel the current process?')) {
            currentProcess.abort();
            currentProcess = null;
            lastEODContext = null;
            lastSprintReviewContext = null;
        } else {
            return;
        }
    }
    showHome();
}

async function quit() {
    if (currentProcess) {
        if (!confirm('Are you sure you want to quit? Current process will be terminated.')) {
            return;
        }
        currentProcess.abort();
    }
    
    try {
        // Send termination signal to server
        await fetch('http://localhost:5001/terminate', {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error terminating server:', error);
    } finally {
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
        updateResponse(accumulatedResponse.trim());
        return;
    }
    
    if (text.includes('Error:')) {
        updateLogs(text);
        if (!text.includes('Process cancelled')) {
            showErrorModal(text.replace('Error:', '').trim());
        }
    } else if (!text.includes('RESPONSE')) {
        updateLogs(text);
    }
}

// Main process handlers
async function handleEOD(isRetry = false) {
    if (!isRetry) {
        lastEODContext = true;
    }
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
            handleError(error);
        } else {
            handleError(error);
        }
    } finally {
        currentProcess = null;
    }
}

async function handleSprintReviewSubmit(context = null) {
    const startDate = context ? context.startDate : document.getElementById('startDate').value;
    const endDate = context ? context.endDate : document.getElementById('endDate').value;
    const tickets = context ? context.tickets : getTickets();

    if (!startDate || !endDate) {
        showErrorModal('Please select both start and end dates');
        return;
    }

    if (!tickets.length) {
        showErrorModal('Please enter at least one ticket');
        return;
    }

    // Save context for potential retry
    if (!context) {
        lastSprintReviewContext = {
            startDate,
            endDate,
            tickets
        };
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
            body: JSON.stringify({ 
                startDate, 
                endDate, 
                tickets,
                metadata: {
                    date_range: {
                        start: startDate,
                        end: endDate
                    },
                    ticket_details: tickets.map(ticket => ({
                        id: ticket,
                        type: ticket.split('-')[0],
                        number: ticket.split('-')[1]
                    }))
                }
            }),
            signal: controller.signal
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        await handleStream(response);
    } catch (error) {
        if (error.name === 'AbortError') {
            handleError(error);
        } else {
            handleError(error);
        }
    } finally {
        currentProcess = null;
    }
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    showHome();
});