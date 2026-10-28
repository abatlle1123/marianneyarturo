// API del panel privado: entrar, leer datos y cargar la lista de invitados.
import crypto from 'node:crypto';
import { json, clientIp, norm, validEmail, limited, listDocs, getDoc, commit, groups, dropGroupsCache, signAdmin, checkAdmin, samePassword, alignAnswers } from '../lib/core.mjs';

export const config = { path: '/api/admin' };

// Id estable por grupo. Al recargar la lista, un grupo conserva su id (y sus respuestas)
// si comparte al menos una persona con un grupo anterior; si no, se genera uno nuevo.
const key = m => norm(m.name);
function assignIds(newGroups, oldGroups) {
  const byName = new Map(); oldGroups.forEach(o => (o.members || []).forEach(m => { if (!m.plus && m.name) byName.set(key(m), o.id); }));
  const used = new Set(), oldIds = new Set(oldGroups.map(o => o.id));
  return newGroups.map(g => {
    let id = null;
    for (const m of g.members) { const o = !m.plus && byName.get(key(m)); if (o && !used.has(o)) { id = o; break; } }
    if (!id) {
      const base = 'g_' + crypto.createHash('sha1').update(key(g.members.find(m => !m.plus) || { name: 'grupo' })).digest('hex').slice(0, 10);
      id = base; let k = 2; while (used.has(id) || oldIds.has(id)) id = base + '_' + k++;
    }
    used.add(id); return id;
  });
}
function alignRows(g, members) {
  const left = (g.members || []).map((m, i) => ({ m, row: (g.rows || [])[i] || {} }));
  return members.map(m => { const i = left.findIndex(x => x.m.plus === m.plus && (m.plus || norm(x.m.name) === norm(m.name)));
    return i >= 0 ? left.splice(i, 1)[0].row : {}; });
}
const names = g => g.members.map(m => m.plus ? 'acompañante' : m.name).join(' · ');

