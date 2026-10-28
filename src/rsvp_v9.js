/* ==========================================================
   RSVP: buscador de grupos + confirmación por persona.
   - Con CONFIG.rsvp.endpoint: POST JSON {action:'search'|'unlock'|'confirm', ...}
     (contrato en docs/rsvp-api.md).
   - Sin endpoint y con CONFIG.rsvp.demo: vista previa con DEMO_GROUPS
     (respuestas guardadas solo en este navegador).
   - Sin endpoint y sin demo: muestra "abrirá pronto" (nunca acepta respuestas falsas).
   ========================================================== */
(function(){
var box=document.getElementById('rsvp-box');if(!box)return;
var RC=CONFIG.rsvp||{},EP=RC.endpoint||'',DEMO=!EP&&!!RC.demo;
var CLOSED=RC.deadline?new Date()>new Date(RC.deadline+'T23:59:59-04:00'):false;
var DEMO_GROUPS=[
  {id:'g1',members:[{name:'Juan Pérez'},{name:'Gabriela Fernández'}]},
  {id:'g2',members:[{name:'Arturo Valle'},{name:'Carolina Mejía'},{name:'Sofía Valle'}]},
  {id:'g3',members:[{name:'María Rodríguez'},{name:'',plus:true}]},
  {id:'g4',members:[{name:'Luis Santana'},{name:'Ana Díaz'},{name:'Pedro Santana'},{name:'Lucía Santana'}]}
];
function label(g,names){var n=g.members.map(function(m,i){return (names&&names[i])||m.name||t('plusTag').toLowerCase()});
  return n.length<2?(n[0]||''):n.slice(0,-1).join(', ')+(isEn?' and ':' y ')+n[n.length-1]}
var T={
 es:{ph:'Primer nombre y primer apellido',go:'Buscar',lbl:'Nombre o apellido',min:'Escribe al menos 3 letras.',busy:'Buscando…',
  none:'No encontramos ese nombre. Prueba solo con tu primer nombre y primer apellido, o escríbenos por WhatsApp.',err:'No pudimos conectar. Inténtalo de nuevo en un momento.',
  found:function(n){return n==1?'Encontramos 1 grupo. Elígelo para continuar:':'Encontramos '+n+' grupos. Elige el tuyo:'},
  seats:function(n){return n==1?'1 lugar reservado':n+' lugares reservados'},conf:'Confirmado',
  kick:'Reserva',guest:'Invitado',yes:'Asistirá',no:'No asistirá',plusName:'Nombre del acompañante',plusPh:'Nombre y apellido',plusTag:'Acompañante',
  email:'Correo electrónico',emailHelp:'Te enviaremos aquí la confirmación de tu cupo.',confirm:'Confirmar',saving:'Enviando…',back:'Buscar otro grupo',
  needAll:'Indica si asistirá cada persona.',needEmail:'Escribe un correo válido.',needName:'Escribe el nombre del acompañante.',
  thanks:'¡Gracias!',done:'Hemos confirmado tu cupo.',thanksNo:'Gracias por avisarnos',doneNo:'¡Te vamos a extrañar!',rate:'Hiciste muchos intentos seguidos. Espera unos minutos e inténtalo de nuevo.',many:'Hay varios invitados con ese nombre. Escribe tu nombre y apellido.',mailFail:'Tu respuesta quedó guardada, pero no pudimos enviar el correo. Revisa que tu correo esté bien escrito.',mailed:function(e){return 'Te enviamos la confirmación a '+e+'.'},
  change:'Modificar respuesta',
  lockTitle:'Este grupo ya confirmó',lockText:'Para modificar la respuesta, escribe el correo que usaste al confirmar.',unlock:'Continuar',badEmail:'Ese correo no coincide con el de la confirmación.',
  soon:'La confirmación de asistencia abrirá pronto.',closed:'La confirmación de asistencia ya cerró. Si necesitas confirmar o hacer algún cambio, escríbenos por WhatsApp.'},
 en:{ph:'First name and last name',go:'Search',lbl:'First or last name',min:'Type at least 3 letters.',busy:'Searching…',
  none:'We couldn\'t find that name. Try just your first name and last name, or message us on WhatsApp.',err:'We couldn\'t connect. Please try again in a moment.',
  found:function(n){return n==1?'We found 1 group. Select it to continue:':'We found '+n+' groups. Select yours:'},
  seats:function(n){return n==1?'1 seat reserved':n+' seats reserved'},conf:'Confirmed',
  kick:'Reservation',guest:'Guest',yes:'Attending',no:'Not attending',plusName:'Guest\'s name',plusPh:'First and last name',plusTag:'Plus one',
  email:'Email',emailHelp:'We\'ll send your seat confirmation here.',confirm:'Confirm',saving:'Sending…',back:'Search another group',
  needAll:'Please tell us if each person is attending.',needEmail:'Please enter a valid email.',needName:'Please enter your guest\'s name.',
  thanks:'Thank you!',done:'Your seats are confirmed.',thanksNo:'Thank you for letting us know',doneNo:"We'll miss you!",rate:'Too many attempts. Please wait a few minutes and try again.',many:'Several guests match that name. Please type your first and last name.',mailFail:"Your response was saved, but we couldn't send the email. Please check your email address.",mailed:function(e){return 'We sent the confirmation to '+e+'.'},
  change:'Change response',
  lockTitle:'This group has already confirmed',lockText:'To change the response, enter the email you used when confirming.',unlock:'Continue',badEmail:'That email doesn\'t match the confirmation.',
  soon:'RSVP will open soon.',closed:'RSVP is now closed. If you need to confirm or make a change, please message us on WhatsApp.'}
};
function t(k,a){var v=T[isEn?'en':'es'][k];return typeof v==='function'?v(a):v}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function norm(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim()}
function validEmail(e){return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e)}

/* ---- "backend" de vista previa (se reemplaza por el endpoint real) ---- */
var store={};try{store=JSON.parse(localStorage.getItem('rsvp-demo')||'{}')}catch(e){}
function persist(){try{localStorage.setItem('rsvp-demo',JSON.stringify(store))}catch(e){}}
function demo(a,p){
  if(a==='search'){var q=norm(p.q).split(' ').filter(Boolean);
    return{groups:DEMO_GROUPS.filter(function(g){var h=norm(g.members.map(function(m){return m.name}).join(' ')).split(' ');return q.every(function(w){return h.some(function(x){return x.indexOf(w)===0})})})
      .map(function(g){return{id:g.id,members:g.members,confirmed:!!store[g.id]}})}}
  if(a==='unlock'){var c=store[p.id];if(c&&norm(c.email)===norm(p.email))return{ok:true,response:c};return{ok:false}}
  if(a==='confirm'){var cur=store[p.id];if(cur&&norm(cur.email)!==norm(p.email))return{ok:false,error:'locked'};
    store[p.id]={email:p.email,answers:p.answers};persist();return{ok:true}}
  return{ok:false}
}
function api(a,p){
  if(EP)return fetch(EP,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({action:a},p))}).then(function(r){if(r.status===429)return{ok:false,error:'rate'};if(!r.ok)throw new Error('http');return r.json()});
  return new Promise(function(res){setTimeout(function(){res(demo(a,p))},350)});
}

