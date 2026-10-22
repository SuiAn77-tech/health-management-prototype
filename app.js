const app = document.querySelector('#app');
const toast = document.querySelector('#toast');
const photoInput = document.querySelector('#photo-input');
const NS = 'http://www.w3.org/2000/svg';
const screenCache = new Map();
const screenKeys = ['home', 'homeDone', 'report', 'journal', 'plan', 'checkin'];
const state = {
  route: 'home', checkedIn: localStorage.getItem('health-checked-in-v3') === 'true',
  cause: '全部高危', water: 1600, photos: {},
  diet: ['清淡低GI餐食', '无奶茶/控糖良好'], feeling: '温和无刺激', cycleOn: true,
  sleepTime: '23:20', sleepDuration: '7.5',
};
let renderVersion = 0;
let photoSlot = 0;
let boundsCache = null;

function toastMessage(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastMessage.timer);
  toastMessage.timer = setTimeout(() => toast.classList.remove('show'), 1900);
}
function element(tag, attributes = {}) {
  const node = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  return node;
}

// Work in the export's original coordinates. The viewBox removes only the device's outer padding.
function bounds(node, root) {
  if (boundsCache?.has(node)) return boundsCache.get(node);
  const b = node.getBBox();
  const m = root.getCTM().inverse().multiply(node.getCTM());
  const a = new DOMPoint(b.x, b.y).matrixTransform(m);
  const z = new DOMPoint(b.x + b.width, b.y + b.height).matrixTransform(m);
  const result = { x: a.x, y: a.y, width: z.x - a.x, height: z.y - a.y };
  boundsCache?.set(node, result);
  return result;
}
function inside(b, [x, y, w, h], epsilon = .7) {
  return b.width > 0 && b.height > 0 && b.x >= x - epsilon && b.y >= y - epsilon && b.x + b.width <= x + w + epsilon && b.y + b.height <= y + h + epsilon;
}
function groupInBox(svg, box) {
  const group = element('g');
  const matches = [...svg.querySelectorAll('g,rect,path,circle,line,polyline,polygon,ellipse,use,image,text')]
    .filter(node => !node.closest('defs,clipPath,mask,pattern,filter,[data-action]') && inside(bounds(node, svg), box));
  const selected = new Set(matches);
  const top = matches.filter(node => {
    let parent = node.parentElement;
    while (parent && parent !== svg) { if (selected.has(parent)) return false; parent = parent.parentElement; }
    return true;
  });
  // Preserve any original transforms when making a component out of the exported shapes.
  for (const node of top) {
    const m = svg.getCTM().inverse().multiply(node.parentElement.getCTM());
    if (Math.abs(m.a - 1) + Math.abs(m.b) + Math.abs(m.c) + Math.abs(m.d - 1) + Math.abs(m.e) + Math.abs(m.f) > .001) {
      const wrapper = element('g', { transform: `matrix(${m.a} ${m.b} ${m.c} ${m.d} ${m.e} ${m.f})` });
      wrapper.append(node); group.append(wrapper);
    } else group.append(node);
  }
  svg.append(group);
  return group;
}
function control(group, action, label, data = {}, role = 'button') {
  group.classList.add('control');
  group.setAttribute('role', role);
  group.setAttribute('tabindex', '0');
  group.setAttribute('aria-label', label);
  group.dataset.action = action;
  for (const [key, value] of Object.entries(data)) group.dataset[key] = value;
  return group;
}
function areaControl(svg, box, action, label, data = {}) {
  return control(groupInBox(svg, box), action, label, data);
}

function configureFilters(svg) {
  const filters = [
    ['全部高危', [40, 105, 76, 28]], ['奶茶高糖', [124.5, 104.5, 81, 29]],
    ['熬夜/少眠', [214.5, 104.5, 85, 29]], ['辣度刺激', [308.5, 104.5, 81, 29]],
  ];
  for (const [label, box] of filters) {
    const group = areaControl(svg, box, 'cause-filter', label, { cause: label });
    group.classList.add('cause-filter');
    group.querySelectorAll('rect').forEach(node => {
      if (node.hasAttribute('fill')) node.classList.add('filter-fill');
      if (node.hasAttribute('stroke')) node.classList.add('filter-border');
    });
    group.querySelectorAll('path').forEach(node => node.classList.add('filter-label'));
  }
}

