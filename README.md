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
``` 
const ps = require('ps-node');
const os = require('os');

// Dictionary to store process information
const processDictionary = {};
let previousProcesses = new Set(); // Set to store previously tracked processes

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    const currentProcesses = new Set(resultList.map(process => process.command));

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();

      if (!previousProcesses.has(process.command)) {
        const timestamp = new Date();
        const time = formatTime(timestamp);
        const date = formatDate(timestamp);
        const user = os.userInfo().username;

        processDictionary[exeName] = {
          user,
          time,
          date,
        };

        console.log(`New exe detected: ${exeName}`);
        console.log('Process Dictionary:', processDictionary);
      }
    });

    previousProcesses = currentProcesses;
  });
};

// Periodically check for new processes
setInterval(checkRunningExe, 5000);

```
```
const psTree = require('ps-tree');

// Dictionary to store process information
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

// Function to check for new processes
const checkNewProcesses = () => {
  psTree(process.pid, (err, children) => {
    if (err) {
      throw new Error(err);
    }

    children.forEach(child => {
      const exeName = child.COMMAND.split('/').pop();
      
      if (!processDictionary[child.PID]) {
        const timestamp = new Date();
        const time = formatTime(timestamp);
        const date = formatDate(timestamp);

        processDictionary[child.PID] = {
          exeName,
          time,
          date,
        };

        console.log(`New process detected: ${exeName}`);
        console.log('Process Dictionary:', processDictionary);
      }
    });
  });
};

// Periodically check for new processes
setInterval(checkNewProcesses, 5000);
```
```
const ps = require('ps-node');
const os = require('os');

// Dictionary to store process information
const processDictionary = {};

// Function to get current timestamp in hh:mm:ss format (IST)
const formatTime = (date) => {
  return date.toLocaleString('en-IN', { hour12: false, timeZone: 'Asia/Kolkata' });
};

// Function to get current date in YYYY-MM-DD format (IST)
const formatDate = (date) => {
  return date.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }).split(',')[0]; // Use split(',') to get only date
};

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      if (!processDictionary[exeName]) {
        const timestamp = new Date();
        const time = formatTime(timestamp);
        const date = formatDate(timestamp);
        const user = os.userInfo().username;

        processDictionary[exeName] = {
          user,
          startTime: timestamp, // Track start time directly
          time,
          date,
        };

        console.log(`New exe detected: ${exeName}`);
        console.log('Process Dictionary:', processDictionary);
      }
    });
  });
};

// Immediately start checking for new processes
checkRunningExe();

// Periodically check for new processes (every 1600 milliseconds)
setInterval(checkRunningExe, 1600);
```
``` 
const ps = require('ps-node');
const os = require('os');

// Array to store process information
const processArray = [];

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const timestamp = new Date();
      const time = formatTime(timestamp);
      const date = formatDate(timestamp);
      const user = os.userInfo().username;

      // Log each instance with its start time
      processArray.push({
        exeName,
        user,
        time,
        date,
      });

      console.log(`New exe detected: ${exeName}`);
      console.log('Process Array:', processArray);
    });
  });
};

// Periodically check for new processes
setInterval(checkRunningExe, 1000);
```
``` 
const ps = require('ps-node');
const os = require('os');

// Array to store process information
const processArray = [];

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const existingProcess = processArray.find((item) => item.exeName === exeName);

      if (!existingProcess) {
        const timestamp = new Date();
        const time = formatTime(timestamp);
        const date = formatDate(timestamp);
        const user = os.userInfo().username;

        // Log new instances only
        console.log(`New exe detected: ${exeName}`);

        // Store in processArray or perform any other actions as needed
        processArray.push({
          exeName,
          user,
          time,
          date,
        });

        console.log('Process Array:', processArray);
      }
    });
  });
};

// Periodically check for new processes
setInterval(checkRunningExe, 1000);

```
``` 
const ps = require('ps-node');
const os = require('os');

// Map to store unique application names and their last log times
const loggedApplications = new Map();

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    // Get current time and date
    const timestamp = new Date();
    const time = formatTime(timestamp);
    const date = formatDate(timestamp);

    // Set to track current running applications
    const currentAppSet = new Set();

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      currentAppSet.add(exeName);

      // Check if the application has already been logged
      if (!loggedApplications.has(exeName)) {
        // Log new applications
        const newLogEntry = {
          exeName,
          time,
          date
        };
        console.log(`New application detected: ${JSON.stringify(newLogEntry)}\n`);

        // Store the application name and its log time
        loggedApplications.set(exeName, timestamp);
      }
    });

    // Remove applications that are no longer running
    loggedApplications.forEach((logTime, appName) => {
      if (!currentAppSet.has(appName)) {
        loggedApplications.delete(appName);
      }
    });
  });
};

// Periodically check for new processes every 10 seconds
setInterval(checkRunningExe, 10000);

// Initial check on startup
checkRunningExe();

```
```
const ps = require('ps-node');
const os = require('os');

// Array to store process information
const processArray = [];

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    // Get current time and date
    const timestamp = new Date();
    const time = formatTime(timestamp);
    const date = formatDate(timestamp);
   // const user = os.userInfo().username;

    // Array to store currently running .exe processes
    const currentProcesses = [];

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const pid = process.pid;

      // Exclude certain processes from logging (e.g., chrome.exe)
      if (exeName.toLowerCase() === 'chrome.exe') {
        return; // Skip logging chrome.exe
      }

      const existingProcess = processArray.find(
        (item) => item.exeName === exeName && item.pid === pid
      );

      if (!existingProcess) {
        // Log new instances or restarted processes in one line
        const newLogEntry = {
          exeName,
          pid,
          time,
          date
        };
        console.log(`New exe detected: ${JSON.stringify(newLogEntry)}\n`);

        // Store in processArray
        processArray.push(newLogEntry);
      }

      // Track current running processes
      currentProcesses.push(pid);
    });

  });
};

// Periodically check for new processes every 10 seconds
setInterval(checkRunningExe, 10000);

// Initial check on startup
checkRunningExe();


```
``` 
const ps = require('ps-node');

// Map to store process information
const processMap = new Map();

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    // Get current time and date
    const timestamp = new Date();
    const time = formatTime(timestamp);
    const date = formatDate(timestamp);

    // Set to track current running .exe processes by unique key
    const currentProcesses = new Set();

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const pid = process.pid;
      const ppid = process.ppid;
      const startTime = process.start_time;

      // Check if the process is a main process based on specific criteria
      const isMainProcess = (ppid === 1 || ppid === 0) || (
        // Add specific criteria for known applications
        exeName.toLowerCase() === 'chrome.exe' && !process.arguments.includes('--type')
      ) || (
        exeName.toLowerCase() === 'msedge.exe' && !process.arguments.includes('--type')
      ) || (
        exeName.toLowerCase() === 'postman.exe' && !process.arguments.includes('--type')
      );

      if (!isMainProcess) {
        return; // Skip child processes
      }

      // Create a unique key for each process using exeName, pid, and startTime
      const processKey = `${exeName}-${pid}-${startTime}`;

      // Log new instances or restarted processes in one line
      if (!processMap.has(processKey)) {
        const newLogEntry = {
          exeName,
          pid,
          ppid,
          startTime,
          time,
          date
        };
        console.log(`New exe detected: ${JSON.stringify(newLogEntry)}\n`);

        // Store in processMap
        processMap.set(processKey, newLogEntry);
      }

      // Track current running processes
      currentProcesses.add(processKey);
    });

    // Remove entries from processMap that are no longer running
    for (const key of processMap.keys()) {
      if (!currentProcesses.has(key)) {
        processMap.delete(key);
      }
    }
  });
};

// Periodically check for new processes every 10 seconds
setInterval(checkRunningExe, 10000);

// Initial check on startup
checkRunningExe();

```
``` 
const ps = require('ps-node');
const os = require('os');

// Map to store process information
const processMap = new Map();

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    // Get current time and date
    const timestamp = new Date();
    const time = formatTime(timestamp);
    const date = formatDate(timestamp);

    // Iterate over resultList to check each process
    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const pid = process.pid;

      // Exclude certain processes from logging (e.g., chrome.exe)
      if (exeName.toLowerCase() === 'chrome.exe') {
        return; // Skip logging chrome.exe
      }

      // Check if the exeName is already in the map
      if (!processMap.has(exeName)) {
        processMap.set(exeName, []);
      }

      // Get the array of processes for the exeName
      const processArray = processMap.get(exeName);

      // Check if the process with the same pid already exists in the array
      const existingProcess = processArray.find((item) => item.pid === pid);

      if (!existingProcess) {
        // Log new instances or restarted processes in one line
        const newLogEntry = {
          exeName,
          pid,
          time,
          date
        };
        console.log(`New exe detected: ${JSON.stringify(newLogEntry)}\n`);

        // Store in the process array
        processArray.push(newLogEntry);
      }
    });
  });
};

// Periodically check for new processes every 10 seconds
setInterval(checkRunningExe, 10000);

// Initial check on startup
checkRunningExe();

```
``` 
const ps = require('ps-node');
const os = require('os');

// Map to store process information
const processMap = new Map();

// Array to store only logged-in .exe processes
const loggedProcesses = [];

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    // Get current time and date
    const timestamp = new Date();
    const time = formatTime(timestamp);
    const date = formatDate(timestamp);

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const pid = process.pid;
      const startTime = process.start_time;

      // Exclude certain processes from logging (e.g., chrome.exe)
      if (exeName.toLowerCase() === 'chrome.exe') {
        return; // Skip logging chrome.exe
      }

      // Check if the exeName is already in the map
      if (!processMap.has(exeName)) {
        processMap.set(exeName, []);
      }

      // Get the array of processes for the exeName
      const processArray = processMap.get(exeName);

      // Check if the process with the same pid already exists in the array
      const existingProcess = processArray.find((item) => item.pid === pid);

      if (!existingProcess) {
        // Log new instances or restarted processes in one line
        const newLogEntry = {
          exeName,
          pid,
          startTime,
          date,
          time
        };
        console.log(`New exe detected: ${JSON.stringify(newLogEntry)}\n`);

        // Store in the process array
        processArray.push(newLogEntry);

        // Store in the loggedProcesses array
        loggedProcesses.push(newLogEntry);
      }
    });
  });
};

// Periodically check for new processes every 10 seconds
setInterval(checkRunningExe, 10000);

// Initial check on startup
checkRunningExe();



```
```
const ps = require('ps-node');
const os = require('os');

// Map to store process information with exe name as key and an array of processes as value
const processMap = new Map();

// Array to store only logged-in .exe processes
const loggedProcesses = [];

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

// Function to check for actively running .exe processes
const checkRunningExe = () => {
  ps.lookup({ command: '.exe', psargs: 'ux' }, (err, resultList) => {
    if (err) {
      throw new Error(err);
    }

    // Get current time and date
    const timestamp = new Date();
    const time = formatTime(timestamp);
    const date = formatDate(timestamp);

    resultList.forEach((process) => {
      const exeName = process.command.split('\\').pop();
      const pid = process.pid;
      const startTime = process.start_time;

      // Exclude certain processes from logging (e.g., chrome.exe)
      if (exeName.toLowerCase() === 'chrome.exe') {
        return; // Skip logging chrome.exe
      }

      // Check if the exeName is already in the map
      if (!processMap.has(exeName)) {
        processMap.set(exeName, []);
      }

      // Get the array of processes for the exeName
      const processArray = processMap.get(exeName);

      // Check if the process with the same pid and startTime already exists in the array
      const existingProcess = processArray.find((item) => item.pid === pid && item.startTime === startTime);

      if (!existingProcess) {
        // Log new instances or restarted processes in one line
        const newLogEntry = {
          exeName,
          pid,
          startTime,
          date,
          time
        };
        console.log(`New exe detected: ${JSON.stringify(newLogEntry)}\n`);

        // Store in the loggedProcesses array
        loggedProcesses.push(newLogEntry);

        // Add to processArray if it's a new entry
        processArray.push(newLogEntry);
      }
    });

    // Log the processes currently in processMap
    processMap.forEach((processArray, exeName) => {
      processArray.forEach((item) => {
        console.log(`Currently tracked process: ${JSON.stringify(item)}\n`);
      });
    });
  });
};

// Periodically check for new processes every 10 seconds
setInterval(checkRunningExe, 10000);

// Initial check on startup
checkRunningExe();

```
```
const { exec } = require('child_process');

// Define the PowerShell script as a string
const psScript = `
$query = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[(EventID=4688)]]
    </Select>
  </Query>
