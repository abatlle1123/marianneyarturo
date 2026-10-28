// Plantillas de correo. Tablas y estilos en línea para que se vean igual en Gmail, Outlook y Apple Mail.
import { EVENT, esc, groupLabel, alignAnswers } from './core.mjs';

const C = { bg: '#f3f1ed', card: '#fbfaf7', ink: '#3d4636', deep: '#3f4b36', olive: '#56654b', muted: '#6c7563', line: '#d9dccf', no: '#8f8478' };
const serif = "'Cormorant Garamond',Georgia,'Times New Roman',serif";
const sans = "'Helvetica Neue',Helvetica,Arial,sans-serif";

const GCAL = 'https://calendar.google.com/calendar/render?action=TEMPLATE'
  + '&text=' + encodeURIComponent('Boda de Marianne y Arturo')
  + '&dates=20270305T223000Z/20270306T050000Z'
  + '&details=' + encodeURIComponent('Ceremonia 6:30 pm · Iglesia y Convento Regina Angelorum\nRecepción 9:00 pm · Santo Domingo Country Club, Country Garden\nhttps://marianneyarturo.com')
  + '&location=' + encodeURIComponent('Iglesia y Convento Regina Angelorum, Zona Colonial, Santo Domingo');
const ICS = EVENT.site + '/boda.ics';

const T = {
  es: {
    subject: '[RSVP Boda] Gracias por confirmar · Marianne y Arturo',
    hi: n => `¡Gracias, ${n}!`, hiNo: n => `Gracias por avisarnos, ${n}`,
    got: g => `Recibimos la confirmación de <b>${g}</b>:`, miss: '¡Te vamos a extrañar!',
    yes: 'Asistirá', no: 'No asistirá',
    det: ['Ceremonia', '6:30 pm', 'Iglesia y Convento Regina Angelorum, Zona Colonial', 'Recepción', '9:00 pm', 'Santo Domingo Country Club · Country Garden', 'Vestimenta', 'Formal garden attire / Chacabana'],
    site: 'Ver la página', cal: 'Agregar al calendario', ics: 'Apple / Outlook (.ics)',
    change: 'Si necesitas cambiar algo, hazlo en marianneyarturo.com/rsvp con este mismo correo, hasta el 5 de febrero.',
    q: '¿Dudas? Escríbenos por WhatsApp: 829-880-8857.',
  },
  en: {
    subject: '[RSVP Boda] Thank you for confirming · Marianne & Arturo',
    hi: n => `Thank you, ${n}!`, hiNo: n => `Thank you for letting us know, ${n}`,
    got: g => `We received the RSVP for <b>${g}</b>:`, miss: "We'll miss you!",
    yes: 'Attending', no: 'Not attending',
    det: ['Ceremony', '6:30 pm', 'Regina Angelorum Church & Convent, Colonial Zone', 'Reception', '9:00 pm', 'Santo Domingo Country Club · Country Garden', 'Dress code', 'Formal garden attire / Chacabana'],
    site: 'Visit the website', cal: 'Add to calendar', ics: 'Apple / Outlook (.ics)',
    change: 'Need to change something? Do it at marianneyarturo.com/rsvp with this same email, until February 5.',
    q: 'Questions? Message us on WhatsApp: +1 829-880-8857.',
  },
};

const btn = (href, label, solid) => `<a href="${href}" style="display:inline-block;margin:6px 4px 0;padding:11px 20px;border:1px solid ${C.olive};border-radius:99px;font-family:${sans};font-size:11px;letter-spacing:2px;text-transform:uppercase;text-decoration:none;color:${solid ? C.bg : C.deep};background:${solid ? C.olive : 'transparent'}">${label}</a>`;

