 'use strict';
let language = 'en';
try { language = localStorage.getItem('tdf-language') === 'ru' ? 'ru' : 'en'; } catch {}
// Keep disclosure content in an independent animated region.
document.querySelectorAll('details').forEach(details=>{
 const content=document.createElement('div');content.className='disclosure-content';
 [...details.childNodes].filter(node=>node.nodeName!=='SUMMARY').forEach(node=>content.append(node));
 details.append(content);
});
document.querySelectorAll('.scenario').forEach(card=>{
 const intro=document.createElement('div');intro.className='scenario-intro';
 [...card.childNodes].filter(node=>node.nodeName!=='DETAILS').forEach(node=>intro.append(node));
 card.prepend(intro);
});
function alignScenarioIntros(){
 const intros=[...document.querySelectorAll('.scenario-intro')];
 intros.forEach(el=>el.style.minHeight='');
 if(innerWidth>700){const tallest=Math.max(...intros.map(el=>el.getBoundingClientRect().height));intros.forEach(el=>el.style.minHeight=`${tallest}px`);}
}
document.fonts.ready.then(alignScenarioIntros);
window.addEventListener('resize',alignScenarioIntros,{passive:true});
const staticText = [];
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
while (walker.nextNode()) {
 const node = walker.currentNode;
 if (!['SCRIPT','STYLE','CODE'].includes(node.parentElement?.tagName) && node.textContent.trim()) staticText.push([node,node.textContent]);
}
const attributes = [...document.querySelectorAll('[aria-label],img[alt]')].flatMap(el =>
 ['aria-label','alt'].filter(name=>el.hasAttribute(name)).map(name=>[el,name,el.getAttribute(name)]));
const tr = text => language === 'ru' ? (window.TDF_RU[text] || text) : text;
let selectedStage = 0, selectedInstall = 0;
function setLanguage(next) {
 language = next;
 document.documentElement.lang = next;
 for (const [node,original] of staticText) {
  if (node.isConnected) node.textContent = original.replace(original.trim(),tr(original.trim()));
 }
 for (const [el,name,original] of attributes) el.setAttribute(name,tr(original));
 const toggle=document.querySelector('#language-toggle');
 toggle.setAttribute('aria-checked',String(language==='ru'));
 toggle.setAttribute('aria-label',language==='ru'?'Русский язык':'Russian language');
 toggle.title=language==='ru'?'Switch to English':'Переключить на русский';
 document.title = language==='ru' ? 'Team Dev Flow — Задайте работе общее направление.' : 'Team Dev Flow — Give the work a shared direction.';
 document.querySelector('meta[name="description"]').content = language==='ru' ? 'Открытый плагин для кодинг-агентов: понятная задача, нужные проверки и результат с доказательствами. Для Codex, Claude Code и Kilo Code.' : 'An open-source workflow for coding agents. Keep scope clear, choose the checks that matter, and finish with evidence. For Codex, Claude Code and Kilo Code.';
 document.querySelector('meta[property="og:title"]').content=document.title;
 document.querySelector('meta[property="og:description"]').content=document.querySelector('meta[name="description"]').content;
 updateStringHint();requestAnimationFrame(alignScenarioIntros);updateMenuLabel();reflectMotion();selectStage(selectedStage);selectInstall(selectedInstall);
 try {localStorage.setItem('tdf-language',language);} catch {}
 draw(performance.now());
}
document.querySelector('#language-toggle').addEventListener('click',()=>setLanguage(language==='en'?'ru':'en'));