function indicatorTemplate(svg) {
  const fill = svg.querySelector('rect[x="83"][y="954.75"]');
  const check = [...svg.querySelectorAll('path')].find(n => n.getAttribute('d')?.startsWith('M88.0833 963.167'));
  const empty = [...svg.querySelectorAll('path')].find(n => n.getAttribute('d')?.startsWith('M256 955.25'));
  return { fill: fill.cloneNode(true), check: check.cloneNode(true), empty: empty.cloneNode(true) };
}
function addIndicator(group, template, cx, cy) {
  const on = element('g', { class: 'indicator-on', transform: `translate(${cx - 91} ${cy - 962.75})` });
  on.append(template.fill.cloneNode(true), template.check.cloneNode(true));
  const off = element('g', { class: 'indicator-off', transform: `translate(${cx - 256} ${cy - 962.75})` });
  off.append(template.empty.cloneNode(true));
  group.append(off, on);
}
function configureChoice(svg, template, config) {
  const { label, box, action, diet = false } = config;
  const group = groupInBox(svg, box);
  control(group, action, label, { value: label }, 'checkbox');
  group.classList.add('choice');
  if (diet) group.classList.add('diet-choice');
  const [x, y, w, h] = box;
  group.dataset.dietBoxX = x;
  group.dataset.dietBoxW = w;
  const cy = y + h / 2;
  const cx = diet ? x + 17.5 : x + 18.5;
  const paths = [...group.querySelectorAll('path')];
  for (const node of paths) {
    const b = bounds(node, svg);
    if (diet) {
      // Keep the updated SVG's own icon/check geometry. The first two options
      // contain their selected check paths; the third remains exactly as drawn.
      if (node.getAttribute('d')?.startsWith('M98.9167') || node.getAttribute('d')?.startsWith('M219.587')) node.classList.add('diet-check');
      else node.classList.add('diet-label');
    } else {
      if (b.x < x + 29 && b.width < 20) { node.remove(); continue; }
      node.classList.add(b.x > x + 100 ? 'choice-sub' : 'choice-label');
    }
  }
      group.querySelectorAll('rect').forEach(node => {
    if (Number(node.getAttribute('width')) < 25) { node.remove(); return; }
    if (node.hasAttribute('fill')) node.classList.add('choice-fill');
    if (node.hasAttribute('stroke')) node.classList.add('choice-border');
    // Dietary pill geometry remains from the updated design SVG.
  });
  if (diet && !group.querySelector('.diet-check')) {
    // The updated export has no check path in the third pill. Reuse the
    // first pill's check geometry at the same 13px/15px inset.
    const source = [...svg.querySelectorAll('path')].find(node => node.getAttribute('d')?.startsWith('M98.9167'));
    if (source) {
      const check = source.cloneNode(true);
      check.classList.add('diet-check');
      // The source check is from the first pill at (85.5, 365.25).
      check.setAttribute('transform', `translate(${x - 85.5} ${y - 365.25})`);
      group.append(check);
    }
  }
  if (diet) {
    const labels = [...group.querySelectorAll('.diet-label')];
    const labelBounds = labels.map(node => bounds(node, svg));
    if (labelBounds.length) {
      const minX = Math.min(...labelBounds.map(b => b.x));
      const maxX = Math.max(...labelBounds.map(b => b.x + b.width));
      labels.forEach(node => { node.dataset.baseTransform = node.getAttribute('transform') || ''; });
      group.dataset.dietLabelMin = minX;
      group.dataset.dietLabelWidth = maxX - minX;
    }
    const check = group.querySelector('.diet-check');
    if (check) {
      const checkBounds = bounds(check, svg);
      check.dataset.baseTransform = check.getAttribute('transform') || '';
      group.dataset.dietCheckMin = checkBounds.x;
      group.dataset.dietCheckWidth = checkBounds.width;
    }
  }
  if (!diet) addIndicator(group, template, cx, cy);
  return group;
}