function shell(inner, preheader) {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light"><title>Marianne y Arturo</title></head>
<body style="margin:0;padding:0;background:${C.bg}" bgcolor="${C.bg}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${C.bg}" style="background:${C.bg};width:100%;min-height:100%"><tr><td align="center" style="padding:32px 14px 40px;background:${C.bg}" bgcolor="${C.bg}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:520px;background:${C.card};border:1px solid ${C.line}" bgcolor="${C.card}"><tr><td style="padding:10px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid ${C.line}"><tr><td align="center" style="padding:34px 26px 30px;font-family:${sans};color:${C.ink}">
<div style="font-family:${serif};font-size:34px;line-height:1.1;color:${C.deep}">Marianne <i style="color:${C.olive}">&amp;</i> Arturo</div>
<div style="font-family:${sans};font-size:10px;letter-spacing:3px;text-transform:uppercase;color:${C.muted};margin:8px 0 22px">05 · 03 · 2027 · Santo Domingo</div>
${inner}
</td></tr></table></td></tr></table>
</td></tr></table></body></html>`;
}

export function guestEmail({ members, answers, email, lang }) {
  const t = T[lang === 'en' ? 'en' : 'es'];
  const names = answers.map(a => a.name);
  const label = esc(groupLabel(members, lang, names));
  const anyYes = answers.some(a => a.attending);
  // Saludo: primeros nombres de quienes asisten (máx. 2, en el orden de la lista); si nadie asiste, los dos primeros del grupo.
  const pick = (anyYes ? answers.filter(a => a.attending) : answers).map(a => (a.name || '').trim().split(' ')[0]).filter(Boolean).slice(0, 2);
  const first = esc(pick.join(lang === 'en' ? ' and ' : ' y '));
  const rows = answers.map(a => `<tr><td style="padding:7px 0;border-bottom:1px dashed ${C.line};font-size:15px;color:${C.ink}">${esc(a.name)}</td><td align="right" style="padding:7px 0;border-bottom:1px dashed ${C.line};font-size:14px;font-weight:600;color:${a.attending ? C.olive : C.no}">${a.attending ? t.yes : t.no}</td></tr>`).join('');
  const d = t.det;
  const details = anyYes ? `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:18px 0 6px;background:${C.bg}" bgcolor="${C.bg}"><tr><td style="padding:14px 16px;font-size:14px;line-height:1.6;color:${C.ink};text-align:left">
<b style="color:${C.deep}">${d[0]}</b> · ${d[1]}<br>${d[2]}<br><br><b style="color:${C.deep}">${d[3]}</b> · ${d[4]}<br>${d[5]}<br><br><b style="color:${C.deep}">${d[6]}</b> · ${d[7]}</td></tr></table>
<div style="margin-top:14px">${btn(EVENT.site, t.site, true)}${btn(GCAL, t.cal)}</div>
<div style="margin-top:10px"><a href="${ICS}" style="font-size:12px;color:${C.olive}">${t.ics}</a></div>` : `<div style="margin-top:16px">${btn(EVENT.site, t.site, true)}</div>`;
  const inner = `<div style="font-family:${serif};font-size:28px;color:${C.deep};margin-bottom:12px">${anyYes ? t.hi(first) : t.hiNo(first)}</div>
<p style="margin:0 0 10px;font-size:15px;line-height:1.6;text-align:left">${t.got(label)}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 6px">${rows}</table>
${anyYes ? '' : `<p style="margin:14px 0 0;font-size:15px">${t.miss}</p>`}
${details}
<div style="border-top:1px solid ${C.line};width:60px;margin:24px auto 16px;font-size:0;line-height:0">&nbsp;</div>
<p style="margin:0;font-size:12px;line-height:1.6;color:${C.muted}">${t.change}<br>${t.q}</p>`;
  const text = `${anyYes ? t.hi(first) : t.hiNo(first)}\n\n${answers.map(a => `${a.name}: ${a.attending ? t.yes : t.no}`).join('\n')}\n\n${anyYes ? d.join(' · ') + '\n\n' : ''}${t.change}\n${t.q}\n${EVENT.site}`;
  return { to: email, subject: t.subject, html: shell(inner, anyYes ? t.got(groupLabel(members, lang, names)).replace(/<\/?b>/g, '') : t.miss), text };
}

export function summaryEmail({ day, changes, totals }) {
  const n = changes.length;
  const subject = `[RSVP Boda] Resumen del ${day}: ${n} ${n === 1 ? 'confirmación nueva' : 'confirmaciones nuevas'}`;
  const li = changes.map(c => {
    const yes = c.answers.filter(a => a.attending).length, tot = c.answers.length;
    const mark = c.edited ? '✎' : yes ? '✓' : '✗';
    return `<tr><td style="padding:8px 0;border-bottom:1px solid ${C.line};font-size:14px;line-height:1.5;text-align:left;color:${C.ink}">${mark} <b style="color:${C.deep}">${esc(c.label)}</b><br><span style="color:${C.muted}">${yes ? `${yes} de ${tot} asisten` : 'no asisten'}${c.edited ? ' · modificó su respuesta' : ''} · ${esc(c.email)}</span></td></tr>`;
  }).join('');
  const inner = `<div style="font-family:${serif};font-size:26px;color:${C.deep};margin-bottom:6px">Resumen del ${esc(day)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:14px 0 18px;background:${C.bg}" bgcolor="${C.bg}"><tr>
${[['Grupos confirmados', `${totals.groupsDone} / ${totals.groups}`], ['Asisten', totals.yes], ['No asisten', totals.no], ['Sin respuesta', totals.pending]].map(([k, v]) => `<td align="center" style="padding:12px 4px;font-family:${sans}"><div style="font-family:${serif};font-size:24px;color:${C.deep}">${v}</div><div style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:${C.muted}">${k}</div></td>`).join('')}
</tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">${li}</table>
<p style="margin:18px 0 0;font-size:13px;color:${C.muted}">Faltan ${totals.daysLeft} días para el cierre del RSVP (5 de febrero).</p>
<div style="margin-top:14px">${btn(EVENT.site + '/panel/', 'Abrir el panel', true)}</div>`;
  const text = `Resumen del ${day}\nGrupos confirmados: ${totals.groupsDone}/${totals.groups} · Asisten: ${totals.yes} · No asisten: ${totals.no} · Sin respuesta: ${totals.pending}\n\n` + changes.map(c => `- ${c.label}: ${c.answers.filter(a => a.attending).length} de ${c.answers.length} asisten (${c.email})`).join('\n');
  return { to: EVENT.notify, subject, html: shell(inner, `${n} confirmaciones nuevas`), text, from: EVENT.fromAdmin };
}

export function totalsOf(groups, responses) {
  const R = new Map(responses.map(r => [r.id, r]));
  let yes = 0, no = 0, pending = 0, groupsDone = 0;
  for (const g of groups) {
    const r = R.get(g.id);
    if (r) { groupsDone++; alignAnswers(g.members, r.answers).forEach(a => a ? (a.attending ? yes++ : no++) : pending++); }
    else pending += g.members.length;
  }
  const daysLeft = Math.max(0, Math.ceil((new Date(EVENT.deadline) - Date.now()) / 864e5));
  return { groups: groups.length, groupsDone, yes, no, pending, daysLeft };
}