</QueryList>
"@

$eventLogWatcher = New-Object System.Diagnostics.Eventing.Reader.EventLogWatcher -ArgumentList $query

$eventAction = {
    param($eventArgs)
    
    $event = [xml]$eventArgs.NewEvent.ToXml()
    $timeCreated = $event.Event.System.TimeCreated.SystemTime
    $exeName = $event.Event.EventData.Data | Where-Object { $_.Name -eq "NewProcessName" } | Select-Object -ExpandProperty '#text'
    $pid = $event.Event.EventData.Data | Where-Object { $_.Name -eq "NewProcessId" } | Select-Object -ExpandProperty '#text'
    $ppid = $event.Event.EventData.Data | Where-Object { $_.Name -eq "ParentProcessId" } | Select-Object -ExpandProperty '#text'
    
    $logEntry = @{
        TimeCreated = $timeCreated
        ExeName = $exeName
        Pid = $pid
        PPid = $ppid
    }

    Write-Output "New process detected: $(ConvertTo-Json $logEntry)"
}

Register-ObjectEvent -InputObject $eventLogWatcher -EventName "EventRecordWritten" -Action $eventAction
$eventLogWatcher.Enabled = $true

Write-Output "Monitoring process creation events. Press Ctrl+C to stop."
while ($true) {
    Start-Sleep -Seconds 1
}
`;

// Run the PowerShell script using the child_process exec method
exec(`powershell -NoProfile -ExecutionPolicy Bypass -Command "${psScript}"`, (error, stdout, stderr) => {
    if (error) {
        console.error(`Error: ${error.message}`);
        return;
    }
    if (stderr) {
        console.error(`Stderr: ${stderr}`);
        return;
    }
    console.log(`Stdout: ${stdout}`);
});

```