function configureCheckin(svg) {
  const template = indicatorTemplate(svg);
  const diets = [
    ['清淡低GI餐食', [85.5, 365.25, 112, 29]],
    ['无奶茶/控糖良好', [206.17, 365.25, 127, 29]],
    ['油炸重盐外卖', [85, 402.75, 98, 30]],
  ];
  const feelings = [
    ['温和无刺激', [72.5, 944.25, 156, 37]], ['轻微泛红', [237.5, 944.25, 156, 37]],
    ['紧绷脱水', [72.5, 990.25, 156, 37]], ['瘙痒脱屑', [237.5, 990.25, 156, 37]],
  ];
  diets.forEach(([label, box]) => configureChoice(svg, template, { label, box, action: 'habit', diet: true }));
  feelings.forEach(([label, box]) => configureChoice(svg, template, { label, box, action: 'feeling' }));
  svg.querySelector('use[transform="translate(72 202.71) scale(0.06875)"]')?.remove();
  const phaseExplanation = [...svg.querySelectorAll('path')].find(node => node.getAttribute('d')?.startsWith('M87.9831 207.429'));
  if (phaseExplanation) phaseExplanation.setAttribute('transform', 'translate(-16 0)');
  // Replace only the original value paths. Keep the card label and all spacing
  // from the SVG, using its compact 14px value scale and baseline.
  // Keep the editable values in the compact value slots from the SVG.
  // The exported paths occupy roughly x96–126 / x249–292 and end at y≈584.
  replaceNumeric(svg, [90, 574, 130, 27], 'sleep-time', state.sleepTime, 111, 583.75, 12, '#1E293B');
  replaceNumeric(svg, [240, 574, 145, 27], 'sleep-duration', `${state.sleepDuration} 小时`, 270.5, 583.9, 12, '#1E293B');
  areaControl(svg, [85, 544, 143, 54], 'sleep', '设置昨晚入睡时间');
  areaControl(svg, [63, 61, 43, 25], 'nav', '返回', { route: 'home' });
  areaControl(svg, [349, 61.5, 58, 26], 'draft', '存草稿');
  const cycle = areaControl(svg, [354, 126, 40, 20], 'cycle', '生理周期开关');
  cycle.setAttribute('role', 'switch');
  cycle.querySelector('rect[width="40"]').classList.add('switch-track');
  cycle.querySelector('rect[width="16"]').classList.add('switch-knob');
  areaControl(svg, [249, 713.5, 63, 28], 'water', '减少 200 毫升', { delta: -200 });
  areaControl(svg, [320, 713.5, 61, 28], 'water', '增加 200 毫升', { delta: 200 });
  svg.querySelector('rect[x="87"][y="666.75"]').id = 'water-progress';
  // Use native SVG text only for editable numeric values; all other lettering stays as exported paths.
  replaceNumeric(svg, [271, 638, 33, 21], 'water-number', 1600, 288, 652.75, 12, '#F43F5E');
  replaceNumeric(svg, [217, 685, 75, 19], 'water-caption', '1600ml (当前)', 253, 698, 10, '#F43F5E');
  const slots = [[72, 1141.28, 100.67, 100.66], [183.67, 1142.28, 98.67, 98.67], [294.34, 1142.28, 98.66, 98.66]];
  slots.forEach((box, i) => {
    const group = areaControl(svg, box, 'photo', ['正面参考', '左旋定点', '右旋定点'][i], { slot: i });
    group.id = `photo-slot-${i}`;
    // Both the rectangular photo fill and later uploads share the design's 19px corner clip.
    group.querySelectorAll('rect[fill^="url(#pattern"]').forEach(n => { n.setAttribute('rx', '19'); n.setAttribute('ry', '19'); });
  });
  areaControl(svg, [55, 1292.92, 356, 48], 'complete', '完成今日打卡');
}

