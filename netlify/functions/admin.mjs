// API del panel privado: entrar, leer datos y cargar la lista de invitados.
import crypto from 'node:crypto';
import { json, clientIp, norm, limited, listDocs, commit, groups, dropGroupsCache, signAdmin, checkAdmin, samePassword } from '../lib/core.mjs';

export const config = { path: '/api/admin' };

// Id estable por grupo: depende del primer nombre del grupo, así recargar la lista no pierde respuestas.
const gid = (members, seen) => {
  const key = norm((members.find(m => !m.plus) || {}).name || 'grupo');
  let id = 'g_' + crypto.createHash('sha1').update(key).digest('hex').slice(0, 10), k = 2;
  while (seen.has(id)) id = id.replace(/(_\d+)?$/, '_' + k++);
  seen.add(id); return id;
};

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
      // p.groups: [{ members:[{name, plus}], rows:[{...columnas originales}] }], p.columns: [...]
      if (!Array.isArray(p.groups) || !p.groups.length || p.groups.length > 1000) return json({ ok: false, error: 'invalid' });
      const seen = new Set(), now = new Date();
      const docs = p.groups.map((g, i) => {
        const members = (g.members || []).slice(0, 20).map(m => ({ name: String(m.name || '').trim().slice(0, 80), plus: !!m.plus }));
        return { id: gid(members, seen), data: { order: i, members, rows: (g.rows || []).slice(0, 20), updatedAt: now } };
      }).filter(d => d.data.members.length);
      const old = await listDocs('groups');
      const keep = new Set(docs.map(d => d.id));
      const ops = docs.map(d => ({ set: { col: 'groups', id: d.id, data: d.data } }))
        .concat(old.filter(o => !keep.has(o.id)).map(o => ({ del: { col: 'groups', id: o.id } })))
        .concat([{ set: { col: 'meta', id: 'list', data: { columns: (p.columns || []).slice(0, 40), uploadedAt: now, count: docs.length } } }]);
      await commit(ops); dropGroupsCache();
      return json({ ok: true, groups: docs.length, removed: old.filter(o => !keep.has(o.id)).length });
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
