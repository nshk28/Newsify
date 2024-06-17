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