function replaceNumeric(svg, box, id, value, x, y, size, color) {
  const old = groupInBox(svg, box);
  old.remove();
  const text = element('text', { id, x, y, 'text-anchor': 'middle', 'font-size': size, 'font-weight': 600, fill: color });
  text.textContent = value;
  svg.append(text);
}

function configureNavigation(svg, key) {
  const heights = { home: 1173, homeDone: 1176, report: 1253.75, journal: 1447, plan: 1294.98 };
  const y = heights[key] - 64;
  ['home', 'report', 'journal', 'plan'].forEach((route, i) => areaControl(svg, [20 + i * 97.5, y, 97.5, 64], 'nav', ['概览', '诱因', '影像', '档案'][i], { route }));
  if (key === 'home') areaControl(svg, [56, 810, 318, 52], 'nav', '开始今日打卡', { route: 'checkin' });
  if (key === 'homeDone') {
    areaControl(svg, [57, 819, 236, 43], 'nav', '查看今日 AI 分析结语', { route: 'report' });
    areaControl(svg, [301, 819, 72, 43], 'nav', '修改打卡', { route: 'checkin' });
  }
  if (key === 'home' || key === 'homeDone') {
    const yy = key === 'home' ? 704 : 710;
    [[56, '生活节律', 'checkin'], [164, '修护体感', 'checkin'], [272, '定点影像', 'checkin']]
      .forEach(([x, label, route]) => areaControl(svg, [x, yy, 101, 94], 'nav', label, { route }));
  }
  if (key === 'report') {
    areaControl(svg, [303, 1071, 70, 36], 'nav', '查看对策', { route: 'plan' });
    areaControl(svg, [57, 1071, 238, 36], 'reminder', '控糖干预提醒');
  }
  if (key === 'journal') areaControl(svg, [274, 43, 117, 34], 'photo', '拍摄定点影像', { slot: 0 });
  if (key === 'plan') areaControl(svg, [57, 1090, 316, 65], 'export', '导出近30天临床就诊报告');
}

function syncState() {
  app.querySelectorAll('.cause-filter').forEach(group => group.setAttribute('aria-pressed', String(state.cause === group.dataset.cause)));
  app.querySelectorAll('.choice').forEach(group => {
    const checked = group.dataset.action === 'habit' ? state.diet.includes(group.dataset.value) : state.feeling === group.dataset.value;
    group.setAttribute('aria-checked', String(checked));
    if (group.classList.contains('diet-choice')) {
      const x = Number(group.dataset.dietBoxX || 0);
      const w = Number(group.dataset.dietBoxW || group.getBBox().width);
      const labelMin = Number(group.dataset.dietLabelMin || 0);
      const labelWidth = Number(group.dataset.dietLabelWidth || 0);
      const checkMin = Number(group.dataset.dietCheckMin || 0);
      const checkWidth = Number(group.dataset.dietCheckWidth || 0);
      const labels = group.querySelectorAll('.diet-label');
      let labelShift;
      let checkShift = 0;
      if (checked && checkWidth) {
        // Center the complete selected cluster and keep exactly 4px between
        // the check mark and the label, for all three dietary pills.
        const clusterWidth = checkWidth + 4 + labelWidth;
        const clusterLeft = x + (w - clusterWidth) / 2;
        checkShift = clusterLeft - checkMin;
        labelShift = clusterLeft + checkWidth + 4 - labelMin;
      } else {
        // Unselected labels use the pill's own 10px horizontal rhythm.
        labelShift = (x + w / 2) - (labelMin + labelWidth / 2);
      }
      labels.forEach(node => {
        const base = node.dataset.baseTransform || '';
        node.setAttribute('transform', [`translate(${labelShift} 0)`, base].filter(Boolean).join(' '));
      });
      const check = group.querySelector('.diet-check');
      if (check) {
        const base = check.dataset.baseTransform || '';
        check.setAttribute('transform', [`translate(${checkShift} 0)`, base].filter(Boolean).join(' '));
      }
    }
  });
  const cycle = app.querySelector('[data-action="cycle"]');
  if (cycle) {
    cycle.setAttribute('aria-checked', String(state.cycleOn));
    const knob = cycle.querySelector('.switch-knob');
    if (knob) knob.setAttribute('x', state.cycleOn ? '376' : '356');
  }
  const progress = app.querySelector('#water-progress');
  if (progress) progress.setAttribute('width', 292 * state.water / 2000);
  const number = app.querySelector('#water-number');
  if (number) number.textContent = state.water;
  const caption = app.querySelector('#water-caption');
  if (caption) caption.textContent = `${state.water}ml (当前)`;
  const sleepTime = app.querySelector('#sleep-time');
  if (sleepTime) sleepTime.textContent = state.sleepTime;
  const sleepDuration = app.querySelector('#sleep-duration');
  if (sleepDuration) sleepDuration.textContent = `${state.sleepDuration} 小时`;
  for (const [i, src] of Object.entries(state.photos)) {
    const slot = app.querySelector(`#photo-slot-${i}`);
    if (!slot || slot.querySelector('.user-photo')) continue;
    const x = [73, 183.67, 294.34][i];
    const y = 1142.28;
    const clip = element('clipPath', { id: `upload-clip-${i}` });
    clip.append(element('rect', { x, y, width: 98.67, height: 98.67, rx: 19 }));
    const image = element('image', { class: 'user-photo', x, y, width: 98.67, height: 98.67, href: src, preserveAspectRatio: 'xMidYMid slice', 'clip-path': `url(#upload-clip-${i})` });
    slot.append(clip, image);
  }
}