/* ---- estado y vistas ---- */
var S={view:'search',q:'',groups:null,msg:'',err:false,group:null,ans:[],names:[],email:'',lockMsg:''};
function focusSoon(sel){setTimeout(function(){var e=box.querySelector(sel);if(e)e.focus({preventScroll:true})},30)}

function renderSearch(){
  if(!EP&&!DEMO||CLOSED){
    var wa=(CONFIG.wa.help||'').replace(/\D/g,''),m=WAMSG.help[isEn?'en':'es'];
    box.innerHTML='<div class="rs-lock"><p class="rs-hint">'+esc(t(CLOSED?'closed':'soon'))+'</p>'
      +(CLOSED&&wa?'<div class="rs-actions"><a class="btn solid" target="_blank" rel="noopener" href="https://wa.me/'+wa+'?text='+encodeURIComponent(m)+'">WhatsApp</a></div>':'')+'</div>';
    var sub=document.getElementById('rs-sub');if(sub)sub.style.display='none';return}
  var h='';
  h+='<form class="rs-search" id="rs-form" role="search"><label class="sr" for="rs-q">'+esc(t('lbl'))+'</label>'
    +'<input id="rs-q" type="search" autocomplete="off" enterkeyhint="search" placeholder="'+esc(t('ph'))+'" value="'+esc(S.q)+'">'
    +'<button class="btn solid" type="submit">'+esc(t('go'))+'</button></form>';
  h+='<p class="rs-hint'+(S.err?' err':'')+'" id="rs-msg">'+esc(S.msg)+'</p><div class="rs-results">';
  (S.groups||[]).forEach(function(g,i){
    h+='<button type="button" class="rs-group" data-i="'+i+'"><strong>'+esc(label(g))+(g.confirmed?'<em>'+esc(t('conf'))+'</em>':'')+'</strong><span>'
      +esc(t('seats',g.members.length))+'</span></button>';
  });
  box.innerHTML=h+'</div>';
}
function renderLock(){
  var g=S.group;
  box.innerHTML='<div class="rs-card"><div class="top"><div class="kick">'+esc(t('kick'))+'</div><h3>'+esc(label(g))+'</h3></div>'
   +'<form class="rs-lock" id="rs-lock"><p><strong>'+esc(t('lockTitle'))+'</strong></p><p>'+esc(t('lockText'))+'</p>'
   +'<div class="rs-field"><label class="sr" for="rs-le">'+esc(t('email'))+'</label><input id="rs-le" type="email" autocomplete="email" placeholder="nombre@correo.com"></div>'
   +'<p class="rs-hint err" id="rs-lm">'+esc(S.lockMsg)+'</p>'
   +'<div class="rs-actions"><button class="btn solid" type="submit">'+esc(t('unlock'))+'</button><button class="btn" type="button" data-act="back">'+esc(t('back'))+'</button></div></form></div>';
  focusSoon('#rs-le');
}
function renderForm(){
  var g=S.group,n=g.members.length,h='<form class="rs-card" id="rs-conf" novalidate><div class="top"><div class="kick">'+esc(t('kick'))+'</div><h3>'+esc(label(g))+'</h3><div class="seats">'+esc(t('seats',n))+'</div></div><ul class="rs-members">';
  g.members.forEach(function(m,i){
    var a=S.ans[i];
    h+='<li class="rs-member"><span class="rs-num" aria-hidden="true">'+(i+1)+'</span><div class="rs-name">';
    if(m.plus){h+='<small>'+esc(t('plusName'))+'</small><input type="text" data-name="'+i+'" autocomplete="off" placeholder="'+esc(t('plusPh'))+'" value="'+esc(S.names[i])+'">'}
    else{h+='<small>'+esc(t('guest'))+' '+(i+1)+'</small>'+esc(m.name)}
    h+='</div><div class="seg" role="radiogroup" aria-label="'+esc(m.name||t('plusTag'))+'">'
      +'<input type="radio" id="a'+i+'y" name="a'+i+'" value="yes"'+(a===true?' checked':'')+'><label for="a'+i+'y">'+esc(t('yes'))+'</label>'
      +'<input class="no" type="radio" id="a'+i+'n" name="a'+i+'" value="no"'+(a===false?' checked':'')+'><label for="a'+i+'n">'+esc(t('no'))+'</label></div></li>';
  });
  h+='</ul><div class="rs-field"><label for="rs-email">'+esc(t('email'))+'</label><input id="rs-email" type="email" autocomplete="email" inputmode="email" placeholder="nombre@correo.com" value="'+esc(S.email)+'"><small>'+esc(t('emailHelp'))+'</small></div>'
   +'<input class="rs-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
   +'<p class="rs-hint err" id="rs-fm" role="alert"></p>'
   +'<div class="rs-actions"><button class="btn solid" type="submit" id="rs-send">'+esc(t('confirm'))+'</button><button class="btn" type="button" data-act="back">'+esc(t('back'))+'</button></div></form>';
  box.innerHTML=h;
}
function renderDone(){
  var g=S.group,any=S.ans.some(function(a){return a===true});
  var h='<div class="rs-card rs-done"><svg class="bq-big" viewBox="0 0 303 319" aria-hidden="true"><use href="#spray"/></svg><h3>'+esc(t(any?'thanks':'thanksNo'))+'</h3><p class="seats">'+esc(t(any?'done':'doneNo'))+'</p><ul class="sum">';
  g.members.forEach(function(m,i){var nm=m.plus?(S.names[i]||t('plusTag')):m.name,y=S.ans[i]===true;
    h+='<li><span>'+esc(nm)+'</span><b class="'+(y?'':'no')+'">'+esc(t(y?'yes':'no'))+'</b></li>'});
  h+='</ul><p class="rs-mail">'+esc(S.mailed===false?t('mailFail'):t('mailed',S.email))+'</p>'
   +'<div class="rs-actions"><button class="btn" type="button" data-act="edit">'+esc(t('change'))+'</button><button class="btn" type="button" data-act="back">'+esc(t('back'))+'</button></div></div>';
  box.innerHTML=h;
}
function render(){
  var sub=document.getElementById('rs-sub');if(sub)sub.style.display=S.view==='search'?'':'none';
  if(S.view==='search'){renderSearch()}else if(S.view==='lock'){renderLock()}else if(S.view==='form'){renderForm()}else{renderDone()}
}
window.rsvpRender=function(){
  /* conserva lo escrito al cambiar de idioma */
  var q=document.getElementById('rs-q');if(q)S.q=q.value;
  var em=document.getElementById('rs-email');if(em)S.email=em.value;
  render();
};

