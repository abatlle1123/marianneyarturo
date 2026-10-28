/* ==========================================================
   CONFIGURACIÓN: aquí se pegan los enlaces y números.
   - Los botones sin enlace aparecen apagados con "pronto".
   - Números de WhatsApp: solo dígitos con código de país
     (ej. '18095551234').
   ========================================================== */
var CONFIG={
  links:{
    registryCasaCuesta:'',  // enlace de la lista en Casa Cuesta
    registryLeTavole:'',    // enlace de la lista en Le Tavole
    receptionMap:'https://www.google.com/maps/search/?api=1&query=Santo+Domingo+Country+Club'
  },
  rsvp:{
    endpoint:'/api/rsvp', // función de Netlify del RSVP
    demo:false,     // true = vista previa con invitados de ejemplo (solo en este navegador). Poner false al publicar.
    deadline:'2027-02-05' // último día para confirmar (hora de RD). Después se cierra y se muestra el WhatsApp.
  },
  wa:{
    help:'18298808857', // asistencia a invitados
    transport:'18099229999', // Seven Stars
    mk1:'',         // Zoe Marie Beauty
    mk2:'',         // Maarape - María Ramírez
    mk3:''          // Ana Gabriela Elías
  }
};
var WAMSG={
  help:{es:'Hola, tengo una consulta sobre la boda de Marianne y Arturo.',en:'Hi, I have a question about Marianne and Arturo\'s wedding.'},
  transport:{es:'Hola, quiero información sobre traslados para la boda de Marianne y Arturo (5 de marzo de 2027).',en:'Hi, I\'d like information about transportation for Marianne and Arturo\'s wedding (March 5, 2027).'},
  mk1:{es:'Hola, vengo de la página de la boda de Marianne y Arturo y quisiera información de maquillaje y peinado para el 5 de marzo de 2027.',en:'Hi, I found you through Marianne and Arturo\'s wedding page and I\'d like information about hair and makeup for March 5, 2027.'}
};
WAMSG.mk2=WAMSG.mk1;WAMSG.mk3=WAMSG.mk1;

var isEn=false;
function applyLinks(){
  document.querySelectorAll('[data-link]').forEach(function(a){
    var u=CONFIG.links[a.getAttribute('data-link')];
    if(u){a.href=u;a.target='_blank';a.rel='noopener';a.classList.remove('soon');a.removeAttribute('aria-disabled')}
    else{a.removeAttribute('href');a.classList.add('soon');a.setAttribute('aria-disabled','true')}
  });
  document.querySelectorAll('[data-wa]').forEach(function(a){
    var k=a.getAttribute('data-wa'),n=(CONFIG.wa[k]||'').replace(/\D/g,'');
    if(n){var m=(WAMSG[k]||WAMSG.help)[isEn?'en':'es'];a.href='https://wa.me/'+n+'?text='+encodeURIComponent(m);a.target='_blank';a.rel='noopener';a.classList.remove('soon');a.removeAttribute('aria-disabled')}
    else{a.removeAttribute('href');a.classList.add('soon');a.setAttribute('aria-disabled','true')}
  });
}

/* idioma ES / EN */
(function(){
  var els=document.querySelectorAll('[data-en]');
  els.forEach(function(e){e.setAttribute('data-es',e.innerHTML)});
  var btn=document.getElementById('lang');
  function set(v){
    isEn=v;
    els.forEach(function(e){e.innerHTML=e.getAttribute(isEn?'data-en':'data-es')});
    document.documentElement.lang=isEn?'en':'es';
    btn.textContent=isEn?'ES':'EN';
    try{localStorage.setItem('lang',isEn?'en':'es')}catch(x){}
    applyLinks();if(window.rsvpRender)window.rsvpRender();if(window.routeTitle)window.routeTitle();if(window.drawCountdown)window.drawCountdown();
  }
  btn.addEventListener('click',function(){set(!isEn)});
  var pref=null;try{pref=localStorage.getItem('lang')}catch(x){}
  if(pref==='en'||(!pref&&!/^es/i.test(navigator.language||'es')))set(true);else applyLinks();
})();

/* ===== RSVP_PLACEHOLDER ===== */

/* páginas: cada sección tiene su propia dirección (/itinerario, /rsvp, …).
   En Netlify se usan rutas reales; al abrir el archivo directo (vista previa) se usa #/ruta. */