async function render() {
  const version = ++renderVersion;
  const key = state.route === 'home' && state.checkedIn ? 'homeDone' : state.route;
  app.setAttribute('aria-busy', 'true');
  try {
    if (!screenCache.has(key)) {
      let lastError;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const controller = new AbortController();
          const timer = setTimeout(() => controller.abort(), 10000);
          const response = await fetch(`assets/screens/${key}.svg?v=vector-10`, { signal: controller.signal, cache: 'force-cache' });
          clearTimeout(timer);
          if (!response.ok) throw new Error(`页面资源 ${response.status}`);
          screenCache.set(key, await response.text());
          lastError = null;
          break;
        } catch (error) { lastError = error; await new Promise(resolve => setTimeout(resolve, 180 * (attempt + 1))); }
      }
      if (lastError) throw lastError;
    }
    if (version !== renderVersion) return;
    const doc = new DOMParser().parseFromString(screenCache.get(key), 'image/svg+xml');
    const svg = document.importNode(doc.documentElement, true);
    svg.classList.add('vector-page');
    svg.setAttribute('aria-label', {home:'概览',homeDone:'概览',report:'AI 诱因关联分析',journal:'皮肤影像日志',plan:'医学基准与个性化调理方案',checkin:'今日习惯与诱因打卡'}[key]);
    app.replaceChildren(svg);
    // getBBox is expensive on mobile browsers. Cache geometry for this render;
    // moved nodes become descendants of data-action groups and are excluded
    // from subsequent grouping passes.
    boundsCache = new WeakMap();
    if (key === 'report') configureFilters(svg);
    if (key === 'checkin') configureCheckin(svg); else configureNavigation(svg, key);
    syncState();
    boundsCache = null;
    window.scrollTo({ top: 0, behavior: 'instant' });
  } catch (error) {
    console.error(error);
    toastMessage('页面加载失败，请刷新重试');
  } finally { app.removeAttribute('aria-busy'); }
}

