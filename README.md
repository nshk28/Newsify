# Newsify
Newsify: Your personalized news app delivering curated content tailored to your interests.Stay informed and connected with Newsify, your personalized news companion!

```
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
```
```
const os = require('os');
const EventLogger = require('node-windows').EventLogger;
const exec = require('child_process').exec;

const log = new EventLogger('Node Event Log Watcher');

// Dictionary to store the process information
const processDictionary = {};

// Function to get current timestamp in hh:mm:ss format
const formatTime = (date) => {
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// Function to get current date in YYYY-MM-DD format
const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Function to detect new processes
const detectNewProcesses = () => {
  exec('powershell "Get-WinEvent -LogName Security | Where-Object {$_.Id -eq 4688} | Select-Object TimeCreated, Properties"', (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return;
    }
    const events = stdout.split('\n');
    events.forEach(event => {
      if (event.includes('.exe')) {
        const timestamp = new Date();
        const time = formatTime(timestamp);
        const date = formatDate(timestamp);
        const user = os.userInfo().username;
        const exeName = event.match(/(?<=New Process Name:).*?\.exe/)[0].trim();

        processDictionary[exeName] = {
          user,
          time,
          date
        };

        console.log(`New exe detected: ${exeName}`);
        console.log('Process Dictionary:', processDictionary);
      }
    });
  });
};

// Periodically check for new processes
setInterval(detectNewProcesses, 5000);

```