const menuButton=document.querySelector('#menu-toggle');
const menuPanel=document.querySelector('#nav-panel');
new ResizeObserver(entries=>document.documentElement.style.setProperty('--header-height',`${entries[0].target.getBoundingClientRect().height}px`)).observe(document.querySelector('.nav'));
function updateMenuLabel(){document.querySelector('#menu-label').textContent=tr(menuButton.getAttribute('aria-expanded')==='true'?'Close':'Menu');}
let menuAnimation=null;
function setMenu(open,returnFocus=false){
 const fromOpacity=menuPanel.hidden?0:Number(getComputedStyle(menuPanel).opacity);
 if(menuAnimation)menuAnimation.cancel();
 menuButton.setAttribute('aria-expanded',String(open));
 document.querySelector('.nav').classList.toggle('menu-open',open);
 document.querySelector('#menu-label').textContent=tr(open?'Close':'Menu');
 menuPanel.inert=!open;
 if(open)menuPanel.hidden=false;
 if(reduced.matches){menuPanel.hidden=!open;menuAnimation=null;}
 else{
  menuAnimation=menuPanel.animate([{opacity:fromOpacity,transform:open?'translateY(-8px) scale(.98)':'translateY(0) scale(1)'},{opacity:open?1:0,transform:open?'translateY(0) scale(1)':'translateY(-6px) scale(.985)'}],{duration:open?260:190,easing:'cubic-bezier(.2,.8,.2,1)',fill:'both'});
  const current=menuAnimation;current.onfinish=()=>{if(menuAnimation!==current)return;menuPanel.hidden=!open;current.cancel();menuAnimation=null;};
 }
 if(returnFocus)menuButton.focus();
}
menuButton.addEventListener('click',()=>setMenu(menuButton.getAttribute('aria-expanded')!=='true'));
document.addEventListener('keydown',event=>{
 if(event.key==='Escape'&&!menuPanel.hidden){event.preventDefault();setMenu(false,true);}
});
document.addEventListener('pointerdown',event=>{
 if(!menuPanel.hidden&&!menuPanel.contains(event.target)&&!menuButton.contains(event.target))setMenu(false);
});
document.addEventListener('focusin',event=>{
 if(!menuPanel.hidden&&!menuPanel.contains(event.target)&&!menuButton.contains(event.target))setMenu(false);
});
menuPanel.querySelectorAll('a[href^="#"]').forEach(link=>link.addEventListener('click',()=>{
 setMenu(false);
 const target=document.querySelector(link.getAttribute('href'));
 if(target){target.setAttribute('tabindex','-1');target.focus({preventScroll:true});}
}));

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
let paused = reduced.matches;
function reflectMotion() {
  document.body.classList.toggle('motion-paused', paused);
  document.body.classList.toggle('motion-enabled', !paused);
}
reduced.addEventListener('change', () => { paused = reduced.matches; reflectMotion(); draw(performance.now()); });
reflectMotion();
document.querySelectorAll('details').forEach(details=>{
 const summary=details.querySelector('summary'),content=details.querySelector('.disclosure-content');
 let animation=null,expanded=details.open;
 summary.setAttribute('aria-expanded',String(expanded));
 summary.addEventListener('click',event=>{
  event.preventDefault();
  const start=details.open?content.getBoundingClientRect().height:0;
  const opacity=details.open?Number(getComputedStyle(content).opacity):0;
  if(animation)animation.cancel();
  expanded=!expanded;summary.setAttribute('aria-expanded',String(expanded));
  details.open=true;content.inert=!expanded;
  if(!expanded&&content.contains(document.activeElement))summary.focus();
  if(reduced.matches){details.open=expanded;animation=null;return;}
  const end=expanded?content.scrollHeight:0;
  animation=content.animate([{height:`${start}px`,opacity},{height:`${end}px`,opacity:expanded?1:0}],{duration:expanded?320:240,easing:'cubic-bezier(.2,.8,.2,1)',fill:'both'});
  const current=animation;current.onfinish=()=>{if(animation!==current)return;details.open=expanded;current.cancel();animation=null;};
 });
});
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) if (entry.isIntersecting) {
    entry.target.classList.add('visible'); observer.unobserve(entry.target);
  }
}, {threshold: .08});
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
document.documentElement.classList.add('js');

