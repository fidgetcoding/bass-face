// Bass Face v1.5 launcher (Node for Max).
// Device load -> tracker spawns (camera on). Device unload / Live quit ->
// tracker dies. CAM toggle on the device face sends launch/halt.
// Note: macOS attributes the camera to the parent app - first run prompts
// to give Ableton Live camera access.

const Max = require('max-api');
const { spawn, execSync } = require('child_process');

// Dev install path; Ship build swaps this for the bundled BassFace.app.
const TRACKER_DIR = '/Users/nathandavidovich/code/bass-face';
const PY = TRACKER_DIR + '/.venv/bin/python';

let child = null;

function alreadyRunning() {
    try {
        execSync('pgrep -f "tracker/core.py"', { stdio: 'pipe' });
        return true;
    } catch (e) {
        return false;
    }
}

function launch() {
    if (child) {
        Max.post('bassface: tracker already ours (pid ' + child.pid + ')');
        return;
    }
    if (alreadyRunning()) {
        Max.post('bassface: tracker already running elsewhere - not spawning');
        Max.outlet('running', 1);
        return;
    }
    child = spawn(PY, ['tracker/core.py', '--autostart'],
                  { cwd: TRACKER_DIR, stdio: 'ignore' });
    Max.post('bassface: tracker launched (pid ' + child.pid + ')');
    Max.outlet('running', 1);
    child.on('exit', (code) => {
        Max.post('bassface: tracker exited (' + code + ')');
        child = null;
        Max.outlet('running', 0);
    });
}

function halt() {
    if (child) {
        child.kill('SIGTERM');
        child = null;
    } else {
        try { execSync('pkill -f "tracker/core.py"'); } catch (e) {}
    }
    Max.post('bassface: tracker stopped');
    Max.outlet('running', 0);
}

Max.addHandler('launch', launch);
Max.addHandler('halt', halt);
process.on('exit', () => { if (child) child.kill('SIGTERM'); });

launch(); // auto-start on device load
