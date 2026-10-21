import json
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
DB_FILE = "leaderboard.json"


def get_badge(score):
    if score >= 400:
        return {"icon": "👑", "title": "Dragon King"}
    if score >= 300:
        return {"icon": "⚡", "title": "Cobra"}
    if score >= 200:
        return {"icon": "🐍", "title": "Viper"}
    if score >= 100:
        return {"icon": "🐣", "title": "Hatchling"}
    return {"icon": "🥚", "title": "Egg"}


def load_scores():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_scores(scores):
    with open(DB_FILE, "w") as f:
        json.dump(scores, f, indent=2)


PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Snake Arcade</title>
<style>
:root { --accent:#65e6a6; --panel:#1c2332; --text:#f3f5fa; }
* { box-sizing:border-box; }
body {
  margin:0; min-height:100vh; background:#10141f; color:var(--text);
  font-family:system-ui,-apple-system,sans-serif;
  display:flex; justify-content:center; align-items:center;
}
main { width:min(94vw,620px); padding:22px 0; }
header { text-align:center; margin-bottom:22px; }
.eyebrow { color:var(--accent); letter-spacing:4px; font-size:11px; font-weight:800; }
h1 { font-size:48px; letter-spacing:-2px; margin:5px 0; }
header p { color:#929bad; margin:0; }
.panel {
  background:var(--panel); border:1px solid #30394b;
  border-radius:15px; padding:18px; margin-bottom:14px;
}
.stats { display:grid; grid-template-columns:1fr 1fr 1fr; gap:9px; margin-bottom:12px; }
.stat { background:var(--panel); padding:12px; text-align:center; border-radius:10px; }
.stat small { display:block; color:#aab3c3; text-transform:uppercase; font-size:10px; letter-spacing:1px; }
.stat strong { display:block; font-size:23px; margin-top:4px; }
canvas {
  width:100%; height:auto; display:block; border-radius:12px;
  border:2px solid #30394b; touch-action:none;
}
h2 { font-size:21px; margin:0 0 14px; }
label { display:block; color:#cbd3df; font-size:12px; margin-bottom:6px; }
select, input[type=color], input[type=text] {
  width:100%; min-height:42px; border:1px solid #414d62;
  border-radius:8px; background:#111725; color:white;
  padding:9px; font:inherit;
}
input[type=color] { padding:4px; cursor:pointer; }
.settings-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.field { min-width:0; }
button {
  border:0; border-radius:9px; padding:12px 15px;
  font-weight:750; cursor:pointer; font-size:13px;
}
.primary { background:var(--accent); color:#10141f; }
.secondary { background:#30394b; color:white; border:1px solid #46536a; }
button:hover { filter:brightness(1.08); }
.actions { display:flex; gap:9px; margin-top:14px; }
.actions button { flex:1; }
.hidden { display:none !important; }
.hint { font-size:12px; color:#929bad; line-height:1.7; text-align:center; margin-top:15px; }
.overlay { position:relative; text-align:center; padding:14px 0 0; color:#cbd3df; font-size:13px; }
#message { color:var(--accent); font-weight:700; min-height:22px; }

/* Leaderboard & Submit Modal */
.modal {
  background:#141a27; border:1px solid #3c485e; border-radius:12px;
  padding:16px; margin-top:14px; text-align:center;
}
.tier-legend {
  display:flex; justify-content:center; gap:8px; flex-wrap:wrap;
  margin:10px 0 16px; font-size:11px; color:#929bad;
}
.tier-badge { background:#111725; padding:4px 8px; border-radius:6px; border:1px solid #2a3447; }
.leaderboard-table { width:100%; border-collapse:collapse; margin-top:10px; font-size:13px; }
.leaderboard-table th { color:#828e9e; text-align:left; padding:8px; border-bottom:1px solid #2a3447; font-size:11px; text-transform:uppercase; }
.leaderboard-table td { padding:10px 8px; border-bottom:1px solid #212939; }
.leaderboard-table tr:last-child td { border-bottom:none; }
.rank-badge { font-size:16px; margin-right:6px; vertical-align:middle; }
</style>
</head>
<body>
<main>
<header>
  <div class="eyebrow">ARCADE SERIES / 001</div>
  <h1>Snake<span style="color:var(--accent)">.</span></h1>
  <p>Make it yours. Beat your best.</p>
</header>

<section id="settings" class="panel">
  <h2>⚙ Game settings</h2>
  <div class="settings-grid">
    <div class="field">
      <label for="mode">Game mode</label>
      <select id="mode">
        <option value="classic">Classic — walls end the game</option>
        <option value="wrap">Wrap-around — pass through edges</option>
        <option value="walls">Wall builder — food leaves a wall</option>
        <option value="peaceful">Peaceful — no collision game over</option>
      </select>
    </div>
    <div class="field">
      <label for="speed">Snake speed</label>
      <select id="speed">
        <option value="slow">Turtle — slow</option>
        <option value="normal" selected>Snake — normal</option>
        <option value="fast">Rabbit — fast</option>
      </select>
    </div>
    <div class="field">
      <label for="board">Board size</label>
      <select id="board">
        <option value="16">Small</option>
        <option value="24" selected>Medium</option>
        <option value="32">Large</option>
      </select>
    </div>
    <div class="field">
      <label for="foodCount">Food on board</label>
      <select id="foodCount">
        <option value="1">1 piece</option>
        <option value="3">3 pieces</option>
        <option value="5">5 pieces</option>
      </select>
    </div>
    <div class="field">
      <label for="snakeColor">Snake color</label>
      <select id="snakeColor">
        <option value="#65e6a6">Mint green</option>
        <option value="#54a0ff">Electric blue</option>
        <option value="#c084fc">Purple</option>
        <option value="#ff647c">Pink</option>
        <option value="#ffd166">Gold</option>
        <option value="#f7f7ff">White</option>
        <option value="rainbow">Rainbow</option>
        <option value="custom">Custom color below</option>
      </select>
    </div>
    <div class="field">
      <label for="customColor">Custom snake color</label>
      <input type="color" id="customColor" value="#65e6a6">
    </div>
    <div class="field">
      <label for="fruit">Food style</label>
      <select id="fruit">
        <option value="🍎">Apple</option>
        <option value="🍌">Banana</option>
        <option value="🍒">Cherries</option>
        <option value="🍊">Orange</option>
        <option value="🍇">Grapes</option>
        <option value="🍍">Pineapple</option>
        <option value="🍓">Strawberry</option>
        <option value="⭐">Star</option>
      </select>
    </div>
    <div class="field">
      <label for="theme">Board theme</label>
      <select id="theme">
        <option value="dark">Midnight</option>
        <option value="forest">Forest</option>
        <option value="ocean">Ocean</option>
        <option value="sunset">Sunset</option>
        <option value="snow">Snow</option>
        <option value="light">Classic light</option>
      </select>
    </div>
  </div>
  <div class="actions">
    <button class="secondary" id="randomize">🎲 Randomize</button>
    <button class="secondary" id="resetSettings">Reset settings</button>
  </div>
  <button class="primary" id="play" style="width:100%;margin-top:12px">▶ Play with these settings</button>
</section>

<section id="gamePanel" class="hidden">
  <div class="stats">
    <div class="stat"><small>Score</small><strong id="score">0</strong></div>
    <div class="stat"><small>Best</small><strong id="best">0</strong></div>
    <div class="stat"><small>Food eaten</small><strong id="eaten">0</strong></div>
  </div>
  <canvas id="game" width="480" height="480"></canvas>
  <div class="overlay">
    <div id="message">Ready!</div>
    <strong id="modeLabel">Classic mode</strong>
  </div>

  <div id="submitModal" class="modal hidden">
    <h3 style="margin-top:0">🎉 Submit to Leaderboard</h3>
    <p style="font-size:12px;color:#929bad;margin:4px 0 12px">
      Rank Tier: <span id="submitBadge" style="font-size:16px"></span> <b id="submitTierName" style="color:var(--accent)"></b>
    </p>
    <div style="display:flex;gap:8px">
      <input type="text" id="playerName" placeholder="Enter your name" maxlength="16" style="flex:1">
      <button class="primary" id="saveScoreBtn">Save</button>
    </div>
  </div>

  <div class="actions">
    <button class="primary" id="pause">Ⅱ Pause</button>
    <button class="secondary" id="restart">↻ Restart</button>
    <button class="secondary" id="changeSettings">⚙ Settings</button>
  </div>
  <p class="hint">Arrow keys / WASD to move · Space to pause</p>
</section>

<section class="panel">
  <h2>🏆 Hall of Fame</h2>
  <div class="tier-legend">
    <span class="tier-badge">🥚 Egg: 0-99</span>
    <span class="tier-badge">🐣 Hatchling: 100-199</span>
    <span class="tier-badge">🐍 Viper: 200-299</span>
    <span class="tier-badge">⚡ Cobra: 300-399</span>
    <span class="tier-badge">👑 Dragon: 400+</span>
  </div>
  <table class="leaderboard-table">
    <thead>
      <tr>
        <th style="width:40px">#</th>
        <th>Player</th>
        <th>Badge</th>
        <th style="text-align:right">Score</th>
      </tr>
    </thead>
    <tbody id="leaderboardBody">
      <tr><td colspan="4" style="text-align:center;color:#6b7688">Loading scores...</td></tr>
    </tbody>
  </table>
</section>
</main>

<script>
const $ = id => document.getElementById(id);
const canvas = $("game"), ctx = canvas.getContext("2d");
const defaults = {
  mode:"classic", speed:"normal", board:"24", foodCount:"1",
  snakeColor:"#65e6a6", customColor:"#65e6a6",
  fruit:"🍎", theme:"dark"
};
let config = {...defaults};
let snake=[], foods=[], walls=[], direction={x:1,y:0}, nextDir={x:1,y:0};
let score=0, eaten=0, best=0, state="ready", timer=null;
let tickMs=115, grid=24, cell=20, stepCount=0;

const themes = {
  dark:   ["#171e2b","#202939","#30394b"],
  forest: ["#14251d","#1b3327","#31513b"],
  ocean:  ["#102533","#173447","#2b5265"],
  sunset: ["#30202b","#40283a","#604052"],
  snow:   ["#eaf0f7","#dbe5ef","#bdcad9"],
  light:  ["#f4f5ed","#e7eadf","#cdd4c3"]
};

function getBadge(s) {
  if (s >= 400) return {icon: "👑", title: "Dragon King"};
  if (s >= 300) return {icon: "⚡", title: "Cobra"};
  if (s >= 200) return {icon: "🐍", title: "Viper"};
  if (s >= 100) return {icon: "🐣", title: "Hatchling"};
  return {icon: "🥚", title: "Egg"};
}

async function fetchLeaderboard() {
  try {
    const res = await fetch("/api/scores");
    const data = await res.json();
    const tbody = $("leaderboardBody");
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#6b7688">No entries yet. Be the first!</td></tr>';
      return;
    }
    tbody.innerHTML = data.map((entry, idx) => `
      <tr>
        <td>${idx + 1}</td>
        <td><strong>${entry.name}</strong></td>
        <td><span class="rank-badge">${entry.badge.icon}</span> ${entry.badge.title}</td>
        <td style="text-align:right;font-weight:700;color:var(--accent)">${entry.score}</td>
      </tr>
    `).join("");
  } catch(e) {
    $("leaderboardBody").innerHTML = '<tr><td colspan="4" style="text-align:center;color:#ff647c">Failed to load leaderboard.</td></tr>';
  }
}

async function submitScore() {
  const name = $("playerName").value.trim() || "Anonymous";
  await fetch("/api/scores", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ name, score })
  });
  $("submitModal").classList.add("hidden");
  fetchLeaderboard();
}

function finishGame(message) {
  if (config.mode === "peaceful") return;
  state = "over";
  clearInterval(timer);
  setMessage(message + " — Score: " + score);

  if (score > 0) {
    const badge = getBadge(score);
    $("submitBadge").textContent = badge.icon;
    $("submitTierName").textContent = badge.title;
    $("submitModal").classList.remove("hidden");
  }
}

function loadSettings() {
  try {
    const saved = JSON.parse(localStorage.getItem("snakeSettings") || "{}");
    config = {...defaults, ...saved};
  } catch(e) { config = {...defaults}; }
  for (const key of Object.keys(defaults)) {
    if ($(key))$(key).value = config[key];
  }
  try { best = Number(localStorage.getItem("snakeBest")) || 0; }
  catch(e) { best = 0; }
  $("best").textContent = best;
  updateAccent();
}

function readSettings() {
  for (const key of Object.keys(defaults)) {
    config[key] = $(key).value;
  }
  try { localStorage.setItem("snakeSettings", JSON.stringify(config)); }
  catch(e) {}
  updateAccent();
}

function updateAccent() {
  const color = config.snakeColor === "custom" ? config.customColor : config.snakeColor;
  document.documentElement.style.setProperty("--accent", color === "rainbow" ? "#65e6a6" : color);
}

function colorFor(index) {
  if (config.snakeColor === "rainbow") return `hsl(${(index * 17 + stepCount * 2) % 360} 85% 62%)`;
  if (config.snakeColor === "custom") return config.customColor;
  return config.snakeColor;
}

function setMessage(text) { $("message").textContent = text; }

function placeFood() {
  let p, attempts = 0;
  do {
    p = {x:Math.floor(Math.random()*grid), y:Math.floor(Math.random()*grid)};
    attempts++;
  } while (
    attempts < 2000 &&
    (snake.some(s=>s.x===p.x&&s.y===p.y) ||
     walls.some(w=>w.x===p.x&&w.y===p.y) ||
     foods.some(f=>f.x===p.x&&f.y===p.y))
  );
  if (attempts < 2000) foods.push(p);
}

function newGame() {
  readSettings();
  $("submitModal").classList.add("hidden");
  grid = Number(config.board);
  cell = canvas.width / grid;
  tickMs = {slow:210,normal:115,fast:65}[config.speed];
  snake = [
    {x:Math.floor(grid/2),y:Math.floor(grid/2)},
    {x:Math.floor(grid/2)-1,y:Math.floor(grid/2)},
    {x:Math.floor(grid/2)-2,y:Math.floor(grid/2)}
  ];
  direction = {x:1,y:0}; nextDir = {x:1,y:0};
  foods = []; walls = []; score = 0; eaten = 0; stepCount = 0;
  $("score").textContent = score;
  $("eaten").textContent = eaten;
  $("modeLabel").textContent = {
    classic:"Classic mode",wrap:"Wrap-around mode",
    walls:"Wall builder mode",peaceful:"Peaceful mode"
  }[config.mode];
  for(let i=0; i<Number(config.foodCount); i++) placeFood();
  $("settings").classList.add("hidden");
  $("gamePanel").classList.remove("hidden");
  state = "playing";
  setMessage("Good luck!");
  draw();
  startTimer();
}

function startTimer() {
  clearInterval(timer);
  timer = setInterval(update, tickMs);
}

function update() {
  if (state !== "playing") return;
  direction = {...nextDir};
  let head = {x:snake[0].x+direction.x, y:snake[0].y+direction.y};

  if (config.mode === "wrap") {
    head.x = (head.x + grid) % grid;
    head.y = (head.y + grid) % grid;
  } else if (head.x < 0 || head.x >= grid || head.y < 0 || head.y >= grid) {
    finishGame("You hit the wall");
    return;
  }

  const foodIndex = foods.findIndex(f => f.x === head.x && f.y === head.y);
  const eating = foodIndex !== -1;
  const body = eating ? snake : snake.slice(0, -1);
  const hitSelf = body.some(s => s.x === head.x && s.y === head.y);
  const hitWall = walls.some(w => w.x === head.x && w.y === head.y);

  if ((hitSelf || hitWall) && config.mode !== "peaceful") {
    finishGame(hitWall ? "You hit an obstacle" : "You hit yourself");
    return;
  }

  if (hitSelf || hitWall) return;

  snake.unshift(head);

  if (eating) {
    foods.splice(foodIndex, 1);
    score += 10; eaten++;
    $("score").textContent = score;
    $("eaten").textContent = eaten;
    if (score > best) {
      best = score; $("best").textContent = best;
      try { localStorage.setItem("snakeBest", String(best)); } catch(e) {}
    }
    if (config.mode === "walls") walls.push({x:head.x-direction.x, y:head.y-direction.y});
    placeFood();
  } else {
    snake.pop();
  }
  stepCount++;
  draw();
}

function draw() {
  const theme = themes[config.theme] || themes.dark;
  ctx.fillStyle = theme[0];
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = theme[1]; ctx.lineWidth = .7;
  for (let i = 0; i <= grid; i++) {
    ctx.beginPath(); ctx.moveTo(i*cell, 0); ctx.lineTo(i*cell, canvas.height); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, i*cell); ctx.lineTo(canvas.width, i*cell); ctx.stroke();
  }

  walls.forEach(w => {
    ctx.fillStyle = "#8b96a8";
    ctx.fillRect(w.x*cell+2, w.y*cell+2, cell-4, cell-4);
  });

  foods.forEach(f => {
    ctx.font = `${Math.max(12, cell*.8)}px sans-serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(config.fruit, (f.x+.5)*cell, (f.y+.52)*cell);
  });

  snake.forEach((s, i) => {
    const pad = Math.max(1, cell*.09);
    ctx.fillStyle = colorFor(i);
    ctx.beginPath();
    ctx.roundRect(s.x*cell+pad, s.y*cell+pad, cell-pad*2, cell-pad*2, Math.max(2, cell*.2));
    ctx.fill();

    if (i === 0) {
      ctx.fillStyle = "#10141f";
      const cx = (s.x+.5)*cell, cy = (s.y+.5)*cell;
      const eyeOffset = cell*.17, eyeRadius = Math.max(1.5, cell*.055);
      let eyes;
      if (direction.x === 1) eyes = [[cx+eyeOffset, cy-eyeOffset], [cx+eyeOffset, cy+eyeOffset]];
      else if (direction.x === -1) eyes = [[cx-eyeOffset, cy-eyeOffset], [cx-eyeOffset, cy+eyeOffset]];
      else if (direction.y === -1) eyes = [[cx-eyeOffset, cy-eyeOffset], [cx+eyeOffset, cy-eyeOffset]];
      else eyes = [[cx-eyeOffset, cy+eyeOffset], [cx+eyeOffset, cy+eyeOffset]];
      eyes.forEach(([x, y]) => {
        ctx.beginPath(); ctx.arc(x, y, eyeRadius, 0, Math.PI*2); ctx.fill();
      });
    }
  });
}

function changeDirection(name) {
  const dirs = { up:{x:0,y:-1}, down:{x:0,y:1}, left:{x:-1,y:0}, right:{x:1,y:0} };
  const d = dirs[name];
  if (!d || (d.x === -direction.x && d.y === -direction.y)) return;
  nextDir = d;
}

function pauseGame() {
  if (state === "playing") {
    state = "paused"; clearInterval(timer); setMessage("Paused");
    $("pause").textContent = "▶ Resume";
  } else if (state === "paused") {
    state = "playing"; setMessage("Back in action!");
    $("pause").textContent = "Ⅱ Pause"; startTimer();
  }
}

$("play").onclick = newGame;
$("restart").onclick = newGame;
$("pause").onclick = pauseGame;
$("saveScoreBtn").onclick = submitScore;
$("changeSettings").onclick = () => {
  clearInterval(timer); state = "ready";
  $("gamePanel").classList.add("hidden");
  $("settings").classList.remove("hidden");
};

$("resetSettings").onclick = () => {
  config = {...defaults};
  for (const key of Object.keys(defaults)) $(key).value = config[key];
  updateAccent();
  try { localStorage.setItem("snakeSettings", JSON.stringify(config)); } catch(e) {}
};

$("randomize").onclick = () => {
  const choices = {
    mode: ["classic","wrap","walls","peaceful"],
    speed: ["slow","normal","fast"],
    board: ["16","24","32"],
    foodCount: ["1","3","5"],
    snakeColor: ["#65e6a6","#54a0ff","#c084fc","#ff647c","#ffd166","rainbow"],
    fruit: ["🍎","🍌","🍒","🍊","🍇","🍍","🍓","⭐"],
    theme: ["dark","forest","ocean","sunset","snow","light"]
  };
  for (const [key, values] of Object.entries(choices)) {
    $(key).value = values[Math.floor(Math.random()*values.length)];
  }
  readSettings();
};

["snakeColor","customColor","theme"].forEach(id => {
  $(id).addEventListener("change", () => {
    readSettings();
    if (state === "playing" || state === "paused") draw();
  });
});

document.addEventListener("keydown", e => {
  const key = e.key.toLowerCase();
  const map = {
    arrowup:"up", w:"up", arrowdown:"down", s:"down",
    arrowleft:"left", a:"left", arrowright:"right", d:"right"
  };
  if (map[key]) { e.preventDefault(); changeDirection(map[key]); }
  if (key === " ") { e.preventDefault(); pauseGame(); }
  if (key === "enter" && state === "over") newGame();
});

loadSettings();
fetchLeaderboard();
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/api/scores", methods=["GET"])
def get_scores():
    scores = load_scores()
    scores.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(scores[:10])


@app.route("/api/scores", methods=["POST"])
def post_score():
    data = request.get_json() or {}
    name = (data.get("name") or "Anonymous").strip()[:16]
    score = int(data.get("score", 0))

    scores = load_scores()
    scores.append({
        "name": name,
        "score": score,
        "badge": get_badge(score)
    })
    scores.sort(key=lambda x: x["score"], reverse=True)
    save_scores(scores[:50])

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)