// Touch visitors see the illustration's active state as its card enters view.
const cardObserver=new IntersectionObserver(entries=>{
 for(const entry of entries)entry.target.classList.toggle('is-in-view',entry.isIntersecting);
},{rootMargin:'-18% 0px -18% 0px',threshold:.15});
document.querySelectorAll('.scenario').forEach(card=>cardObserver.observe(card));
const stages = [
  ['THE AGREEMENT','One clear outcome.','Scope agreed','THE “WHILE WE’RE HERE” CAN WAIT.','Start with the same understanding.','Use your chat request or a selected task. Resolve the questions that change the outcome. Add a specification only when you or your project needs one.'],
  ['THE WORK','A bounded change.','User work preserved','KEEP THE CHANGE ABOUT THE TASK.','Make room for focused work.','Implement within the agreed scope. Preserve existing work. Capture useful discoveries without quietly adding them to the current change.'],
  ['THE EVIDENCE','Checks that matter.','Behavior verified','REVIEW WHEN THE WORK NEEDS IT.','Check the behavior you changed.','Run relevant checks and required project gates. Use independent review when needed. Tie the evidence to the actual code and accepted scope.'],
  ['THE HANDOFF','An inspectable finish.','Limits made visible','CHANGE → CHECK → NEXT STEP','Leave a result someone can use.','Explain what changed, how it was checked and what remains. Keep source, package, installation and deployment status distinct.']
];
const stagesRu = [
 ['ДОГОВОРЁННОСТЬ','Один понятный результат.','Границы согласованы','ИДЕИ «ЗАОДНО» МОГУТ ПОДОЖДАТЬ.','Начните с общего понимания.','Возьмите запрос из чата или выбранную задачу. Уточните вопросы, которые меняют результат. Добавляйте спецификацию, только когда она нужна вам или проекту.'],
 ['РАБОТА','Ограниченное изменение.','Чужая работа сохранена','ДЕРЖИТЕ ФОКУС НА ЗАДАЧЕ.','Сосредоточьтесь на нужном изменении.','Реализуйте согласованный объём. Сохраняйте существующую работу. Фиксируйте полезные находки, не добавляя их незаметно в текущую задачу.'],
 ['ДОКАЗАТЕЛЬСТВА','Нужные проверки.','Поведение проверено','РЕВЬЮ — КОГДА ОНО НУЖНО.','Проверьте изменённое поведение.','Выполните подходящие проверки и обязательные требования проекта. При необходимости подключите независимое ревью. Свяжите доказательства с проверенным кодом и согласованным объёмом.'],
 ['РЕЗУЛЬТАТ','Проверяемая готовность.','Ограничения обозначены','ИЗМЕНЕНИЕ → ПРОВЕРКА → СЛЕДУЮЩИЙ ШАГ','Передайте понятный результат.','Объясните, что изменилось, как это проверено и что осталось. Различайте готовность исходников, пакета, установки и деплоя.']
];
const steps = [...document.querySelectorAll('[data-step]')];
const panel = document.querySelector('#flow-panel');
function selectStage(index) {
  selectedStage=index;
  steps.forEach((el,i) => { el.classList.toggle('active', i===index); el.setAttribute('aria-selected',String(i===index)); el.tabIndex=i===index?0:-1; });
  panel.dataset.stage=String(index);panel.setAttribute('aria-labelledby',`step-${index}`);
  const ids=['panel-kicker','paper-title','paper-check','orbit-label','panel-title','panel-text'];
  ids.forEach((id,i)=>{document.getElementById(id).textContent=(language==='ru'?stagesRu:stages)[index][i];});
  document.querySelector('#panel-count').textContent=`0${index+1} / 04`;
}
function keyboardTabs(buttons, activate, vertical=false) {
  buttons.forEach((button,index)=>button.addEventListener('keydown',event=>{
    const previous=vertical?'ArrowUp':'ArrowLeft',next=vertical?'ArrowDown':'ArrowRight';
    let target=index;
    if(event.key===next) target=(index+1)%buttons.length;
    else if(event.key===previous) target=(index-1+buttons.length)%buttons.length;
    else if(event.key==='Home') target=0;
    else if(event.key==='End') target=buttons.length-1;
    else return;
    event.preventDefault();activate(target);buttons[target].focus();
  }));
}
steps.forEach((el,i)=>el.addEventListener('click',()=>selectStage(i)));
keyboardTabs(steps,selectStage,true);
const installs={
  codex:{title:'Install the published canary',description:'Add the public marketplace, then install the plugin. Restart Codex and open a new task.',code:'codex plugin marketplace add https://github.com/gvukamolle/team-dev-flow-marketplace.git --json\ncodex plugin add team-dev-flow@team-flow --json'},
  kilo:{title:'Install this preview in your project',description:'Download and extract the preview package below. From its folder, replace /path/to/project with your project, then preview, install and check. Run /reload in Kilo Code.',code:'python3 scripts/host_package.py preview --host kilo --workspace /path/to/project\npython3 scripts/host_package.py install --host kilo --workspace /path/to/project\npython3 scripts/host_package.py check --host kilo --workspace /path/to/project'}
};
installs.codex.titleRu='Установить опубликованную версию';
installs.codex.descriptionRu='Добавьте публичный marketplace и установите плагин. Перезапустите Codex и откройте новую задачу.';
installs.kilo.titleRu='Установить preview в свой проект';
installs.kilo.descriptionRu='Скачайте и распакуйте пакет ниже. Из его папки выполните команды, заменив /path/to/project путём к проекту. Затем выполните /reload в Kilo Code.';
installs.claude={title:'Load the preview in Claude Code',titleRu:'Подключить preview в Claude Code',
 description:'Download and extract the package below. From your project, start Claude Code with the absolute path to the extracted plugin. It loads for this session; no marketplace setup is needed.',
 descriptionRu:'Скачайте и распакуйте пакет ниже. Из своего проекта запустите Claude Code, указав полный путь к папке плагина. Он подключится на эту сессию без настройки marketplace.',
 code:'claude --plugin-dir /absolute/path/to/team-dev-flow-0.7.0-dev.1'};
