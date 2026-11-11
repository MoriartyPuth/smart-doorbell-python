// Behaviour of the control panel (index.html).
// It asks the board for /api/status every 2 seconds and redraws the page.
// Buttons POST to /api/<action>; the list is in bridge/web_bridge.py.

const $ = id => document.getElementById(id);
let cameraUrl = null;

// Redraws the page from a status object sent by the board.
function show(s) {
  $('doorState').textContent = s.locked ? 'Locked' : 'Unlocked';
  $('doorState').className = s.locked ? 'locked' : 'unlocked';
  $('waiting').textContent = s.waiting ? 'Someone is at the door!' : '';
  $('muteBtn').textContent = s.muted ? 'Unmute buzzer' : 'Mute buzzer';
  $('visitors').textContent = s.visitors;
  $('lastVisit').textContent = s.lastVisit;
  $('rssi').textContent = s.rssi + ' dBm';
  $('uptime').textContent = s.uptimeMin + ' min';
  if (s.camera !== cameraUrl) {           // only touch the stream when it changes
    cameraUrl = s.camera;
    $('stream').style.display = cameraUrl ? 'block' : 'none';
    $('noCam').style.display = cameraUrl ? 'none' : 'block';
    if (cameraUrl) $('stream').src = cameraUrl.replace(/\/$/, '') + ':81/stream';
  }
}

function setOnline(online) {
  $('link').textContent = online ? 'online' : 'offline';
  $('link').className = online ? 'dot' : 'dot off';
}

function note(text) {
  $('note').textContent = text;
  setTimeout(() => { if ($('note').textContent === text) $('note').textContent = ''; }, 4000);
}

// Sends one action to the board (POST /api/<name>). The board carries it out
// a moment later, so the page re-reads the status shortly afterwards.
async function act(name, body) {
  if (name === 'photo' && !cameraUrl) return note('Camera is offline');
  try {
    const reply = await fetch('/api/' + name, { method: 'POST', body });
    note(reply.ok ? 'Sent: ' + name : await reply.text());
    setTimeout(refresh, 700);
    setTimeout(refresh, 2500);
  } catch (e) {
    note('Board did not answer');
  }
}

function sendMessage(event) {
  event.preventDefault();
  const text = $('msg').value.trim();
  if (!text) return;
  act('msg', text);
  $('msg').value = '';
}

async function refresh() {
  try {
    const reply = await fetch('/api/status');
    show(await reply.json());
    setOnline(true);
  } catch (e) {
    setOnline(false);
  }
}

refresh();
setInterval(refresh, 2000);