function openGroup(g){
  S.group=g;S.names=g.members.map(function(m){return m.name||''});S.ans=g.members.map(function(){return null});S.email='';S.lockMsg='';
  if(g.confirmed){S.view='lock'}else{S.view='form'}
  render();if(S.view==='form')focusSoon('.seg input');
  box.scrollIntoView({behavior:'smooth',block:'start'});
}
function backToSearch(){S.view='search';S.group=null;S.msg='';S.err=false;render();focusSoon('#rs-q')}

box.addEventListener('submit',function(e){
  e.preventDefault();
  var f=e.target;
  if(f.id==='rs-form'){
    var q=document.getElementById('rs-q').value.trim();S.q=q;
    if(norm(q).replace(/ /g,'').length<3){S.msg=t('min');S.err=true;S.groups=null;render();focusSoon('#rs-q');return}
    S.msg=t('busy');S.err=false;document.getElementById('rs-msg').textContent=S.msg;
    api('search',{q:q}).then(function(r){
      if(r&&r.error==='rate'){S.groups=null;S.err=true;S.msg=t('rate');render();return}
      if(r&&r.error==='many'){S.groups=null;S.err=true;S.msg=t('many');render();focusSoon('#rs-q');return}
      S.groups=(r&&r.groups)||[];S.err=!S.groups.length;S.msg=S.groups.length?t('found',S.groups.length):t('none');render();
    }).catch(function(){S.groups=null;S.err=true;S.msg=t('err');render()});
  }else if(f.id==='rs-lock'){
    var le=document.getElementById('rs-le').value.trim();
    api('unlock',{id:S.group.id,email:le}).then(function(r){
      if(r&&r.ok){var resp=r.response||{answers:[]};S.email=le;
        var left=(resp.answers||[]).slice(),al=S.group.members.map(function(m){for(var k=0;k<left.length;k++){var x=left[k];if(x&&(m.plus?x.plus:(!x.plus&&norm(x.name)===norm(m.name))))return left.splice(k,1)[0]}return null});
        S.ans=al.map(function(a){return a?a.attending:null});
        S.names=S.group.members.map(function(m,i){return(al[i]&&al[i].name)||m.name||''});
        S.view='form';render();focusSoon('.seg input')}
      else{S.lockMsg=t(r&&r.error==='rate'?'rate':'badEmail');document.getElementById('rs-lm').textContent=S.lockMsg}
    }).catch(function(){S.lockMsg=t('err');document.getElementById('rs-lm').textContent=S.lockMsg});
  }else if(f.id==='rs-conf'){
    if(f.website&&f.website.value)return; /* trampa para bots */
    var g=S.group,answers=[],fm=document.getElementById('rs-fm'),ok=true;
    g.members.forEach(function(m,i){
      var chk=f.querySelector('input[name="a'+i+'"]:checked');S.ans[i]=chk?chk.value==='yes':null;
      var ni=f.querySelector('input[data-name="'+i+'"]');if(ni)S.names[i]=ni.value.trim();
    });
    S.email=document.getElementById('rs-email').value.trim();
    if(S.ans.some(function(a){return a===null})){fm.textContent=t('needAll');return}
    for(var i=0;i<g.members.length;i++){if(g.members[i].plus&&S.ans[i]&&!S.names[i]){fm.textContent=t('needName');var x=f.querySelector('input[data-name="'+i+'"]');if(x)x.focus();return}}
    if(!validEmail(S.email)){fm.textContent=t('needEmail');document.getElementById('rs-email').focus();return}
    fm.textContent='';
    g.members.forEach(function(m,i){answers.push({name:m.plus?S.names[i]:m.name,attending:S.ans[i]})});
    var btn=document.getElementById('rs-send');btn.disabled=true;btn.textContent=t('saving');
    api('confirm',{id:g.id,email:S.email,answers:answers,lang:isEn?'en':'es',website:f.website?f.website.value:''}).then(function(r){
      if(r&&r.ok){S.mailed=r.mailed!==false;S.view='done';render();box.scrollIntoView({behavior:'smooth',block:'start'})}
      else{btn.disabled=false;btn.textContent=t('confirm');fm.textContent=t(r&&r.error==='closed'?'closed':r&&r.error==='locked'?'badEmail':r&&r.error==='rate'?'rate':'err')}
    }).catch(function(){btn.disabled=false;btn.textContent=t('confirm');fm.textContent=t('err')});
  }
});
box.addEventListener('click',function(e){
  var gb=e.target.closest('.rs-group');if(gb){openGroup(S.groups[+gb.getAttribute('data-i')]);return}
  var a=e.target.closest('[data-act]');if(!a)return;
  var act=a.getAttribute('data-act');
  if(act==='back')backToSearch();
  if(act==='edit'){S.view='form';render();focusSoon('.seg input')}
});
render();
})();