installs.local={title:'Keep structured work in Markdown',titleRu:'Вести задачи в Markdown и Obsidian',
 description:'An optional task store for your coding agent. From the extracted package, replace /path/to/vault and initialize a dedicated folder. Existing vault settings stay untouched.',
 descriptionRu:'Необязательное хранилище задач для вашего кодинг-агента. Из папки пакета выполните команды, заменив /path/to/vault. Настройки существующего хранилища сохраняются.',
 code:'python3 scripts/local_task_store.py init --vault "/path/to/vault" --folder "Projects/Team Dev Flow"\npython3 scripts/local_task_store.py upsert --root "/path/to/vault/Projects/Team Dev Flow" --project FLOW --kind project --id FLOW --title "Team Dev Flow"'};
const installTabs=[...document.querySelectorAll('[data-install]')];
function selectInstall(index){
  selectedInstall=index;
  const method=installs[installTabs[index].dataset.install];
  installTabs.forEach((el,i)=>{el.setAttribute('aria-selected',String(i===index));el.tabIndex=i===index?0:-1;});
  document.querySelector('#install-panel').setAttribute('aria-labelledby',`install-tab-${index}`);
  document.querySelector('#install-title').textContent=language==='ru'?method.titleRu:method.title;
  document.querySelector('#install-description').textContent=language==='ru'?method.descriptionRu:method.description;
  document.querySelector('#install-code').textContent=method.code;
  document.querySelector('#copy-status').textContent='';
}
installTabs.forEach((el,i)=>el.addEventListener('click',()=>selectInstall(i)));
keyboardTabs(installTabs,selectInstall);
document.querySelector('#copy-install').addEventListener('click',async()=>{
  const code=document.querySelector('#install-code');
  try{await navigator.clipboard.writeText(code.textContent);document.querySelector('#copy-status').textContent=language==='ru'?'Команды скопированы.':'Commands copied.';}
  catch{const range=document.createRange();range.selectNodeContents(code);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);document.querySelector('#copy-status').textContent=language==='ru'?'Команды выделены. Нажмите сочетание клавиш для копирования.':'Commands selected. Use your system copy shortcut.';}
});