export default async (req) => {
  if (req.method !== 'POST') return json({ ok: false }, 405);
  let p; try { p = await req.json(); } catch { return json({ ok: false }, 400); }
  const ip = clientIp(req);
  try {
    if (p.action === 'login') {
      if (limited('l:' + ip, 6, 15 * 60e3)) return json({ ok: false, error: 'rate' }, 429);
      await new Promise(r => setTimeout(r, 400));
      if (!samePassword(p.password)) return json({ ok: false, error: 'bad' }, 401);
      return json({ ok: true, token: signAdmin() });
    }
    if (!checkAdmin(req)) return json({ ok: false, error: 'auth' }, 401);

    if (p.action === 'data') {
      const [gs, rs] = await Promise.all([groups(true), listDocs('responses')]);
      return json({ ok: true, groups: gs, responses: rs });
    }

    if (p.action === 'upload') {
      // p.groups: [{ members:[{name, plus}], rows:[{...columnas originales}] }], p.columns, p.dryRun
      if (!Array.isArray(p.groups) || !p.groups.length || p.groups.length > 1000) return json({ ok: false, error: 'invalid' });
      const now = new Date();
      const incoming = p.groups.map((g, i) => ({
        order: i, rows: (g.rows || []).slice(0, 20),
        members: (g.members || []).slice(0, 20).map(m => ({ name: String(m.name || '').replace(/\s+/g, ' ').trim().slice(0, 80), plus: !!m.plus })),
      })).filter(g => g.members.length);
      const [old, rs] = await Promise.all([listDocs('groups'), listDocs('responses')]);
      const ids = assignIds(incoming, old);
      const O = new Map(old.map(o => [o.id, o])), R = new Set(rs.map(r => r.id)), keep = new Set(ids);
      old.forEach(o => { if (o.addedBy === 'admin') keep.add(o.id); });   // los grupos agregados en el panel no se borran al recargar
      const diff = { groups: incoming.length, people: incoming.reduce((a, g) => a + g.members.length, 0), added: [], changed: [], removed: [] };
      incoming.forEach((g, i) => {
        const o = O.get(ids[i]);
        if (!o) diff.added.push(names(g));
        else if (names(o) !== names(g)) diff.changed.push({ before: names(o), after: names(g), answered: R.has(ids[i]) });
      });
      old.filter(o => !keep.has(o.id)).forEach(o => diff.removed.push({ names: names(o), answered: R.has(o.id) }));
      if (p.dryRun) return json({ ok: true, diff });
      const ops = incoming.map((g, i) => ({ set: { col: 'groups', id: ids[i], data: { ...g, updatedAt: now } } }))
        .concat(old.filter(o => !keep.has(o.id)).map(o => ({ del: { col: 'groups', id: o.id } })))
        .concat([{ set: { col: 'meta', id: 'list', data: { columns: (p.columns || []).slice(0, 40), uploadedAt: now, count: incoming.length } } }]);
      await commit(ops); dropGroupsCache();
      return json({ ok: true, diff });
    }

    // Crear o editar un grupo y, opcionalmente, su respuesta (confirmaciones por teléfono, etc.)
    if (p.action === 'saveGroup') {
      const members = (p.members || []).slice(0, 20).map(m => ({ name: String(m.name || '').replace(/\s+/g, ' ').trim().slice(0, 80), plus: !!m.plus }))
        .filter(m => m.plus || m.name);
      if (!members.length) return json({ ok: false, error: 'invalid', detail: 'El grupo necesita al menos una persona.' });
      const all = await groups(true);
      let g = p.id ? all.find(x => x.id === p.id) : null;
      if (p.id && !g) return json({ ok: false, error: 'invalid', detail: 'No se encontró el grupo.' });
      const id = g ? g.id : assignIds([{ members }], all)[0];
      const oldRows = g ? alignRows(g, members) : members.map(() => ({}));
      const now = new Date(), ops = [];
      ops.push({ set: { col: 'groups', id, data: { order: g ? g.order : (all.reduce((a, x) => Math.max(a, x.order || 0), 0) + 1), members, rows: oldRows, updatedAt: now, ...(g ? {} : { addedBy: 'admin' }) } } });
      const ans = (p.answers || []).slice(0, members.length);
      const answers = members.map((m, i) => {
        const a = ans[i] || {}; if (typeof a.attending !== 'boolean') return null;
        return { name: m.plus ? String(a.name || '').trim().slice(0, 80) || 'Acompañante' : m.name, attending: a.attending, plus: m.plus };
      }).filter(Boolean);
      const prev = await getDoc('responses', id);
      // Evita guardar encima: si el invitado respondió (o alguien cambió algo) desde que se abrió "Editar"
      if (g && (prev ? prev.updatedAt : null) !== (p.base || null)) return json({ ok: false, error: 'conflict' });
      const email = String(p.email || '').trim().slice(0, 200);
      if (email && !validEmail(email)) return json({ ok: false, error: 'invalid', detail: 'Correo no válido.' });
      if (answers.length) {
        const history = prev ? [...(prev.history || []), { answers: prev.answers, email: prev.email, at: prev.updatedAt, by: prev.lastBy || 'invitado' }].slice(-20) : [];
        ops.push({ set: { col: 'responses', id, data: { email: email || (prev && prev.email) || '', lang: (prev && prev.lang) || 'es', answers,
          createdAt: prev ? prev.createdAt : now, updatedAt: now, history, edited: !!prev, lastBy: 'admin', note: String(p.note || '').slice(0, 200) } } });
      } else if (prev) ops.push({ del: { col: 'responses', id } });
      await commit(ops); dropGroupsCache();
      return json({ ok: true, id });
    }

    if (p.action === 'deleteGroup') {
      const id = String(p.id || ''); if (!id) return json({ ok: false });
      await commit([{ del: { col: 'groups', id } }, { del: { col: 'responses', id } }]); dropGroupsCache();
      return json({ ok: true });
    }

    if (p.action === 'meta') {
      const m = (await listDocs('meta')).find(x => x.id === 'list') || null;
      return json({ ok: true, meta: m });
    }
    return json({ ok: false }, 400);
  } catch (e) {
    console.error(e);
    return json({ ok: false, error: 'server', detail: String(e.message).slice(0, 200) }, 500);
  }
};