``` 

const Service = require('node-windows').Service;
const path = require('path');

// Define the PowerShell script as a string
const psScript = `
$query = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[(EventID=4688)]]
    </Select>
  </Query>
</QueryList>
"@

$eventLogWatcher = New-Object System.Diagnostics.Eventing.Reader.EventLogWatcher -ArgumentList $query

$eventAction = {
    param($eventArgs)
    
    $event = [xml]$eventArgs.NewEvent.ToXml()
    $timeCreated = $event.Event.System.TimeCreated.SystemTime
    $exeName = $event.Event.EventData.Data | Where-Object { $_.Name -eq "NewProcessName" } | Select-Object -ExpandProperty '#text'
    $pid = $event.Event.EventData.Data | Where-Object { $_.Name -eq "NewProcessId" } | Select-Object -ExpandProperty '#text'
    $ppid = $event.Event.EventData.Data | Where-Object { $_.Name -eq "ParentProcessId" } | Select-Object -ExpandProperty '#text'
    
    $logEntry = @{
        TimeCreated = $timeCreated
        ExeName = $exeName
        Pid = $pid
        PPid = $ppid
    }

    Write-Output "New process detected: $(ConvertTo-Json $logEntry)"
}

Register-ObjectEvent -InputObject $eventLogWatcher -EventName "EventRecordWritten" -Action $eventAction
$eventLogWatcher.Enabled = $true