function updateStringHint(){
 const touch=matchMedia('(pointer:coarse)').matches;
 document.querySelector('#string-hint').textContent=touch?(language==='ru'?'Коснитесь струны.':'Tap a string.'):(language==='ru'?'Потяните струну и отпустите.':'Pull a string. Let it go.');
 document.querySelector('#flow-canvas').setAttribute('aria-label',touch?(language==='ru'?'Коснитесь струны для анимации.':'Tap a string to set it in motion.'):(language==='ru'?'Потяните струну мышью или нажмите пробел, чтобы дёрнуть её.':'Pull a string with the mouse, or press Space to pluck it.'));
}
matchMedia('(pointer:coarse)').addEventListener('change',updateStringHint);
const canvas=document.querySelector('#flow-canvas');
// The original canvas is the hit target/guide; strings use a viewport overlay.
// A canvas bitmap clips its own pixels regardless of CSS overflow.
const guide=canvas.getContext('2d');
const overlay=document.createElement('canvas');
overlay.id='string-overlay';overlay.setAttribute('aria-hidden','true');
document.body.append(overlay);
const ctx=overlay.getContext('2d');
let overlayWidth=0,overlayHeight=0,overlayScale=0;
let width=0,height=0,frame=null,visible=true,lastTime=0,animationTime=0;
const strings=Array.from({length:8},()=>({offset:0,velocity:0,anchor:.5}));
let grab=null;
const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
function basePoint(t,lane){
 const convergence=1/(1+Math.exp(-(t-.48)*13));
 const chaos=Math.sin(t*11+lane*1.7+animationTime*.22)*height*.13+Math.sin(t*21-lane+animationTime*.13)*height*.035;
 const loose=(lane-3.5)*height*.065+chaos;
 const orderly=(lane-3.5)*height*.029;
 return {x:t*width,y:height*.5+loose*(1-convergence)+orderly*convergence};
}
function point(t,lane){
 const p=basePoint(t,lane),string=strings[lane];
 // Fixed endpoints, with a smooth peak at the captured point on the string.
 const ratio=t<string.anchor?t/string.anchor:(1-t)/(1-string.anchor);
 p.y+=string.offset*Math.sin(clamp(ratio,0,1)*Math.PI/2);
 return p;
}
function coords(event){const rect=canvas.getBoundingClientRect();return {x:event.clientX-rect.left,y:event.clientY-rect.top};}
function nearest(p){
 const t=clamp(p.x/width,.04,.96);
 let lane=0,distance=Infinity;
 for(let i=0;i<8;i++){const d=Math.abs(p.y-point(t,i).y);if(d<distance){distance=d;lane=i;}}
 return {lane,distance,t};
}
canvas.addEventListener('pointerdown',event=>{
 if(!ctx||!width||event.button!==0||grab)return;
 const p=coords(event),hit=nearest(p);
 if(hit.distance>24)return;
 const string=strings[hit.lane];const displacement=point(hit.t,hit.lane).y-basePoint(hit.t,hit.lane).y;
 string.anchor=hit.t;string.offset=displacement;string.velocity=0;
 grab={id:event.pointerId,lane:hit.lane,y:point(hit.t,hit.lane).y,touch:event.pointerType==='touch',startX:event.clientX,startY:event.clientY,moved:false};
 canvas.setPointerCapture(event.pointerId);canvas.classList.add('dragging');
 canvas.dataset.interaction='dragging';event.preventDefault();draw(performance.now());
});
canvas.addEventListener('pointermove',event=>{
 const p=coords(event);
 if(!grab){canvas.style.cursor=nearest(p).distance<24?'grab':'default';return;}
 if(event.pointerId!==grab.id)return;
 if(Math.hypot(event.clientX-grab.startX,event.clientY-grab.startY)>8)grab.moved=true;
 strings[grab.lane].anchor=clamp(p.x/width,.04,.96);
 grab.y=p.y;
 strings[grab.lane].offset=grab.y-basePoint(strings[grab.lane].anchor,grab.lane).y;
 strings[grab.lane].velocity=0;draw(performance.now());
});
function release(event){
 if(!grab||(event&&event.pointerId!==grab.id))return;
 if(event?.type==='pointerup'&&grab.touch&&!grab.moved&&!paused){strings[grab.lane].offset=-height*.22;strings[grab.lane].velocity=0;}
 const id=grab.id;grab=null;canvas.classList.remove('dragging');canvas.dataset.interaction='spring';
 if(canvas.hasPointerCapture(id))canvas.releasePointerCapture(id);
 if(paused)strings.forEach(s=>{s.offset=0;s.velocity=0;});
 draw(performance.now());
}
canvas.addEventListener('pointerup',release);
canvas.addEventListener('pointercancel',release);
canvas.addEventListener('lostpointercapture',release);
window.addEventListener('blur',()=>release());
canvas.addEventListener('keydown',event=>{
 if(event.key!==' '&&event.key!=='Enter')return;
 event.preventDefault();strings[4].anchor=.5;strings[4].offset=paused?0:-height*.25;strings[4].velocity=0;
 canvas.dataset.interaction=paused?'idle':'spring';draw(performance.now());
});
function resize(){
 release();const box=canvas.getBoundingClientRect();width=box.width;height=box.height;
 const scale=Math.min(window.devicePixelRatio||1,2);canvas.width=width*scale;canvas.height=height*scale;
 if(guide)guide.setTransform(scale,0,0,scale,0,0);
 strings.forEach(s=>{s.offset=0;s.velocity=0;});draw(performance.now());
}
function draw(now){
 if(frame){cancelAnimationFrame(frame);frame=null;}
 if(!ctx||!width)return;
 const dt=Math.min(lastTime?(now-lastTime)/1000:0,.025);lastTime=now;
 const active=grab||strings.some(s=>s.offset!==0||s.velocity!==0);
 const running=(visible||active)&&!document.hidden&&!paused;
 if(running)animationTime+=dt;
 // Keep the held point under the pointer while the stream keeps advancing.
 if(grab){
  const held=strings[grab.lane];
  held.offset=grab.y-basePoint(held.anchor,grab.lane).y;
 }
 for(let i=0;i<8;i++){
  const s=strings[i];
  if(grab?.lane===i)continue;
  if(paused){s.offset=0;s.velocity=0;}
  else if(running){
   // Damped spring: time-based integration, independent of display refresh rate.
   const sub=dt/3;
   for(let n=0;n<3;n++){s.velocity+=(-155*s.offset-9*s.velocity)*sub;s.offset+=s.velocity*sub;}
   if(Math.abs(s.offset)<.05&&Math.abs(s.velocity)<.15){s.offset=0;s.velocity=0;}
  }
 }
 if(!grab&&strings.every(s=>s.offset===0))canvas.dataset.interaction='idle';
 const scale=Math.min(window.devicePixelRatio||1,2);
 if(overlayWidth!==innerWidth||overlayHeight!==innerHeight||overlayScale!==scale){
  overlayWidth=innerWidth;overlayHeight=innerHeight;overlayScale=scale;
  overlay.width=Math.round(innerWidth*scale);overlay.height=Math.round(innerHeight*scale);
 }
 ctx.setTransform(scale,0,0,scale,0,0);ctx.clearRect(0,0,innerWidth,innerHeight);
 const origin=canvas.getBoundingClientRect();ctx.translate(origin.left,origin.top);
 if(guide)guide.clearRect(0,0,width,height);
 for(let lane=0;lane<8;lane++){
  ctx.beginPath();for(let i=0;i<=180;i++){const p=point(i/180,lane);if(i===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);}
  ctx.strokeStyle=grab?.lane===lane?'#111':lane===4?'#111':`rgba(17,17,17,${.15+lane*.035})`;
  ctx.lineWidth=grab?.lane===lane?2:lane===4?1.5:.8;ctx.stroke();
  for(let packet=0;packet<2;packet++){
   const t=((animationTime*.045+lane*.127+packet*.5)%1);const p=point(t,lane);const q=point(Math.min(1,t+.001),lane);
   ctx.save();ctx.translate(p.x,p.y);ctx.rotate(Math.atan2(q.y-p.y,q.x-p.x));ctx.fillStyle=lane===4?'#111':'#fff';ctx.strokeStyle='#777';ctx.lineWidth=.6;ctx.fillRect(-5,-3.5,10,7);ctx.strokeRect(-5,-3.5,10,7);ctx.restore();
  }
 }
 if(guide){
 const cx=width*.53;guide.strokeStyle='#bbb';guide.setLineDash([2,5]);guide.beginPath();guide.moveTo(cx,height*.1);guide.lineTo(cx,height*.95);guide.stroke();guide.setLineDash([]);
 guide.font='9px Plex,monospace';guide.textAlign='center';guide.fillStyle='#666';guide.fillText(language==='ru'?'ГРАНИЦЫ ЗАДАЧИ':'AGREED SCOPE',cx,12);
 }
 if(grab){const p=point(strings[grab.lane].anchor,grab.lane);ctx.beginPath();ctx.arc(p.x,p.y,5,0,Math.PI*2);ctx.fillStyle='#111';ctx.fill();}
 if(running)frame=requestAnimationFrame(draw);
}
new ResizeObserver(resize).observe(canvas);
new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;lastTime=0;draw(performance.now());}).observe(canvas);
window.addEventListener('scroll',()=>{draw(performance.now());},{passive:true});
document.addEventListener('visibilitychange',()=>{if(document.hidden)release();lastTime=0;draw(performance.now());});
setLanguage(language);
