#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = process.env.PORT || 4060;
const PUBLIC_DIR = path.join(__dirname, 'public');
const CASHCLAW_DIR = path.join(os.homedir(), '.cashclaw');
const MISSIONS_DIR = path.join(CASHCLAW_DIR, 'missions');
const EARNINGS_FILE = path.join(CASHCLAW_DIR, 'earnings.jsonl');

function readJsonSafe(p, fallback = null) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return fallback; }
}

function readMissions() {
  if (!fs.existsSync(MISSIONS_DIR)) return [];
  return fs.readdirSync(MISSIONS_DIR)
    .filter((f) => f.endsWith('.json'))
    .map((f) => readJsonSafe(path.join(MISSIONS_DIR, f), null))
    .filter(Boolean);
}

function readEarnings() {
  if (!fs.existsSync(EARNINGS_FILE)) return [];
  return fs.readFileSync(EARNINGS_FILE, 'utf8')
    .split('\n').map((x) => x.trim()).filter(Boolean)
    .map((line) => { try { return JSON.parse(line); } catch { return null; } })
    .filter(Boolean);
}

function getMetrics() {
  const missions = readMissions();
  const earnings = readEarnings();
  const count = (s) => missions.filter((m) => m.status === s).length;
  return {
    generatedAt: new Date().toISOString(),
    summary: {
      totalMissions: missions.length,
      appliedMissions: count('created'),
      inProgressMissions: count('in_progress'),
      completedMissions: count('completed'),
      cancelledMissions: count('cancelled'),
      unpaidMissions: missions.filter((m) => m.payment?.status === 'unpaid').length,
      paidMissions: missions.filter((m) => m.payment?.status === 'paid').length,
      totalValueUsd: missions.reduce((s, m) => s + Number(m.price_usd || 0), 0),
      totalEarnedUsd: earnings.reduce((s, e) => s + Number(e.amount || 0), 0)
    },
    missions: missions
      .sort((a, b) => new Date(b.updated_at || b.created_at || 0) - new Date(a.updated_at || a.created_at || 0))
      .slice(0, 100)
      .map((m) => ({
        id: m.id,
        name: m.name,
        status: m.status,
        service: m.service_type,
        tier: m.tier,
        priceUsd: Number(m.price_usd || 0),
        client: m.client?.name || '',
        payment: m.payment?.status || 'unknown',
        updatedAt: m.updated_at || m.created_at
      }))
  };
}

function sendJson(res, obj) {
  res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(obj));
}

function serveStatic(req, res) {
  const file = req.url === '/' ? '/index.html' : req.url;
  const p = path.normalize(path.join(PUBLIC_DIR, file));
  if (!p.startsWith(PUBLIC_DIR) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) {
    res.writeHead(404); res.end('Not found'); return;
  }
  const type = p.endsWith('.html') ? 'text/html' : p.endsWith('.js') ? 'application/javascript' : 'text/plain';
  res.writeHead(200, { 'Content-Type': type });
  fs.createReadStream(p).pipe(res);
}

http.createServer((req, res) => {
  if (req.url === '/api/metrics') return sendJson(res, getMetrics());
  return serveStatic(req, res);
}).listen(PORT, () => {
  console.log(`CashClaw live site running on http://localhost:${PORT}`);
});
