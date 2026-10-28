// Resumen diario a Arturo: 8:00 am hora RD (12:00 UTC). Solo se envía si hubo movimiento en las últimas 24 h.
import { groups, listDocs, sendMail, groupLabel } from '../lib/core.mjs';
import { summaryEmail, totalsOf } from '../lib/emails.mjs';

export const config = { schedule: '0 12 * * *' };

export default async () => {
  const [gs, rs] = await Promise.all([groups(true), listDocs('responses')]);
  const since = Date.now() - 24 * 3600e3;
  const G = new Map(gs.map(g => [g.id, g]));
  const changes = rs.filter(r => new Date(r.updatedAt).getTime() > since && G.has(r.id) && r.lastBy !== 'admin')
    .sort((a, b) => new Date(a.updatedAt) - new Date(b.updatedAt))
    .map(r => ({ label: groupLabel(G.get(r.id).members, 'es', r.answers.map(a => a.name)), answers: r.answers, email: r.email, edited: !!r.edited }));
  if (!changes.length) return new Response('sin cambios');
  const day = new Date(since).toLocaleDateString('es-DO', { day: 'numeric', month: 'short', timeZone: 'America/Santo_Domingo' });
  await sendMail(summaryEmail({ day, changes, totals: totalsOf(gs, rs) }));
  return new Response('enviado ' + changes.length);
};