Write-Output "Monitoring process creation events. Press Ctrl+C to stop."
while ($true) {
    Start-Sleep -Seconds 1
}
`;

// Save the PowerShell script to a file
const fs = require('fs');
const psScriptPath = path.join(__dirname, 'monitorEvents.ps1');
fs.writeFileSync(psScriptPath, psScript);

// Create a new service object
const svc = new Service({
  name: 'EventLogMonitorService',
  description: 'A service that monitors Windows Event Logs and logs to the console',
  script: path.join(__dirname, 'monitorEvents.js')
});

// Define what to do when the service is installed
svc.on('install', () => {
  svc.start();
});

// Install the service
svc.install();
```
```
const { exec } = require('child_process');
const path = require('path');

// Path to the PowerShell script
const psScriptPath = path.join(__dirname, 'monitorEvents.ps1');

// Run the PowerShell script using the child_process exec method
exec(`powershell -NoProfile -ExecutionPolicy Bypass -File "${psScriptPath}"`, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`Stderr: ${stderr}`);
    return;
  }
  console.log(`Stdout: ${stdout}`);
});
```
``` 
# Define the event log query
$query = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[(EventID=4688)]]
    </Select>
  </Query>
</QueryList>
"@

# Create an event log watcher
$eventLogWatcher = New-Object System.Diagnostics.Eventing.Reader.EventLogWatcher -ArgumentList $query

# Define the action to take on each event
$eventAction = {
    param($eventArgs)
    
    $event = [xml]$eventArgs.NewEvent.ToXml()
    $timeCreated = $event.Event.System.TimeCreated.SystemTime
    $exeName = $event.Event.EventData.Data | Where-Object { $_.Name -eq "NewProcessName" } | Select-Object -ExpandProperty '#text'
    $pid = $event.Event.EventData.Data | Where-Object { $_.Name -eq "NewProcessId" } | Select-Object -ExpandProperty '#text'
    
    $logEntry = @{
        TimeCreated = $timeCreated
        Date = [DateTime]$timeCreated.ToString("yyyy-MM-dd")
        ExeName = $exeName
        Pid = $pid
    }

    Write-Output "New process detected: $(ConvertTo-Json $logEntry)"
}

# Subscribe to the event
Register-ObjectEvent -InputObject $eventLogWatcher -EventName "EventRecordWritten" -Action $eventAction

# Start the event log watcher
$eventLogWatcher.Enabled = $true

# Keep the script running
Write-Host "Monitoring process creation events. Press Ctrl+C to stop."
while ($true) {
    Start-Sleep -Seconds 1
}

```
``` 
const { WinEventEmitter } = require('win-getevent');

// Create a new WinEventEmitter
const winEmitter = new WinEventEmitter({
  providers: ['Microsoft-Windows-Security-Auditing'],
  // or use LogName filter, defaults to 'System','Setup','Application','Security'
  logNames: ['Security'],
  frequency: 1000 /* ms */
});

// Event handler for 'data' event
winEmitter.on('data', logs => {
  // Contains an array of log objects
  logs.forEach(log => {
    const message = log.message;
    if (message.includes('.exe')) {
      const exePathMatch = message.match(/New Process Name:\s*(.*\.exe)/);
      const startTime = log.timeCreated;

      if (exePathMatch) {
        const exePath = exePathMatch[1];
        console.log(`exepath: ${exePath}, start time: ${startTime}`);
      }
    }
  });
});

// Event handler for 'error' event
winEmitter.on('error', err => {
  console.log(`Error: ${err}`);
});

// Event handler for 'end' event
winEmitter.on('end', () => {
  console.log('Ended');
});

// Start polling
winEmitter.start();

// To stop the emitter, use: winEmitter.stop();
// This will emit the 'end' event

```
``` 
const { WinEventEmitter } = require('win-getevent').WinEventEmitter;

// Create a new WinEventEmitter
const winEmitter = new WinEventEmitter({
  providers: ['Microsoft-Windows-Security-Auditing'],
  logNames: ['Security'],
  frequency: 1000, // polling frequency in ms
});

// Event handler for 'data' event
winEmitter.on('data', logs => {
  // Contains an array of log objects
  logs.forEach(log => {
    if (log.id === 4688) { // Check for Event ID 4688 (Process Creation)
      const message = log.message;
      const exePathMatch = message.match(/New Process Name:\s*(.*\.exe)/);
      const startTime = log.timeCreated;

      if (exePathMatch) {
        const exePath = exePathMatch[1];
        console.log(`exepath: ${exePath}, start time: ${startTime}`);
      }
    }
  });
});

// Event handler for 'error' event
winEmitter.on('error', err => {
  console.error(`Error: ${err}`);
});

// Event handler for 'end' event
winEmitter.on('end', () => {
  console.log('Ended');
});

// Start polling
winEmitter.start();

// To stop the emitter, use: winEmitter.stop();
// This will emit the 'end' event
```
'''

2.5.1 Components
Account ID Entry:

Users are required to enter their account ID to access their entitlement usage history.
Entitlement Details Table:

Columns:
Entitlement: The unique identifier for the entitlement.
Entitlement Name: The name of the entitlement.
Entitlement Owner: The owner of the entitlement.
Risk Level Tier: The risk level associated with the entitlement.
Last Access Time: The most recent time the entitlement was accessed.
Last Access Time of Dependencies: The most recent access time of any dependent entitlements.
Access Time Log: A list of all access timestamps for the entitlement.
Entitlement with Dependencies:

When a user clicks on an entitlement that has dependent entitlements, a dropdown opens showing a list of all dependent entitlements.
Users can access the access time log for these dependent entitlements.
Access Time Log Details:

The Access Time Log column contains a list of all access timestamps for the specific entitlement.
Clicking on an access detail opens a dropdown that shows location details such as IP address, MAC ID, datacenter, etc.
Action Required Table:

This section lists entitlements that have not been used for more than 2 days.
For testing purposes, this value is set to 2 days, but in a real scenario, it will be preset to a longer period, like 45 days.
By highlighting these entitlements, users can quickly identify potentially inactive or unnecessary entitlements.
2.5.2 Functionality
View and manage entitlements: Users can see detailed information about their entitlements and take necessary actions.
Track recent activities and changes: Users can monitor their access history and changes in their entitlements.
Receive notifications about important events or required actions: Alerts and notifications ensure users are aware of important updates and actions they need to take.
2.6 Manager Page (/manager)
The Manager Page is designed for managers to oversee team activities and manage entitlements at a higher level. It provides tools and insights to ensure compliance and optimize team performance.

Components:
Team Entitlements Overview: Summarizes entitlements and statuses for the manager's team.
Team Activity Log: Displays recent activities and changes in entitlements for team members.
Performance Metrics: Provides insights into team performance and usage statistics.
Notifications: Alerts about required actions, compliance issues, or important updates.
Functionality:
Monitor team activities and entitlements.
Track performance metrics and usage trends.
Receive and manage notifications related to team management.
2.7 App Owner Page (/appowner)
The App Owner Page is tailored for app owners to manage their applications and monitor performance metrics. It provides a detailed view of application-related activities and entitlements.

Components:
Application Entitlements Overview: Displays current entitlements related to the app owner's applications.
Application Activity Log: A list of recent activities and changes in entitlements for the applications.
Performance Metrics: Provides insights into application performance and usage statistics.
Notifications: Alerts about required actions or important updates related to the applications.
Functionality:
Manage application entitlements.
Track application activities and performance.
Receive and act on notifications related to application management.
By defining these routes and their specific functionalities, the Dashboard ensures that users, app owners, and managers can efficiently access the information and tools they need to manage entitlements and activities within the Access Chronicle portal.










ChatGPT can make mistakes. Check important info.
'''
'''
.
Employee Access Details Table:

Columns:
Account ID: The unique identifier for the employee's account.
Employee ID: The identifier for the employee.
Employee Name: The name of the employee.
Is Tracked: Indicates whether the employee's activities are being tracked.
Number of Entitlements: The total number of entitlements assigned to the employee.
Entitlement Details: Detailed information about each entitlement.
Action Required Table:

This section lists entitlements that have not been used for a customizable period, allowing managers to set the threshold based on days and hours.
By providing this functionality, managers can tailor the inactivity threshold to suit their specific operational needs and promptly identify potentially inactive entitlements.
Sporadic Access Details:

Columns:
Account ID: The unique identifier for the employee's account.
Entitlement ID: The identifier for the entitlement.
Access Count: The number of times the entitlement has been accessed.
First Access Time: The first time the entitlement was accessed.
Last Access Time: The most recent time the entitlement was accessed.
Anomalous Access Details:

Columns:
Account ID: The unique identifier for the employee's account.
Entitlement ID: The identifier for the entitlement.
Entitlement Name: The name of the entitlement.
Risk Level: The risk level associated with the entitlement.
Access Details: Detailed information about the access, including any anomalies detected.
2.6.3 Functionality
Monitor and manage team entitlements: Managers can view detailed information about their team members' entitlements and take necessary actions.
Track employee activities and changes: Managers can monitor access history and changes in entitlements for their team.
Customize inactivity thresholds: Managers can set custom periods for identifying inactive entitlements, allowing for flexible and responsive management.
Identify sporadic and anomalous access patterns: Detailed tables help managers detect unusual access patterns and take appropriate actions to mitigate risks.
2.7 App Owner Page (/appowner)
The App Owner Page is tailored for app owners to manage their applications and monitor performance metrics. It provides a detailed view of application-related activities and entitlements.

Components:
Application Entitlements Overview: Displays current entitlements related to the app owner's applications.
Application Activity Log: A list of recent activities and changes in entitlements for the applications.
Performance Metrics: Provides insights into application performance and usage statistics.
Notifications: Alerts about required actions or important updates related to the applications.
Functionality:
Manage application entitlements.
Track application activities and performance.
Receive and act on notifications related to application management.
By defining these routes and their specific functionalities, the Dashboard ensures that users, app owners, and managers can efficiently access the information and tools they need to manage entitlements and activities within the Access Chronicle portal.










ChatGPT can make mistakes. Check important info.
'''
'''
/manager-info:

This route fetches the entitlement details of all the employees under the specified employee ID. It retrieves information such as the account ID, employee name, whether the employee's activities are being tracked (isTracked), and the number of entitlements assigned to each employee. This data is then displayed in the Employee Access Details Table.
/action-required:

This route fetches and displays entitlements that have not been used for more than the time period set by the manager. The route queries the database for entitlements with an inactivity period exceeding the specified threshold (customizable in days and hours) and presents this information in the Action Required Table. This helps managers identify potentially inactive entitlements promptly.
/sporadic-access:

This route identifies and fetches entitlements that have been accessed less frequently than a set threshold within a specified time period. For example, if the period is set to the last month and the frequency threshold is set to less than five accesses, the route will retrieve entitlements accessed in the last month with fewer than five access events. This data is displayed in the Sporadic Access Details table, allowing managers to spot underused entitlements.
/anomalous-logs:

This route leverages a machine learning model running in the background to detect and display anomalous access entries. It identifies unusual patterns or activities that deviate from the norm, such as unexpected access times or locations. The route fetches these anomalous entries and displays them in the Anomalous Access Details table, providing managers with insights into potential security threats or irregularities in entitlement usage.
2.6.4 Functionality
Monitor and manage team entitlements: Managers can view detailed information about their team members' entitlements and take necessary actions.
Track employee activities and changes: Managers can monitor access history and changes in entitlements for their team.
Customize inactivity thresholds: Managers can set custom periods for identifying inactive entitlements, allowing for flexible and responsive management.
Identify sporadic and anomalous access patterns: Detailed tables help managers detect unusual access patterns and take appropriate actions to mitigate risks.









ChatGPT can make mistakes. Check important info.

'''