app.addEventListener('click', event => {
  const target = event.target.closest('[data-action]');
  if (!target) return;
  const action = target.dataset.action;
  if (action === 'nav') { state.route = target.dataset.route; render(); return; }
  if (action === 'cause-filter') state.cause = target.dataset.cause;
  if (action === 'habit') { const value = target.dataset.value; state.diet = state.diet.includes(value) ? state.diet.filter(v => v !== value) : [...state.diet, value]; }
  if (action === 'feeling') state.feeling = state.feeling === target.dataset.value ? '' : target.dataset.value;
  if (action === 'water') state.water = Math.max(0, Math.min(2000, state.water + Number(target.dataset.delta)));
  if (action === 'cycle') state.cycleOn = !state.cycleOn;
  if (action === 'sleep') { openSleepSheet(); return; }
  if (action === 'photo') { photoSlot = Number(target.dataset.slot || 0); photoInput.value = ''; photoInput.click(); return; }
  if (action === 'complete') { state.checkedIn = true; localStorage.setItem('health-checked-in-v3', 'true'); state.route = 'home'; render(); toastMessage('今日打卡完成，AI模型已同步'); return; }
  if (action === 'draft') toastMessage('草稿已保存');
  if (action === 'reminder') toastMessage('控糖干预提醒已开启');
  if (action === 'export') toastMessage('报告导出功能为原型演示');
  syncState();
});
app.addEventListener('keydown', event => {
  if ((event.key === 'Enter' || event.key === ' ') && event.target.closest('[data-action]')) { event.preventDefault(); event.target.closest('[data-action]').dispatchEvent(new MouseEvent('click', { bubbles: true })); }
});
photoInput.addEventListener('change', event => {
  const file = event.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    state.photos[photoSlot] = reader.result;
    if (state.route !== 'checkin') { state.route = 'checkin'; render(); }
    else {
      app.querySelector(`#photo-slot-${photoSlot} .user-photo`)?.remove();
      app.querySelector(`#upload-clip-${photoSlot}`)?.remove();
      syncState();
    }
    toastMessage('影像已添加');
  };
  reader.readAsDataURL(file);
});
render();

// Warm the other screens in the background so the first navigation tap does
// not wait for a large SVG request. The service worker also keeps these assets
// available when the temporary public tunnel briefly reconnects.
setTimeout(() => {
  const warm = () => Promise.all(screenKeys.filter(key => !screenCache.has(key)).map(async key => {
    try {
      const response = await fetch(`assets/screens/${key}.svg?v=vector-10`, { cache: 'force-cache' });
      if (response.ok) screenCache.set(key, await response.text());
    } catch { /* the next navigation retries */ }
  }));
  if ('requestIdleCallback' in window) requestIdleCallback(warm, { timeout: 2500 }); else warm();
}, 350);

const timeSheet = document.querySelector('#time-sheet');
const hourSelect = document.querySelector('#sleep-hour');
const minuteSelect = document.querySelector('#sleep-minute');
for (let hour = 0; hour < 24; hour++) hourSelect.add(new Option(String(hour).padStart(2, '0'), String(hour).padStart(2, '0')));
for (let minute = 0; minute < 60; minute += 5) minuteSelect.add(new Option(String(minute).padStart(2, '0'), String(minute).padStart(2, '0')));
function openSleepSheet() {
  const [hour, minute] = state.sleepTime.split(':');
  hourSelect.value = hour;
  minuteSelect.value = String(Math.round(Number(minute) / 5) * 5 % 60).padStart(2, '0');
  timeSheet.hidden = false;
}
function closeSleepSheet(commit) {
  if (commit) {
    state.sleepTime = `${hourSelect.value}:${minuteSelect.value}`;
    const [h, m] = state.sleepTime.split(':').map(Number);
    const wake = 6 * 60 + 50;
    let duration = (wake - (h * 60 + m) + 1440) % 1440;
    if (duration < 180) duration += 1440;
    state.sleepDuration = (duration / 60).toFixed(1);
    syncState();
  }
  timeSheet.hidden = true;
}
timeSheet.addEventListener('click', event => {
  const action = event.target.closest('[data-time-action]')?.dataset.timeAction;
  if (action === 'cancel') closeSleepSheet(false);
  if (action === 'done') closeSleepSheet(true);
});


