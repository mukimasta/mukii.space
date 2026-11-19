---
title: "SoundMat"
date: 2026-10-20
draft: false
---

{{< html >}}
<style>
  /* ---- 这一页新加的（草图，之后交给 blog-bot 进主题） ---- */
  :root { --accent: #c9782e; --faint: color-mix(in srgb, var(--fg) 55%, transparent); }
  .content-container > * { margin-bottom: 64px; }
  .content-container > h1 { margin-bottom: 0; }
  .lead { font-weight: 500; }
  .note { font-size: 14px; line-height: 24px; color: var(--faint); }

  /* hero：左字居中，右主图 */
  .hero { display: grid; grid-template-columns: 1fr 62%; gap: 32px; align-items: center; }
  .hero__text p { margin: 0; }
  .hero__text .big { font-size: 18px; font-weight: 500; margin-bottom: 12px; }
  .hero img { display: block; width: 100%; border-radius: var(--radius); }

  /* 比 800 宽的块 */
  .wide { width: min(1040px, calc(100vw - 48px)); position: relative; left: 50%; transform: translateX(-50%); }

  /* 两个交互 */
  .play { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
  /* color-scheme 和小部件自己的一致，深色模式下浏览器才不给 iframe 铺白底 */
  .play__item iframe { display: block; width: 100%; aspect-ratio: 500 / 548; border: 0; background: transparent; color-scheme: light; }
  .play__item p { margin: 12px 0 0; }
  .play-intro { text-align: center; max-width: 600px; margin-inline: auto; }
  .play-intro p { margin: 0; }

  /* 两张示意图并排 */
  .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start; }
  .pair h3, .block-title { font-size: 16px; font-weight: 500; margin: 0 0 4px; }
  .pair .sub { margin: 0 0 20px; }
  svg.dia { display: block; width: 100%; height: auto; color: var(--fg); font-family: var(--sans); }
  svg.dia text { fill: currentColor; font-size: 14px; }
  svg.dia .soft { fill: var(--faint); }
  svg.dia .ln { stroke: currentColor; fill: none; stroke-width: 1.2; }
  svg.dia .ln2 { stroke: var(--faint); fill: none; stroke-width: 1; }
  svg.dia .acc { stroke: var(--accent); }
  svg.dia .accf { fill: var(--accent); }
  svg.dia .felt { fill: color-mix(in srgb, #d9cfbd 70%, var(--bg)); }
  svg.dia .bg { fill: var(--bg); }

  /* 从放石头到发声 */
  .steps { list-style: none; margin: 0; padding: 0; position: relative; }
  .steps li { display: grid; grid-template-columns: 72px 1fr; gap: 16px; align-items: center; margin-bottom: 18px; }
  .steps li:last-child { margin-bottom: 0; }
  .steps .ic { width: 72px; height: 56px; }
  .steps p { margin: 0; }
  .steps .n { color: var(--faint); font-size: 14px; margin-right: 6px; }

  /* 理念 */
  .quote { max-width: 560px; margin-inline: auto; text-align: center; }
  .quote p { margin: 0; }
  .quote .q { text-wrap: balance; font-size: 18px; line-height: 32px; font-weight: 500; }
  .quote .note { margin-top: 12px; }

  /* 时间线 */
  .tl { position: relative; display: grid; grid-template-columns: repeat(8, 1fr); height: 200px; }
  .tl::before { content: ""; position: absolute; left: 0; right: 9%; top: 100px; border-top: 1px solid var(--fg); }
  .tl::after { content: ""; position: absolute; left: 91%; right: 0; top: 100px; border-top: 1px dashed var(--faint); }
  .tl__i { position: relative; }
  .tl__i::before { content: ""; position: absolute; left: 0; top: 96px; width: 9px; height: 9px; border-radius: 50%; background: var(--fg); }
  .tl__i.future::before { background: var(--bg); border: 1px solid var(--faint); }
  .tl__i.key::before { background: var(--accent); width: 11px; height: 11px; top: 95px; }
  .tl__i > div { position: absolute; left: 0; width: 140%; font-size: 14px; line-height: 20px; padding-left: 0; }
  .tl__i.up > div { bottom: 116px; }
  .tl__i.down > div { top: 116px; }
  .tl__i.up::after, .tl__i.down::after { content: ""; position: absolute; left: 4px; border-left: 1px solid var(--line); }
  .tl__i.up::after { top: 66px; height: 30px; }
  .tl__i.down::after { top: 105px; height: 8px; }
  .tl b { display: block; font-weight: 500; font-size: 14px; }
  .tl span { color: var(--faint); }

  /* 照片 */
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .ph img, .full img { display: block; width: 100%; border-radius: var(--radius); cursor: zoom-in; }
  .ph img { aspect-ratio: 4 / 3; object-fit: cover; }
  .ph p { margin: 8px 0 0; }
  figure { margin: 0; }
  figcaption { font-size: 14px; line-height: 24px; color: var(--faint); margin-top: 8px; }
  video { display: block; width: 100%; border-radius: var(--radius); background: #000; }

  .section-head p { margin: 0; }

  @media (max-width: 760px) {
    .hero, .play, .pair, .grid3 { grid-template-columns: 1fr; }
    .hero__text { order: 2; }
    .tl { grid-template-columns: 1fr; height: auto; padding-left: 20px; }
    .tl::before { left: 4px; right: auto; top: 6px; bottom: 6px; border-top: 0; border-left: 1px solid var(--fg); }
    .tl::after { display: none; }
    .tl__i { padding: 0 0 18px 0; }
    .tl__i::before { left: -20px; top: 6px; }
    .tl__i.key::before { top: 5px; left: -21px; }
    .tl__i > div { position: static; width: auto; }
    .tl__i.up::after, .tl__i.down::after { display: none; }
  }
</style>
<!-- ① 放置石头，音乐生长 -->
<div class="hero">
  <div class="hero__text">
    <p class="big">放置石头，音乐生长</p>
    <p>一件声音装置。圆形毛毡下面藏着压力传感器，石头放在哪、放几颗，房间里的音乐就跟着变。不用会音乐，谁都能玩。</p>
  </div>
  <img src="img/hero.jpg" alt="草地上的 SoundMat">
</div>

<!-- ② 两个可以玩的垫子 -->
<div class="play-intro">
  <p class="lead">试试看。</p>
  <p>点圆垫放一颗石头，再点一下拿走。它有两种玩法。</p>
</div>

<div class="wide play">
  <div class="play__item">
    <iframe src="widgets/ambient.html" title="SoundMat 氛围模式" loading="lazy" allow="autoplay"></iframe>
    <p><b>氛围模式</b>　没有节拍。每一圈是一种声音：外圈是鸟鸣、钟声和雨，往里是旋律、和声，最里面是低音。放上石头，那一层就响起来，怎么放都好听。</p>
  </div>
  <div class="play__item">
    <iframe src="widgets/jam.html" title="SoundMat 合奏模式" loading="lazy" allow="autoplay"></iframe>
    <p><b>合奏模式</b>　一根光线绕着圆心转，扫到石头就弹一个音：靠外是旋律，靠里是贝斯，底下有鼓和和弦一直在走。几个人围着摆，就是在一起编一段曲子。</p>
  </div>
</div>

<!-- ③ 它长什么样、怎么发声 -->
<div class="pair">
  <div>
    <h3>它是什么做的</h3>
    <p class="note sub">一张圆桌大小，直径 60 厘米。</p>
    <svg class="dia" viewBox="0 0 400 380" role="img" aria-label="SoundMat 分层结构">
      <!-- 毛毡 -->
      <ellipse class="felt" cx="130" cy="50" rx="115" ry="30"/>
      <ellipse class="ln" cx="130" cy="50" rx="115" ry="30"/>
      <ellipse class="ln2" cx="130" cy="50" rx="78" ry="20"/>
      <ellipse class="ln2" cx="130" cy="50" rx="40" ry="10"/>
      <ellipse cx="105" cy="44" rx="11" ry="5" fill="currentColor" opacity=".55"/>
      <ellipse cx="165" cy="55" rx="9" ry="4" fill="currentColor" opacity=".4"/>
      <ellipse cx="140" cy="36" rx="7" ry="3.5" fill="currentColor" opacity=".7"/>
      <!-- 感应层 -->
      <g transform="translate(0,90)">
        <ellipse class="bg" cx="130" cy="50" rx="115" ry="30"/>
        <ellipse class="ln acc" cx="130" cy="50" rx="115" ry="30"/>
        <ellipse class="ln2" cx="130" cy="50" rx="100" ry="26"/>
        <ellipse class="ln2" cx="130" cy="50" rx="85" ry="22"/>
        <ellipse class="ln2" cx="130" cy="50" rx="70" ry="18"/>
        <ellipse class="ln2" cx="130" cy="50" rx="55" ry="14"/>
        <ellipse class="ln2" cx="130" cy="50" rx="40" ry="10"/>
        <ellipse class="ln2" cx="130" cy="50" rx="25" ry="6.5"/>
        <g class="ln2">
          <line x1="130" y1="50" x2="245" y2="50"/><line x1="130" y1="50" x2="15" y2="50"/>
          <line x1="130" y1="50" x2="130" y2="20"/><line x1="130" y1="50" x2="130" y2="80"/>
          <line x1="130" y1="50" x2="211" y2="29"/><line x1="130" y1="50" x2="49" y2="71"/>
          <line x1="130" y1="50" x2="211" y2="71"/><line x1="130" y1="50" x2="49" y2="29"/>
        </g>
      </g>
      <!-- 木板 + 灯环 -->
      <g transform="translate(0,170)">
        <ellipse class="bg" cx="130" cy="50" rx="115" ry="30"/>
        <ellipse class="ln" cx="130" cy="50" rx="115" ry="30"/>
        <ellipse cx="130" cy="50" rx="108" ry="27" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-dasharray="1 5" stroke-linecap="round"/>
      </g>
      <!-- 碗形外壳 -->
      <g transform="translate(0,250)">
        <path class="ln bg" d="M15 40 L55 105 A75 18 0 0 0 205 105 L245 40"/>
        <ellipse class="ln" cx="130" cy="40" rx="115" ry="30" fill="none"/>
        <rect class="ln2" x="95" y="55" width="30" height="20" rx="3"/>
        <rect class="ln2" x="135" y="58" width="22" height="16" rx="3"/>
        <path class="ln2" d="M125 65 L135 66"/>
      </g>
      <!-- 引线和标签 -->
      <g class="ln2"><path d="M248 50 H268"/><path d="M248 140 H268"/><path d="M248 220 H268"/><path d="M248 300 H268"/></g>
      <text x="274" y="46">毛毡</text><text class="soft" x="274" y="64">手摸得到的一面</text>
      <text x="274" y="136">压力感应层</text><text class="soft" x="274" y="154">8 圈，224 个格子</text>
      <text x="274" y="216">木板和一圈灯</text><text class="soft" x="274" y="234">108 颗</text>
      <text x="274" y="296">碗形外壳</text><text class="soft" x="274" y="314">电路都藏在里面</text>
    </svg>
  </div>

  <div>
    <h3>放下一颗石头之后</h3>
    <p class="note sub">整个过程是实时的。</p>
    <ol class="steps">
      <li>
        <svg class="dia ic" viewBox="0 0 72 56"><ellipse class="felt" cx="36" cy="42" rx="32" ry="9"/><ellipse class="ln" cx="36" cy="42" rx="32" ry="9"/><ellipse cx="36" cy="22" rx="9" ry="5.5" fill="currentColor" opacity=".6"/><path class="ln2" d="M36 30 V36 M33 33 L36 36 L39 33"/></svg>
        <p><span class="n">1</span>把石头放在毛毡上。</p>
      </li>
      <li>
        <svg class="dia ic" viewBox="0 0 72 56"><ellipse class="ln" cx="36" cy="30" rx="32" ry="12"/><ellipse class="ln2" cx="36" cy="30" rx="22" ry="8"/><ellipse class="ln2" cx="36" cy="30" rx="12" ry="4.5"/><path class="ln2" d="M36 30 L68 30 M36 30 L36 18 M36 30 L60 21"/><path d="M57 22.5 L66 26 L67 30 L58 30 Z" fill="var(--accent)" opacity=".85"/></svg>
        <p><span class="n">2</span>下面的感应层被压到，知道它在第几圈、第几格，有多重。</p>
      </li>
      <li>
        <svg class="dia ic" viewBox="0 0 72 56"><rect class="ln" x="18" y="14" width="36" height="28" rx="4"/><path class="ln2" d="M24 14 V9 M32 14 V9 M40 14 V9 M48 14 V9 M24 42 V47 M32 42 V47 M40 42 V47 M48 42 V47"/><path d="M33 34 V22 L42 20 V31" class="ln acc"/><circle cx="31" cy="34" r="2.6" class="accf"/><circle cx="40" cy="31" r="2.6" class="accf"/></svg>
        <p><span class="n">3</span>装置里的小电脑按位置挑出声音，当场合成。</p>
      </li>
      <li>
        <svg class="dia ic" viewBox="0 0 72 56"><rect class="ln" x="14" y="12" width="22" height="34" rx="3"/><circle class="ln" cx="25" cy="34" r="6"/><circle class="ln" cx="25" cy="20" r="3"/><path class="ln2" d="M44 22 Q49 29 44 36 M50 17 Q58 29 50 41 M56 12 Q67 29 56 46"/></svg>
        <p><span class="n">4</span>房间里的音箱放出来，那颗石头旁边的灯同时亮一下。</p>
      </li>
    </ol>
  </div>
</div>

<!-- ④ 理念 -->
<div class="quote">
  <p class="q">“那里有一个奇怪的装置，上面放着好多石头。挪动一下，会听到什么呢？”</p>
  <p class="note">想让人在大厅、展厅里路过时，被它勾起好奇心。</p>
</div>

<figure class="full"><img src="img/stones.jpg" alt="几个人围着 SoundMat 摆石头"></figure>

<div class="quote">
  <p class="q">希望大家体验到音乐与声音的乐趣。</p>
  <p class="note">不需要会乐器，也不会放错。音乐可以认真听，也可以只当作空间里的背景。</p>
</div>

<!-- ⑤ 怎么造出来的 -->
<div class="section-head">
  <p class="lead">它是怎么做出来的</p>
  <p>从一个念头到能搬上草地，两个月做出第一版，之后一直在改。</p>
</div>

<div class="tl">
  <div class="tl__i up key"><div><b>4 月 8 日</b><span>想到用石头演奏音乐</span></div></div>
  <div class="tl__i down"><div><b>4 月</b><span>先做一块小感应垫试试</span></div></div>
  <div class="tl__i up"><div><b>5 月</b><span>感应层、电路、外壳</span></div></div>
  <div class="tl__i down"><div><b>5 月底</b><span>声音和软件</span></div></div>
  <div class="tl__i up key"><div><b>6 月 4 日</b><span>课上第一次展示</span></div></div>
  <div class="tl__i down"><div><b>之后</b><span>进入 DXARTS 的实验室继续做</span></div></div>
  <div class="tl__i up key"><div><b>10 月</b><span>正式拍摄</span></div></div>
  <div class="tl__i down future"><div><b>以后</b><span>继续做下去</span></div></div>
</div>

<div>
  <h3 class="block-title">里面是什么</h3>
  <p class="note" style="margin:0 0 24px">感应、计算、发声、灯光，一根电源线带动全部。</p>
  <svg class="dia" viewBox="0 0 800 250" role="img" aria-label="SoundMat 内部系统">
    <defs><marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="currentColor" stroke-width="1.2"/></marker></defs>
    <!-- 盒子 -->
    <g>
      <rect class="ln" x="1" y="30" width="150" height="74" rx="8"/>
      <text x="16" y="60">压力感应层</text><text class="soft" x="16" y="84">224 个格子</text>
      <rect class="ln" x="216" y="30" width="150" height="74" rx="8"/>
      <text x="231" y="60">ESP32</text><text class="soft" x="231" y="84">每秒扫二三十遍</text>
      <rect class="ln acc" x="431" y="30" width="190" height="74" rx="8"/>
      <text x="446" y="60">树莓派</text><text class="soft" x="446" y="84">决定响什么，合成声音</text>
      <rect class="ln" x="686" y="30" width="113" height="74" rx="8"/>
      <text x="701" y="60">音箱</text><text class="soft" x="701" y="84">房间里的</text>
      <rect class="ln" x="216" y="160" width="150" height="74" rx="8"/>
      <text x="231" y="190">灯环</text><text class="soft" x="231" y="214">108 颗灯</text>
      <rect class="ln2" x="431" y="160" width="190" height="74" rx="8" stroke-dasharray="4 4"/>
      <text x="446" y="190">电源 20V</text><text class="soft" x="446" y="214">降压后分给电脑和灯</text>
    </g>
    <!-- 箭头 -->
    <g class="ln" marker-end="url(#ar)">
      <path d="M155 67 H210"/>
      <path d="M370 58 H425"/>
      <path d="M625 67 H680"/>
      <path d="M291 108 V154"/>
    </g>
    <path class="ln2" d="M425 78 H372" marker-end="url(#ar)"/>
    <text class="soft" x="378" y="96" style="font-size:12px">亮哪里</text>
    <text class="soft" x="378" y="50" style="font-size:12px">数据</text>
  </svg>
</div>

<div class="grid3">
  <figure class="ph"><img src="img/sensor-build.jpg" alt=""><figcaption>感应层：导电布剪成一圈圈、一条条，中间夹一层压敏膜。</figcaption></figure>
  <figure class="ph"><img src="img/board.jpg" alt=""><figcaption>电路焊在洞洞板上，ESP32 和多路开关一格格去读。</figcaption></figure>
  <figure class="ph"><img src="img/making-inside.jpg" alt=""><figcaption>装进碗形外壳，盖上毛毡。</figcaption></figure>
</div>

<!-- ⑥ 拍摄的照片 -->
<figure class="full"><img src="img/leaves.jpg" alt=""></figure>
<div class="grid2">
  <figure class="ph"><img src="img/waiting.jpg" alt=""></figure>
  <figure class="ph"><img src="img/together.jpg" alt=""></figure>
</div>
<div class="grid2">
  <figure class="ph"><img src="img/ring.jpg" alt=""></figure>
  <figure class="ph"><img src="img/hands-dark.jpg" alt=""></figure>
</div>

<!-- ⑦ 视频 -->
<figure>
  <video controls preload="none" poster="img/poster.jpg" src="https://media.mukii.space/soundmat/soundmat-film-20261023.mp4"></video>
  <figcaption>2026 年 10 月，华盛顿大学 DXARTS Media Lab。</figcaption>
</figure>

<p>和 Po-Yu Chen、Fay Ma、Sora Kim 一起做。完整的设计和制作文档：<a href="https://mukii.space/soundmat/">mukii.space/soundmat</a></p>


<script>
  // 两个垫子：一个开始播放，另一个停；网页切深浅色时告诉垫子
  const frames = [...document.querySelectorAll('.play iframe')];
  window.addEventListener('message', (e) => {
    if (e.data && e.data.soundmat === 'playing') {
      frames.forEach(f => { if (f.contentWindow !== e.source) f.contentWindow.postMessage({ soundmat: 'stop' }, '*'); });
    }
  });
  const theme = () => {
    const t = document.documentElement.dataset.theme;
    return t || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  };
  const send = () => frames.forEach(f => f.contentWindow && f.contentWindow.postMessage({ theme: theme() }, '*'));
  new MutationObserver(send).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  frames.forEach(f => f.addEventListener('load', send));
</script>
{{< /html >}}
