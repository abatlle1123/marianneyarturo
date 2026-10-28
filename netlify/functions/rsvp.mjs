// API pública del RSVP: buscar grupo, desbloquear (grupo ya confirmado) y confirmar.
import { EVENT, json, clientIp, norm, validEmail, limited, isClosed, groups, getDoc, setDoc, sendMail } from '../lib/core.mjs';
import { guestEmail } from '../lib/emails.mjs';

export const config = { path: '/api/rsvp' };

const publicGroup = (g, done) => ({ id: g.id, members: g.members.map(m => m.plus ? { name: '', plus: true } : { name: m.name }), confirmed: !!done });

export default async (req) => {
  if (req.method !== 'POST') return json({ ok: false, error: 'method' }, 405);
  let p; try { p = await req.json(); } catch { return json({ ok: false, error: 'invalid' }, 400); }
  const ip = clientIp(req);
  try {
    if (p.action === 'search') {
      if (limited('s:' + ip, 20, 10 * 60e3)) return json({ ok: false, error: 'rate' }, 429);
      const words = norm(p.q).split(' ').filter(Boolean);
      if (words.join('').length < 3) return json({ groups: [], error: 'short' });
      const all = await groups();
      const hits = all.filter(g => {
        const toks = norm(g.members.map(m => m.name).join(' ')).split(' ');
        return words.every(w => toks.some(t => t.startsWith(w)));
      });
      if (hits.length > 8) return json({ groups: [], error: 'many' });
      const done = await Promise.all(hits.map(g => getDoc('responses', g.id)));
      return json({ groups: hits.map((g, i) => publicGroup(g, done[i] && done[i].email)) });
    }

    if (p.action === 'unlock') {
      if (limited('u:' + ip, 5, 10 * 60e3)) return json({ ok: false, error: 'rate' }, 429);
      const r = await getDoc('responses', String(p.id || ''));
      if (r && norm(r.email) === norm(p.email)) return json({ ok: true, response: { answers: r.answers } });
      return json({ ok: false });
    }

    if (p.action === 'confirm') {
      if (limited('c:' + ip, 10, 10 * 60e3)) return json({ ok: false, error: 'rate' }, 429);
      if (p.website) return json({ ok: true });                           // bot: se ignora
      if (isClosed()) return json({ ok: false, error: 'closed' });
      const id = String(p.id || ''), email = String(p.email || '').trim().slice(0, 200);
      if (!validEmail(email)) return json({ ok: false, error: 'invalid' });
      const g = (await groups(true)).find(x => x.id === id);
      if (!g || !Array.isArray(p.answers) || p.answers.length !== g.members.length) return json({ ok: false, error: 'invalid' });
      const answers = [];
      for (let i = 0; i < g.members.length; i++) {
        const m = g.members[i], a = p.answers[i] || {};
        if (typeof a.attending !== 'boolean') return json({ ok: false, error: 'invalid' });
        let name = m.name;
        if (m.plus) {
          name = String(a.name || '').replace(/\s+/g, ' ').trim().slice(0, 80);
          if (a.attending && name.length < 2) return json({ ok: false, error: 'invalid' });
        }
        answers.push({ name, attending: a.attending, plus: !!m.plus });
      }
      const prev = await getDoc('responses', id);
      if (prev && prev.email && norm(prev.email) !== norm(email)) return json({ ok: false, error: 'locked' });
      const now = new Date();
      const history = prev ? [...(prev.history || []), { answers: prev.answers, email: prev.email, at: prev.updatedAt, by: prev.lastBy || 'invitado' }].slice(-20) : [];
      const lang = p.lang === 'en' ? 'en' : 'es';
      await setDoc('responses', id, { email, lang, answers, createdAt: prev ? prev.createdAt : now, updatedAt: now, history, edited: !!prev, lastBy: 'invitado' });
      let mailed = true;
      try { await sendMail(guestEmail({ members: g.members, answers, email, lang })); }
      catch (e) { mailed = false; console.error('correo', e.message); }
      return json({ ok: true, mailed });
    }
    return json({ ok: false, error: 'invalid' }, 400);
  } catch (e) {
    console.error(e);
    return json({ ok: false, error: 'server' }, 500);
  }
};
