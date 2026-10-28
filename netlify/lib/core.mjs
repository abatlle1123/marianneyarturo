// Utilidades compartidas: Firestore (REST con cuenta de servicio, sin dependencias), Resend y helpers.
import crypto from 'node:crypto';

export const EVENT = {
  deadline: '2027-02-05T23:59:59-04:00',       // cierre del RSVP (hora RD)
  site: 'https://marianneyarturo.com',
  from: 'Marianne y Arturo <rsvp@marianneyarturo.com>',
  fromAdmin: 'RSVP Boda <rsvp@marianneyarturo.com>',
  replyTo: 'arturobatllem@outlook.com',
  notify: 'arturobatllem@outlook.com',
  whatsapp: '18298808857',
};
export const isClosed = () => Date.now() > new Date(EVENT.deadline).getTime();

// ---------- respuestas HTTP ----------
export const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
export const clientIp = req => req.headers.get('x-nf-client-connection-ip') || req.headers.get('x-forwarded-for') || 'ip';

// ---------- texto ----------
export const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[^a-z0-9@._+ -]/g, ' ').replace(/\s+/g, ' ').trim();
export const validEmail = e => /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/.test(e || '');
export const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ---------- límite de intentos (en memoria, por instancia) ----------
const buckets = new Map();
export function limited(key, max, windowMs) {
  const now = Date.now(); const b = buckets.get(key) || [];
  const recent = b.filter(t => now - t < windowMs);
  if (recent.length >= max) { buckets.set(key, recent); return true; }
  recent.push(now); buckets.set(key, recent);
  if (buckets.size > 5000) buckets.clear();
  return false;
}

// ---------- Firestore REST ----------
let SA = null, TOKEN = null;
function sa() {
  if (!SA) {
    const raw = process.env.FIREBASE_SERVICE_ACCOUNT;
    if (!raw) throw new Error('Falta FIREBASE_SERVICE_ACCOUNT');
    SA = JSON.parse(raw);
  }
  return SA;
}
const b64u = b => Buffer.from(b).toString('base64').replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
async function token() {
  if (TOKEN && TOKEN.exp > Date.now() + 60000) return TOKEN.v;
  const s = sa(), now = Math.floor(Date.now() / 1000);
  const unsigned = b64u(JSON.stringify({ alg: 'RS256', typ: 'JWT' })) + '.' + b64u(JSON.stringify({
    iss: s.client_email, scope: 'https://www.googleapis.com/auth/datastore',
    aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600 }));
  const sig = crypto.createSign('RSA-SHA256').update(unsigned).sign(s.private_key);
  const r = await fetch('https://oauth2.googleapis.com/token', { method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + unsigned + '.' + b64u(sig) });
  const j = await r.json(); if (!j.access_token) throw new Error('Token de Firebase: ' + JSON.stringify(j));
  TOKEN = { v: j.access_token, exp: Date.now() + (j.expires_in || 3600) * 1000 };
  return TOKEN.v;
}
const base = () => `https://firestore.googleapis.com/v1/projects/${sa().project_id}/databases/(default)/documents`;
async function fsFetch(path, opts = {}) {
  const r = await fetch(path.startsWith('http') ? path : base() + path, { ...opts,
    headers: { authorization: 'Bearer ' + await token(), 'content-type': 'application/json', ...(opts.headers || {}) } });
  if (r.status === 404) return null;
  const j = await r.json(); if (!r.ok) throw new Error('Firestore ' + r.status + ': ' + JSON.stringify(j).slice(0, 300));
  return j;
}
function enc(v) {
  if (v === null || v === undefined) return { nullValue: null };
  if (typeof v === 'boolean') return { booleanValue: v };
  if (typeof v === 'number') return Number.isInteger(v) ? { integerValue: String(v) } : { doubleValue: v };
  if (v instanceof Date) return { timestampValue: v.toISOString() };
  if (Array.isArray(v)) return { arrayValue: { values: v.map(enc) } };
  if (typeof v === 'object') return { mapValue: { fields: Object.fromEntries(Object.entries(v).map(([k, x]) => [k, enc(x)])) } };
  return { stringValue: String(v) };
}
function dec(v) {
  if (!v) return null;
  if ('stringValue' in v) return v.stringValue;
  if ('integerValue' in v) return Number(v.integerValue);
  if ('doubleValue' in v) return v.doubleValue;
  if ('booleanValue' in v) return v.booleanValue;
  if ('timestampValue' in v) return v.timestampValue;
  if ('nullValue' in v) return null;
  if ('arrayValue' in v) return (v.arrayValue.values || []).map(dec);
  if ('mapValue' in v) return decFields(v.mapValue.fields || {});
  return null;
}
const decFields = f => Object.fromEntries(Object.entries(f || {}).map(([k, x]) => [k, dec(x)]));
const fromDoc = d => d ? { id: d.name.split('/').pop(), ...decFields(d.fields) } : null;