(function(){
  var pages={},menu=document.getElementById('menu'),HASH=location.protocol==='file:'||!history.pushState;
  document.querySelectorAll('[data-page]').forEach(function(p){pages[p.getAttribute('data-page')]=p});
  function current(){
    var r=HASH?location.hash.replace(/^#\/?/,''):location.pathname.replace(/^\/+|\/+$/g,'');
    r=decodeURIComponent(r||'inicio').toLowerCase();return pages[r]?r:'inicio';
  }
  function title(){
    var r=current(),p=pages[r],t=p.getAttribute(isEn?'data-title-en':'data-title');
    document.title=(t?t+' · ':'')+'Marianne y Arturo · 5.03.2027';
  }
  function show(r,push){
    Object.keys(pages).forEach(function(k){pages[k].hidden=k!==r});
    document.body.setAttribute('data-page',r);
    menu.querySelectorAll('a').forEach(function(a){
      var on=a.getAttribute('data-route')===r;a.classList.toggle('active',on);
      if(on)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
    });
    if(push){if(HASH)location.hash=r==='inicio'?'':'#/'+r;else history.pushState({r:r},'',r==='inicio'?'/':'/'+r)}
    window.scrollTo(0,0);title();if(window.closeMenu)window.closeMenu();
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[data-route]');if(!a||e.metaKey||e.ctrlKey||e.shiftKey)return;
    e.preventDefault();var r=a.getAttribute('data-route');show(r,true);
  });
  window.addEventListener(HASH?'hashchange':'popstate',function(){show(current(),false)});
  window.routeTitle=title;
  show(current(),false);
})();

/* aparición suave */
if('IntersectionObserver' in window){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1});
  document.querySelectorAll('.reveal').forEach(function(e){io.observe(e)});
}else{document.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in')})}

/* cuenta regresiva (solo días) */
(function(){
  var el=document.getElementById('countdown');if(!el)return;
  function draw(){
    var ev=new Date('2027-03-05T18:30:00-04:00'),now=new Date();
    var d=Math.ceil((ev-now)/864e5);
    if(d>1)el.innerHTML='<b>'+d+'</b>'+(isEn?'days to go':'días para el gran día');
    else if(d===1)el.innerHTML='<b>1</b>'+(isEn?'day to go':'día para el gran día');
    else if(d===0||(now-ev)<864e5/2)el.innerHTML=isEn?'Today is the day':'Hoy es el gran día';
    else el.innerHTML='';
  }
  draw();window.drawCountdown=draw;setInterval(draw,36e5);
})();

/* pétalos que caen suavemente en el inicio */
(function(){
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var h=document.querySelector('.hero');
  var cols=['#dfe5ea','#cfd8e0','#dbe2d4','#eadfd2','#fbfaf7','#d3dccb'];
  var n=window.innerWidth<700?9:14;
  for(var i=0;i<n;i++){
    var p=document.createElement('span'),k=document.createElement('i');
    p.className='petal';
    p.style.left=(Math.random()*100)+'%';
    p.style.setProperty('--dx',(Math.random()*140-40)+'px');
    p.style.animationDuration=(18+Math.random()*16)+'s';p.style.animationDelay=(-Math.random()*30)+'s';
    k.style.setProperty('--s',(8+Math.random()*7)+'px');
    k.style.setProperty('--c',cols[i%cols.length]);
    k.style.animationDuration=(3.5+Math.random()*3)+'s';k.style.animationDelay=(-Math.random()*4)+'s';
    p.appendChild(k);h.appendChild(p);
  }
})();

/* copiar números de cuenta */
document.querySelectorAll('.cp').forEach(function(b){b.addEventListener('click',function(){
  var t=b.previousElementSibling.textContent,lbl=b.innerHTML;
  function ok(){b.textContent=isEn?'Copied':'Copiado';setTimeout(function(){b.innerHTML=b.getAttribute(isEn?'data-en':'data-es')||lbl},1600)}
  if(navigator.clipboard)navigator.clipboard.writeText(t).then(ok,ok);else ok();
})});

/* menú lateral */
(function(){
  var btn=document.getElementById('burger'),dr=document.getElementById('drawer'),sc=document.getElementById('scrim');
  function set(o){btn.setAttribute('aria-expanded',o);dr.classList.toggle('open',o);sc.classList.toggle('open',o);dr.setAttribute('aria-hidden',!o);dr.inert=!o;
    if(o){var a=dr.querySelector('a.active')||dr.querySelector('a');a&&a.focus({preventScroll:true})}}
  btn.addEventListener('click',function(){set(btn.getAttribute('aria-expanded')!=='true')});
  sc.addEventListener('click',function(){set(false)});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&dr.classList.contains('open')){set(false);btn.focus()}});
  window.closeMenu=function(){set(false)};dr.inert=true;
})();
