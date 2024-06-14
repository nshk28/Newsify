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
```
const os = require('os');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

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
const detectNewProcesses = async () => {
  try {
    const { stdout, stderr } = await execAsync('powershell "Get-WinEvent -LogName Security | Where-Object {$_.Id -eq 4688} | Select-Object TimeCreated, Properties"');
    
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }

    const events = stdout.split('\n');
    events.forEach(event => {
      if (event.includes('.exe')) {
        const timestamp = new Date();
        const time = formatTime(timestamp);
        const date = formatDate(timestamp);
        const user = os.userInfo().username;
        const exeNameMatch = event.match(/NewProcessName\s*:\s*(.*?\.exe)/i);
        
        if (exeNameMatch) {
          const exeName = exeNameMatch[1].trim();
          
          processDictionary[exeName] = {
            user,
            time,
            date
          };
  
          console.log(`New exe detected: ${exeName}`);
          console.log('Process Dictionary:', processDictionary);
        }
      }
    });
  } catch (error) {
    console.error(`exec error: ${error.message}`);
    if (error.message.includes('Access is denied')) {
      console.error('You need to run this script with administrative privileges.');
    }
  }
};


```
``` 
const psList = require('ps-list');
const watch = require('node-watch');
const fs = require('fs');

let appDetails = {};  // Dictionary to store app details

// Function to get the current time
const getCurrentTime = () => {
    return new Date().toISOString();
};

// Function to get entitlements associated with an application
const getEntitlements = (exePath) => {
    // For the sake of example, returning a dummy entitlement.
    // In a real-world scenario, you would fetch the actual entitlement.
    return "basic-entitlement";
};

// Function to track applications
const trackApplications = async () => {
    const processes = await psList();

    processes.forEach((process) => {
        const exePath = process.cmd;

        if (!appDetails[exePath]) {
            appDetails[exePath] = {
                exePath: exePath,
                startTime: getCurrentTime(),
                entitlement: getEntitlements(exePath),
            };
            console.log(`Started tracking application: ${exePath}`);
        }
    });
};

// Function to update the tracking dictionary when an application closes
const updateTrackingOnClose = async () => {
    const processes = await psList();
    const runningExePaths = processes.map(process => process.cmd);

    for (const exePath in appDetails) {
        if (!runningExePaths.includes(exePath)) {
            console.log(`Application closed: ${exePath}`);
            delete appDetails[exePath];
        }
    }
};

// Watch for changes in running processes
watch('.', { recursive: true, filter: (f, skip) => {
    if (f.includes('node_modules') || f.includes('.git')) return skip;
    return true;
}}, async (evt, name) => {
    await trackApplications();
    await updateTrackingOnClose();
});

// Initial tracking of applications
trackApplications().then(() => {
    console.log('Initial tracking complete.');
});

// Save the application details to a file every minute
setInterval(() => {
    fs.writeFileSync('appDetails.json', JSON.stringify(appDetails, null, 2));
    console.log('App details saved.');
}, 60000);

```
``` 
// Using top-level await (ensure Node.js version supports it)

let psList;
let watch;
let fs;

(async () => {
    psList = await import('ps-list');
    watch = (await import('node-watch')).default;
    fs = await import('fs');

    let appDetails = {};  // Dictionary to store app details

    // Function to get the current time
    const getCurrentTime = () => {
        return new Date().toISOString();
    };

    // Function to get entitlements associated with an application
    const getEntitlements = (exePath) => {
        // For the sake of example, returning a dummy entitlement.
        // In a real-world scenario, you would fetch the actual entitlement.
        return "basic-entitlement";
    };

    // Function to track applications
    const trackApplications = async () => {
        const processes = await psList.default();

        processes.forEach((process) => {
            const exePath = process.cmd;

            if (!appDetails[exePath]) {
                appDetails[exePath] = {
                    exePath: exePath,
                    startTime: getCurrentTime(),
                    entitlement: getEntitlements(exePath),
                };
                console.log(`Started tracking application: ${exePath}`);
            }
        });
    };

    // Function to update the tracking dictionary when an application closes
    const updateTrackingOnClose = async () => {
        const processes = await psList.default();
        const runningExePaths = processes.map(process => process.cmd);

        for (const exePath in appDetails) {
            if (!runningExePaths.includes(exePath)) {
                console.log(`Application closed: ${exePath}`);
                delete appDetails[exePath];
            }
        }
    };

    // Watch for changes in running processes
    watch('.', { recursive: true, filter: (f, skip) => {
        if (f.includes('node_modules') || f.includes('.git')) return skip;
        return true;
    }}, async (evt, name) => {
        await trackApplications();
        await updateTrackingOnClose();
    });

    // Initial tracking of applications
    await trackApplications();
    console.log('Initial tracking complete.');

    // Save the application details to a file every minute
    setInterval(() => {
        fs.writeFileSync('appDetails.json', JSON.stringify(appDetails, null, 2));
        console.log('App details saved.');
    }, 60000);
})();

```
``` 
// Ensure Node.js version supports top-level await
let psList;
let watch;
let fs;

(async () => {
    psList = await import('ps-list');
    fs = await import('fs');

    let appDetails = {};  // Dictionary to store app details

    // Function to get the current time
    const getCurrentTime = () => {
        return new Date().toISOString();
    };

    // Function to get entitlements associated with an application
    const getEntitlements = (exePath) => {
        // For the sake of example, returning a dummy entitlement.
        // In a real-world scenario, you would fetch the actual entitlement.
        return "basic-entitlement";
    };

    // Function to track applications
    const trackApplications = async () => {
        const processes = await psList.default();

        processes.forEach((process) => {
            const exePath = process.cmd;

            if (!appDetails[exePath]) {
                appDetails[exePath] = {
                    exePath: exePath,
                    startTime: getCurrentTime(),
                    entitlement: getEntitlements(exePath),
                };
                console.log(`Started tracking application: ${exePath}`);
            }
        });
    };

    // Function to update the tracking dictionary when an application closes
    const updateTrackingOnClose = async () => {
        const processes = await psList.default();
        const runningExePaths = processes.map(process => process.cmd);

        for (const exePath in appDetails) {
            if (!runningExePaths.includes(exePath)) {
                console.log(`Application closed: ${exePath}`);
                delete appDetails[exePath];
            }
        }
    };

    // Periodically check for running processes every 5 seconds
    setInterval(async () => {
        await trackApplications();
        await updateTrackingOnClose();
    }, 5000); // Check every 5 seconds

    // Initial tracking of applications
    await trackApplications();
    console.log('Initial tracking complete.');

    // Save the application details to a file every minute
    setInterval(() => {
        fs.writeFileSync('appDetails.json', JSON.stringify(appDetails, null, 2));
        console.log('App details saved.');
    }, 60000);
})();
```
