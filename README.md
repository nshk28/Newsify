# Newsify
Newsify: Your personalized news app delivering curated content tailored to your interests.Stay informed and connected with Newsify, your personalized news companion!

'''
Design Considerations
Introduction
The design considerations section outlines the key aspects that have influenced the overall design of the Access Chronicle portal. This includes the choice of technology stack, the system architecture, and various design diagrams that provide a detailed view of the system components and their interactions.

Technology Stack
The following technology stack has been selected for the development of the Access Chronicle portal:

Frontend: React.js, TypeScript
Backend: Node.js, Express.js
Database: MSSQL
Version Control: Git
Deployment: Docker, Kubernetes
Monitoring and Logging: Prometheus, Grafana, ELK Stack
The chosen technologies ensure scalability, maintainability, and high performance for the application.

Entity-Relationship (ER) Diagram
The ER diagram provides a visual representation of the data model used in the Access Chronicle portal. It illustrates the entities, attributes, and relationships within the system, ensuring a clear understanding of how data is structured and related.


System Architecture
The system architecture section describes the overall structure of the Access Chronicle portal, including the interaction between various components and services. The architecture is designed to ensure modularity, scalability, and robustness.


Key Components:
Frontend Application: Handles user interface and interactions.
Backend Services: Manages business logic and database interactions.
Database: Stores all relevant data securely.
Authentication Service: Manages user authentication and authorization.
Monitoring and Logging: Ensures the system's health and performance are continuously monitored.
Sequence Diagram
The sequence diagram illustrates the interaction between different system components during a specific process. It provides a step-by-step view of how requests and responses flow through the system.


Example Process: User Accessing Entitlement Details
User Request: The user requests to view entitlement details from the frontend application.
API Call: The frontend application sends an API request to the backend service.
Data Retrieval: The backend service retrieves the required data from the database.
Response: The backend service sends the data back to the frontend application.
Display: The frontend application displays the entitlement details to the user.
Conclusion
The design considerations outlined above provide a comprehensive overview of the critical decisions and diagrams that influence the development and functionality of the Access Chronicle portal. These considerations ensure that the system is built using a robust, scalable, and maintainable approach.

This structure covers all the required topics and integrates them into a cohesive "Design Considerations" section.










ChatGPT can make mistakes. Check important inf
'''

'''
Introduction
In the Access Chronicle portal, the App Owner section is designed to cater to the needs of individuals responsible for managing in-house and desktop applications. For instance, suppose "A" is the owner of an in-house application, and "B" is the owner of a desktop application. This section provides these owners with comprehensive tools and insights to manage their applications' entitlements effectively.

Components
1. Action Required Section
The Action Required Section displays entitlements that have not been used for more than the period set by the app owner. This helps in identifying and managing inactive entitlements. The table includes the following columns:

Entitlement: The unique identifier for the entitlement.
Entitlement Name: The descriptive name of the entitlement.
Access Details: A link to view detailed information about the usage of the entitlement.
Last Access Time: The most recent time the entitlement was accessed.
When the app owner clicks on the Access Details link for a particular entitlement, a detailed view is presented. This view includes:

Account ID: The identifier for each account that has accessed the entitlement.
Employee ID: The identifier for the employee associated with the account.
Employee Name: The name of the employee associated with the account.
Last Access Time: The most recent time the entitlement was accessed by the account.
Last Access Time for Dependency: The most recent time the dependent entitlement was accessed.
2. Anomalous Access Details Table
The Anomalous Access Details Table provides app owners with insights into any unusual access patterns detected for their applications. This table is crucial for identifying potential security risks and ensuring that only authorized users have access to sensitive entitlements. The table includes information such as:

Entitlement: The unique identifier for the entitlement with anomalous access.
Access Details: A link to view the detailed anomalous access information.
Last Access Time: The most recent time the entitlement was accessed.
Clicking on the Access Details link will show a detailed view of the anomalous access, including:

Account ID: The identifier for each account with anomalous access.
Employee ID: The identifier for the employee associated with the account.
Employee Name: The name of the employee associated with the account.
Anomalous Access Time: The time when the anomalous access occurred.
Reason for Flagging: The reason why the access was flagged as anomalous.
3. Application Cards
In the App Owner section, each application, whether in-house or desktop, is represented by a separate card. These cards provide a consolidated view of the application's details and its entitlements. The cards include the following information:

Application ID: The unique identifier for the application.
Executable Path (for Desktop Applications): The file path to the executable of the desktop application.
Entitlement Access Details: A detailed view of the access information for each entitlement associated with the application.
Additionally, the cards display information about all dependent entitlements within the same card, ensuring that the app owner has a complete view of how entitlements are being used and managed across their applications.

This documentation provides app owners with a clear understanding of the tools available to them for managing their applications' entitlements, ensuring efficient and secure access management.






Is this conversation helpful so far?







ChatGPT can make mistakes. Check important info.

'''
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
