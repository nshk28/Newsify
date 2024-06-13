# Newsify
Newsify: Your personalized news app delivering curated content tailored to your interests.Stay informed and connected with Newsify, your personalized news companion!

const { exec } = require('child_process');
const cron = require('node-cron');

// Function to get the list of running .exe processes
function getRunningExeProcesses(callback) {
    exec('tasklist', (err, stdout, stderr) => {
        if (err) {
            console.error(`Error executing tasklist: ${err}`);
            return;
        }
        const processes = stdout
            .split('\n')
            .filter(line => line.endsWith('.exe')) // Filter lines ending with .exe
            .map(line => {
                const parts = line.trim().split(/\s+/);
                return parts[0]; // Return the process name
            });
        callback(processes);
    });
}

// Store the previously detected processes
let previousProcesses = new Set();

// Function to check for new processes
function checkForNewProcesses() {
    getRunningExeProcesses((currentProcesses) => {
        const currentSet = new Set(currentProcesses);
        currentSet.forEach(process => {
            if (!previousProcesses.has(process)) {
                const timestamp = new Date().toISOString();
                console.log(`New process detected: ${process} at ${timestamp}`);
            }
        });
        previousProcesses = currentSet;
    });
}

// Initial list of processes
getRunningExeProcesses((initialProcesses) => {
    previousProcesses = new Set(initialProcesses);
    console.log('Initial running processes:', Array.from(previousProcesses));
});

// Schedule the check to run every minute
cron.schedule('* * * * *', () => {
    checkForNewProcesses();
});