export async function getDoc(col, id) { return fromDoc(await fsFetch(`/${col}/${encodeURIComponent(id)}`)); }
export async function setDoc(col, id, data) {
  return fromDoc(await fsFetch(`/${col}/${encodeURIComponent(id)}`, { method: 'PATCH',
    body: JSON.stringify({ fields: Object.fromEntries(Object.entries(data).map(([k, v]) => [k, enc(v)])) }) }));
}
export async function listDocs(col) {
  const out = []; let page = '';
  do {
    const j = await fsFetch(`/${col}?pageSize=300${page ? '&pageToken=' + encodeURIComponent(page) : ''}`);
    (j && j.documents || []).forEach(d => out.push(fromDoc(d))); page = j && j.nextPageToken;
  } while (page);
  return out;
}
// Escritura en lote: [{set:{col,id,data}} | {del:{col,id}}]
export async function commit(ops) {
  const root = `projects/${sa().project_id}/databases/(default)/documents`;
  for (let i = 0; i < ops.length; i += 400) {
    const writes = ops.slice(i, i + 400).map(o => o.set
      ? { update: { name: `${root}/${o.set.col}/${o.set.id}`, fields: Object.fromEntries(Object.entries(o.set.data).map(([k, v]) => [k, enc(v)])) } }
      : { delete: `${root}/${o.del.col}/${o.del.id}` });
    await fsFetch(`https://firestore.googleapis.com/v1/${root}:commit`, { method: 'POST', body: JSON.stringify({ writes }) });
  }
}

// Caché corta de la lista de grupos (se lee mucho y cambia poco)
let GROUPS = null;
export async function groups(force) {
  if (!force && GROUPS && Date.now() - GROUPS.t < 60000) return GROUPS.v;
  const v = (await listDocs('groups')).sort((a, b) => (a.order || 0) - (b.order || 0));
  GROUPS = { t: Date.now(), v }; return v;
}
export const dropGroupsCache = () => { GROUPS = null; };

// ---------- correo (Resend) ----------
export async function sendMail({ to, subject, html, text, from = EVENT.from, replyTo = EVENT.replyTo }) {
  const key = process.env.RESEND_API_KEY; if (!key) throw new Error('Falta RESEND_API_KEY');
  const r = await fetch('https://api.resend.com/emails', { method: 'POST',
    headers: { authorization: 'Bearer ' + key, 'content-type': 'application/json' },
    body: JSON.stringify({ from, to: [].concat(to), subject, html, text, reply_to: replyTo }) });
  if (!r.ok) throw new Error('Resend ' + r.status + ': ' + (await r.text()).slice(0, 300));
  return r.json();
}

// ---------- etiquetas de grupo ----------
export function groupLabel(members, lang = 'es', names) {
  const n = members.map((m, i) => (names && names[i]) || m.name || (lang === 'en' ? 'guest' : 'acompañante'));
  if (n.length <= 1) return n[0] || '';
  return n.slice(0, -1).join(', ') + (lang === 'en' ? ' and ' : ' y ') + n[n.length - 1];
}

// ---------- token del panel ----------
export function signAdmin(hours = 12) {
  const exp = Date.now() + hours * 3600e3, body = String(exp);
  return body + '.' + crypto.createHmac('sha256', process.env.ADMIN_PASSWORD || 'x').update(body).digest('hex');
}
export function checkAdmin(req) {
  const t = (req.headers.get('authorization') || '').replace(/^Bearer /, '');
  const [body, mac] = t.split('.'); if (!body || !mac || Number(body) < Date.now()) return false;
  const good = crypto.createHmac('sha256', process.env.ADMIN_PASSWORD || 'x').update(body).digest('hex');
  return mac.length === good.length && crypto.timingSafeEqual(Buffer.from(mac), Buffer.from(good));
}
export function samePassword(p) {
  const a = Buffer.from(String(p || '')), b = Buffer.from(String(process.env.ADMIN_PASSWORD || ''));
  return b.length > 0 && a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Alinea las respuestas guardadas con los miembros actuales del grupo (por nombre; acompañantes por orden).
// Si la lista cambió después de confirmar, las personas nuevas quedan sin respuesta (pendientes).
export function alignAnswers(members, answers) {
  const left = [...(answers || [])], out = [];
  for (const m of members) {
    let i = m.plus ? left.findIndex(a => a && a.plus) : left.findIndex(a => a && !a.plus && norm(a.name) === norm(m.name));
    out.push(i >= 0 ? left.splice(i, 1)[0] : null);
  }
  return out;
}
