#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Satranç Pro — Cross-platform satranç sunucusu (Linux + Windows)
# Gereksinim: Python 3.8+. Başka hiçbir paket/internet gerekmez.

import argparse, glob, hmac, io, ipaddress, json, math, os, platform, queue, re, secrets, shutil, socket, subprocess, sys, threading, time, wave, webbrowser
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

VERSION = "2.0"
TR = (os.environ.get("LC_ALL") or os.environ.get("LANG") or "").lower().startswith("tr")
def tx(tr, en): return tr if TR else en

# ---------- Gömülü arayüz dosyaları ----------
INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Chess</title>
<meta name="theme-color" content="#0b1020">
<meta name="color-scheme" content="dark light">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icon.svg">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="stylesheet" href="/app.css">
</head>
<body>
<div id="bg"><i></i><i></i><i></i></div>
<div class="app">
  <header class="top">
    <div class="brand"><span class="logo">&#9822;&#xFE0E;</span><span id="appName">Satranç Pro</span></div>
    <nav class="nav-links">
      <button class="nav-btn on" id="btnPlayTab" title="Yeni Oyun / Oyna"><img src="/sprite/play-white.svg" alt="" class="nav-ic"><span>Oyna</span></button>
      <button class="nav-btn" id="btnBotTab" title="Botlar & Stockfish"><img src="/sprite/device-bot.svg" alt="" class="nav-ic"><span>Botlar</span></button>
      <button class="nav-btn" id="btnPuzzleTab" title="Taktik Bulmacalar"><img src="/sprite/puzzle-piece.svg" alt="" class="nav-ic"><span>Bulmacalar</span></button>
      <button class="nav-btn" id="btnOnlineTab" title="Çok Oyunculu Davet"><img src="/sprite/friends.svg" alt="" class="nav-ic"><span>Online</span></button>
    </nav>
    <nav class="tools">
      <button class="ib" id="bConnect" data-it="connect" title="Bağlantı / QR">&#9638;</button>
      <button class="ib" id="bSettings" data-it="settings" title="Ayarlar">&#9881;&#xFE0E;</button>
      <button class="ib" id="bFull" data-it="fullscreen" title="Tam Ekran">&#9974;&#xFE0E;</button>
    </nav>
  </header>
  <main class="layout">
    <section class="stage" id="stage">
      <div class="pl" id="plTop"></div>
      <div class="bw">
        <div id="board">
          <div id="sqs"></div>
          <div id="pieces"></div>
          <svg id="ov" viewBox="0 0 8 8"></svg>
        </div>
        <div class="promo" id="promo" hidden></div>
        <div class="result" id="result" hidden></div>
      </div>
      <div class="pl" id="plBot"></div>
    </section>
    <aside class="panel">
      <div id="gamePanel" style="display:flex;flex-direction:column;gap:12px;width:100%;min-width:0;box-sizing:border-box;">
        <div class="status" id="status"></div>
        <div class="banner" id="banner" hidden></div>
        <div class="moves" id="moves"></div>
        <div class="nav">
          <button class="btn" id="nFirst">&laquo;</button><button class="btn" id="nPrev">&lsaquo;</button>
          <button class="btn" id="nNext">&rsaquo;</button><button class="btn" id="nLast">&raquo;</button>
        </div>
        <button class="btn" id="aReview" style="background:linear-gradient(145deg,#2e7d32,#1b5e20);color:#fff;font-weight:700;display:none;width:100%;border-color:rgba(255,255,255,.2);box-shadow:0 4px 14px rgba(46,125,50,.35);align-items:center;justify-content:center;gap:7px;"><img src="/sprite/magnifier-analysis.svg" alt="" style="width:18px;height:18px;object-fit:contain;"><span>Maçı Analiz Et (Game Review)</span></button>
      </div>
      <div id="reviewSidebar" style="display:none;flex-direction:column;gap:10px;width:100%;min-width:0;box-sizing:border-box;"></div>
      <div class="acts" id="gameActs">
        <button class="btn pri" id="aNew" data-i="newGame"></button>
        <button class="btn" id="aFlip" data-i="flip"></button>
        <button class="btn" id="aUndo" data-i="undo"></button>
        <button class="btn" id="aHint"><img src="/sprite/puzzle-hint.svg" alt="" style="width:16px;height:16px;object-fit:contain;"><span data-i="hint"></span></button>
        <button class="btn" id="aDraw" data-i="draw"></button>
        <button class="btn" id="aResign" data-i="resign"></button>
        <button class="btn" id="aInvite" data-i="invite" hidden></button>
        <button class="btn" id="aPgn" data-i="pgn"></button>
      </div>
    </aside>
  </main>
</div>
<canvas id="fx"></canvas>
<div id="toasts" aria-live="polite"></div>
<div id="modals"></div>
<button id="bExitGame" class="exit-btn" title="Çıkış / Ayrıl"><svg viewBox="0 0 24 24"><path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg><span>Çıkış</span></button>
<script src="/i18n.js"></script>
<script src="/engine.js"></script>
<script src="/app.js"></script>
</body>
</html>
"""
APP_CSS = r"""
/* Nav-links & Chess.com Sprites */
.nav-links{display:flex;align-items:center;gap:6px;margin:0 12px}
.nav-btn{display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:10px;border:1px solid transparent;background:transparent;color:var(--ink);font-weight:600;font-size:13px;cursor:pointer;transition:all .15s}
.nav-btn:hover{background:rgba(255,255,255,.08);border-color:var(--line)}
.nav-btn.on{background:var(--acc);color:#1b1206}
.nav-ic{width:20px;height:20px;object-fit:contain}
@media (max-width:768px){.nav-btn span{display:none}.nav-btn{padding:6px 8px}}

/* Eval Bar */
.bw-container{display:flex;align-items:center;justify-content:center;gap:12px;position:relative}
.eval-wrap{width:22px;height:min(86vmin,640px);background:#22252a;border-radius:6px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,.4);display:flex;flex-direction:column;position:relative;border:1px solid var(--line);flex-shrink:0}
.eval-fill{background:#f0f2f5;width:100%;margin-top:auto;transition:height .35s cubic-bezier(.4,0,.2,1)}
.eval-badge{position:absolute;left:0;right:0;text-align:center;font:700 10px/1.2 sans-serif;pointer-events:none;z-index:2;color:#111;padding:2px 0}
.eval-badge.top{top:4px;color:#eee;text-shadow:0 0 2px rgba(0,0,0,.8)}
.eval-badge.bot{bottom:4px;color:#111}

/* Bot Selection Grid & Cards */
.bot-tabs{display:flex;gap:8px;margin-bottom:12px}
.bot-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;max-height:440px;overflow-y:auto;padding-right:4px}
.bot-card{display:flex;flex-direction:column;align-items:center;text-align:center;gap:8px;padding:12px 10px;border-radius:16px;border:1px solid var(--line);background:var(--glass);cursor:pointer;transition:all .15s}
.bot-card:hover{transform:translateY(-3px);border-color:var(--acc);background:rgba(255,255,255,.08)}
.bot-card.on{border-color:var(--acc);box-shadow:0 0 0 2px var(--acc) inset}
.bot-avatar{width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid var(--acc);box-shadow:0 4px 10px rgba(0,0,0,.35)}
.bot-name{font-weight:700;font-size:14px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:100%}
.bot-elo{font-size:12px;font-weight:600;padding:2px 8px;border-radius:99px;background:rgba(255,255,255,.1);color:var(--acc)}
.bot-desc{font-size:11px;color:var(--mute);line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* Opponent Avatar & Card in Player Bar */
.pl-avatar{width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid var(--line);margin-right:8px;flex-shrink:0}
.pl-info{display:flex;align-items:center;gap:4px}
.pl-elo{font-size:11px;padding:1px 6px;border-radius:6px;background:rgba(255,255,255,.12);color:var(--acc);font-weight:700}

/* Chess.com Tarzı İnsan Bot Konuşma Baloncuğu (Tahtayı Asla İtmez, Havada Sabit Süzülür) */
.pl{position:relative;display:flex;align-items:center;gap:10px;height:46px;min-height:46px}
.bot-bubble-wrap{position:absolute;left:240px;top:50%;transform:translateY(-50%);z-index:40;pointer-events:none}
.bot-bubble{position:relative;background:rgba(18,24,46,.94);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.2);color:#f0f3fa;padding:7px 16px;border-radius:12px;font-size:13px;font-weight:500;box-shadow:0 8px 24px rgba(0,0,0,.5);white-space:nowrap;max-width:320px;overflow:hidden;text-overflow:ellipsis;animation:bubblePop .24s cubic-bezier(.175,.885,.32,1.275)}
.bot-bubble::before{content:"";position:absolute;left:-7px;top:50%;transform:translateY(-50%);border-width:6px 7px 6px 0;border-style:solid;border-color:transparent rgba(255,255,255,.2) transparent transparent}
.bot-bubble::after{content:"";position:absolute;left:-6px;top:50%;transform:translateY(-50%);border-width:5px 6px 5px 0;border-style:solid;border-color:transparent rgba(18,24,46,.95) transparent transparent}
@keyframes bubblePop{from{opacity:0;transform:scale(.85) translateX(-8px)}to{opacity:1;transform:scale(1) translateX(0)}}
.bot-bubble.fade-out{animation:bubbleFade .4s ease-out forwards}
@keyframes bubbleFade{to{opacity:0;transform:translateY(-4px)}}


/* Koç Analizi & Game Review */
.coach-wrap{display:flex;flex-direction:column;gap:10px;background:var(--bg2);border-radius:14px;padding:12px;border:1px solid var(--line);box-shadow:0 6px 20px rgba(0,0,0,.3);width:100%;min-width:0;box-sizing:border-box}
.coach-header{display:flex;align-items:center;gap:10px}
.coach-av{width:46px;height:46px;border-radius:50%;object-fit:cover;border:2px solid var(--acc);box-shadow:0 4px 12px rgba(0,0,0,.4);flex-shrink:0}
.coach-title{font-weight:700;font-size:15px;color:var(--ink)}
.coach-sub{font-size:11px;color:var(--mute)}
.coach-bubble{position:relative;background:var(--glass2);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font-size:13px;line-height:1.45;color:var(--ink);box-shadow:0 4px 14px rgba(0,0,0,.2);width:100%;min-width:0;box-sizing:border-box;word-break:break-word}
.coach-bubble::before{content:"";position:absolute;top:-8px;left:20px;border-width:0 8px 8px 8px;border-style:solid;border-color:transparent transparent var(--line) transparent}
.coach-audio-btn{display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:99px;border:1px solid var(--line);background:var(--glass);font-size:11px;font-weight:600;color:var(--ink);cursor:pointer;margin-top:6px;transition:all .15s}
.coach-audio-btn:hover{background:var(--acc);color:#1b1206}
.coach-audio-btn.playing{background:var(--acc);color:#1b1206;animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.7}}

/* Accuracy Bars & Circles */
.acc-row{display:flex;gap:10px;align-items:center;margin:6px 0;width:100%;box-sizing:border-box}
.acc-box{flex:1;display:flex;flex-direction:column;gap:3px;padding:8px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid var(--line);text-align:center;min-width:0}
.acc-val{font-size:20px;font-weight:800;color:var(--acc)}
.acc-label{font-size:10px;color:var(--mute);text-transform:uppercase;letter-spacing:1px}

/* Chess.com Style Game Review Tabs */
.review-tabs{display:flex;gap:0;border-bottom:2px solid var(--line);margin-bottom:8px;width:100%;min-width:0;box-sizing:border-box}
.review-tab{flex:1;padding:8px 4px;text-align:center;font-weight:700;font-size:12px;cursor:pointer;border-bottom:3px solid transparent;color:var(--mute);transition:all .15s;background:none;border-top:0;border-left:0;border-right:0;white-space:nowrap}
.review-tab.on{color:var(--ink);border-bottom-color:var(--acc)}
.review-tab:hover{color:var(--ink)}

/* Accuracy Display */
.acc-big{display:flex;align-items:center;justify-content:space-around;gap:12px;padding:8px 4px;margin:4px 0;width:100%;min-width:0;box-sizing:border-box}
.acc-circle{width:62px;height:62px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;border:3px solid;flex-shrink:0}
.acc-circle.w{border-color:#f0f2f5;color:#f0f2f5;background:rgba(240,242,245,.1)}
.acc-circle.b{border-color:#555;color:#bbb;background:rgba(60,60,60,.3)}
.acc-side{text-align:center;display:flex;flex-direction:column;align-items:center;gap:4px;min-width:0}
.acc-name{font-size:11px;color:var(--mute);font-weight:600}
.acc-score-label{font-size:10px;color:var(--mute)}

/* Game Description Badge */
.game-desc{text-align:center;padding:6px;font-size:12px;font-weight:700;color:var(--acc);letter-spacing:1.5px;width:100%;box-sizing:border-box}
.game-desc-text{font-size:11px;color:var(--mute);font-weight:400;font-style:italic;margin-top:3px}

/* Category Count Table */
.cat-table{width:100%;min-width:0;border-collapse:collapse;margin:6px 0;box-sizing:border-box}
.cat-table td{padding:5px 4px;font-size:11px;font-weight:600;border-bottom:1px solid rgba(255,255,255,.06);white-space:nowrap}
.cat-table td:first-child{text-align:right;width:55px;padding-right:12px}
.cat-table td:nth-child(2){text-align:center}
.cat-table td:last-child{text-align:left;width:55px;padding-left:12px}
.cat-icon{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;font-size:10px;font-weight:800;vertical-align:middle;box-shadow:0 2px 6px rgba(0,0,0,.3);flex-shrink:0}
.ci-brilliant{background:#26c9c9;color:#041824}
.ci-great{background:#5b9bd5;color:#fff}
.ci-best{background:#96bc4b;color:#102202}
.ci-excellent{background:#96bc4b;color:#102202}
.ci-good{background:#a3c947;color:#102202}
.ci-book{background:#a1887f;color:#fff}
.ci-inaccuracy{background:#f0c348;color:#2e2202}
.ci-mistake{background:#e58c2a;color:#2e1500}
.ci-miss{background:#db6249;color:#fff}
.ci-blunder{background:#ca3431;color:#fff}

/* Move Badges */
.badge-brilliant{background:#26c9c9;color:#041824;font-weight:800;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px;box-shadow:0 0 10px rgba(38,201,201,.5)}
.badge-great{background:#5b9bd5;color:#fff;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-best{background:#96bc4b;color:#102202;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-excellent{background:#96bc4b;color:#102202;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-good{background:#a3c947;color:#102202;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-book{background:#a1887f;color:#fff;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-inaccuracy{background:#f0c348;color:#2e2202;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-mistake{background:#e58c2a;color:#2e1500;font-weight:700;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-miss{background:#db6249;color:#fff;font-weight:800;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px}
.badge-blunder{background:#ca3431;color:#fff;font-weight:800;padding:2px 6px;border-radius:6px;display:inline-flex;align-items:center;gap:4px;box-shadow:0 0 10px rgba(202,52,49,.5)}

/* Phase Rating Row */
.phase-row{display:flex;align-items:center;justify-content:space-between;padding:5px 8px;border-bottom:1px solid rgba(255,255,255,.06);width:100%;box-sizing:border-box}
.phase-name{font-size:12px;font-weight:600;flex:1}
.phase-badge{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;font-size:10px;flex-shrink:0}

/* Game Rating */
.game-rating-row{display:flex;align-items:center;justify-content:space-between;padding:7px 10px;background:rgba(255,255,255,.04);border-radius:8px;margin:6px 0;width:100%;box-sizing:border-box}
.game-rating-label{font-size:12px;font-weight:600}
.game-rating-val{padding:3px 10px;border-radius:6px;font-weight:800;font-size:13px}
.gr-w{background:#444;color:#f0f2f5}
.gr-b{background:#222;color:#bbb}

/* Eval Graph */
.eval-graph-wrap{position:relative;width:100%;height:70px;background:rgba(0,0,0,.25);border-radius:8px;overflow:hidden;margin:6px 0;border:1px solid var(--line);box-sizing:border-box}
.eval-graph-mid{position:absolute;top:50%;left:0;right:0;height:1px;background:rgba(255,255,255,.15)}
.eval-graph-svg{width:100%;height:100%;display:block}
.eval-area-w{fill:rgba(240,242,245,.25)}
.eval-area-b{fill:rgba(30,30,30,.45)}
.eval-line{fill:none;stroke:rgba(255,255,255,.65);stroke-width:1.5}
.eval-dot{r:3;fill:var(--acc);stroke:var(--bg2);stroke-width:1}
.eval-dot.bad{fill:#ca3431}
.eval-dot.miss{fill:#db6249}
.eval-dot.inac{fill:#f0c348}

/* Review Progress Card */
.review-prog-card{display:flex;flex-direction:column;align-items:center;text-align:center;padding:24px 14px;gap:12px;width:100%;box-sizing:border-box;background:var(--bg2);border-radius:16px;border:1px solid var(--line);box-shadow:0 10px 30px rgba(0,0,0,.35)}
.review-prog-track{width:100%;height:10px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden;border:1px solid var(--line);margin:6px 0}
.review-prog-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#81b64c,#5fe0a0);transition:width .2s ease-out;box-shadow:0 0 10px rgba(95,224,160,.5)}
.review-prog-pct{font-size:26px;font-weight:800;color:var(--acc);font-variant-numeric:tabular-nums}

/* Review Move Detail */
.review-detail{display:flex;align-items:flex-start;gap:10px;padding:10px;border-radius:10px;background:rgba(255,255,255,.04);border:1px solid var(--line);margin:6px 0;transition:all .15s;width:100%;box-sizing:border-box}
.review-detail:hover{background:rgba(255,255,255,.08);border-color:var(--acc)}
.review-played{display:flex;flex-direction:column;gap:2px}
.review-played-move{font-size:16px;font-weight:800}
.review-best-line{font-size:12px;color:var(--mute)}
.review-best-move{color:#96bc4b;font-weight:700}

/* Start Review Button */
.start-review-btn{width:100%;padding:14px;border-radius:14px;font-size:16px;font-weight:800;cursor:pointer;border:none;background:linear-gradient(145deg,#81b64c,#5a8a32);color:#fff;box-shadow:0 4px 18px rgba(90,138,50,.45);transition:all .15s;display:flex;align-items:center;justify-content:center;gap:10px;margin-top:10px}
.start-review-btn:hover{transform:translateY(-1px);box-shadow:0 6px 24px rgba(90,138,50,.55)}

/* Analysis Move List */
.analysis-moves{max-height:240px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--acc) transparent;border-radius:10px;background:rgba(0,0,0,.15);padding:4px}
.analysis-move-row{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:8px;cursor:pointer;transition:all .1s}
.analysis-move-row:hover{background:rgba(255,255,255,.08)}
.analysis-move-row.on{background:rgba(255,214,102,.15);border:1px solid var(--acc)}
.analysis-move-num{font-size:11px;color:var(--mute);min-width:28px;text-align:right}
.analysis-move-san{font-size:14px;font-weight:700;flex:1}
.analysis-move-badge{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;font-size:9px;font-weight:800}

/* Moves Review Grid */
.moves-review-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:6px;max-height:180px;overflow-y:auto;padding-right:4px}
.review-item{padding:6px 8px;border-radius:8px;background:rgba(255,255,255,.05);border:1px solid var(--line);font-size:12px;font-weight:600;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:all .12s}
.review-item:hover{background:rgba(255,255,255,.12);border-color:var(--acc)}
.review-item.on{border-color:var(--acc);background:rgba(255,214,102,.15)}

/* Review Sidebar Layout */
#reviewSidebar{display:none;flex-direction:column!important;gap:10px;width:100%!important;min-width:0!important;box-sizing:border-box!important}
#reviewSidebar>*{width:100%!important;min-width:0!important;box-sizing:border-box!important}
#reviewSidebar .mhead{display:flex!important;justify-content:space-between!important;align-items:center!important;width:100%!important;box-sizing:border-box!important;padding:4px 0 8px 0;border-bottom:1px solid var(--line)}

/* Exit Button (Sağ altta hafif kırmızılıkta çıkış) */
.exit-btn{position:fixed;bottom:16px;right:16px;z-index:55;display:none;align-items:center;gap:6px;padding:8px 16px;border-radius:12px;border:1px solid rgba(255,80,80,.4);background:rgba(40,10,10,.85);backdrop-filter:blur(12px);color:#ff6b6b;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(255,80,80,.2);transition:all .15s}
.exit-btn:hover{background:rgba(80,15,15,.95);border-color:rgba(255,80,80,.7);transform:translateY(-1px)}
.exit-btn svg{width:16px;height:16px;fill:currentColor}

/* Puzzles */
.puzzle-box{display:flex;flex-direction:column;gap:12px;align-items:center;text-align:center}
.puzzle-title{font:600 20px/1.2 var(--serif);color:var(--ink)}
.puzzle-desc{font-size:14px;color:var(--mute)}
.puzzle-badge{display:inline-block;padding:3px 10px;border-radius:99px;background:var(--acc);color:#1b1206;font-weight:700;font-size:12px}
*{box-sizing:border-box;margin:0}
:root{
  --bg1:#0b1020;--bg2:#141c3d;--ink:#eef0f7;--mute:#9aa3c2;--glass:rgba(255,255,255,.07);--glass2:rgba(255,255,255,.13);
  --line:rgba(255,255,255,.14);--acc:#e6b566;--acc2:#54d2c0;--bad:#ff6b81;--good:#5fe0a0;--dur:.26s;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Noto Serif",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","Helvetica Neue",Arial,sans-serif;
  --u:1cqw;--light:#f0d9b5;--dark:#b58863;--cl:var(--dark);--cd:var(--light);
  --last:rgba(255,213,74,.45);--sel:rgba(80,210,140,.5);--dot:rgba(15,30,20,.32);
  color-scheme:dark}
:root[data-mode=light]{--bg1:#eef1fa;--bg2:#d9e1f7;--ink:#161c36;--mute:#59628a;--glass:rgba(255,255,255,.62);--glass2:rgba(255,255,255,.9);
  --line:rgba(22,28,54,.14);--acc:#b87a14;--acc2:#0e8f80;color-scheme:light}
[data-board=wood]{--light:#f0d9b5;--dark:#b58863}
[data-board=emerald]{--light:#eeeed2;--dark:#769656;--cl:#769656;--cd:#eeeed2}
[data-board=ice]{--light:#e8f0f8;--dark:#7fa3c7}
[data-board=night]{--light:#6c7792;--dark:#394159;--cl:#394159;--cd:#aab3cc;--last:rgba(255,200,80,.35)}
[data-board=violet]{--light:#ece0f9;--dark:#8d6fc4;--sel:rgba(255,220,120,.55)}
[data-board=marble]{--light:#f4f4f0;--dark:#a6a9a8;--last:rgba(230,160,40,.4)}
[data-board=glass]{--light:rgba(255,255,255,.2);--dark:rgba(255,255,255,.05);--cl:rgba(255,255,255,.7);--cd:rgba(255,255,255,.7);--last:rgba(120,220,255,.28);--sel:rgba(255,255,255,.3);--dot:rgba(255,255,255,.5)}
[data-board=neon]{--light:#121b3d;--dark:#0a1029;--cl:#4fd8ff;--cd:#4fd8ff;--last:rgba(255,60,200,.28);--sel:rgba(79,216,255,.35);--dot:rgba(79,216,255,.7)}
html,body{height:100%}
body{font:15px/1.45 var(--sans);color:var(--ink);background:var(--bg1);overflow-x:hidden;-webkit-tap-highlight-color:transparent}
button,select,input{font:inherit;color:inherit}
button{cursor:pointer}
:focus-visible{outline:2px solid var(--acc2);outline-offset:2px}
#bg{position:fixed;inset:0;z-index:-1;background:linear-gradient(160deg,var(--bg1),var(--bg2));overflow:hidden}
#bg i{position:absolute;width:55vmax;height:55vmax;border-radius:50%;filter:blur(90px);opacity:.38;animation:drift 26s ease-in-out infinite alternate}
#bg i:nth-child(1){background:#3b4fd8;left:-15vmax;top:-18vmax}
#bg i:nth-child(2){background:#0f9d8a;right:-20vmax;bottom:-22vmax;animation-delay:-9s}
#bg i:nth-child(3){background:#b9792b;width:30vmax;height:30vmax;left:45%;top:35%;opacity:.16;animation-delay:-17s}
:root[data-mode=light] #bg i{opacity:.22}
@keyframes drift{to{transform:translate(6vmax,4vmax) scale(1.12)}}
.app{min-height:100dvh;display:flex;flex-direction:column}
.top{display:flex;align-items:center;justify-content:space-between;padding:calc(10px + env(safe-area-inset-top)) 18px 6px;max-width:1240px;width:100%;margin:0 auto}
.brand{display:flex;align-items:center;gap:10px;font:600 26px/1 var(--serif);letter-spacing:.2px}
.logo{display:grid;place-items:center;width:38px;height:38px;border-radius:11px;background:linear-gradient(145deg,var(--acc),#a86a1c);color:#1b1206;font:24px/1 "Segoe UI Symbol","Noto Sans Symbols 2","Apple Symbols","DejaVu Sans",sans-serif;box-shadow:0 6px 18px rgba(230,181,102,.35)}
.tools{display:flex;gap:8px}
.ib{width:42px;height:42px;border-radius:12px;border:1px solid var(--line);background:var(--glass);backdrop-filter:blur(14px);font-size:19px;display:grid;place-items:center;transition:transform .15s,background .15s}
.ib:hover{background:var(--glass2);transform:translateY(-1px)}
.layout{flex:1;display:grid;grid-template-columns:minmax(0,1fr) 370px;gap:22px;padding:10px 18px calc(22px + env(safe-area-inset-bottom));max-width:1240px;width:100%;margin:0 auto;align-items:start}
.stage{width:min(100%,calc(100dvh - 190px));min-width:300px;margin:0 auto;display:flex;flex-direction:column;gap:10px}
.pl{display:flex;align-items:center;gap:10px;min-height:46px}
.av{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font:25px/1 "Segoe UI Symbol","Noto Sans Symbols 2","Apple Symbols","DejaVu Sans",sans-serif;border:1px solid var(--line);flex:none;position:relative;overflow:hidden;background:rgba(255,255,255,.05)}
.av img{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px}
.av.w{background:linear-gradient(145deg,#fff,#cfd5e6);color:#20263d}
.av.b{background:linear-gradient(145deg,#3a4262,#161b30);color:#f2f4ff}
.av .dot{position:absolute;right:-3px;bottom:-3px;width:11px;height:11px;border-radius:50%;background:#6b7390;border:2px solid var(--bg1)}
.av .dot.on{background:var(--good)}
.nm{flex:1;min-width:0;display:flex;flex-direction:column}
.nm b{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cp{display:flex;align-items:center;height:20px;font:16px/1 "Segoe UI Symbol","Noto Sans Symbols 2","Apple Symbols","DejaVu Sans",sans-serif;white-space:nowrap;gap:4px}
.mat-pieces{color:rgba(255,255,255,.75);font-size:16px;letter-spacing:1px}
.mat-lead{font:700 11px/1 var(--sans);color:#10b981;background:rgba(16,185,129,.18);border:1px solid rgba(16,185,129,.35);padding:2px 6px;border-radius:6px;margin-left:4px;font-style:normal}
.clk{font:600 20px/1 var(--sans);font-variant-numeric:tabular-nums;padding:9px 12px;border-radius:10px;background:var(--glass);border:1px solid var(--line);min-width:78px;text-align:center}
.clk.run{background:var(--glass2);border-color:var(--acc)}
.clk.low{color:var(--bad);animation:blink 1s steps(2) infinite}
.clk[hidden]{display:none}
@keyframes blink{50%{opacity:.55}}
.bw{position:relative;width:100%}
#board{position:relative;width:100%;aspect-ratio:1;container-type:inline-size;border-radius:12px;box-shadow:0 22px 55px rgba(0,0,0,.5),0 0 0 6px rgba(255,255,255,.06);touch-action:none;user-select:none;-webkit-user-select:none;direction:ltr}
#sqs{position:absolute;inset:0;display:grid;grid-template:repeat(8,1fr)/repeat(8,1fr);border-radius:12px;overflow:hidden}
.sq{position:relative;background:var(--light)}
.sq.d{background:var(--dark)}
.sq::before,.sq::after{position:absolute;font:700 1.9cqw/1 var(--sans);pointer-events:none;z-index:1}
.sq::before{content:attr(data-rk);top:.6cqw;left:.7cqw}
.sq::after{content:attr(data-fl);right:.7cqw;bottom:.6cqw}
.sq.l::before,.sq.l::after{color:var(--cl)}
.sq.d::before,.sq.d::after{color:var(--cd)}
[data-coords="0"] .sq::before,[data-coords="0"] .sq::after{display:none}
.hl{position:absolute;inset:0;pointer-events:none;z-index:1}
.sq.last .hl{background:var(--last)}
.sq.sel .hl{background:var(--sel)}
.sq.tgt .hl::after{content:"";position:absolute;left:50%;top:50%;width:30%;aspect-ratio:1;border-radius:50%;background:var(--dot);transform:translate(-50%,-50%);animation:dotin .18s ease-out}
.sq.cap .hl::after{content:"";position:absolute;inset:4%;border-radius:50%;border:.9cqw solid var(--dot);animation:dotin .18s ease-out}
.sq.hov .hl{box-shadow:inset 0 0 0 .55cqw rgba(255,255,255,.75)}
.sq.chk .hl{background:radial-gradient(circle,rgba(255,45,75,.95) 0,rgba(255,45,75,.55) 38%,rgba(255,45,75,0) 74%);animation:chk 1s ease-in-out infinite alternate}
@keyframes chk{from{opacity:.6}}
@keyframes dotin{from{transform:translate(-50%,-50%) scale(.2);opacity:0}}
.sq.cap .hl::after{animation-name:ringin}
@keyframes ringin{from{transform:scale(.6);opacity:0}}
[data-board=marble] .sq.l{background-image:linear-gradient(118deg,transparent 38%,rgba(0,0,0,.06) 39%,transparent 41%,transparent 62%,rgba(0,0,0,.05) 63%,transparent 64%)}
[data-board=marble] .sq.d{background-image:linear-gradient(62deg,transparent 30%,rgba(255,255,255,.18) 31%,transparent 33%,transparent 70%,rgba(255,255,255,.12) 71%,transparent 72%)}
[data-board=wood] .sq{background-image:linear-gradient(90deg,rgba(0,0,0,.025),rgba(255,255,255,.04) 40%,rgba(0,0,0,.03))}
[data-board=glass] #board{background:rgba(255,255,255,.06);backdrop-filter:blur(16px) saturate(170%);box-shadow:inset 0 0 0 1px rgba(255,255,255,.35),0 22px 60px rgba(0,0,0,.4)}
[data-board=glass] .sq{box-shadow:inset 0 0 0 .5px rgba(255,255,255,.18)}
[data-board=neon] #board{box-shadow:0 0 0 1px rgba(79,216,255,.55),0 0 40px rgba(79,120,255,.35),0 0 90px rgba(255,60,200,.18)}
[data-board=neon] .sq{box-shadow:inset 0 0 0 .5px rgba(79,216,255,.18)}
#pieces{position:absolute;inset:0;pointer-events:none}
.pc{position:absolute;left:0;top:0;width:12.5%;height:12.5%;display:grid;place-items:center;transition:transform var(--dur) cubic-bezier(.2,.9,.25,1);will-change:transform;z-index:2}
.pc span{display:block;font-family:"Segoe UI Symbol","Noto Sans Symbols 2","Apple Symbols","DejaVu Sans","Arial Unicode MS",sans-serif;font-size:min(8.6vw,7vh);font-size:calc(var(--u)*9.9);line-height:1;transition:transform .16s;text-align:center;width:100%;text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.pc.sel span{transform:translateY(-5%) scale(1.08)}
.pc.mv{z-index:5}
.pc.drag{transition:none;z-index:9}
.pc.drag span{transform:scale(1.2)}
.pc.cap{z-index:1}
.pc.cap span{animation:capt .36s ease-in forwards}
@keyframes capt{to{transform:scale(1.7) rotate(24deg);opacity:0}}
.pc.in span{animation:pin .55s cubic-bezier(.3,1.4,.5,1) both;animation-delay:var(--d,0s)}
@keyframes pin{from{transform:scale(.1) translateY(-40%);opacity:0}}
.pc.fall span{animation:fall 1s .25s ease-in forwards}
@keyframes fall{to{transform:rotate(84deg) translateY(28%);opacity:.4}}
.pc.promo span{animation:pro .5s ease-out}
@keyframes pro{40%{transform:scale(1.5) rotate(12deg)}}
:root[data-piece=classic] #pieces .pc.w span,.pv[data-piece=classic] .pc.w span{color:#fff;text-shadow:0 0 1px #000,0 0 1px #000,1px 0 0 #000,-1px 0 0 #000,0 1px 0 #000,0 -1px 0 #000;filter:drop-shadow(0 calc(var(--u)*.5) calc(var(--u)*.4) rgba(0,0,0,.45))}
:root[data-piece=classic] #pieces .pc.b span,.pv[data-piece=classic] .pc.b span{color:#1a1a20;text-shadow:0 0 .8px rgba(255,255,255,.75),0 0 1px rgba(255,255,255,.5);filter:drop-shadow(0 calc(var(--u)*.5) calc(var(--u)*.4) rgba(0,0,0,.45))}
:root[data-piece=flat] #pieces .pc.w span,.pv[data-piece=flat] .pc.w span{color:#f7f6f2;text-shadow:0 calc(var(--u)*.25) 0 #b9b6ad;filter:drop-shadow(0 calc(var(--u)*.4) calc(var(--u)*.5) rgba(0,0,0,.3))}
:root[data-piece=flat] #pieces .pc.b span,.pv[data-piece=flat] .pc.b span{color:#2b2d36;text-shadow:0 calc(var(--u)*.25) 0 #0f1015;filter:drop-shadow(0 calc(var(--u)*.4) calc(var(--u)*.5) rgba(0,0,0,.3))}
:root[data-piece=gold] #pieces .pc.w span,.pv[data-piece=gold] .pc.w span{color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;position:relative;background-image:linear-gradient(172deg,#fff6cf 0%,#f6d77f 24%,#d9a838 50%,#b98626 68%,#ecc866 100%);-webkit-text-stroke:calc(var(--u)*.13) rgba(92,60,8,.9);filter:drop-shadow(0 calc(var(--u)*.5) calc(var(--u)*.5) rgba(0,0,0,.45))}
:root[data-piece=gold] #pieces .pc.b span,.pv[data-piece=gold] .pc.b span{color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;position:relative;background-image:linear-gradient(172deg,#7a5a36 0%,#46301b 28%,#24160b 56%,#3b2713 80%,#6a4c2a 100%);-webkit-text-stroke:calc(var(--u)*.12) rgba(236,196,110,.85);filter:drop-shadow(0 calc(var(--u)*.5) calc(var(--u)*.5) rgba(0,0,0,.5))}
:root[data-piece=gold] #pieces .pc.w span::after,.pv[data-piece=gold] .pc.w span::after{content:attr(data-g);position:absolute;inset:0;color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;-webkit-text-stroke:0;pointer-events:none;background-image:linear-gradient(110deg,transparent 28%,rgba(255,255,255,.6) 44%,transparent 60%);}
:root[data-piece=gold] #pieces .pc.b span::after,.pv[data-piece=gold] .pc.b span::after{content:attr(data-g);position:absolute;inset:0;color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;-webkit-text-stroke:0;pointer-events:none;background-image:linear-gradient(110deg,transparent 28%,rgba(255,225,160,.32) 44%,transparent 60%);}
:root[data-piece=glass] #pieces .pc.w span,.pv[data-piece=glass] .pc.w span{color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;position:relative;background-image:linear-gradient(165deg,rgba(255,255,255,.92) 0%,rgba(214,238,255,.62) 30%,rgba(160,208,245,.42) 62%,rgba(236,248,255,.8) 100%);-webkit-text-stroke:calc(var(--u)*.16) rgba(255,255,255,.85);filter:drop-shadow(0 0 calc(var(--u)*.25) rgba(120,196,255,.75)) drop-shadow(0 calc(var(--u)*.6) calc(var(--u)*.6) rgba(10,40,90,.38))}
:root[data-piece=glass] #pieces .pc.b span,.pv[data-piece=glass] .pc.b span{color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;position:relative;background-image:linear-gradient(165deg,rgba(120,135,190,.78) 0%,rgba(48,58,110,.82) 38%,rgba(18,22,52,.9) 70%,rgba(60,70,130,.85) 100%);-webkit-text-stroke:calc(var(--u)*.14) rgba(190,205,255,.55);filter:drop-shadow(0 0 calc(var(--u)*.22) rgba(140,160,255,.7)) drop-shadow(0 calc(var(--u)*.6) calc(var(--u)*.6) rgba(0,0,30,.5))}
:root[data-piece=glass] #pieces .pc.w span::after,.pv[data-piece=glass] .pc.w span::after{content:attr(data-g);position:absolute;inset:0;color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;-webkit-text-stroke:0;pointer-events:none;background-image:linear-gradient(135deg,rgba(255,255,255,.95) 0%,rgba(255,255,255,.35) 28%,rgba(255,255,255,0) 52%);transform:translate(calc(var(--u)*-.18),calc(var(--u)*-.22)) scale(.93);transform-origin:50% 55%;}
:root[data-piece=glass] #pieces .pc.b span::after,.pv[data-piece=glass] .pc.b span::after{content:attr(data-g);position:absolute;inset:0;color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;-webkit-text-stroke:0;pointer-events:none;background-image:linear-gradient(135deg,rgba(255,255,255,.7) 0%,rgba(255,255,255,.18) 26%,rgba(255,255,255,0) 50%);transform:translate(calc(var(--u)*-.18),calc(var(--u)*-.22)) scale(.93);transform-origin:50% 55%;}
:root[data-piece=glass] #pieces .pc.w span::before,.pv[data-piece=glass] .pc.w span::before{content:attr(data-g);position:absolute;inset:0;color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;-webkit-text-stroke:0;pointer-events:none;background-image:linear-gradient(315deg,rgba(60,140,220,.55) 0%,rgba(60,140,220,0) 45%);}
:root[data-piece=glass] #pieces .pc.b span::before,.pv[data-piece=glass] .pc.b span::before{content:attr(data-g);position:absolute;inset:0;color:transparent;-webkit-text-fill-color:transparent;-webkit-background-clip:text;background-clip:text;-webkit-text-stroke:0;pointer-events:none;background-image:linear-gradient(315deg,rgba(120,90,255,.5) 0%,rgba(120,90,255,0) 45%);}
:root[data-piece=neon] #pieces .pc.w span,.pv[data-piece=neon] .pc.w span{color:rgba(10,28,56,.82);-webkit-text-stroke:calc(var(--u)*.2) #7fe6f0;filter:drop-shadow(0 0 calc(var(--u)*.5) rgba(80,220,240,.55))}
:root[data-piece=neon] #pieces .pc.b span,.pv[data-piece=neon] .pc.b span{color:rgba(36,10,44,.85);-webkit-text-stroke:calc(var(--u)*.2) #f089e4;filter:drop-shadow(0 0 calc(var(--u)*.5) rgba(240,100,220,.5))}
#ov{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:6}
.promo,.result{position:absolute;inset:0;z-index:20;display:grid;place-items:center;border-radius:12px;background:rgba(5,8,20,.55);backdrop-filter:blur(6px);animation:fade .25s}
.promo[hidden],.result[hidden]{display:none}
@keyframes fade{from{opacity:0}}
.pbox{display:flex;gap:10px;padding:14px;border-radius:18px;background:var(--glass2);border:1px solid var(--line);backdrop-filter:blur(20px);animation:rise .3s cubic-bezier(.3,1.3,.5,1)}
.pbox button{width:min(17cqw,84px);aspect-ratio:1;border-radius:14px;border:1px solid var(--line);background:var(--glass);font:min(11vw,52px)/1 "Segoe UI Symbol","Noto Sans Symbols 2","Apple Symbols","DejaVu Sans",sans-serif;transition:transform .12s}
.pbox button:hover{transform:scale(1.08);background:var(--acc);color:#1b1206}
@keyframes rise{from{transform:translateY(16px) scale(.92);opacity:0}}
.rcard{width:min(86%,360px);padding:26px 22px 20px;border-radius:22px;text-align:center;background:var(--glass2);border:1px solid var(--line);backdrop-filter:blur(22px);box-shadow:0 30px 80px rgba(0,0,0,.5);animation:rise .45s cubic-bezier(.3,1.3,.5,1)}
.rcard h2{font:600 34px/1.1 var(--serif);margin-bottom:6px}
.rcard p{color:var(--mute);margin-bottom:18px}
.rcard .row{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.panel{border-radius:22px;border:1px solid var(--line);background:var(--glass);backdrop-filter:blur(20px) saturate(140%);padding:16px;display:flex;flex-direction:column;gap:12px;box-shadow:0 20px 50px rgba(0,0,0,.25);position:sticky;top:10px;max-height:calc(100dvh - 20px);overflow-y:auto;overflow-x:hidden;width:100%;min-width:0;box-sizing:border-box;scrollbar-width:thin;scrollbar-color:var(--acc) rgba(10,15,30,.25)}
.status{font:600 19px/1.25 var(--serif);min-height:26px}
.status.bad{color:var(--bad)}
.banner{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 12px;border-radius:12px;background:rgba(230,181,102,.16);border:1px solid var(--acc);font-size:14px}
.banner[hidden]{display:none}
.banner span{flex:1;min-width:140px}
.moves{position:relative;height:230px;overflow:auto;border-radius:12px;background:rgba(0,0,0,.16);padding:6px;scrollbar-width:thin}
:root[data-mode=light] .moves{background:rgba(255,255,255,.5)}
.mr{display:grid;grid-template-columns:34px 1fr 1fr;align-items:center;font-variant-numeric:tabular-nums}
.mr i{font-style:normal;color:var(--mute);font-size:13px;padding-left:6px}
.mr b{font-weight:500;padding:5px 8px;border-radius:8px;cursor:pointer;white-space:nowrap}
.mr b:hover{background:var(--glass2)}
.mr b.on{background:var(--acc);color:#1b1206;font-weight:700}
.nav,.acts{display:grid;gap:8px}
.nav{grid-template-columns:repeat(4,1fr)}
.acts{grid-template-columns:repeat(auto-fit,minmax(104px,1fr))}
.btn{min-height:42px;padding:9px 12px;border-radius:12px;border:1px solid var(--line);background:var(--glass);display:inline-flex;align-items:center;justify-content:center;gap:7px;transition:background .15s,transform .1s;white-space:nowrap}
.btn img{max-width:22px;max-height:22px;object-fit:contain}
.btn:hover:not(:disabled){background:var(--glass2)}
.btn:active:not(:disabled){transform:scale(.97)}
.btn:disabled{opacity:.38;cursor:default}
.btn.pri{background:linear-gradient(145deg,var(--acc),#c98a2c);border-color:transparent;color:#1b1206;font-weight:700}
.btn.pri:hover:not(:disabled){background:linear-gradient(145deg,#f3c77f,#d9983a)}
.btn[hidden]{display:none}
.btn.ghost{background:transparent}
#fx{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:50}
#toasts{position:fixed;left:0;right:0;bottom:calc(20px + env(safe-area-inset-bottom));display:flex;flex-direction:column;align-items:center;gap:8px;z-index:70;pointer-events:none}
.toast{padding:10px 16px;border-radius:999px;background:rgba(14,18,38,.92);color:#fff;border:1px solid var(--line);box-shadow:0 10px 30px rgba(0,0,0,.4);animation:rise .25s,fade .3s 2.2s reverse forwards}
.mback{position:fixed;inset:0;z-index:60;display:grid;place-items:center;padding:16px;background:rgba(4,7,18,.58);backdrop-filter:blur(8px);animation:fade .2s}
.modal{width:min(100%,580px);max-height:calc(100dvh - 32px);overflow-y:auto;overflow-x:hidden;scrollbar-width:thin;scrollbar-color:var(--acc) transparent;border-radius:24px;border:1px solid var(--line);background:var(--bg2);background-image:linear-gradient(160deg,var(--glass2),var(--glass));padding:22px;box-shadow:0 40px 100px rgba(0,0,0,.55);animation:rise .3s cubic-bezier(.3,1.3,.5,1);display:flex;flex-direction:column;gap:16px;box-sizing:border-box}
.modal::-webkit-scrollbar,::-webkit-scrollbar{width:6px;height:6px}
.modal::-webkit-scrollbar-track,::-webkit-scrollbar-track{background:transparent;border-radius:99px}
.modal::-webkit-scrollbar-thumb,::-webkit-scrollbar-thumb{background:rgba(230,181,102,.45);border-radius:99px;transition:background .2s}
.modal::-webkit-scrollbar-thumb:hover,::-webkit-scrollbar-thumb:hover{background:var(--acc)}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:6px;border-radius:99px;background:rgba(255,255,255,.14);outline:none;accent-color:var(--acc);margin:4px 0}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:18px;height:18px;border-radius:50%;background:linear-gradient(135deg,#ffe082,#d4af37);box-shadow:0 2px 6px rgba(0,0,0,.4);border:2px solid #fff;cursor:pointer;transition:transform .12s}
input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.2)}
.modal h3{font:600 26px/1.1 var(--serif)}
.modal h4{font-weight:600;font-size:14px;color:var(--mute);margin-bottom:8px}
.mhead{display:flex;justify-content:space-between;align-items:center}
.seg{display:flex;gap:4px;padding:4px;border-radius:14px;background:rgba(0,0,0,.2);border:1px solid var(--line)}
:root[data-mode=light] .seg{background:rgba(255,255,255,.55)}
.seg button{flex:1;padding:8px 10px;border-radius:10px;border:0;background:transparent;transition:background .15s;min-height:38px}
.seg button.on{background:var(--acc);color:#1b1206;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:10px}
.tile{display:flex;flex-direction:column;align-items:center;gap:7px;padding:10px 8px;border-radius:14px;border:1px solid var(--line);background:var(--glass);font-size:13px;transition:transform .12s}
.tile:hover{transform:translateY(-2px)}
.tile.on{border-color:var(--acc);box-shadow:0 0 0 2px var(--acc) inset}
.sw{width:64px;height:64px;border-radius:10px;display:grid;grid-template:1fr 1fr/1fr 1fr;overflow:hidden;border:1px solid rgba(255,255,255,.2)}
.pv{--u:3px;width:64px;height:64px;border-radius:10px;display:flex;overflow:hidden;background:linear-gradient(90deg,var(--dark) 50%,var(--light) 50%)}
.pv .pc{position:static;width:32px;height:64px;display:grid;place-items:center;transition:none}
.pv .pc span{width:auto}
.row{display:flex;gap:10px;align-items:center}
.row.sp{justify-content:space-between}
.tg{position:relative;width:46px;height:26px;border-radius:99px;border:1px solid var(--line);background:rgba(0,0,0,.25);flex:none;transition:background .2s}
.tg::after{content:"";position:absolute;top:2px;left:2px;width:20px;height:20px;border-radius:50%;background:#fff;transition:transform .2s}
.tg.on{background:var(--acc2)}
.tg.on::after{transform:translateX(20px)}
[dir=rtl] .tg::after{left:auto;right:2px}
[dir=rtl] .tg.on::after{transform:translateX(-20px)}
input[type=range]{accent-color:var(--acc);width:100%}
select,.inp{padding:10px 12px;border-radius:12px;border:1px solid var(--line);background:rgba(0,0,0,.22);width:100%;min-height:42px}
select option{color:#111}
.inp{letter-spacing:4px;text-transform:uppercase;font-weight:700;text-align:center;font-size:18px}
.qrbox{display:grid;place-items:center;gap:10px;text-align:center}
.qrbox img{width:min(62vw,240px);aspect-ratio:1;border-radius:16px;background:#fff;padding:8px}
.code{font:700 30px/1 var(--serif);letter-spacing:6px}
.url{font-size:13px;color:var(--mute);word-break:break-all;user-select:all}
.mut{color:var(--mute);font-size:14px}
.dots::after{content:"";animation:dots 1.2s steps(4) infinite}
@keyframes dots{25%{content:"."}50%{content:".."}75%{content:"..."}}
@media (max-width:900px){
  .layout{grid-template-columns:1fr;gap:14px;padding:6px 10px calc(18px + env(safe-area-inset-bottom))}
  .stage{width:min(100%,560px);min-width:300px;margin:0 auto}
  .moves{height:150px}
  .top{padding-left:12px;padding-right:12px}
}
@media (prefers-reduced-motion:reduce){#bg i{animation:none}}
[dir=rtl] .mr i{padding-left:0;padding-right:6px}
"""
APP_JS = r"""'use strict';
(() => {
const $ = (s, r = document) => r.querySelector(s);
const Chess = window.Chess, I18N = window.I18N, FILES = Chess.FILES;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const mkStore = o => ({
  get(k, d) { try { const v = o.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { o.setItem(k, JSON.stringify(v)); } catch (e) {} },
});
const store = mkStore(window.localStorage || { getItem() {}, setItem() {} });
const sess = mkStore(window.sessionStorage || { getItem() {}, setItem() {} });

/* ---------- DOM yardımcıları (innerHTML kullanılmaz) ---------- */
function h(tag, a, ...kids) {
  const e = document.createElement(tag);
  if (a) for (const k in a) {
    const v = a[k];
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k === 'style') Object.assign(e.style, v);
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
}
const sv = (tag, a) => { const e = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const k in a) e.setAttribute(k, a[k]); return e; };
function toast(msg) { const e = h('div', { class: 'toast', text: msg }); $('#toasts').append(e); setTimeout(() => e.remove(), 2700); }
async function copyText(s) {
  try { await navigator.clipboard.writeText(s); return true; } catch (e) {}
  try {
    const ta = h('textarea', { style: { position: 'fixed', opacity: '0' } }); ta.value = s; document.body.append(ta); ta.select();
    const ok = document.execCommand('copy'); ta.remove(); return ok;
  } catch (e) { return false; }
}
let modals = [];
function modal(build) {
  const back = h('div', { class: 'mback', onclick: e => { if (e.target === back) api.close(); } });
  const box = h('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true' });
  const api = { box, onclose: null, close() { back.remove(); modals = modals.filter(x => x !== api); if (api.onclose) api.onclose(); } };
  back.append(box); build(box, api.close); $('#modals').append(back); modals.push(api); return api;
}
function ask(msg, onYes) {
  modal((box, close) => box.append(h('h3', { text: msg }),
    h('div', { class: 'row' }, h('button', { class: 'btn pri', style: { flex: '1' }, text: t('yes'), onclick: () => { close(); onYes(); } }),
      h('button', { class: 'btn', style: { flex: '1' }, text: t('no'), onclick: close }))));
}

/* ---------- Ayarlar ---------- */
const BOARDS = [
  { id: 'wood', l: '#f0d9b5', d: '#b58863', piece: 'classic', sound: 'wood' },
  { id: 'emerald', l: '#eeeed2', d: '#769656', piece: 'flat', sound: 'wood' },
  { id: 'ice', l: '#e8f0f8', d: '#7fa3c7', piece: 'glass', sound: 'glass' },
  { id: 'night', l: '#6c7792', d: '#394159', piece: 'gold', sound: 'soft' },
  { id: 'violet', l: '#ece0f9', d: '#8d6fc4', piece: 'flat', sound: 'synth' },
  { id: 'marble', l: '#f4f4f0', d: '#a6a9a8', piece: 'classic', sound: 'soft' },
  { id: 'glass', l: '#9fb6d6', d: '#4b648c', piece: 'glass', sound: 'glass' },
  { id: 'neon', l: '#121b3d', d: '#0a1029', piece: 'neon', sound: 'synth' },
];
const PIECES = ['classic', 'flat', 'gold', 'glass', 'neon'];
const SOUNDS = ['wood', 'glass', 'synth', 'soft', 'off'];
const ANIM = [0, .13, .26, .5];
const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
const DEF = { lang: 'auto', board: 'wood', piece: 'classic', sound: 'wood', volume: .7, bg: 'auto', anim: reduce ? 0 : 2,
  coords: true, legal: true, hl: true, autoq: false, vib: true, level: 3, tc: '0', side: 'w', mode: 'ai' };
const S = Object.assign({}, DEF, store.get('satranc.v2', {}));
if (!BOARDS.some(b => b.id === S.board)) S.board = DEF.board;
if (!PIECES.includes(S.piece)) S.piece = DEF.piece;
if (!SOUNDS.includes(S.sound)) S.sound = DEF.sound;
S.volume = clamp(+S.volume || 0, 0, 1); S.anim = clamp(S.anim | 0, 0, 3); S.level = clamp(S.level | 0, 1, 5);
const save = () => store.set('satranc.v2', S);

/* ---------- Dil ---------- */
let L = 'en';
const detect = () => {
  for (const l of (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || 'en'])) {
    const b = String(l).toLowerCase().split('-')[0];
    if (b !== 'names' && I18N[b]) return b;
  }
  return 'en';
};
const t = (k, v) => {
  let s = (I18N[L] && I18N[L][k]) ?? I18N.en[k] ?? k;
  if (v) for (const x in v) s = s.replace('{' + x + '}', v[x]);
  return s;
};

/* ---------- Ses motoru (WebAudio ile sentezlenir, dosya gerekmez) ---------- */
const PK = {
  wood: { w: 'sine', hi: 660,
    m: [['n', 0, .07, 1300, 1.4, .55], ['t', 0, 190, 'sine', .11, .9, 95], ['t', 0, 430, 'triangle', .05, .25, 260]],
    c: [['n', 0, .12, 850, 1, .9], ['t', 0, 150, 'sine', .18, 1, 70], ['t', .05, 210, 'sine', .1, .6, 110], ['n', .035, .06, 2400, 2, .35]] },
  glass: { w: 'sine', hi: 1568,
    m: [['t', 0, 1760, 'sine', .22, .4], ['t', 0, 2637, 'sine', .12, .18], ['n', 0, .012, 7000, 1, .18, 'highpass']],
    c: [['t', 0, 1568, 'sine', .3, .4], ['t', .03, 2093, 'sine', .26, .32], ['t', .06, 1319, 'sine', .3, .3], ['n', 0, .03, 6000, 1, .35, 'highpass']] },
  synth: { w: 'square', hi: 880,
    m: [['t', 0, 620, 'square', .09, .13, 310], ['t', 0, 310, 'triangle', .09, .25, 155]],
    c: [['t', 0, 520, 'sawtooth', .2, .2, 70], ['n', 0, .08, 1800, .8, .3, 'bandpass']] },
  soft: { w: 'triangle', hi: 520,
    m: [['n', 0, .05, 500, .8, .32, 'lowpass'], ['t', 0, 140, 'sine', .07, .35, 90]],
    c: [['n', 0, .09, 420, .8, .5, 'lowpass'], ['t', 0, 110, 'sine', .12, .5, 60]] },
};
const shift = (a, d) => a.map(x => { const y = x.slice(); y[1] += d; return y; });
const arp = (fr, w, step, dur, vol) => fr.map((f, i) => ['t', i * step, f, w, dur, vol]);
function sfxSpec(pk, ev) {
  const p = PK[pk]; if (!p) return null;
  switch (ev) {
    case 'move': return p.m;
    case 'capture': return p.c;
    case 'castle': return p.m.concat(shift(p.m, .13));
    case 'check': return p.m.concat([['t', .1, p.hi, p.w, .3, .28], ['t', .22, p.hi, p.w, .3, .22]]);
    case 'promote': return p.m.concat(shift(arp([523, 659, 784, 1047], p.w, .07, .25, .2), .08));
    case 'start': return arp([392, 523], p.w, .1, .3, .2);
    case 'win': return arp([523, 659, 784, 1047, 1319], p.w, .09, .45, .2);
    case 'lose': return arp([392, 330, 262, 196], p.w, .14, .5, .2);
    case 'draw': return arp([440, 440, 330], p.w, .15, .4, .2);
    case 'illegal': return [['t', 0, 130, 'square', .14, .1, 90]];
    case 'tick': return [['t', 0, 1900, 'square', .03, .06]];
    case 'select': return [['t', 0, 950, 'sine', .04, .1]];
    case 'notify': return arp([784, 1047], p.w, .1, .25, .2);
  }
  return null;
}
const Snd = {
  ctx: null, out: null, nb: null,
  init() {
    if (this.ctx) return;
    try {
      const A = window.AudioContext || window.webkitAudioContext; if (!A) return;
      const c = new A(), comp = c.createDynamicsCompressor(); this.out = c.createGain(); this.out.connect(comp); comp.connect(c.destination);
      const n = c.sampleRate; this.nb = c.createBuffer(1, n, n); const d = this.nb.getChannelData(0);
      for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      this.ctx = c;
    } catch (e) { this.ctx = null; }
  },
  resume() { this.init(); if (this.ctx && this.ctx.state !== 'running') this.ctx.resume().catch(() => {}); },
  tone(t0, f, type, dur, vol, to) {
    const c = this.ctx, o = c.createOscillator(), g = c.createGain();
    o.type = type; o.frequency.setValueAtTime(f, t0); if (to) o.frequency.exponentialRampToValueAtTime(to, t0 + dur);
    g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(vol, t0 + .004); g.gain.exponentialRampToValueAtTime(.0001, t0 + dur);
    o.connect(g); g.connect(this.out); o.start(t0); o.stop(t0 + dur + .03);
  },
  noise(t0, dur, f, q, vol, type) {
    const c = this.ctx, s = c.createBufferSource(), fl = c.createBiquadFilter(), g = c.createGain();
    s.buffer = this.nb; s.loop = true; fl.type = type || 'bandpass'; fl.frequency.value = f; fl.Q.value = q;
    g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(vol, t0 + .003); g.gain.exponentialRampToValueAtTime(.0001, t0 + dur);
    s.connect(fl); fl.connect(g); g.connect(this.out); s.start(t0, Math.random() * .5); s.stop(t0 + dur + .03);
  },
  lastEv: null, lastTime: 0,
  play(ev) {
    if (S.sound === 'off' || !this.ctx || this.ctx.state !== 'running') return;
    const nowMs = performance.now();
    // Çift çalmayı ve 70ms içindeki mükerrer ses patlamalarını engelle
    if (nowMs - this.lastTime < 70 && (this.lastEv === ev || (ev === 'move' && this.lastEv === 'select'))) return;
    this.lastEv = ev; this.lastTime = nowMs;

    const sp = sfxSpec(S.sound, ev); if (!sp) return;
    this.out.gain.value = S.volume * S.volume * 1.3;
    const now = this.ctx.currentTime + .005;
    for (const x of sp) {
      if (x[0] === 't') this.tone(now + x[1], x[2], x[3], x[4], x[5], x[6]);
      else this.noise(now + x[1], x[2], x[3], x[4], x[5], x[6]);
    }
  },
};
const vib = p => { if (S.vib && navigator.vibrate) try { navigator.vibrate(p); } catch (e) {} };

/* ---------- Parçacık efektleri ---------- */
const FX = {
  cv: $('#fx'), cx: null, ps: [], on: false, last: 0,
  size() {
    const d = window.devicePixelRatio || 1;
    this.cv.width = innerWidth * d; this.cv.height = innerHeight * d; this.cx = this.cv.getContext('2d'); this.cx.setTransform(d, 0, 0, d, 0, 0);
  },
  add(p) { this.ps.push(p); if (!this.on) { this.on = true; this.last = performance.now(); requestAnimationFrame(x => this.loop(x)); } },
  burst(x, y, color, n) {
    if (!S.anim) return;
    for (let i = 0; i < (n || 16); i++) {
      const a = Math.random() * 6.283, v = 60 + Math.random() * 220;
      this.add({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 40, g: 520, life: 0, max: .45 + Math.random() * .35,
        s: 2 + Math.random() * 4, c: Math.random() < .35 ? '#e6b566' : color, r: 0, vr: 0, sq: false });
    }
  },
  confetti() {
    if (!S.anim) return;
    const cols = ['#e6b566', '#54d2c0', '#ff6b81', '#7c9cff', '#ffffff', '#f7d774'];
    for (let i = 0; i < 150; i++) {
      this.add({ x: innerWidth * (.15 + Math.random() * .7), y: -20 - Math.random() * 200, vx: (Math.random() - .5) * 260, vy: 120 + Math.random() * 260,
        g: 260, life: 0, max: 2.6 + Math.random() * 1.6, s: 6 + Math.random() * 6, c: cols[i % cols.length], r: Math.random() * 6, vr: (Math.random() - .5) * 12, sq: true });
    }
  },
  loop(now) {
    if (!this.cx) this.size();
    const dt = Math.min(.05, (now - this.last) / 1000); this.last = now;
    const cx = this.cx; cx.clearRect(0, 0, innerWidth, innerHeight);
    this.ps = this.ps.filter(p => {
      p.life += dt; if (p.life >= p.max) return false;
      p.vy += p.g * dt; p.x += p.vx * dt; p.y += p.vy * dt; p.r += p.vr * dt;
      cx.globalAlpha = clamp(1 - p.life / p.max, 0, 1) ** .6; cx.fillStyle = p.c;
      if (p.sq) { cx.save(); cx.translate(p.x, p.y); cx.rotate(p.r); cx.fillRect(-p.s / 2, -p.s / 3, p.s, p.s * .6); cx.restore(); }
      else { cx.beginPath(); cx.arc(p.x, p.y, p.s * (1 - p.life / p.max * .5), 0, 6.283); cx.fill(); }
      return true;
    });
    if (this.ps.length) requestAnimationFrame(x => this.loop(x)); else { this.on = false; cx.clearRect(0, 0, innerWidth, innerHeight); }
  },
};
addEventListener('resize', () => FX.size());

/* ---------- Oyun durumu ---------- */
const GL = ['', '\u265F', '\u265E', '\u265D', '\u265C', '\u265B', '\u265A'], VS = '\uFE0E', VAL = [0, 1, 3, 3, 5, 9, 0];

/* =====================================================================
   BOTLAR, STOCKFISH, SES VE BULMACALAR
   ===================================================================== */
const BOTS = {
  engine: [
    { id: 1, name: 'Motor Seviye 1', elo: 400, skill: 1, depth: 6, time: 250, img: '/bot/Engine-level/1_Engine_level.png', desc: 'Yeni başlayan seviyesi. Temel taş hareketleri ve basit savunma.' },
    { id: 2, name: 'Motor Seviye 2', elo: 600, skill: 2, depth: 6, time: 260, img: '/bot/Engine-level/2_Engine_level.png', desc: 'Temel taş alımları ve merkez hamleleri.' },
    { id: 3, name: 'Motor Seviye 3', elo: 800, skill: 3, depth: 7, time: 280, img: '/bot/Engine-level/3_Engine_level.png', desc: 'Hafif taktik anlayışı, piyon yapısını korumaya çalışır.' },
    { id: 4, name: 'Motor Seviye 4', elo: 950, skill: 4, depth: 7, time: 300, img: '/bot/Engine-level/4_Engine_level.png', desc: 'Merkez kontrolü ve hafif taş uyumu.' },
    { id: 5, name: 'Motor Seviye 5', elo: 1100, skill: 5, depth: 8, time: 320, img: '/bot/Engine-level/5_Engine_level.png', desc: 'Açılış ilkelerini uygular, basit tuzakları görür.' },
    { id: 6, name: 'Motor Seviye 6', elo: 1250, skill: 6, depth: 8, time: 350, img: '/bot/Engine-level/6_Engine_level.png', desc: 'Çatal ve şiş tehditlerini değerlendirir.' },
    { id: 7, name: 'Motor Seviye 7', elo: 1350, skill: 7, depth: 9, time: 380, img: '/bot/Engine-level/7_Engine_level.png', desc: 'Orta seviye kulüp oyuncusu gücünde.' },
    { id: 8, name: 'Motor Seviye 8', elo: 1450, skill: 8, depth: 10, time: 400, img: '/bot/Engine-level/8_Engine_level.png', desc: 'Kombinezon arayışı ve sağlam piyon yapısı.' },
    { id: 9, name: 'Motor Seviye 9', elo: 1550, skill: 9, depth: 11, time: 420, img: '/bot/Engine-level/9_Engine_level.png', desc: 'Dinamik karşı saldırı ve taş uyumu.' },
    { id: 10, name: 'Motor Seviye 10', elo: 1650, skill: 10, depth: 12, time: 450, img: '/bot/Engine-level/10_Engine_level.png', desc: 'Konumsal üstünlük ve stratejik baskı.' },
    { id: 11, name: 'Motor Seviye 11', elo: 1750, skill: 11, depth: 13, time: 480, img: '/bot/Engine-level/11_Engine_level.png', desc: 'İleri düzey kulüp oyuncusu ayarında.' },
    { id: 12, name: 'Motor Seviye 12', elo: 1850, skill: 12, depth: 14, time: 500, img: '/bot/Engine-level/12_Engine_level.png', desc: 'Keskin taktikler ve son oyun teknikleri.' },
    { id: 13, name: 'Motor Seviye 13', elo: 1950, skill: 13, depth: 15, time: 550, img: '/bot/Engine-level/13_Engine_level.png', desc: 'Aday Usta (CM) düzeyinde derin hesap.' },
    { id: 14, name: 'Motor Seviye 14', elo: 2050, skill: 14, depth: 16, time: 600, img: '/bot/Engine-level/14_Engine_level.png', desc: 'FIDE Ustası (FM) ayarında güçlü hesaplama.' },
    { id: 15, name: 'Motor Seviye 15', elo: 2150, skill: 15, depth: 17, time: 650, img: '/bot/Engine-level/15_Engine_level.png', desc: 'Zorlu taktik ve konumsal ustalık.' },
    { id: 16, name: 'Motor Seviye 16', elo: 2250, skill: 16, depth: 18, time: 700, img: '/bot/Engine-level/16_Engine_level.png', desc: 'Uluslararası Usta (IM) seviyesi.' },
    { id: 17, name: 'Motor Seviye 17', elo: 2350, skill: 17, depth: 19, time: 750, img: '/bot/Engine-level/17_Engine_level.png', desc: 'Güçlü IM ayarında taktik vizyon.' },
    { id: 18, name: 'Motor Seviye 18', elo: 2450, skill: 18, depth: 20, time: 800, img: '/bot/Engine-level/18_Engine_level.png', desc: 'Büyükusta (GM) normunda derin analiz.' },
    { id: 19, name: 'Motor Seviye 19', elo: 2550, skill: 19, depth: 21, time: 850, img: '/bot/Engine-level/19_Engine_level.png', desc: 'Büyükusta gücünde acımasız baskı.' },
    { id: 20, name: 'Motor Seviye 20', elo: 2650, skill: 20, depth: 22, time: 900, img: '/bot/Engine-level/20_Engine_level.png', desc: 'Süper Büyükusta ayarında oyun.' },
    { id: 21, name: 'Motor Seviye 21', elo: 2750, skill: 20, depth: 23, time: 950, img: '/bot/Engine-level/21_Engine_level.png', desc: 'Dünyanın en iyi oyuncuları düzeyinde.' },
    { id: 22, name: 'Motor Seviye 22', elo: 2850, skill: 20, depth: 24, time: 1000, img: '/bot/Engine-level/22_Engine_level.png', desc: 'Dünya Şampiyonu Magnus Carlsen ayarında.' },
    { id: 23, name: 'Motor Seviye 23', elo: 2950, skill: 20, depth: 25, time: 1050, img: '/bot/Engine-level/23_Engine_level.png', desc: 'Üst düzey yapay zeka taktik üstünlüğü.' },
    { id: 24, name: 'Motor Seviye 24', elo: 3050, skill: 20, depth: 26, time: 1100, img: '/bot/Engine-level/24_Engine_level.png', desc: 'Kusursuz derinlik ve tam pozisyon hakimiyeti.' },
    { id: 25, name: 'Motor Seviye 25', elo: 3200, skill: 20, depth: 28, time: 1200, img: '/bot/Engine-level/25_Engine_level.png', desc: 'Maksimum derinlikte üstün Stockfish satrancı.' },
    { id: 26, name: 'Stockfish 19 (Saf Güç)', elo: 3500, skill: 20, pure: true, time: 1200, img: '/bot/Stockfish/stockfish.png', desc: 'Sınırsız sistem imkanı! Tam güç NNUE sinir ağları, tüm CPU çekirdekleri, 128 MB Hash ile tavizsiz büyükusta zekası.' }
  ],
  people: [
    { id: 'm1', name: 'Martin', elo: 400, skill: 1, depth: 6, time: 250, img: '/bot/people-bot/man/1_man.png', desc: 'Satranca yeni başladım, eğlenmeyi severim!' },
    { id: 'm2', name: 'Wayne', elo: 600, skill: 2, depth: 6, time: 260, img: '/bot/people-bot/man/2_man.png', desc: 'Piyonları sürmeyi ve eğlenmeyi seviyorum.' },
    { id: 'm3', name: 'Fabian', elo: 750, skill: 3, depth: 7, time: 280, img: '/bot/people-bot/man/3_man.png', desc: 'Hızlı oynarım, dikkatli ol!' },
    { id: 'w1', name: 'Aron', elo: 900, skill: 4, depth: 7, time: 300, img: '/bot/people-bot/woman/1_woman.png', desc: 'Hadi keyifli ve sakin bir maç yapalım.' },
    { id: 'm4', name: 'Juan', elo: 1050, skill: 5, depth: 8, time: 320, img: '/bot/people-bot/man/4_man.png', desc: 'Merkezi tutmaya çalışırım.' },
    { id: 'm5', name: 'Oliver', elo: 1200, skill: 6, depth: 8, time: 350, img: '/bot/people-bot/man/5_man.png', desc: 'Açılış teorilerini okudum.' },
    { id: 'w2', name: 'Elena', elo: 1350, skill: 7, depth: 9, time: 380, img: '/bot/people-bot/woman/2_woman.png', desc: 'Atları ve filleri etkin kullanırım.' },
    { id: 'm6', name: 'Nelson', elo: 1450, skill: 8, depth: 10, time: 400, img: '/bot/people-bot/man/6_man.png', desc: 'Erken vezir saldırılarını çok severim!' },
    { id: 'w3', name: 'Laura', elo: 1550, skill: 9, depth: 11, time: 420, img: '/bot/people-bot/woman/3_woman.png', desc: 'Kanat hücumları ve dinamik oyun.' },
    { id: 'm7', name: 'Antonio', elo: 1650, skill: 10, depth: 12, time: 450, img: '/bot/people-bot/man/7_man.png', desc: 'Sakin ve stratejik hamleler yaparım.' },
    { id: 'w4', name: 'Wendy', elo: 1750, skill: 11, depth: 13, time: 480, img: '/bot/people-bot/woman/4_woman.png', desc: 'Konumsal baskı ve taş uyumu.' },
    { id: 'm8', name: 'David', elo: 1850, skill: 12, depth: 14, time: 520, img: '/bot/people-bot/man/8_man.png', desc: 'Taktik fırsatları asla kaçırmam.' },
    { id: 'm9', name: 'Francis', elo: 2050, skill: 14, depth: 16, time: 600, img: '/bot/people-bot/man/9_man.png', desc: 'Sağlam savunma, keskin karşı saldırı.' },
    { id: 'm10', name: 'Mateo', elo: 2200, skill: 16, depth: 18, time: 680, img: '/bot/people-bot/man/10_man.png', desc: 'Usta adayı seviyesinde hesaplama.' },
    { id: 'w5', name: 'Isabel', elo: 2400, skill: 17, depth: 19, time: 750, img: '/bot/people-bot/woman/5_woman.png', desc: 'Zarif teknik ve kusursuz son oyunlar.' },
    { id: 'm11', name: 'Magnus Bot', elo: 2850, skill: 20, depth: 24, time: 1000, img: '/bot/people-bot/man/11_man.png', desc: 'Gevşek hamlelere acımayan sezgisel baskı.' },
    { id: 'm12', name: 'Usta Stockfish', elo: 3200, skill: 20, depth: 28, time: 1200, img: '/bot/people-bot/man/12_man.png', desc: 'Maksimum derinlik ve hatasız satranç.' },
    { id: 'sf_unleashed', name: 'Stockfish 19 (Saf Güç)', elo: 3500, skill: 20, pure: true, time: 1200, img: '/bot/Stockfish/stockfish.png', desc: 'Sınırsız sistem imkanı! Tam güç NNUE sinir ağları, tüm CPU çekirdekleri, 128 MB Hash ile tavizsiz büyükusta zekası.' }
  ]
};

const PUZZLES = [
  {"id": 1, "cat": "Arka Sıra Matı", "title": "Klasik Arka Sıra Matı", "fen": "6k1/5ppp/8/8/8/8/4QPPP/6K1 w - - 0 1", "moves": ["e2e8"], "rule": "Şahın önündeki piyonlar hava deliği bırakmadığında arka sıradan kaçış imkansızdır.", "desc": "Şahın önündeki piyonlar hava deliği bırakmadığında arka sıradan kaçış imkansızdır."},
  {"id": 2, "cat": "Arka Sıra Matı", "title": "Koru ve Vur: Arka Sıra", "fen": "3r2k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1", "moves": ["d1d8"], "rule": "Arka sırayı savunan tek kale düştüğünde şah mat olmaktan kurtulamaz.", "desc": "Arka sırayı savunan tek kale düştüğünde şah mat olmaktan kurtulamaz."},
  {"id": 3, "cat": "Arka Sıra Matı", "title": "Vezir Girişi", "fen": "2r3k1/5ppp/8/8/8/8/1Q3PPP/2R3K1 w - - 0 1", "moves": ["c1c8"], "rule": "Açık c-hattını kontrol eden kale, arka sıraya sızarak oyunu anında bitirir.", "desc": "Açık c-hattını kontrol eden kale, arka sıraya sızarak oyunu anında bitirir."},
  {"id": 4, "cat": "Arka Sıra Matı", "title": "Ağır Taş Bataryası", "fen": "r5k1/5ppp/8/8/8/8/R4PPP/R5K1 w - - 0 1", "moves": ["a2a8"], "rule": "Üst üste dizilmiş iki kale açık hatta arka sıradaki savunmayı ezer geçer.", "desc": "Üst üste dizilmiş iki kale açık hatta arka sıradaki savunmayı ezer geçer."},
  {"id": 5, "cat": "Arka Sıra Matı", "title": "Saptırma ile Arka Sıra", "fen": "5rk1/5ppp/8/8/8/8/1Q3PPP/4R1K1 w - - 0 1", "moves": ["b2b8"], "rule": "Savunmacıyı saptıran bir vezir hamlesi arka sırayı tamamen savunmasız bırakır.", "desc": "Savunmacıyı saptıran bir vezir hamlesi arka sırayı tamamen savunmasız bırakır."},
  {"id": 6, "cat": "Çatal", "title": "Kraliyet At Çatalı", "fen": "4k3/8/8/3N4/8/8/8/4K2R w K - 0 1", "moves": ["d5c7"], "rule": "Atlar L şeklinde sıçradığı için aynı anda şah ve ağır taşlara çatal atabilir.", "desc": "Atlar L şeklinde sıçradığı için aynı anda şah ve ağır taşlara çatal atabilir."},
  {"id": 7, "cat": "Çatal", "title": "At ile Şah ve Vezir", "fen": "r3k2r/ppp2ppp/2n5/3q4/3N4/8/PPP2PPP/R1BQK2R w KQkq - 0 10", "moves": ["d4c6"], "rule": "Merkezi açarak rakip taşların dengesini boz ve taş kazan.", "desc": "Merkezi açarak rakip taşların dengesini boz ve taş kazan."},
  {"id": 8, "cat": "Çatal", "title": "Piyon Çatalı", "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/3Pn3/2P2N2/PP3PPP/RNBQKB1R w KQkq - 0 5", "moves": ["d4d5"], "rule": "Piyon sürüşü ile rakip hafif taşları sıkıştırıp alan kazan.", "desc": "Piyon sürüşü ile rakip hafif taşları sıkıştırıp alan kazan."},
  {"id": 9, "cat": "Çatal", "title": "Vezir Çatalı: Şah & Taş", "fen": "r1bqk2r/ppp2ppp/2n5/3pP3/3P4/2b2N2/PPP2PPP/R1BQKB1R w KQkq - 0 8", "moves": ["b2c3"], "rule": "Rakibin taktik fedasını soğukkanlılıkla karşıla ve taş üstünlüğünü koru.", "desc": "Rakibin taktik fedasını soğukkanlılıkla karşıla ve taş üstünlüğünü koru."},
  {"id": 10, "cat": "Çatal", "title": "Merkezde At Çatalı", "fen": "r1bqk2r/pppp1ppp/2n5/4p3/1b2n3/2NP1N2/PPP1BPPP/R1BQK2R w KQkq - 0 6", "moves": ["d3e4"], "rule": "Dikkatsizce ileri atılan rakip atı cezalandırıp merkez piyonunu güçlendir.", "desc": "Dikkatsizce ileri atılan rakip atı cezalandırıp merkez piyonunu güçlendir."},
  {"id": 11, "cat": "Boğmaca Matı", "title": "Saf Boğmaca Matı", "fen": "6rk/5Npp/8/8/8/8/8/7K w - - 0 1", "moves": ["f7h6"], "rule": "Kendi taşları arasına sıkışan şah, atın şah çekişine karşı hamlesiz kalır.", "desc": "Kendi taşları arasına sıkışan şah, atın şah çekişine karşı hamlesiz kalır."},
  {"id": 12, "cat": "Boğmaca Matı", "title": "Philidor Mirası", "fen": "6rk/6pp/7N/8/8/8/8/6QK w - - 0 1", "moves": ["h6f7"], "rule": "Vezirin köşeyi bağlaması ve atın f7 sıçrayışı efsanevi boğmaca matını gerçekleştirir.", "desc": "Vezirin köşeyi bağlaması ve atın f7 sıçrayışı efsanevi boğmaca matını gerçekleştirir."},
  {"id": 13, "cat": "Boğmaca Matı", "title": "Atın Sessiz Ölümü", "fen": "r5rk/5Npp/8/8/8/8/8/1R5K w - - 0 1", "moves": ["f7h6"], "rule": "Savunma kalesi kendi şahının kaçış yolunu tıkadığında at tek başına mat eder.", "desc": "Savunma kalesi kendi şahının kaçış yolunu tıkadığında at tek başına mat eder."},
  {"id": 14, "cat": "Boğmaca Matı", "title": "Açarak Şah ile Köşeye İtme", "fen": "5rk1/6pp/5N2/8/8/8/8/6QK w - - 0 1", "moves": ["f6h7"], "rule": "Şah çekişlerle rakibi köşeye hapsederek boğmaca ağını ör.", "desc": "Şah çekişlerle rakibi köşeye hapsederek boğmaca ağını ör."},
  {"id": 15, "cat": "Boğmaca Matı", "title": "Son Hamle Boğmaca", "fen": "5rk1/6pp/7N/8/8/8/8/6QK w - - 0 1", "moves": ["h6f7"], "rule": "Atın rakip şahın hemen yanına inmesi köşede nefes alacak yer bırakmaz.", "desc": "Atın rakip şahın hemen yanına inmesi köşede nefes alacak yer bırakmaz."},
  {"id": 16, "cat": "Şiş", "title": "Kale ile Şah ve Vezir Şişi", "fen": "4k3/8/8/8/8/8/4q3/4R1K1 w - - 0 1", "moves": ["e1e2"], "rule": "Şiş taktiğinde öndeki değerli taş kaçtığında arkadaki savunmasız taş düşer.", "desc": "Şiş taktiğinde öndeki değerli taş kaçtığında arkadaki savunmasız taş düşer."},
  {"id": 17, "cat": "Şiş", "title": "Fil Şişi: Kale Düşürme", "fen": "r3k3/8/8/8/8/8/4B3/4K3 w - - 0 1", "moves": ["e2f3"], "rule": "Çapraz boyunca uzanan fil, şah veya vezir hattında arkadaki kaleyi avlar.", "desc": "Çapraz boyunca uzanan fil, şah veya vezir hattında arkadaki kaleyi avlar."},
  {"id": 18, "cat": "Şiş", "title": "Yatay Şiş", "fen": "4k2r/8/8/8/8/8/8/R3K3 w Qk - 0 1", "moves": ["a1a8"], "rule": "Aynı yatayda bulunan şah ve kale, açık hattan gelen kale şişine dayanamaz.", "desc": "Aynı yatayda bulunan şah ve kale, açık hattan gelen kale şişine dayanamaz."},
  {"id": 19, "cat": "Şiş", "title": "Vezir ile Uzak Şiş", "fen": "k7/8/1q6/8/8/8/8/1Q4K1 w - - 0 1", "moves": ["b1b6"], "rule": "Vezir takasında arkada kalan zayıf piyonlar oyunu kazandırır.", "desc": "Vezir takasında arkada kalan zayıf piyonlar oyunu kazandırır."},
  {"id": 20, "cat": "Şiş", "title": "Çapraz Şiş Baskısı", "fen": "8/8/2k5/8/8/5B2/8/4K2r w - - 0 1", "moves": ["f3h1"], "rule": "Uzun köşegeni kontrol eden fil, tahtanın bir ucundan diğerine şiş atar.", "desc": "Uzun köşegeni kontrol eden fil, tahtanın bir ucundan diğerine şiş atar."},
  {"id": 21, "cat": "Açmaz", "title": "Mutlak Açmaz", "fen": "r1b1k2r/pppp1ppp/2n5/4p3/1b2P3/2NP1N2/PPP2PPP/R1BQK2R w KQkq - 0 7", "moves": ["c1d2"], "rule": "Şaha karşı yapılan açmaz mutlak açmazdır; açmazdaki taş kesinlikle hareket edemez.", "desc": "Şaha karşı yapılan açmaz mutlak açmazdır; açmazdaki taş kesinlikle hareket edemez."},
  {"id": 22, "cat": "Açmaz", "title": "Açmazdaki Taşa Yüklenme", "fen": "4k3/4r3/8/4P3/8/8/8/4R1K1 w - - 0 1", "moves": ["e5e6"], "rule": "Açmazdaki taş hareket edemediği için ona piyon veya hafif taşla saldırmak esastır.", "desc": "Açmazdaki taş hareket edemediği için ona piyon veya hafif taşla saldırmak esastır."},
  {"id": 23, "cat": "Açmaz", "title": "Fil Açmazını Bozma", "fen": "r1b1k2r/pppp1ppp/8/8/1b1qP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 8", "moves": ["c1d2"], "rule": "Kendi taşını açmazdan kurtarmak rakibin erken vezir saldırısını boşa çıkarır.", "desc": "Kendi taşını açmazdan kurtarmak rakibin erken vezir saldırısını boşa çıkarır."},
  {"id": 24, "cat": "Açmaz", "title": "Açmazdan Güvenli Çıkış", "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4", "moves": ["e4f6"], "rule": "Tehdit altındaki taşı güvenli kareye çekerek rakibin merkez üstünlüğünü sınırla.", "desc": "Tehdit altındaki taşı güvenli kareye çekerek rakibin merkez üstünlüğünü sınırla."},
  {"id": 25, "cat": "Açmaz", "title": "Sağlam Piyon Yapısı", "fen": "r1bqk2r/ppppbppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 4 5", "moves": ["d2d3"], "rule": "Sağlam piyon zinciri kurmak taşlarınıza hareket alanı ve taktik koruma sağlar.", "desc": "Sağlam piyon zinciri kurmak taşlarınıza hareket alanı ve taktik koruma sağlar."},
  {"id": 26, "cat": "Açarak Saldırı", "title": "Açarak Şah ile Savunma", "fen": "r1b1k2r/pppp1Npp/8/4p3/2Bn3q/8/PPPP2PP/RNBQ1K1R b kq - 0 9", "moves": ["h8f8"], "rule": "Açarak şah tehditlerine karşı kaleyi aktif hatta getirip şaha koruma sağla.", "desc": "Açarak şah tehditlerine karşı kaleyi aktif hatta getirip şaha koruma sağla."},
  {"id": 27, "cat": "Açarak Saldırı", "title": "Merkezde Vezir Tehdidi", "fen": "r1bqkb1r/pppp1ppp/2n5/8/2B1n3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5", "moves": ["d1e2"], "rule": "Merkez hattını açarak rakip taşı açmaza almak büyük taktik avantaj sağlar.", "desc": "Merkez hattını açarak rakip taşı açmaza almak büyük taktik avantaj sağlar."},
  {"id": 28, "cat": "Açarak Saldırı", "title": "Erken Vezir Saldırısını Cezalandırma", "fen": "r1b1k2r/pppp1ppp/2n5/4p3/2B1P2q/3P1N2/PPP2KPP/RNBQ4 w kq - 1 8", "moves": ["f3h4"], "rule": "Rakibin erkenden fırlattığı veziri alarak oyunda kesin taş üstünlüğü kur.", "desc": "Rakibin erkenden fırlattığı veziri alarak oyunda kesin taş üstünlüğü kur."},
  {"id": 29, "cat": "Açarak Saldırı", "title": "Taş Gelişimi ile Tehdit", "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2", "moves": ["b8c6"], "rule": "Açılışta önce hafif taşları oyuna sokarak merkezi kontrol altına al.", "desc": "Açılışta önce hafif taşları oyuna sokarak merkezi kontrol altına al."},
  {"id": 30, "cat": "Açarak Saldırı", "title": "Zayıf f7 Karesine Hücum", "fen": "r1b2rk1/ppp2ppp/8/4N3/2B5/8/PPP2PPP/3R2K1 w - - 0 1", "moves": ["c4f7"], "rule": "f7 karesi açılışta ve oyun ortasında şahın en hassas noktasıdır.", "desc": "f7 karesi açılışta ve oyun ortasında şahın en hassas noktasıdır."},
  {"id": 31, "cat": "Saptırma", "title": "Savunma Kalesini Saptırma", "fen": "5rk1/5ppp/8/8/8/8/1q3PPP/4Q1K1 b - - 0 1", "moves": ["f8a8"], "rule": "Savunma taşını kritik kareden uzaklaştırdığında arkadaki savunma hattı çöker.", "desc": "Savunma taşını kritik kareden uzaklaştırdığında arkadaki savunma hattı çöker."},
  {"id": 32, "cat": "Saptırma", "title": "Vezir Fedası ile Saptırma", "fen": "r1b2rk1/pp3ppp/2n5/8/2B5/5Q2/PPP2PPP/4R1K1 w - - 0 1", "moves": ["f3f7"], "rule": "Feda ile rakip koruyucuyu saptırmak mat ağını anında tamamlar.", "desc": "Feda ile rakip koruyucuyu saptırmak mat ağını anında tamamlar."},
  {"id": 33, "cat": "Saptırma", "title": "Açarak Taş Alma", "fen": "r1b1k2r/pppp1ppp/8/4q3/1b6/2P5/PP1PnPPP/RNBQKB1R b KQkq - 0 9", "moves": ["e2c3"], "rule": "Şah açığa çıktığında tüm taktik darbeler kat kat daha etkili hale gelir.", "desc": "Şah açığa çıktığında tüm taktik darbeler kat kat daha etkili hale gelir."},
  {"id": 34, "cat": "Saptırma", "title": "Kareyi Boşaltma Fedası", "fen": "6k1/5ppp/8/8/8/8/4qPPP/4R1K1 b - - 0 1", "moves": ["e2e1"], "rule": "Taktik kazanç için doğru kareyi boşaltmak oyunun kaderini belirler.", "desc": "Taktik kazanç için doğru kareyi boşaltmak oyunun kaderini belirler."},
  {"id": 35, "cat": "Saptırma", "title": "Saptırma ile Piyon Terfisi", "fen": "8/4P3/8/8/8/6k1/6p1/6K1 w - - 0 1", "moves": ["e7e8q"], "rule": "Rakibin dikkatini saptırarak piyonu vezire dönüştürmek maçı kazandırır.", "desc": "Rakibin dikkatini saptırarak piyonu vezire dönüştürmek maçı kazandırır."},
  {"id": 36, "cat": "Yok Etme", "title": "Kilit Taşı Kesip Atma", "fen": "r1b1k2r/pppp1ppp/2n5/4p3/1b2P3/2NP1N2/PPP1BPPP/R1BQK2R b KQkq - 0 6", "moves": ["b4c3"], "rule": "Rakibin savunmasını ayakta tutan tek bir kilit taşı yok ettiğinde tüm kale çöker.", "desc": "Rakibin savunmasını ayakta tutan tek bir kilit taşı yok ettiğinde tüm kale çöker."},
  {"id": 37, "cat": "Yok Etme", "title": "Koruyucu Atı Tehdit Etme", "fen": "r1bqk2r/pppp1ppp/2n2n2/4p3/1bB1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 4 5", "moves": ["c3d5"], "rule": "Merkezi savunan taşları tehdit ederek rakibi taviz vermeye zorla.", "desc": "Merkezi savunan taşları tehdit ederek rakibi taviz vermeye zorla."},
  {"id": 38, "cat": "Yok Etme", "title": "f7 Savunmasını Çökertme", "fen": "r1bqk2r/pppp1ppp/5n2/4p3/1bB1P3/2NP1N2/PPP2PPP/R1BQK2R w KQkq - 0 6", "moves": ["c4f7"], "rule": "Savunmacıyı ortadan kaldırmak şahı korumasız bırakır ve taş dengesini bozar.", "desc": "Savunmacıyı ortadan kaldırmak şahı korumasız bırakır ve taş dengesini bozar."},
  {"id": 39, "cat": "Yok Etme", "title": "Kale Takası ile Matı Netleştirme", "fen": "4r1k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1", "moves": ["e1e8"], "rule": "Savunma taşını tahtadan temizlemek en basit ve temiz kazanç yoludur.", "desc": "Savunma taşını tahtadan temizlemek en basit ve temiz kazanç yoludur."},
  {"id": 40, "cat": "Yok Etme", "title": "Merkezi Piyonla Yarma", "fen": "r1bqk2r/pppp1ppp/2n5/4P3/1bB1n3/2N2N2/PPP2PPP/R1BQK2R w KQkq - 0 7", "moves": ["c4f7"], "rule": "Piyon siperini kırdığında şah tahtanın ortasında avlanır.", "desc": "Piyon siperini kırdığında şah tahtanın ortasında avlanır."},
  {"id": 41, "cat": "Aşırı Yükleme", "title": "İki Yeri Birden Koruyan Taş", "fen": "r4rk1/5ppp/8/8/8/8/1q3PPP/R2Q2K1 b - - 0 1", "moves": ["a8a1"], "rule": "Bir taş aynı anda iki kritik görevi yerine getiremez; yüklendiğinde yıkılır.", "desc": "Bir taş aynı anda iki kritik görevi yerine getiremez; yüklendiğinde yıkılır."},
  {"id": 42, "cat": "Aşırı Yükleme", "title": "Ara Hamle ile Taş Kurtarma", "fen": "r1b1k2r/pppp1ppp/2n5/4p3/1b2q3/2N2N2/PPPPBPPP/R1BQK2R w KQkq - 0 7", "moves": ["c3e4"], "rule": "Rakibin hamlesine aceleyle yanıt vermek yerine araya sıkıştırılan darbe maçı kazandırır.", "desc": "Rakibin hamlesine aceleyle yanıt vermek yerine araya sıkıştırılan darbe maçı kazandırır."},
  {"id": 43, "cat": "Aşırı Yükleme", "title": "Aşırı Yüklü Vezir", "fen": "r1b2rk1/ppp2ppp/8/8/1bB5/5Q2/PPP2PPP/R1B1R1K1 w - - 0 1", "moves": ["f3f7"], "rule": "Aşırı yüklü vezir arka sırayı tutamaz; taktik darbe oyunu bitirir.", "desc": "Aşırı yüklü vezir arka sırayı tutamaz; taktik darbe oyunu bitirir."},
  {"id": 44, "cat": "Aşırı Yükleme", "title": "Ara Şah ile İnisiyaf", "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5", "moves": ["c4f7"], "rule": "Taş kaybetmeden önce çekilen bir ara şah, inisiyatifi sana geçirir.", "desc": "Taş kaybetmeden önce çekilen bir ara şah, inisiyatifi sana geçirir."},
  {"id": 45, "cat": "Aşırı Yükleme", "title": "Savunmayı Aşırı Zorlama", "fen": "4r1k1/5ppp/8/8/8/8/1Q3PPP/4R1K1 w - - 0 1", "moves": ["e1e8"], "rule": "Rakip savunmayı birden fazla cephede test et, aşırı yüklenen hat çökecektir.", "desc": "Rakip savunmayı birden fazla cephede test et, aşırı yüklenen hat çökecektir."},
  {"id": 46, "cat": "Terfi", "title": "Durdurulamayan Geçer Piyon", "fen": "8/4P1k1/8/8/8/8/8/6K1 w - - 0 1", "moves": ["e7e8q"], "rule": "Önünde engel kalmayan geçer piyon vezire çıkarak oyunu kesin zafere ulaştırır.", "desc": "Önünde engel kalmayan geçer piyon vezire çıkarak oyunu kesin zafere ulaştırır."},
  {"id": 47, "cat": "Terfi", "title": "Piyon Yarma Harekatı", "fen": "8/5k2/8/8/8/8/5P2/4K3 w - - 0 1", "moves": ["f2f4"], "rule": "Son oyunda geçer piyon yaratmak büyükustaların en önemli hedefidir.", "desc": "Son oyunda geçer piyon yaratmak büyükustaların en önemli hedefidir."},
  {"id": 48, "cat": "Terfi", "title": "Kare Kuralı ile Kaçış", "fen": "8/8/8/8/3P4/8/1k6/4K3 w - - 0 1", "moves": ["d4d5"], "rule": "Kare kuralına göre rakip şah piyonun karesine giremiyorsa piyon tek başına vezir olur.", "desc": "Kare kuralına göre rakip şah piyonun karesine giremiyorsa piyon tek başına vezir olur."},
  {"id": 49, "cat": "Terfi", "title": "Omuzlama ile Şahı Engelleme", "fen": "8/8/8/8/8/3k4/4p3/4K3 b - - 0 1", "moves": ["d3e3"], "rule": "Kendi şahınla rakip şahı omuzlayarak piyonun terfi karesini garantiye al.", "desc": "Kendi şahınla rakip şahı omuzlayarak piyonun terfi karesini garantiye al."},
  {"id": 50, "cat": "Terfi", "title": "Vezir Terfisi ile Galibiyet", "fen": "8/1P6/8/8/8/8/5k2/7K w - - 0 1", "moves": ["b7b8q"], "rule": "Vezire terfi eden piyon tek başına kalan şaha karşı anında mat ağını örer.", "desc": "Vezire terfi eden piyon tek başına kalan şaha karşı anında mat ağını örer."},
];

let activeBot = BOTS.engine[2];
let currentPuzzle = null;

/* Chess.com Tarzı İnsan Bot Konuşması (Sessiz, Emojisiz, Sadece Balon Mesajı) */
let bubbleTimer = null;
const BotChat = {
  enabled: true,
  show(text) {
    if (!this.enabled || !text || G.mode !== 'ai') return;
    const topBar = document.getElementById('plTop');
    if (!topBar) return;
    const nm = topBar.querySelector('.nm');
    if (!nm) return;

    let wrap = topBar.querySelector('.bot-bubble-wrap');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.className = 'bot-bubble-wrap';
      topBar.appendChild(wrap);
    }
    wrap.textContent = '';
    const b = document.createElement('div');
    b.className = 'bot-bubble';
    b.textContent = text;
    wrap.appendChild(b);

    if (bubbleTimer) clearTimeout(bubbleTimer);
    bubbleTimer = setTimeout(() => {
      b.classList.add('fade-out');
      setTimeout(() => { if (wrap.contains(b)) wrap.removeChild(b); }, 400);
    }, 4500);
  },
  onStart(bot) {
    const list = [
      `İyi şanslar, keyifli bir maç olsun.`,
      `Merhaba! İlk hamleni bekliyorum.`,
      `Hadi başlayalım, iyi olan kazansın.`
    ];
    this.show(list[Math.floor(Math.random() * list.length)]);
  },
  onCapture(isBot) {
    const bQuotes = ['Bu taşı almam gerekiyordu.', 'Merkezdeki baskıyı artırıyorum.', 'Dengeli bir takas oldu.'];
    const pQuotes = ['Taşımı aldın, dikkatli oynamalıyım.', 'İyi gördün bunu.', 'Planımı gözden geçirmem gerek.'];
    const list = isBot ? bQuotes : pQuotes;
    this.show(list[Math.floor(Math.random() * list.length)]);
  },
  onCheck(isBot) {
    if (isBot) this.show('Şah! Bakalım nasıl savunacaksın.');
    else this.show('Şah mı? Savunmaya geçmeliyim.');
  },
  onOver(won, draw) {
    if (draw) this.show('Berabere! Denk ve güzel bir mücadeleydi.');
    else if (won) this.show('Tebrik ederim, gerçekten harika oynadın.');
    else this.show('Şah ve mat! İyi bir oyundu, rövanş yapmak ister misin?');
  }
};

/* Canlı Eval Çubuğu */
function updateEvalBar(score, isMate) {
  const fill = document.getElementById('evalFill');
  const tBadge = document.getElementById('evalScoreTop');
  const bBadge = document.getElementById('evalScoreBot');
  if (!fill) return;

  let txt = '0.0';
  let pct = 50;

  if (isMate) {
    txt = 'M' + Math.abs(score);
    pct = score > 0 ? 98 : 2;
  } else {
    txt = (score > 0 ? '+' : '') + score.toFixed(1);
    pct = 50 + 50 * (2 / (1 + Math.exp(-0.35 * score)) - 1);
    pct = Math.max(3, Math.min(97, pct));
  }

  if (G.flipped) pct = 100 - pct;
  fill.style.height = pct + '%';

  if (pct > 50) {
    if (bBadge) bBadge.textContent = txt;
    if (tBadge) tBadge.textContent = '';
  } else {
    if (tBadge) tBadge.textContent = txt;
    if (bBadge) bBadge.textContent = '';
  }
}

let evalAbortCtrl = null;
async function requestEval() {
  if (!G.st) return;
  // AI modunda bot sırasıysa ayrı eval isteği atma, bot hamlesi zaten skoru getiriyor
  if (G.mode === 'ai' && G.st.t !== G.me) return;
  if (evalAbortCtrl) {
    try { evalAbortCtrl.abort(); } catch (e) {}
  }
  evalAbortCtrl = new AbortController();
  try {
    const fen = Chess.toFEN(G.st);
    const r = await fetch('/api/eval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fen }),
      signal: evalAbortCtrl.signal
    });
    if (r.ok) {
      const d = await r.json();
      if (d && typeof d.score === 'number') {
        updateEvalBar(d.score, d.is_mate);
      }
    }
  } catch (e) {}
}

/* Bot Seçim Modalı */

/* =====================================================================
   SESLİ KOÇ ANALİZİ (PIPER TURKISH TTS & GAME REVIEW)
   ===================================================================== */
let coachAudio = null;
let currentAnalysisSession = 0;
const reviewAudioCache = new Map(); // idx -> ObjectURL in RAM

async function speakWithPiper(text, onEnded, moveIdx) {
  if (!text) { if (onEnded) onEnded(); return; }
  const mySession = currentAnalysisSession;
  const btn = document.getElementById('coachPlayBtn');
  if (btn) btn.classList.add('playing');

  // Piper TTS için emojileri ve simgeleri tamamen temizle
  const cleanText = text
    .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu, '')
    .replace(/[💡🎯⚔🏆👍✓📖✕★!?#—]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  let finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    if (btn) btn.classList.remove('playing');
    if (onEnded && mySession === currentAnalysisSession) onEnded();
  };

  if (!cleanText) { finish(); return; }

  try {
    let url = (moveIdx !== undefined && reviewAudioCache.has(moveIdx)) ? reviewAudioCache.get(moveIdx) : null;
    if (!url) {
      const res = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText })
      });
      if (mySession !== currentAnalysisSession) return;
      if (res.ok) {
        const blob = await res.blob();
        if (mySession !== currentAnalysisSession) return;
        url = URL.createObjectURL(blob);
        if (moveIdx !== undefined) reviewAudioCache.set(moveIdx, url);
      }
    }

    if (mySession !== currentAnalysisSession) return;

    if (url) {
      if (coachAudio) {
        coachAudio.pause();
        coachAudio.src = '';
        coachAudio = null;
      }
      coachAudio = new Audio(url);
      coachAudio.playbackRate = 1.0;
      coachAudio.onended = finish;
      coachAudio.onerror = finish;
      coachAudio.play().catch(finish);
      return;
    }
  } catch (e) {}
  finish();
}

function uciToSanSimple(st, uci) {
  if (!uci || uci.length < 4) return uci || '';
  try {
    const m = Chess.fromUci(st, uci);
    if (m != null) return Chess.san(st, m);
  } catch (e) {}
  return uci;
}

// 50 Adet Eğitici Satranç Kuralı & Koçluk Tavsiyesi (Her biri farklı alanda geliştirir)
const COACH_TIPS = [
  { area: 'taktik', tip: 'Çatal (Fork): Bir taşla aynı anda iki düşman taşını tehdit et. Özellikle at çatalları vezir ve kaleyi aynı anda yakalamada ölümcüldür!' },
  { area: 'taktik', tip: 'Şiş (Skewer): Öndeki değerli taşa şah veya saldırı yaparak kaçmaya zorla, arkasındaki savunmasız taşı düşür.' },
  { area: 'taktik', tip: 'Açmaz (Pin): Rakibin taşını şahın önüne bağla. Açmazdaki taş asla hareket edemez, üzerine baskıyı artır.' },
  { area: 'taktik', tip: 'Açarak Şah (Discovered Check): Önündeki taşı çekerek arkadaki kalenin veya filin şah çekmesini sağla. Çifte şah kaçınılmazdır!' },
  { area: 'taktik', tip: 'Boğmaca Matı: Şah kendi taşları arasına sıkışmışken at ile yapılan efsanevi mat türüdür.' },
  { area: 'taktik', tip: 'Arka Sıra Matı: Rok yapmış şahın önündeki piyonlar sürülmemişse, kale veya vezir 1. ya da 8. yataydan mat eder.' },
  { area: 'taktik', tip: 'Saptırma Fedası: Rakibin kritik kareyi koruyan taşını feda ile saptır, ardından ana hedefe vur.' },
  { area: 'taktik', tip: 'Savunmayı Yok Etme: Rakip taşı koruyan taşı al veya kov; böylece asıl hedef savunmasız kalsın.' },
  { area: 'taktik', tip: 'Zorlayıcı Hamleler: Hesap yaparken her zaman sırasıyla: 1. Şah çekişler, 2. Taş alışları, 3. Doğrudan tehditleri hesapla.' },
  { area: 'taktik', tip: 'İki Hamle Kuralı: Hamleni yapmadan önce tahtadaki en iyi alternatif 2. hamleyi de mutlaka düşün ve karşılaştır.' },
  { area: 'konum', tip: 'Merkez Kontrolü: e4, d4, e5, d5 kareleri tahtanın kalbidir. Merkezi tutan taraf kanat hücumlarını kolayca püskürtür.' },
  { area: 'konum', tip: 'Hafif Taş Gelişimi: İlk 10 hamlede atları ve filleri hızlıca oyuna sok. Aynı taşla art arda oynamaktan kaçın.' },
  { area: 'konum', tip: 'Erken Rok: Şahını ilk 8-10 hamle içinde güvenli köşeye al, kaleni merkeze bağla.' },
  { area: 'konum', tip: 'Açık Hat Hakimiyeti: Kalelerini daima açık veya yarı açık hatlara yerleştir; 7. yataya sızan kale maç kazandırır.' },
  { area: 'konum', tip: 'Fil Çifti Üstünlüğü: Açık pozisyonlarda iki fil tahtayı çaprazlama dilimler. Sebepsiz yere filini ata değişme.' },
  { area: 'konum', tip: 'Zayıf Kareler: Rakip piyonların koruyamadığı delikleri atların için karakol (outpost) olarak kullan.' },
  { area: 'konum', tip: 'İzole Piyonlar: Desteksiz kalan izole piyonların önündeki kareyi bloke et ve arkadan baskı kur.' },
  { area: 'konum', tip: 'Bağlı Geçer Piyonlar: Yan yana ilerleyen iki geçer piyon bir kaleye bile bedel olabilir; durdurulamaz bir güçtür.' },
  { area: 'konum', tip: 'Alan Avantajı: Piyon zincirinle rakibi geriye ittiğinde taşların daha serbest manevra yapar, rakip boğulur.' },
  { area: 'konum', tip: 'Taş Uyumu (Harmoni): Taşların birbirini korumalı ve ortak bir hedefe odaklanmalı. Dağınık taş hedef olur.' },
  { area: 'konum', tip: 'Profilaksi: Kendi planını kurmadan önce daima "Rakibimin bu hamledeki gizli amacı ne?" sorusunu sor.' },
  { area: 'konum', tip: 'Kanat Hücumu Kuralı: Kanattan saldırmadan önce merkezin kapalı veya kontrolünde olduğundan emin ol.' },
  { area: 'sonoyun', tip: 'Aktif Şah: Son oyunda şah korkak değil, tahtanın en güçlü hücum taşlarından biridir; merkeze koş!' },
  { area: 'sonoyun', tip: 'Geçer Piyon Yarat: Son oyunun ana hedefi vezire koşan bir geçer piyon üretmektir.' },
  { area: 'sonoyun', tip: 'Kare Kuralı: Şahın vezire koşan piyonu yakalayıp yakalayamayacağını piyon karesini çizerek bir saniyede hesapla.' },
  { area: 'sonoyun', tip: 'Muhalefet (Opposition): Şahlar arasında 1 kare kaldığında hamle sırası rakipteyse muhalefeti sen almışsındır.' },
  { area: 'sonoyun', tip: 'Kale Piyonun Arkasında: Kaleni kendi geçer piyonunun arkasına koyarak piyonu ileri it, rakip piyonu ise arkadan kovala.' },
  { area: 'sonoyun', tip: 'Lucena Pozisyonu: Kale son oyunlarında köprü kurma tekniğini bilmek kesin galibiyet getirir.' },
  { area: 'sonoyun', tip: 'Philidor Savunması: Kale son oyunlarında 6. yatay kalesiyle pasif beraberlik alma tekniğini uygula.' },
  { area: 'sonoyun', tip: 'Karşıt Renkli Filler: Bir piyon eksik olsan bile karşıt renkli fil son oyunlarında beraberlik şansı çok yüksektir.' },
  { area: 'sonoyun', tip: 'İki Zayıflık İlkesi: Rakibin tek zayıflığını koruması kolaydır; tahtanın diğer tarafında ikinci bir zayıflık yarat.' },
  { area: 'sonoyun', tip: 'Zugzwang: Rakibi öyle bir pozisyona sok ki, yapacağı her hamle durumunu daha da kötüleştirsin.' },
  { area: 'acilis', tip: 'Erken Vezir Tuzağı: Veziri ilk birkaç hamlede oyuna sokma; rakip hafif taşlarını geliştirirken vezirini kovalar.' },
  { area: 'acilis', tip: 'Piyon Çılgınlığı Yapma: Açılışta sadece merkezi tutacak kadar (genelde 2-3) piyon sür, taşlarını uyutma.' },
  { area: 'acilis', tip: 'Atlar Filden Önce: Genellikle atları c3/f3 veya c6/f6 karelerine fillerden önce geliştirmek konumu sağlam tutar.' },
  { area: 'acilis', tip: 'Açılış İlkeleri: 1. Merkeze hakim ol, 2. Hafif taşları geliştir, 3. Rok yap, 4. Kaleleri bağla.' },
  { area: 'acilis', tip: 'Gambit Mantığı: Rakip piyon feda ettiğinde gelişimin geri kalacaksa gambiti hemen kabul etme.' },
  { area: 'acilis', tip: 'f Piyonuna Dikkat: Açılışta f2 veya f7 piyonunu sürmek şah çaprazını açar ve ani matlara yol açabilir.' },
  { area: 'acilis', tip: 'Fianchetto Gücü: Fili g2 veya b2ye yerleştirmek uzun diyagonal boyunca müthiş bir baskı kurar.' },
  { area: 'acilis', tip: 'Tempo Kazan: Rakibin taşını tehdit ederek geliştirdiğin her hamle sana bedava bir tempo kazandırır.' },
  { area: 'psikoloji', tip: 'Avantajda Acele Etme: Üstün pozisyondayken maçı tek hamlede bitirmeye çalışma; konumu adım adım sıkılaştır.' },
  { area: 'psikoloji', tip: 'Hata Sonrası Soğukkanlılık: Büyük bir taş kaybettiğinde panikleme; rakip gevşediğinde karşı şanslar doğar.' },
  { area: 'psikoloji', tip: 'Zaman Yönetimi: Açılışta bildiğin hamleleri hızlı oyna, kritik taktik dönemeçlerde süreni cömertçe kullan.' },
  { area: 'psikoloji', tip: 'Sadeleştirme Sanatı: Malzeme olarak öndeysen taşları takas et ve temiz bir son oyuna gir.' },
  { area: 'psikoloji', tip: 'Karşı Oyun Arayışı: Savunmadayken pasif kalma, rakip şaha veya zayıf piyonlara karşı tehditler üret.' },
  { area: 'psikoloji', tip: 'Umutsuz Pozisyon Yoktur: Mat olana kadar tahtada her zaman bir pat veya rakip gafı ihtimali vardır.' },
  { area: 'psikoloji', tip: 'Rakibin Tehdidini Gör: Kendi hamlenden önce "Rakibim en son neyi tehdit etti?" diye sormadan elini uzatma.' },
  { area: 'psikoloji', tip: 'Dikkatsiz Alış Yapma: Otomatik hamle yapma; her taş alışından sonra tahtanın dengesini yeniden tara.' },
  { area: 'psikoloji', tip: 'Kör Noktalar: Geriye doğru yapılan at ve vezir hamleleri insan gözünün en çok kaçırdığı taktiklerdir.' },
  { area: 'psikoloji', tip: 'Her Maç Bir Derstir: Analiz ekranını inceleyerek nerede koptuğunu görmek, 10 maç oynamaktan daha öğreticidir.' }
];

function getRandomTip() {
  return COACH_TIPS[Math.floor(Math.random() * COACH_TIPS.length)];
}

const CAT_INFO = {
  brilliant:   { label: 'Harika!',    icon: '!!', cls: 'ci-brilliant', color: '#26c9c9' },
  great:       { label: 'Çok İyi',    icon: '!',  cls: 'ci-great',     color: '#5b9bd5' },
  best:        { label: 'En İyi',     icon: '★',  cls: 'ci-best',      color: '#96bc4b' },
  excellent:   { label: 'Mükemmel',   icon: '👍', cls: 'ci-excellent', color: '#96bc4b' },
  good:        { label: 'İyi',        icon: '✓',  cls: 'ci-good',      color: '#a3c947' },
  book:        { label: 'Kitap',      icon: '📖', cls: 'ci-book',      color: '#a1887f' },
  inaccuracy:  { label: 'Kusurlu',    icon: '?!', cls: 'ci-inaccuracy',color: '#f0c348' },
  mistake:     { label: 'Hata',       icon: '?',  cls: 'ci-mistake',   color: '#e58c2a' },
  miss:        { label: 'Kaçırma',    icon: '✕',  cls: 'ci-miss',      color: '#db6249' },
  blunder:     { label: 'Vahim Hata', icon: '??', cls: 'ci-blunder',   color: '#ca3431' }
};

function uciSquare(sqStr) {
  if (!sqStr || sqStr.length < 2) return -1;
  const col = sqStr.charCodeAt(0) - 97;
  const row = 8 - Number(sqStr[1]);
  if (col < 0 || col > 7 || row < 0 || row > 7) return -1;
  return row * 8 + col;
}

function generateCoachExplanation(san, bestSan, cat, isWhite, diff, idx, mateIn) {
  const isUser = (isWhite ? 0 : 1) === G.me;
  const mateText = mateIn ? ` ve ${Math.abs(mateIn)} hamlede mat var.` : '.';

  if (isUser) {
    switch (cat) {
      case 'brilliant':
        return `Harika bir taktik hamle! ${san} ile tahtadaki tüm üstünlüğü eline aldın${mateText}`;
      case 'great':
        return `Çok güçlü bir tercih! ${san} ile konumunu belirgin şekilde güçlendirdin${mateText}`;
      case 'best':
        return `${san} bu konumda motorun önerdiği en kusursuz hamle.`;
      case 'excellent':
        return `${san} gayet sağlam ve dengeli bir hamle.`;
      case 'good':
        return `${san} konumu koruyan doğal ve dengeli bir hamle.`;
      case 'book':
        return `${san} standart açılış teorisine tam uyan bir kitap hamlesi.`;
      case 'inaccuracy':
        return `${san} biraz pasif kaldı. Bunun yerine ${bestSan} oynamak daha güçlüydü.`;
      case 'mistake':
        return `${san} hatalı bir tercih oldu. Doğru hamle ${bestSan} olmalıydı.`;
      case 'miss':
        return `${san} ile büyük bir fırsatı kaçırdın. En iyi hamle ${bestSan} idi${mateText}`;
      case 'blunder':
      default:
        return `${san} vahim bir hata oldu ve ciddi bir avantaj kaybettirdi. Doğrusu ${bestSan} olmalıydı${mateText}`;
    }
  } else {
    switch (cat) {
      case 'brilliant':
        return `Rakip çok etkili bir taktik buldu. ${san} ile tahtada tehlikeli bir baskı kurdu${mateText}`;
      case 'great':
        return `Rakip güçlü bir hamle yaptı. ${san} ile pozisyonunu sağlamlaştırdı${mateText}`;
      case 'best':
        return `Rakip bu konumdaki en iyi hamleyi buldu: ${san}.`;
      case 'excellent':
        return `Rakip ${san} ile sağlam ve dengeli bir hamle tercih etti.`;
      case 'good':
        return `Rakip oyunu dengede tutan ${san} hamlesini oynadı.`;
      case 'book':
        return `Rakip standart açılış teorisine uygun olarak ${san} oynadı.`;
      case 'inaccuracy':
        return `Rakip ${san} ile pasif bir hamle yaptı. En iyi tercihi ${bestSan} idi, bu senin lehine.`;
      case 'mistake':
        return `Rakip ${san} oynayarak hata yaptı. Doğru hamlesi ${bestSan} olmalıydı.`;
      case 'miss':
        return `Rakip büyük bir şansı kaçırdı. ${san} yerine ${bestSan} oynayabilirdi.`;
      case 'blunder':
      default:
        return `Rakip ${san} ile vahim bir hata yaptı! En iyi tercihi ${bestSan} idi, şimdi fırsat sende${mateText}`;
    }
  }
}

// Chess.com Tarzı Avantaj Grafiği (SVG)
function buildEvalGraph(scores, moveData, onDotClick) {
  const w = 320, ht = 66;
  const wrap = h('div', { class: 'eval-graph-wrap' });
  wrap.append(h('div', { class: 'eval-graph-mid' }));

  if (!scores || scores.length < 2) {
    wrap.append(h('div', { class: 'mut', text: 'Analiz grafiği hazırlanıyor...', style: { textAlign: 'center', padding: '28px', fontSize: '12px' } }));
    return wrap;
  }

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${w} ${ht}`);
  svg.setAttribute('preserveAspectRatio', 'none');
  svg.classList.add('eval-graph-svg');

  const toY = sc => {
    const c = Math.max(-7, Math.min(7, sc));
    return (ht / 2) - (c / 7) * (ht / 2 - 4);
  };
  const toX = i => (i / (scores.length - 1)) * w;

  // Beyaz avantaj alanı (orta çizginin üstü)
  let wPath = `M 0,${ht / 2}`;
  for (let i = 0; i < scores.length; i++) {
    const y = Math.min(ht / 2, toY(scores[i]));
    wPath += ` L ${toX(i)},${y}`;
  }
  wPath += ` L ${w},${ht / 2} Z`;
  const wArea = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  wArea.setAttribute('d', wPath); wArea.classList.add('eval-area-w');
  svg.appendChild(wArea);

  // Siyah avantaj alanı (orta çizginin altı)
  let bPath = `M 0,${ht / 2}`;
  for (let i = 0; i < scores.length; i++) {
    const y = Math.max(ht / 2, toY(scores[i]));
    bPath += ` L ${toX(i)},${y}`;
  }
  bPath += ` L ${w},${ht / 2} Z`;
  const bArea = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  bArea.setAttribute('d', bPath); bArea.classList.add('eval-area-b');
  svg.appendChild(bArea);

  // Eval eğrisi
  let linePath = '';
  for (let i = 0; i < scores.length; i++) {
    linePath += (i === 0 ? 'M ' : ' L ') + `${toX(i)},${toY(scores[i])}`;
  }
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  line.setAttribute('d', linePath); line.classList.add('eval-line');
  svg.appendChild(line);

  // Hatalı hamle noktacıkları (Tıklanabilir)
  if (moveData) {
    moveData.forEach((m, i) => {
      if (['blunder', 'miss', 'mistake', 'inaccuracy'].includes(m.category)) {
        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', toX(i + 1));
        dot.setAttribute('cy', toY(scores[i + 1] || 0));
        dot.setAttribute('r', m.category === 'blunder' || m.category === 'miss' ? '4.5' : '3.5');
        dot.classList.add('eval-dot');
        if (m.category === 'blunder') dot.classList.add('bad');
        else if (m.category === 'miss') dot.classList.add('miss');
        else if (m.category === 'inaccuracy') dot.classList.add('inac');
        else dot.classList.add('bad');
        dot.style.cursor = 'pointer';
        dot.addEventListener('click', () => onDotClick && onDotClick(i));
        svg.appendChild(dot);
      }
    });
  }

  wrap.append(svg);
  return wrap;
}

/* =====================================================================
   CHESS.COM KALİTESİNDE SAĞ PANEL MAÇ ANALİZİ (GAME REVIEW)
   ===================================================================== */
let reviewAutoTimer = null;
let isReviewAuto = false;
let currentReviewIndex = 0;
let cachedReviewData = null;

function closeSidebarReview() {
  currentAnalysisSession++;
  if (reviewAutoTimer) { clearTimeout(reviewAutoTimer); reviewAutoTimer = null; }
  isReviewAuto = false;
  if (coachAudio) { coachAudio.pause(); coachAudio.src = ''; coachAudio = null; }
  G.ov = []; drawOv();

  reviewAudioCache.forEach(url => URL.revokeObjectURL(url));
  reviewAudioCache.clear();

  G.mode = 'ai';

  const sb = document.getElementById('reviewSidebar');
  const gp = document.getElementById('gamePanel');
  if (sb) { sb.style.display = 'none'; sb.textContent = ''; }
  if (gp) gp.style.display = 'flex';

  goto(G.moves.length);
  updateAll();
}

async function startSidebarReview() {
  hideResult();
  currentAnalysisSession++;
  const thisSession = currentAnalysisSession;
  if (reviewAutoTimer) { clearTimeout(reviewAutoTimer); reviewAutoTimer = null; }
  isReviewAuto = false;
  if (coachAudio) { coachAudio.pause(); coachAudio.src = ''; coachAudio = null; }
  reviewAudioCache.forEach(url => URL.revokeObjectURL(url));
  reviewAudioCache.clear();

  const gp = document.getElementById('gamePanel');
  const sb = document.getElementById('reviewSidebar');
  if (!sb || !gp) return;

  gp.style.display = 'none';
  sb.style.display = 'flex';
  sb.style.flexDirection = 'column';
  sb.style.width = '100%';
  sb.textContent = '';

  const header = h('div', { class: 'mhead', style: { width: '100%', boxSizing: 'border-box', padding: '4px 0 8px 0', borderBottom: '1px solid var(--line)' } },
    h('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
      h('img', { src: '/sprite/magnifier-analysis.svg', style: { width: '22px', height: '22px' } }),
      h('h3', { text: 'Game Review', style: { fontSize: '18px' } })
    ),
    h('button', { class: 'btn ghost', style: { padding: '4px 10px', fontSize: '12px' }, text: '✕ Kapat', onclick: closeSidebarReview })
  );
  sb.append(header);

  if (!G.moves.length) {
    sb.append(h('div', { class: 'coach-wrap', style: { textAlign: 'center', padding: '20px' } },
      h('img', { class: 'coach-av', src: '/sprite/coachdavid.png', style: { width: '56px', height: '56px', margin: '0 auto 8px auto' }, alt: 'Coach David' }),
      h('h4', { text: 'Koç David Hazır' }),
      h('p', { class: 'mut', text: 'Maçta henüz hamle oynanmadı. Maç bittikten sonra tüm hamleleri analiz edeceğim.' }),
      h('button', { class: 'btn pri', style: { marginTop: '12px' }, text: 'Tahtaya Dön', onclick: closeSidebarReview })
    ));
    return;
  }

  const progPct = h('div', { class: 'review-prog-pct', text: '0%' });
  const progFill = h('div', { class: 'review-prog-fill', style: { width: '0%' } });
  const progStatus = h('div', { style: { fontSize: '12px', color: 'var(--mute)' }, text: 'Stockfish 19 motoru konumları derinlemesine inceliyor...' });

  const progCard = h('div', { class: 'review-prog-card', style: { width: '100%', boxSizing: 'border-box' } },
    h('img', { class: 'coach-av', src: '/sprite/coachdavid.png', style: { width: '52px', height: '52px', margin: '0 auto' } }),
    h('h4', { text: 'Koç David Maçı İnceliyor...' }),
    progPct,
    h('div', { class: 'review-prog-track' }, progFill),
    progStatus
  );
  sb.append(progCard);

  function setProgress(pct, statusText) {
    const p = Math.max(0, Math.min(100, Math.round(pct)));
    progPct.textContent = p + '%';
    progFill.style.width = p + '%';
    if (statusText) progStatus.textContent = statusText;
  }

  let currentPct = 10;
  setProgress(10, 'Açılış teorisi ve piyon yapıları inceleniyor...');
  const progTimer = setInterval(() => {
    if (thisSession !== currentAnalysisSession) { clearInterval(progTimer); return; }
    if (currentPct < 65) {
      currentPct += (65 - currentPct) * 0.15 + 1;
      let msg = 'Koç David kritik hamleleri değerlendiriyor...';
      if (currentPct > 35) msg = 'Taktik fırsatlar ve mat mesafeleri hesaplanıyor...';
      setProgress(currentPct, msg);
    }
  }, 200);

  const fens = G.states.slice(0, G.moves.length + 1).map(s => Chess.toFEN(s));
  const uciMoves = G.moves.map(m => Chess.toUci(m));

  let analysisResp = { moves: [], summary: {} };
  try {
    const resp = await fetch('/api/analyze/game', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fens, moves: uciMoves })
    });
    if (resp.ok) {
      analysisResp = await resp.json();
    }
  } catch (e) {}

  clearInterval(progTimer);

  const moveResults = analysisResp.moves || [];
  const summary = analysisResp.summary || {};

  if (!moveResults.length) {
    progCard.remove();
    sb.append(h('p', { class: 'mut', text: 'Analiz verisi alınamadı. Lütfen tekrar deneyin.' }));
    return;
  }

  cachedReviewData = analysisResp;

  const wStats = summary.white || { accuracy: 75, rating: 1500, counts: {}, phase_ratings: {} };
  const bStats = summary.black || { accuracy: 75, rating: 1500, counts: {}, phase_ratings: {} };
  const gameDesc = summary.game_desc || 'DENGELİ';
  const scores = summary.scores || [];

  const reviewItems = moveResults.map((it, idx) => {
    const isW = (idx % 2 === 0);
    const st = G.states[idx];
    const san = G.sans[idx] || it.played;
    const bestSan = uciToSanSimple(st, it.best);
    const catInfo = CAT_INFO[it.category] || CAT_INFO.good;
    const expl = generateCoachExplanation(san, bestSan, it.category, isW, it.diff, idx, it.mate_in);
    return {
      idx,
      san,
      bestSan,
      playedUci: it.played,
      bestUci: it.best,
      score: it.score,
      diff: it.diff,
      loss: it.loss,
      mateIn: it.mate_in,
      category: it.category,
      phase: it.phase,
      label: catInfo.label,
      icon: catInfo.icon,
      cls: catInfo.cls,
      color: catInfo.color,
      comment: expl,
      isWhite: isW
    };
  });

  // RAM'e Ses Önbellekleme (Audio Pre-caching into RAM) - Hızlı ve Akıllı Paralel Yükleme
  setProgress(70, "Koç David kritik hamleleri ve fırsatları değerlendiriyor...");
  const itemsToPreload = reviewItems.filter((it, idx) => idx < 8 || ['blunder', 'miss', 'mistake'].includes(it.category));
  let loadedCount = 0;

  const batchSize = 3;
  for (let i = 0; i < itemsToPreload.length; i += batchSize) {
    if (thisSession !== currentAnalysisSession) return;
    const chunk = itemsToPreload.slice(i, i + batchSize);
    await Promise.all(chunk.map(async (it) => {
      if (thisSession !== currentAnalysisSession) return;
      if (!reviewAudioCache.has(it.idx)) {
        try {
          const res = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: it.comment })
          });
          if (thisSession === currentAnalysisSession && res.ok) {
            const blob = await res.blob();
            if (thisSession === currentAnalysisSession) {
              reviewAudioCache.set(it.idx, URL.createObjectURL(blob));
            }
          }
        } catch (e) {}
      }
      loadedCount++;
      if (thisSession === currentAnalysisSession) {
        const p = 70 + (loadedCount / itemsToPreload.length) * 30;
        setProgress(p, `Koç David maçı inceliyor (%${Math.round(p)})...`);
      }
    }));
  }

  // Kalan tüm hamleleri de arka planda sessizce RAM'e önbellekle
  (async () => {
    for (const it of reviewItems) {
      if (thisSession !== currentAnalysisSession) break;
      if (!reviewAudioCache.has(it.idx)) {
        try {
          const res = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: it.comment })
          });
          if (thisSession !== currentAnalysisSession) break;
          if (res.ok) {
            const blob = await res.blob();
            if (thisSession === currentAnalysisSession) {
              reviewAudioCache.set(it.idx, URL.createObjectURL(blob));
            }
          }
        } catch (e) {}
      }
    }
  })();

  setProgress(100, 'Analiz Tamamlandı! Rapor açılıyor...');
  await new Promise(r => setTimeout(r, 250));
  progCard.remove();

  const content = h('div', { style: { display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', minWidth: '0', boxSizing: 'border-box' } });
  let activeTab = 'report';

  const tabs = h('div', { class: 'review-tabs' });
  const tabReport = h('button', { class: 'review-tab on', text: 'Rapor', onclick: () => switchTab('report') });
  const tabAnalysis = h('button', { class: 'review-tab', text: 'Analiz & Akış', onclick: () => switchTab('analysis') });
  tabs.append(tabReport, tabAnalysis);
  sb.append(tabs, content);

  function switchTab(tab) {
    activeTab = tab;
    [tabReport, tabAnalysis].forEach(t => t.classList.remove('on'));
    if (tab === 'report') {
      tabReport.classList.add('on');
      renderReport();
    } else {
      tabAnalysis.classList.add('on');
      renderAnalysis();
    }
  }

  // ==================== 1. RAPOR BÖLÜMÜ ====================
  function renderReport() {
    content.textContent = '';

    const descMap = {
      'USTALIK': 'Büyükusta seviyesinde kusursuz ve tavizsiz bir oyun!',
      'DENGELİ': 'Her iki tarafın da sağlam durduğu, dengeli ve taktiksel bir maç.',
      'ÇILGIN': 'Büyük fırsatların yakalanıp kaçırıldığı çılgın bir mücadele!',
      'SERT': 'Keskin hamleler ve agresif saldırılarla dolu çetin bir kapışma.'
    };

    content.append(h('div', { class: 'game-desc' },
      h('div', { text: '⚔ ' + gameDesc }),
      h('div', { class: 'game-desc-text', text: descMap[gameDesc] || descMap['DENGELİ'] })
    ));

    // Doğruluk Çemberleri
    content.append(h('div', { class: 'acc-big' },
      h('div', { class: 'acc-side' },
        h('div', { class: 'acc-circle w', text: '%' + wStats.accuracy.toFixed(1) }),
        h('div', { class: 'acc-name', text: 'Beyaz' }),
        h('div', { class: 'acc-score-label', text: 'Doğruluk' })
      ),
      h('div', { style: { fontSize: '18px', fontWeight: '700', color: 'var(--mute)' }, text: 'VS' }),
      h('div', { class: 'acc-side' },
        h('div', { class: 'acc-circle b', text: '%' + bStats.accuracy.toFixed(1) }),
        h('div', { class: 'acc-name', text: 'Siyah' }),
        h('div', { class: 'acc-score-label', text: 'Doğruluk' })
      )
    ));

    // Avantaj Grafiği
    content.append(buildEvalGraph(scores, moveResults, i => {
      switchTab('analysis');
      setTimeout(() => stepTo(i), 50);
    }));

    // Kategori Sayım Tablosu
    const cats = ['brilliant', 'great', 'best', 'excellent', 'good', 'book', 'inaccuracy', 'mistake', 'miss', 'blunder'];
    const table = h('table', { class: 'cat-table' });
    cats.forEach(c => {
      const info = CAT_INFO[c];
      const wc = (wStats.counts && wStats.counts[c]) || 0;
      const bc = (bStats.counts && bStats.counts[c]) || 0;
      if (wc === 0 && bc === 0 && (c === 'brilliant' || c === 'great' || c === 'miss')) return;

      const row = h('tr', {},
        h('td', { text: String(wc), style: { color: wc > 0 ? '#f0f2f5' : 'var(--mute)', fontWeight: wc > 0 ? '800' : '500' } }),
        h('td', {},
          h('div', { style: { display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' } },
            h('span', { class: 'cat-icon ' + info.cls, text: info.icon }),
            h('span', { text: info.label, style: { color: info.color, fontWeight: '700' } })
          )
        ),
        h('td', { text: String(bc), style: { color: bc > 0 ? '#bbb' : 'var(--mute)', fontWeight: bc > 0 ? '800' : '500' } })
      );
      table.append(row);
    });
    content.append(table);

    // Oyun Derecesi (Elo)
    content.append(h('div', { class: 'game-rating-row' },
      h('div', { class: 'game-rating-label', text: 'Tahmini Derece (Elo)' }),
      h('span', { class: 'game-rating-val gr-w', text: String(wStats.rating || 1500) }),
      h('span', { class: 'game-rating-val gr-b', text: String(bStats.rating || 1500) })
    ));

    // Fazlar
    const phaseList = [['opening', 'Açılış'], ['middlegame', 'Orta Oyun'], ['endgame', 'Son Oyun']];
    phaseList.forEach(([key, label]) => {
      const wp = (wStats.phase_ratings && wStats.phase_ratings[key]) || null;
      const bp = (bStats.phase_ratings && bStats.phase_ratings[key]) || null;
      if (!wp && !bp) return;
      const wpInfo = wp ? (CAT_INFO[wp] || CAT_INFO.good) : null;
      const bpInfo = bp ? (CAT_INFO[bp] || CAT_INFO.good) : null;
      content.append(h('div', { class: 'phase-row' },
        wpInfo ? h('span', { class: 'phase-badge ' + wpInfo.cls, text: wpInfo.icon }) : h('span'),
        h('span', { class: 'phase-name', text: label, style: { textAlign: 'center' } }),
        bpInfo ? h('span', { class: 'phase-badge ' + bpInfo.cls, text: bpInfo.icon }) : h('span')
      ));
    });

    // İncelemeyi Başlat Butonu
    content.append(h('button', { class: 'start-review-btn', onclick: () => { switchTab('analysis'); } },
      h('img', { src: '/sprite/magnifier-analysis.svg', style: { width: '22px', height: '22px' } }),
      h('span', { text: 'İncelemeyi Başlat (Start Review)' })
    ));
  }

  // ==================== 2. ANALİZ VE SESLİ AKIŞ BÖLÜMÜ ====================
  function renderAnalysis() {
    content.textContent = '';

    const badgeSpan = h('span', { class: 'cat-icon ' + reviewItems[0].cls, text: reviewItems[0].icon, style: { width: '22px', height: '22px', fontSize: '11px', flexShrink: '0' } });
    const moveLabelSpan = h('span', { text: reviewItems[0].san, style: { fontWeight: '800', fontSize: '15px' } });
    const catLabelSpan = h('span', { text: reviewItems[0].label, style: { color: reviewItems[0].color, fontWeight: '700' } });
    const bestMoveInfo = h('div', { style: { fontSize: '12px', color: '#96bc4b', fontWeight: '700', marginBottom: '4px' } });
    const coachText = h('div', { text: reviewItems[0].comment, style: { fontSize: '13px', lineHeight: '1.45', whiteSpace: 'pre-line', wordBreak: 'break-word' } });

    const continueBtn = h('button', {
      class: 'btn pri',
      style: { width: '100%', fontSize: '14px', fontWeight: '800', background: 'linear-gradient(145deg,#2e7d32,#1b5e20)', color: '#fff', marginTop: '6px' },
      text: 'Devam Et ▶',
      onclick: () => {
        if (coachAudio) coachAudio.pause();
        continueBtn.hidden = true;
        tryPuzzleBtn.hidden = true;
        showSolutionBtn.hidden = true;
        isReviewAuto = true;
        G.mode = 'ai';
        const tb = document.getElementById('autoToggleBtnSidebar');
        if (tb) tb.textContent = '⏸ Duraklat';
        stepTo(currentReviewIndex + 1);
      }
    });
    continueBtn.hidden = true;

    const tryPuzzleBtn = h('button', {
      class: 'btn',
      style: { width: '100%', fontSize: '13px', fontWeight: '700', background: 'rgba(230,181,102,.2)', color: 'var(--acc)', border: '1px solid var(--acc)', marginTop: '4px' },
      text: '🎯 Hamleyi Bul (Bulmaca Modu)',
      onclick: () => {
        const it = reviewItems[currentReviewIndex];
        startBlunderPuzzle(it);
      }
    });
    tryPuzzleBtn.hidden = true;

    const showSolutionBtn = h('button', {
      class: 'btn ghost',
      style: { width: '100%', fontSize: '12px', padding: '5px', color: 'var(--acc)', border: '1px dashed var(--acc)', marginTop: '4px' },
      text: '💡 Çözümü Göster',
      onclick: () => {
        const it = reviewItems[currentReviewIndex];
        toast('En iyi hamle: ' + it.bestSan);
        coachText.textContent = `En iyi hamle: ${it.bestSan}. Şimdi bu hamleyi tahtada oyna!`;
        speakWithPiper('En iyi hamle: ' + it.bestSan);
        if (it.bestUci && it.bestUci.length >= 4) {
          const bf = uciSquare(it.bestUci.slice(0, 2));
          const bt = uciSquare(it.bestUci.slice(2, 4));
          G.ov = [{ t: 'a', a: bf, b: bt, color: 'rgb(40, 220, 100)', k: 'best-sol' }];
          drawOv();
        }
      }
    });
    showSolutionBtn.hidden = true;

    const navRow = h('div', { class: 'row', style: { gap: '3px', margin: '4px 0', width: '100%', boxSizing: 'border-box' } },
      h('button', { class: 'btn', style: { flex: '1', minWidth: '0', fontSize: '11px', padding: '5px 2px' }, text: '⏮', title: 'İlk', onclick: () => { G.mode = 'ai'; stopAuto(); stepTo(0); } }),
      h('button', { class: 'btn', style: { flex: '1', minWidth: '0', fontSize: '11px', padding: '5px 2px' }, text: '◀', title: 'Önceki', onclick: () => { G.mode = 'ai'; stopAuto(); stepTo(currentReviewIndex - 1); } }),
      h('button', { class: 'btn', style: { flex: '1', minWidth: '0', fontSize: '11px', padding: '5px 2px' }, text: '▶', title: 'Sonraki', onclick: () => { G.mode = 'ai'; stopAuto(); stepTo(currentReviewIndex + 1); } }),
      h('button', { class: 'btn', style: { flex: '1', minWidth: '0', fontSize: '11px', padding: '5px 2px' }, text: '⏭', title: 'Son', onclick: () => { G.mode = 'ai'; stopAuto(); stepTo(reviewItems.length - 1); } }),
      h('button', { class: 'btn ghost', id: 'autoToggleBtnSidebar', text: '▶ Akış', style: { flex: '1.4', minWidth: '0', fontSize: '11px', padding: '5px 2px' }, onclick: () => {
        if (isReviewAuto) {
          stopAuto();
        } else {
          isReviewAuto = true;
          const tb = document.getElementById('autoToggleBtnSidebar');
          if (tb) tb.textContent = '⏸ Duraklat';
          continueBtn.hidden = true;
          tryPuzzleBtn.hidden = true;
          G.mode = 'ai';
          stepTo(currentReviewIndex + 1);
        }
      } })
    );

    const coachCard = h('div', { class: 'coach-wrap', style: { padding: '12px', gap: '8px', width: '100%', boxSizing: 'border-box' } },
      h('div', { class: 'coach-header', style: { gap: '8px' } },
        h('img', { class: 'coach-av', src: '/sprite/coachdavid.png', style: { width: '42px', height: '42px' }, alt: 'Coach David' }),
        h('div', {},
          h('div', { class: 'coach-title', text: 'Koç David', style: { fontSize: '14px' } }),
          h('div', { class: 'coach-sub', text: 'Stockfish 19 Analizi (Sesli)', style: { fontSize: '11px' } })
        )
      ),
      h('div', { class: 'coach-bubble', style: { padding: '10px 12px', width: '100%', boxSizing: 'border-box' } },
        h('div', { style: { display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' } }, badgeSpan, moveLabelSpan, h('span', { text: '—' }), catLabelSpan),
        bestMoveInfo,
        coachText,
        continueBtn,
        tryPuzzleBtn,
        showSolutionBtn,
        navRow
      )
    );
    content.append(coachCard);

    // Hamle Listesi
    const moveList = h('div', { class: 'analysis-moves', style: { maxHeight: '180px', width: '100%', boxSizing: 'border-box' } });
    reviewItems.forEach((it, i) => {
      const info = CAT_INFO[it.category];
      const moveLabel = (Math.floor(i / 2) + 1) + (i % 2 === 0 ? '.' : '...');
      const row = h('div', { class: 'analysis-move-row' + (i === 0 ? ' on' : ''), 'data-aidx': i },
        h('span', { class: 'analysis-move-num', text: moveLabel }),
        h('span', { class: 'analysis-move-san', text: it.san }),
        h('span', { class: 'analysis-move-badge ' + info.cls, text: info.icon })
      );
      row.onclick = () => { G.mode = 'ai'; stopAuto(); stepTo(i); };
      moveList.append(row);
    });
    content.append(moveList);

    function startBlunderPuzzle(item) {
      if (!item) return;
      const preState = G.states[item.idx];
      G.mode = 'review_puzzle';
      G.reviewTargetUci = item.bestUci;
      G.reviewTargetSan = item.bestSan;
      G.reviewReturnIdx = item.idx;
      G.st = preState;
      G.legalList = Chess.legal(preState);
      // G.me DEĞİŞTİRİLMEZ! Oyuncunun kartı ve avatarı ("Sen") her zaman aşağıda kalır!
      G.vi = item.idx;
      layout();
      buildPieces(preState, false);
      updateAll();
      G.ov = []; drawOv();

      const isUser = (item.isWhite ? 0 : 1) === G.me;
      const promptText = isUser
        ? 'Kendi hatanı düzelt bakalım! Bu konumda oynaman gereken en iyi hamleyi bul.'
        : 'Rakibin büyük bir hata yaptı! Şimdi rakibinin yerine geç ve onun kaçırdığı en iyi hamleyi tahtada bul.';

      toast(promptText);
      speakWithPiper(promptText);
      coachText.textContent = `🎯 Bulmaca Antrenmanı:\n${promptText}`;
      tryPuzzleBtn.hidden = true;
      continueBtn.hidden = true;
      showSolutionBtn.hidden = false;
    }

    window._finishReviewPuzzle = (success, correctMove) => {
      showSolutionBtn.hidden = true;
      tryPuzzleBtn.hidden = true;
      continueBtn.hidden = false;
      const targetSan = reviewItems[currentReviewIndex].bestSan;
      coachText.textContent = `Harika! En iyi hamleyi (${targetSan}) buldun!\nMaç incelemesine devam etmek için "Devam Et ▶" butonuna tıkla.`;
      // TAŞ BIRAKILAN KAREDE DURUR! goto çağrılmaz!
    };

    window._onPuzzleWrong = () => {
      coachText.textContent = 'Bu hamle en iyisi değildi. Tekrar dene!';
    };

    // Tahtaya Ok ve Kare Rozetini Çizme
    function showAnalysisArrows(item) {
      G.ov = [];
      if (!item) { drawOv(); return; }

      const isWrong = ['blunder', 'miss', 'mistake', 'inaccuracy'].includes(item.category);

      if (item.playedUci && item.playedUci.length >= 4) {
        const pf = uciSquare(item.playedUci.slice(0, 2));
        const pt = uciSquare(item.playedUci.slice(2, 4));
        if (pf >= 0 && pt >= 0) {
          if (isWrong) {
            G.ov.push({ t: 'a', a: pf, b: pt, color: 'rgb(255, 60, 60)', k: 'played-' + item.playedUci });
          } else {
            G.ov.push({ t: 'a', a: pf, b: pt, color: item.color || 'rgb(50, 220, 100)', k: 'played-' + item.playedUci });
          }
          G.ov.push({ t: 'badge', a: pt, icon: item.icon, color: item.color, k: 'badge-' + pt });
        }
      }

      if (isWrong && item.bestUci && item.bestUci.length >= 4) {
        const bf = uciSquare(item.bestUci.slice(0, 2));
        const bt = uciSquare(item.bestUci.slice(2, 4));
        if (bf >= 0 && bt >= 0) {
          G.ov.push({ t: 'a', a: bf, b: bt, color: 'rgb(40, 220, 100)', k: 'best-' + item.bestUci });
        }
      }

      drawOv();
    }

    function stopAuto() {
      isReviewAuto = false;
      if (reviewAutoTimer) { clearTimeout(reviewAutoTimer); reviewAutoTimer = null; }
      const toggle = document.getElementById('autoToggleBtnSidebar');
      if (toggle) toggle.textContent = '▶ Akış';
    }

    function stepTo(targetIdx) {
      if (reviewAutoTimer) { clearTimeout(reviewAutoTimer); reviewAutoTimer = null; }
      if (targetIdx < 0) targetIdx = 0;

      if (targetIdx >= reviewItems.length) {
        stopAuto();
        continueBtn.hidden = true;
        tryPuzzleBtn.hidden = true;
        showSolutionBtn.hidden = true;
        const endMsg = `Tüm maç incelendi! Beyaz %${wStats.accuracy.toFixed(1)}, Siyah %${bStats.accuracy.toFixed(1)} doğrulukla oynadı.`;
        coachText.textContent = endMsg;
        badgeSpan.className = 'cat-icon ci-best'; badgeSpan.textContent = '★';
        moveLabelSpan.textContent = 'Bitti';
        catLabelSpan.textContent = 'Analiz Tamamlandı';
        catLabelSpan.style.color = '#96bc4b';
        bestMoveInfo.textContent = '';
        G.ov = []; drawOv();
        speakWithPiper(endMsg);
        return;
      }

      currentReviewIndex = targetIdx;
      const it = reviewItems[currentReviewIndex];

      moveList.querySelectorAll('.analysis-move-row').forEach(el => {
        el.classList.toggle('on', Number(el.dataset.aidx) === currentReviewIndex);
      });

      badgeSpan.className = 'cat-icon ' + it.cls;
      badgeSpan.textContent = it.icon;
      moveLabelSpan.textContent = it.san;
      catLabelSpan.textContent = it.label;
      catLabelSpan.style.color = it.color;
      coachText.textContent = it.comment;

      const isBad = ['blunder', 'miss', 'mistake'].includes(it.category);
      if (isBad && it.bestSan) {
        bestMoveInfo.textContent = `En iyi alternatif: ${it.bestSan}`;
      } else {
        bestMoveInfo.textContent = '';
      }

      continueBtn.hidden = true;
      tryPuzzleBtn.hidden = true;
      showSolutionBtn.hidden = true;

      G.vi = -1;
      goto(currentReviewIndex + 1);
      if (G.states && G.states[currentReviewIndex + 1]) {
        buildPieces(G.states[currentReviewIndex + 1], false);
      }
      updateAll();
      showAnalysisArrows(it);

      // KOÇ SESLENDİRMESİ VE SENKRONİZASYON:
      // Ses durmadan hamleyi ASLA geçmez!
      speakWithPiper(it.comment, () => {
        // Seslendirme bittiğinde burası çalışır:
        if (isBad) {
          // Vahim hata veya hata: ses bittiğinde devam et ve bulmaca butonlarını göster!
          stopAuto();
          continueBtn.hidden = false;
          tryPuzzleBtn.hidden = false;
        } else if (isReviewAuto) {
          // Normal hamle ve akış açıksa: ses bittikten 650ms sonra bir sonraki hamleye geç!
          reviewAutoTimer = setTimeout(() => {
            stepTo(currentReviewIndex + 1);
          }, 650);
        }
      }, currentReviewIndex);

      const activeRow = moveList.querySelector('.analysis-move-row.on');
      if (activeRow) activeRow.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    window._sidebarReviewStepTo = stepTo;
    stepTo(0);
  }

  function stepTo(idx) {
    if (activeTab !== 'analysis') {
      switchTab('analysis');
      setTimeout(() => { if (window._sidebarReviewStepTo) window._sidebarReviewStepTo(idx); }, 50);
    } else if (window._sidebarReviewStepTo) {
      window._sidebarReviewStepTo(idx);
    }
  }

  renderReport();
}

const analysisModal = startSidebarReview;

function botsModal() {
  modal((box, close) => {
    let tab = 'engine';
    const draw = () => {
      box.textContent = '';
      box.append(mhead('Botlar & Yapay Zeka', close));
      const tabs = h('div', { class: 'bot-tabs' },
        h('button', { class: 'btn' + (tab === 'engine' ? ' pri' : ''), text: 'Motor Seviyeleri (1-26)', onclick: () => { tab = 'engine'; draw(); } }),
        h('button', { class: 'btn' + (tab === 'people' ? ' pri' : ''), text: 'Karakter Botları', onclick: () => { tab = 'people'; draw(); } })
      );
      box.append(tabs);

      const grid = h('div', { class: 'bot-grid' });
      const list = tab === 'engine' ? BOTS.engine : BOTS.people;

      list.forEach(bot => {
        const card = h('div', { class: 'bot-card' + (activeBot && activeBot.id === bot.id ? ' on' : '') },
          h('img', { class: 'bot-avatar', src: bot.img, alt: bot.name }),
          h('div', { class: 'bot-name', text: bot.name }),
          h('div', { class: 'bot-elo', text: bot.elo + ' Elo' }),
          h('div', { class: 'bot-desc', text: bot.desc }),
          h('button', { class: 'btn pri', text: 'Oyna', onclick: () => {
            activeBot = bot;
            close();
            resetGame({ mode: 'ai', me: 0, flipped: false, level: bot.skill || 3, tc: null });
            BotChat.onStart(bot);
            updatePlayerCards();
          } })
        );
        grid.append(card);
      });
      box.append(grid);
    };
    draw();
  });
}

/* Bulmacalar Modalı */
function puzzlesModal() {
  modal((box, close) => {
    box.append(mhead('Taktik Bulmacalar & 50 Kural', close));
    const list = h('div', { class: 'grid', style: { maxHeight: '65vh', overflowY: 'auto', paddingRight: '4px', gridTemplateColumns: 'repeat(auto-fill,minmax(140px,1fr))' } });
    PUZZLES.forEach((p, idx) => {
      const btn = h('button', { class: 'tile', style: { textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '4px', padding: '10px' } },
        h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' } },
          h('span', { class: 'puzzle-badge', text: '#' + (idx + 1) }),
          h('span', { style: { fontSize: '10px', color: 'var(--acc)', fontWeight: '700' }, text: p.cat || '' })
        ),
        h('strong', { style: { fontSize: '13px' }, text: p.title }),
        h('span', { class: 'mut', style: { fontSize: '11px', lineHeight: '1.3' }, text: p.rule || p.desc })
      );
      btn.onclick = () => {
        close();
        loadPuzzle(p);
      };
      list.append(btn);
    });
    box.append(list);
  });
}

function loadPuzzle(p) {
  currentPuzzle = p;
  toast('Bulmaca: ' + p.title);
  speakWithPiper(p.title + '. ' + (p.rule || ''));
  const st = Chess.fromFEN(p.fen);
  G.st = st;
  G.states = [st];
  G.keys = [Chess.posKey(st)];
  G.mode = 'puzzle';
  G.me = (st.t === 0) ? 0 : 1;
  G.flipped = (G.me === 1);
  G.moves = [];
  G.sans = [];
  G.snaps = [];
  G.over = null;
  G.legalList = Chess.legal(st);
  G.sel = null; G.tg = new Map(); G.hint = null;
  layout();
  buildPieces(st, false);
  updateAll();
}

function updatePlayerCards() {
  updateBars();
}

const G = { mode: 'ai', me: 0, spectator: false, level: 3, flipped: false, st: null, states: [], moves: [], sans: [], keys: [], snaps: [],
  vi: 0, over: null, sel: null, tg: new Map(), legalList: [], thinking: false, clk: null, net: null, ov: [], hint: null, drag: null,
  arr: null, busy: false, aiTok: 0, opts: null, hintBusy: false };
const cur = () => G.states[G.vi];
const live = () => G.vi === G.moves.length;
const cap1 = s => s.charAt(0).toUpperCase() + s.slice(1);

/* ---------- Tahta DOM ---------- */
const boardEl = $('#board'), sqsEl = $('#sqs'), pcsEl = $('#pieces'), ovEl = $('#ov');
const sqEls = [];
for (let i = 0; i < 64; i++) { const e = h('div', { class: 'sq ' + ((((i >> 3) + (i & 7)) & 1) ? 'd' : 'l') }, h('i', { class: 'hl' })); sqEls.push(e); sqsEl.append(e); }
const pieceEls = new Map();
const scr = i => { const c = i & 7, r = i >> 3; return G.flipped ? [7 - c, 7 - r] : [c, r]; };
function layout() {
  for (let i = 0; i < 64; i++) {
    const e = sqEls[i], [c, r] = scr(i);
    e.style.gridColumn = c + 1; e.style.gridRow = r + 1;
    e.dataset.rk = c === 0 ? String(8 - (i >> 3)) : ''; e.dataset.fl = r === 7 ? FILES[i & 7] : '';
  }
}
const place = (el, i) => { const [c, r] = scr(i); el.style.transform = 'translate(' + c * 100 + '%,' + r * 100 + '%)'; };
const placeAll = () => pieceEls.forEach((el, i) => place(el, i));
function mkPiece(p, i) {
  const e = h('div', { class: 'pc ' + ((p >> 3) ? 'b' : 'w') }, h('span', { text: GL[p & 7] + VS, 'data-g': GL[p & 7] + VS }));
  place(e, i); pcsEl.append(e); pieceEls.set(i, e); return e;
}
function buildPieces(st, anim) {
  pcsEl.textContent = ''; pieceEls.clear();
  for (let i = 0; i < 64; i++) {
    if (!st.b[i]) continue;
    const e = mkPiece(st.b[i], i);
    if (anim && S.anim) { e.classList.add('in'); e.style.setProperty('--d', ((i & 7) + (i >> 3)) * 28 + 'ms'); }
  }
}
function squareXY(sq) {
  const rc = boardEl.getBoundingClientRect(), s = rc.width / 8, [c, r] = scr(sq);
  return [rc.left + (c + .5) * s, rc.top + (r + .5) * s];
}
function animateMove(before, m) {
  const f = m & 63, to = (m >> 6) & 63, pr = m >> 12, p = before.b[f], k = p & 7;
  let capSq = to;
  if (k === 1 && (f & 7) !== (to & 7) && !before.b[to]) capSq = to + (before.t === 0 ? 8 : -8);
  const el = pieceEls.get(f);
  if (!el) { buildPieces(Chess.make(before, m), false); return; }
  const capEl = before.b[capSq] ? pieceEls.get(capSq) : null;
  if (capEl && capEl !== el) {
    pieceEls.delete(capSq); capEl.classList.add('cap');
    const xy = squareXY(capSq); FX.burst(xy[0], xy[1], (before.b[capSq] >> 3) ? '#8a93b8' : '#ffffff', 16);
    setTimeout(() => capEl.remove(), S.anim ? 380 : 0);
  }
  pieceEls.delete(f); pieceEls.set(to, el); el.classList.remove('sel', 'drag');
  el.classList.add('mv'); place(el, to); setTimeout(() => el.classList.remove('mv'), ANIM[S.anim] * 1000 + 60);
  if (pr) {
    const apply = () => { el.firstChild.textContent = GL[pr] + VS; el.firstChild.setAttribute('data-g', GL[pr] + VS); el.classList.add('promo'); setTimeout(() => el.classList.remove('promo'), 520); };
    S.anim ? setTimeout(apply, ANIM[S.anim] * 1000 * .7) : apply();
  }
  if (k === 6 && Math.abs(to - f) === 2) {
    const rf = to > f ? f + 3 : f - 4, rt = to > f ? f + 1 : f - 1, rel = pieceEls.get(rf);
    if (rel) { pieceEls.delete(rf); pieceEls.set(rt, rel); place(rel, rt); }
  }
}

/* ---------- Boyama: vurgular, ok ve işaretler ---------- */
function interactive() { return canMove(); }
function canMove() {
  if (G.mode === 'review_puzzle' || G.mode === 'puzzle') return true;
  if (G.over || G.spectator || !live() || G.thinking || G.busy) return false;
  if (G.mode === 'local') return true;
  if (G.st.t !== G.me) return false;
  if (G.mode === 'online' && !(G.net && G.net.both)) return false;
  return true;
}
function paint() {
  const st = cur(), last = G.vi > 0 ? G.moves[G.vi - 1] : null;
  const ck = Chess.inCheck(st.b, st.t) ? st.b.indexOf((st.t << 3) | 6) : -1, can = interactive() && S.legal;
  for (let i = 0; i < 64; i++) {
    const c = sqEls[i].classList;
    c.toggle('last', !!(S.hl && last != null && (i === (last & 63) || i === ((last >> 6) & 63))));
    c.toggle('sel', G.sel === i && interactive());
    c.toggle('tgt', !!(can && G.tg.has(i) && !G.tg.get(i)));
    c.toggle('cap', !!(can && G.tg.get(i)));
    c.toggle('chk', i === ck); c.remove('hov');
  }
  pieceEls.forEach((el, i) => el.classList.toggle('sel', G.sel === i && interactive()));
}
const ctr = i => { const [c, r] = scr(i); return [c + .5, r + .5]; };
function arrowEl(a, b, color) {
  const [ax, ay] = ctr(a), [bx, by] = ctr(b), dx = bx - ax, dy = by - ay, d = Math.hypot(dx, dy) || 1, ux = dx / d, uy = dy / d;
  const ex = bx - ux * .42, ey = by - uy * .42, g = sv('g', { opacity: '.82' });
  g.append(sv('line', { x1: ax + ux * .18, y1: ay + uy * .18, x2: ex, y2: ey, stroke: color, 'stroke-width': .17, 'stroke-linecap': 'round' }),
    sv('polygon', { points: bx - ux * .06 + ',' + (by - uy * .06) + ' ' + (ex - uy * .3) + ',' + (ey + ux * .3) + ' ' + (ex + uy * .3) + ',' + (ey - ux * .3), fill: color }));
  return g;
}
function drawOv() {
  ovEl.textContent = '';
  for (const it of G.ov) {
    if (it.t === 'm') {
      const [x, y] = ctr(it.a);
      ovEl.append(sv('circle', { cx: x, cy: y, r: .44, fill: 'none', stroke: it.color || 'rgba(255,170,0,.85)', 'stroke-width': .08 }));
    } else if (it.t === 'badge') {
      const [c, r] = scr(it.a);
      const g = sv('g', { class: 'board-badge' });
      const bx = c + 0.80, by = r + 0.20;
      g.append(sv('circle', { cx: bx, cy: by, r: 0.17, fill: it.color || '#ca3431', stroke: '#ffffff', 'stroke-width': 0.025 }));
      const txt = sv('text', {
        x: bx, y: by + 0.05, fill: '#ffffff',
        'font-size': '0.14', 'font-weight': '900', 'text-anchor': 'middle',
        'font-family': 'system-ui, -apple-system, sans-serif'
      });
      txt.textContent = it.icon || '?';
      g.append(txt);
      ovEl.append(g);
    } else {
      ovEl.append(arrowEl(it.a, it.b, it.color || 'rgb(255,170,0)'));
    }
  }
  if (G.hint != null && live()) ovEl.append(arrowEl(G.hint & 63, (G.hint >> 6) & 63, 'rgb(40,210,190)'));
}
function toggleOv(it) {
  it.k = it.t + it.a + '-' + (it.b == null ? '' : it.b);
  const i = G.ov.findIndex(x => x.k === it.k);
  if (i >= 0) G.ov.splice(i, 1); else G.ov.push(it);
  drawOv();
}

/* ---------- Oyuncu çubukları, hamle listesi, durum ---------- */
function mkBar(el) {
  const gl = h('span'), dot = h('span', { class: 'dot' }), av = h('div', { class: 'av' }, gl, dot), nb = h('b'), cp = h('div', { class: 'cp' }),
    clk = h('div', { class: 'clk', hidden: true });
  el.append(av, h('div', { class: 'nm' }, nb, cp), clk); return { el, av, gl, dot, nb, cp, clk };
}
const bars = { top: mkBar($('#plTop')), bot: mkBar($('#plBot')) };
const GL_BLACK = ['', '\u265F', '\u265E', '\u265D', '\u265C', '\u265B', '\u265A'];
const GL_WHITE = ['', '\u2659', '\u2658', '\u2657', '\u2656', '\u2655', '\u2654'];

function materialInfo(st) {
  const cnt = [new Array(7).fill(0), new Array(7).fill(0)];
  let mat0 = 0, mat1 = 0;
  for (let i = 0; i < 64; i++) {
    const p = st.b[i];
    if (p) {
      const col = p >> 3, k = p & 7;
      cnt[col][k]++;
    }
  }
  for (let k = 1; k <= 5; k++) {
    mat0 += cnt[0][k] * VAL[k];
    mat1 += cnt[1][k] * VAL[k];
  }
  const diff = mat0 - mat1; // Beyaz lehine fark

  // Chess.com Net Üstünlükteki Taşlar:
  // res[0]: Beyaz'ın önde olduğu taşlar (aldığı Siyah taşlar)
  // res[1]: Siyah'ın önde olduğu taşlar (aldığı Beyaz taşlar)
  const res = [[], []];
  for (let k = 5; k >= 1; k--) {
    const net = cnt[0][k] - cnt[1][k];
    if (net > 0) {
      for (let n = 0; n < net; n++) res[0].push(k);
    } else if (net < 0) {
      for (let n = 0; n < -net; n++) res[1].push(k);
    }
  }
  return { by: res, diff };
}
function nameOf(c) {
  if (G.mode === 'ai') {
    if (c === G.me) return t('you');
    if (activeBot) return activeBot.name;
    return 'Motor Seviye ' + (G.level || 3);
  }
  if (G.mode === 'online' && !G.spectator) return c === G.me ? t('you') : t('opponent');
  return c ? t('black') : t('white');
}
function updateBars() {
  if (!activeBot && typeof BOTS !== 'undefined' && BOTS.engine) {
    activeBot = BOTS.engine[2] || BOTS.engine[0];
  }
  const bot = G.flipped ? 1 : 0, mi = materialInfo(cur());
  for (const [b, c] of [[bars.bot, bot], [bars.top, bot ^ 1]]) {
    b.av.className = 'av ' + (c ? 'b' : 'w');
    b.av.textContent = '';
    const img = document.createElement('img');
    if (G.mode === 'ai' && c !== G.me && activeBot && activeBot.img) {
      img.src = activeBot.img;
      img.alt = activeBot.name;
    } else if (c === G.me) {
      img.src = '/sprite/user-image.007dad08.svg';
      img.alt = 'Sen';
    } else {
      img.src = c ? '/sprite/black_400.png' : '/sprite/white_400.png';
      img.alt = c ? 'Siyah' : 'Beyaz';
    }
    img.style.cssText = 'width:100%;height:100%;border-radius:10px;object-fit:cover;display:block;';
    b.av.appendChild(img);
    b.av.appendChild(b.dot);

    b.nb.textContent = '';
    if (G.mode === 'ai' && c !== G.me && activeBot) {
      const nm = document.createTextNode(activeBot.name + ' ');
      const elo = document.createElement('span');
      elo.className = 'pl-elo';
      elo.textContent = activeBot.elo + ' Elo';
      b.nb.append(nm, elo);
    } else {
      b.nb.textContent = nameOf(c);
    }

    b.dot.hidden = G.mode !== 'online' || G.spectator || c === G.me;
    b.dot.classList.toggle('on', !!(G.net && G.net.present && G.net.present[c ? 'b' : 'w']));

    const d = c === 0 ? mi.diff : -mi.diff;
    b.cp.textContent = '';
    if (d > 0) {
      const glyphs = c === 0 ? GL_BLACK : GL_WHITE;
      const pcsSpan = document.createElement('span');
      pcsSpan.className = 'mat-pieces';
      pcsSpan.textContent = mi.by[c].map(k => glyphs[k]).join('');
      b.cp.appendChild(pcsSpan);

      const em = document.createElement('em');
      em.className = 'mat-lead';
      em.textContent = '+' + d;
      b.cp.appendChild(em);
    }
    b.clk.dataset.c = c;
  }
  updateClockUI();
}
function renderMoves() {
  const box = $('#moves'); box.textContent = '';
  for (let i = 0; i < G.sans.length; i += 2) {
    const row = h('div', { class: 'mr' }, h('i', { text: (i / 2 + 1) + '.' }));
    for (const j of [i, i + 1]) row.append(j < G.sans.length ? h('b', { class: j + 1 === G.vi ? 'on' : '', text: G.sans[j], onclick: () => goto(j + 1) }) : h('b'));
    box.append(row);
  }
  const on = $('.on', box);
  if (!on || live()) box.scrollTop = box.scrollHeight;
  else if (on.offsetTop < box.scrollTop) box.scrollTop = on.offsetTop - 6;
  else if (on.offsetTop + on.offsetHeight > box.scrollTop + box.clientHeight) box.scrollTop = on.offsetTop + on.offsetHeight - box.clientHeight + 6;
}
function resultTitle() {
  const r = G.over.res;
  if (r === '1/2-1/2') return t('drawn');
  if (G.mode === 'local' || G.spectator) return r === '1-0' ? t('whiteWins') : t('blackWins');
  return (r === '1-0') === (G.me === 0) ? t('youWon') : t('youLost');
}
function updateStatus() {
  const el = $('#status'), n = G.net; let s, bad = false;
  if (G.over) s = resultTitle() + ' \u2014 ' + t('w_' + G.over.why);
  else if (G.mode === 'online' && n && !n.both) s = t('waitingOpp');
  else if (G.thinking) s = t('thinking');
  else {
    s = t('toMove', { c: G.st.t ? t('black') : t('white') });
    if (Chess.inCheck(G.st.b, G.st.t)) { s += ' \u00B7 ' + t('check'); bad = true; }
    if (G.mode === 'online' && n && n.both && !G.spectator && !n.present[G.me ? 'w' : 'b']) s += ' \u00B7 ' + t('oppLeft');
  }
  el.textContent = s; el.classList.toggle('bad', bad);
  const bn = $('#banner'); bn.textContent = ''; bn.hidden = true;
  if (n && G.mode === 'online' && !G.over && !G.spectator && n.draw) {
    bn.hidden = false;
    if (n.draw !== (G.me ? 'b' : 'w')) bn.append(h('span', { text: t('drawOffered') }),
      h('button', { class: 'btn pri', text: t('accept'), onclick: () => Net.act('draw_accept') }),
      h('button', { class: 'btn', text: t('decline'), onclick: () => Net.act('draw_decline') }));
    else bn.append(h('span', { text: t('drawSent') }));
  }
}
function updateButtons() {
  const on = G.mode === 'online', n = G.net, ended = !!G.over;
  const set = (id, hid, dis) => { const b = $(id); b.hidden = !!hid; b.disabled = !!dis; };
  set('#aUndo', on || G.spectator, !G.moves.length);
  set('#aHint', on || G.spectator, !canMove());
  set('#aDraw', G.mode === 'ai' || G.spectator, ended || (on && (!n || !n.both || n.draw)));
  set('#aResign', G.spectator, ended || (on && (!n || !n.both)));
  set('#aInvite', !(on && !G.spectator && n && !n.both), false);
  const rev = $('#aReview');
  if (rev) rev.style.display = (ended && G.moves.length > 0) ? 'flex' : 'none';
  const exitBtn = $('#bExitGame');
  if (exitBtn) exitBtn.style.display = (on && n && n.code) ? 'inline-flex' : 'none';
  $('#nFirst').disabled = $('#nPrev').disabled = G.vi === 0;
  $('#nNext').disabled = $('#nLast').disabled = live();
}
function updateAll() {
  try { updateBars(); } catch (e) { console.error('updateBars:', e); }
  try { renderMoves(); } catch (e) { console.error('renderMoves:', e); }
  try { updateStatus(); } catch (e) { console.error('updateStatus:', e); }
  try { updateButtons(); } catch (e) { console.error('updateButtons:', e); }
  try { paint(); } catch (e) { console.error('paint:', e); }
  try { drawOv(); } catch (e) { console.error('drawOv:', e); }
}

/* ---------- Saat ---------- */
function setClock(tc) {
  G.clk = tc && tc.base ? { w: tc.base * 1000, b: tc.base * 1000, inc: tc.inc * 1000, last: performance.now(), lt: -1 } : null;
  G.snaps = [G.clk ? { w: G.clk.w, b: G.clk.b } : null];
}
const fmt = ms => {
  if (ms < 10000) return (Math.max(0, ms) / 1000).toFixed(1);
  const s = Math.ceil(ms / 1000), m = Math.floor(s / 60);
  return m >= 60 ? Math.floor(m / 60) + ':' + String(m % 60).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0') : m + ':' + String(s % 60).padStart(2, '0');
};
function updateClockUI() {
  const c = G.clk;
  for (const b of [bars.top, bars.bot]) {
    b.clk.hidden = !c; if (!c) continue;
    const col = +b.clk.dataset.c, ms = c[col ? 'b' : 'w'], running = !G.over && G.moves.length > 0 && G.st.t === col;
    b.clk.textContent = fmt(ms); b.clk.classList.toggle('run', running);
  }
}
setInterval(() => {
  const c = G.clk; if (!c) return;
  const now = performance.now(), dt = now - c.last; c.last = now;
  if (G.over || !G.moves.length) return updateClockUI();
  const side = G.st.t ? 'b' : 'w'; c[side] -= dt;
  if (c[side] <= 0) {
    c[side] = 0; updateClockUI();
    const win = side === 'w' ? '0-1' : '1-0', loserBoard = G.st.b;
    // rakipte mat verecek materyal yoksa berabere
    let n = 0, major = false;
    for (let i = 0; i < 64; i++) { const p = loserBoard[i]; if (p && (p >> 3) === (side === 'w' ? 1 : 0) && (p & 7) !== 6) { if ((p & 7) === 1 || (p & 7) >= 4) major = true; else n++; } }
    const mat = major || n >= 2;
    const res = mat ? win : '1/2-1/2';
    if (G.mode === 'online' && !G.over) Net.act('timeout');
    endGame(res, 'timeout'); return;
  }
  updateClockUI();
}, 100);

/* ---------- Oyun akışı ---------- */
function resetGame(o) {
  if (reviewAutoTimer) { clearTimeout(reviewAutoTimer); reviewAutoTimer = null; }
  isReviewAuto = false;
  if (coachAudio) { coachAudio.pause(); coachAudio = null; }
  const sb = document.getElementById('reviewSidebar');
  const gp = document.getElementById('gamePanel');
  if (sb) { sb.style.display = 'none'; sb.textContent = ''; }
  if (gp) gp.style.display = 'flex';

  G.aiTok++; G.thinking = false; hideResult(); G.opts = o;
  Object.assign(G, { mode: o.mode, me: o.me || 0, spectator: !!o.spectator, level: o.level || S.level, flipped: !!o.flipped });
  G.st = Chess.startState(); G.states = [G.st]; G.moves = []; G.sans = []; G.keys = [Chess.posKey(G.st)];
  G.vi = 0; G.over = null; G.sel = null; G.tg = new Map(); G.ov = []; G.hint = null; G.drag = null; G.busy = false;
  setClock(o.tc); G.legalList = Chess.legal(G.st);
  layout(); buildPieces(G.st, true); updateAll();
  if (!o.quiet) Snd.play('start');
  maybeAI();
}
function playMove(m, o) {
  o = o || {};
  const before = G.st, leg = G.legalList, wasLive = live(), mover = before.t;
  const s = Chess.san(before, m, leg), f = m & 63, to = (m >> 6) & 63, pr = m >> 12, k = before.b[f] & 7;
  const isCap = before.b[to] !== 0 || (k === 1 && (f & 7) !== (to & 7)), isCastle = k === 6 && Math.abs(to - f) === 2;
  const after = Chess.make(before, m);
  G.moves.push(m); G.sans.push(s); G.states.push(after); G.keys.push(Chess.posKey(after)); G.st = after;
  if (G.clk) { G.clk[mover ? 'b' : 'w'] += G.clk.inc; G.clk.last = performance.now(); }
  G.snaps.push(G.clk ? { w: G.clk.w, b: G.clk.b } : null);
  G.legalList = Chess.legal(after); G.sel = null; G.tg = new Map(); G.hint = null;
  if (wasLive) { G.vi = G.moves.length; if (!o.silent) animateMove(before, m); }
  if (!o.silent) {
    const chk = Chess.inCheck(after.b, after.t);
    Snd.play(chk ? 'check' : pr ? 'promote' : isCastle ? 'castle' : isCap ? 'capture' : 'move');
    vib(isCap ? [18, 30, 18] : 12);
    requestEval();
    if (chk) BotChat.onCheck(after.t === G.me);
    else if (isCap) BotChat.onCapture(after.t !== G.me);
  }
  if (G.mode === 'review_puzzle') {
    const playedUci = Chess.toUci(m);
    if (playedUci === G.reviewTargetUci) {
      // DOĞRU HAMLE YAPILDIĞINDA:
      // 1. Taş bırakılan karede duracak (playMove ve animateMove taşı hedefe koydu).
      // 2. Kare ve ok Yeşil parlayacak:
      G.ov = [
        { t: 'a', a: f, b: to, color: 'rgb(75, 215, 85)', k: 'puzzle-correct' },
        { t: 'badge', a: to, icon: '★', color: '#96bc4b', k: 'badge-correct' }
      ];
      drawOv();
      // 3. Başarı sesi (win) çalacak:
      Snd.play('win');
      // 4. Koç tebrik edecek ve "Devam Et ▶" butonu açılacak:
      toast('Tebrikler! Doğru en iyi hamleyi buldun: ' + G.reviewTargetSan);
      speakWithPiper('Harika! Doğru en iyi hamleyi buldun.');
      if (window._finishReviewPuzzle) window._finishReviewPuzzle(true, m);
    } else {
      // YANLIŞ HAMLE YAPILDIĞINDA:
      // 1. Taş durduğu karede kalıp kırmızı yansın ve hata rozeti çıksın:
      G.ov = [
        { t: 'a', a: f, b: to, color: 'rgb(235, 50, 50)', k: 'puzzle-wrong' },
        { t: 'badge', a: to, icon: '??', color: '#ca3431', k: 'badge-wrong' }
      ];
      drawOv();
      // 2. Hata sesi çalacak:
      Snd.play('lose');
      // 3. Koç uyaracak:
      toast('Bu hamle en iyisi değildi. Tekrar dene!');
      speakWithPiper('Bu hamle en iyisi değildi, tekrar dene.');
      if (window._onPuzzleWrong) window._onPuzzleWrong();
      // 4. 800ms sonra taş eski karesine geri dönecek (tekrar denemek için):
      const preIdx = G.reviewReturnIdx;
      const preState = G.states[preIdx];
      G.busy = true;
      setTimeout(() => {
        G.busy = false;
        if (G.mode === 'review_puzzle') {
          G.st = preState;
          G.legalList = Chess.legal(preState);
          G.sel = null; G.tg = new Map(); G.hint = null;
          buildPieces(preState, false);
          updateAll();
          G.ov = []; drawOv();
        }
      }, 800);
    }
    return;
  }
  if (G.mode === 'puzzle' && currentPuzzle) {
    const playedUci = Chess.toUci(m);
    const expected = currentPuzzle.moves[0];
    if (playedUci === expected) {
      Snd.play('win');
      toast('Doğru hamle! 🎯 ' + (currentPuzzle.rule || ''));
      speakWithPiper('Harika! Doğru hamle. ' + (currentPuzzle.rule || ''));
      FX.confetti();
      toast('Tebrikler! Bulmaca çözüldü! 🏆');
    } else {
      Snd.play('lose');
      toast('Hatalı hamle! Kural: ' + (currentPuzzle.rule || 'Tekrar dene.'));
      speakWithPiper('Hatalı hamle! ' + (currentPuzzle.rule || 'Tekrar deneyin.'));
      const st0 = Chess.fromFEN(currentPuzzle.fen);
      setTimeout(() => {
        G.st = st0;
        G.moves = [];
        G.sans = [];
        G.states = [st0];
        G.legalList = Chess.legal(st0);
        G.sel = null; G.tg = new Map(); G.hint = null;
        buildPieces(st0, false);
        updateAll();
      }, 800);
    }
    return;
  }
  if (G.mode !== 'online') { const stt = Chess.status(after, G.keys); if (stt.over) endGame(stt.res, stt.why); }
  if (!o.silent) updateAll();
  if (!o.remote && G.mode === 'online') Net.sendMove(m);
  if (!o.silent) maybeAI();
}
function endGame(res, why) {
  if (G.over) return;
  G.over = { res, why }; G.aiTok++; G.thinking = false;
  const win = res === '1/2-1/2' ? 0 : (G.mode === 'local' || G.spectator) ? 2 : ((res === '1-0') === (G.me === 0) ? 1 : -1);
  BotChat.onOver(win === 1, win === 0);
  setTimeout(() => Snd.play(win === 1 || win === 2 ? 'win' : win === -1 ? 'lose' : 'draw'), why === 'checkmate' ? 450 : 0);
  if (why === 'checkmate') {
    const ks = G.st.b.indexOf(((res === '1-0' ? 1 : 0) << 3) | 6), el = pieceEls.get(ks);
    if (el) el.classList.add('fall');
  }
  if (win === 1 || win === 2) setTimeout(() => FX.confetti(), 500);
  setTimeout(showResult, why === 'checkmate' ? 1100 : 500);
  updateAll();
}
function hideResult() { const r = $('#result'); r.hidden = true; r.textContent = ''; }
function showResult() {
  if (!G.over) return;
  const r = $('#result'); r.textContent = ''; r.hidden = false;
  const rem = G.mode === 'online' ? () => { Net.act('rematch'); toast(t('rematch') + '\u2026'); } : () => resetGame(G.opts);
  r.append(h('div', { class: 'rcard' },
    h('img', { src: '/sprite/coachdavid.png', style: { width: '56px', height: '56px', borderRadius: '50%', border: '2px solid var(--acc)', margin: '0 auto 8px auto', display: 'block', boxShadow: '0 4px 14px rgba(0,0,0,.4)' } }),
    h('h2', { text: resultTitle() }),
    h('p', { text: cap1(t('w_' + G.over.why)) }),
    h('div', { class: 'row', style: { marginTop: '12px' } },
      h('button', { class: 'btn pri', style: { width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }, onclick: () => { hideResult(); analysisModal(); } },
        h('img', { src: '/sprite/magnifier-analysis.svg', style: { width: '20px', height: '20px', objectFit: 'contain' } }),
        h('span', { text: 'Maçı Analiz Et (Koç David)' })
      ),
      h('button', { class: 'btn', style: { flex: '1' }, text: t('rematch'), onclick: () => { rem(); if (G.mode !== 'online') hideResult(); } }),
      h('button', { class: 'btn', style: { flex: '1' }, text: t('newGame'), onclick: () => { hideResult(); newGameModal(); } }),
      h('button', { class: 'btn ghost', style: { width: '100%', marginTop: '4px' }, text: 'Tahtayı İncele (Kapat)', onclick: hideResult })
    )
  ));
}
function goto(i) {
  i = clamp(i, 0, G.moves.length); if (i === G.vi) return;
  const old = G.vi; G.vi = i; G.sel = null; G.tg = new Map(); G.hint = null;
  if (i === old + 1) animateMove(G.states[old], G.moves[old]); else buildPieces(G.states[i], false);
  Snd.play('select'); updateAll();
}
function undo() {
  if (G.mode === 'online' || G.spectator || !G.moves.length) return;
  let n = G.mode === 'ai' && G.st.t === G.me ? 2 : 1; n = Math.min(n, G.moves.length);
  G.aiTok++; G.thinking = false;
  for (let i = 0; i < n; i++) { G.moves.pop(); G.sans.pop(); G.states.pop(); G.keys.pop(); G.snaps.pop(); }
  G.st = G.states[G.states.length - 1]; G.vi = G.moves.length; G.over = null; hideResult();
  G.legalList = Chess.legal(G.st); G.sel = null; G.tg = new Map(); G.hint = null;
  const sn = G.snaps[G.snaps.length - 1]; if (G.clk && sn) { G.clk.w = sn.w; G.clk.b = sn.b; G.clk.last = performance.now(); }
  buildPieces(G.st, false); Snd.play('select'); updateAll(); maybeAI();
}
function flip() { G.flipped = !G.flipped; layout(); placeAll(); updateAll(); }

/* ---------- Yapay zeka (Web Worker) ---------- */
let worker = null, seq = 0; const pending = new Map();
function initWorker() {
  try {
    worker = new Worker('/engine.js');
    worker.onmessage = e => { const cb = pending.get(e.data.id); if (cb) { pending.delete(e.data.id); cb(e.data); } };
    worker.onerror = () => { worker = null; pending.forEach(cb => cb({ m: -1 })); pending.clear(); };
  } catch (e) { worker = null; }
}
async function askEngine(st, level, keys, time, options = {}) {
  const fen = Chess.toFEN(st);
  const controller = new AbortController();
  const isHint = !!options.hint;
  const isPure = isHint || !!options.pure || !!(activeBot && activeBot.pure);
  const reqTime = isHint ? 1200 : (time || (activeBot && activeBot.time ? activeBot.time : 350));
  const reqDepth = isHint ? null : (options.depth !== undefined ? options.depth : (activeBot && activeBot.depth ? activeBot.depth : null));
  const reqSkill = isHint ? 20 : (activeBot ? activeBot.skill : 10);
  const reqElo = isHint ? null : (activeBot ? activeBot.elo : null);

  const safetyTimeout = setTimeout(() => {
    try { controller.abort(); } catch (e) {}
  }, Math.max(4000, reqTime + 3500));

  try {
    const res = await fetch('/api/bot/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fen,
        level: reqSkill,
        elo: reqElo,
        time: reqTime,
        depth: reqDepth,
        pure: isPure,
        hint: isHint
      }),
      signal: controller.signal
    });
    clearTimeout(safetyTimeout);
    if (res.ok) {
      const data = await res.json();
      if (data && data.uci) {
        if (typeof data.score === 'number') updateEvalBar(data.score, data.is_mate);
        const m = Chess.fromUci(st, data.uci);
        if (m != null) return { m };
      }
    }
  } catch (e) {
    clearTimeout(safetyTimeout);
  }

  // Stockfish yanıt vermezse yedek dahili motoru devreye sok
  try {
    if (typeof Chess.bestMove === 'function') {
      const bm = Chess.bestMove(st, Math.min(3, level || 2), keys || [], 300);
      if (bm != null && bm >= 0) return { m: bm };
    }
  } catch (err) {}

  // Son çare kilitlenmeyi önleyici yasal hamle
  const leg = Chess.legal(st);
  return { m: leg.length ? leg[0] : -1 };
}
function maybeAI() {
  if (G.mode !== 'ai' || G.over || G.st.t === G.me || !G.legalList.length) return;
  const tok = ++G.aiTok;
  G.thinking = true;
  updateStatus(); updateButtons(); paint();

  const reqWait = activeBot && activeBot.time ? activeBot.time : 400;
  const safetyTimer = setTimeout(() => {
    if (tok === G.aiTok && G.thinking) {
      G.thinking = false;
      const leg = Chess.legal(G.st);
      if (leg.length && !G.over) playMove(leg[0]);
      else { updateStatus(); updateButtons(); paint(); }
    }
  }, Math.max(5000, reqWait + 4000));

  askEngine(G.st, G.level, G.keys).then(r => {
    clearTimeout(safetyTimer);
    if (tok !== G.aiTok || G.over) return;
    G.thinking = false;
    if (r && r.m >= 0) {
      playMove(r.m);
    } else {
      const leg = Chess.legal(G.st);
      if (leg.length) playMove(leg[0]);
      else { updateStatus(); updateButtons(); paint(); }
    }
  }).catch(() => {
    clearTimeout(safetyTimer);
    if (tok === G.aiTok && !G.over) {
      G.thinking = false;
      const leg = Chess.legal(G.st);
      if (leg.length) playMove(leg[0]);
      else { updateStatus(); updateButtons(); paint(); }
    }
  });
}
async function doHint() {
  if (!canMove() || G.hintBusy) return;
  G.hintBusy = true; const n = G.moves.length; toast(t('thinking'));
  // İpucu daima en yüksek seviyede ve derin hesaplamayla Stockfish 19'dan alınır
  const r = await askEngine(G.st, 20, G.keys, 1200, { hint: true }); G.hintBusy = false;
  if (r.m >= 0 && n === G.moves.length && !G.over) { G.hint = r.m; drawOv(); }
}

/* ---------- Etkileşim: tıkla-oyna, sürükle-bırak, sağ tık oklar ---------- */
function sqAt(e) {
  const rc = boardEl.getBoundingClientRect(), x = (e.clientX - rc.left) / rc.width * 8, y = (e.clientY - rc.top) / rc.height * 8;
  if (x < 0 || y < 0 || x >= 8 || y >= 8) return -1;
  let c = Math.floor(x), r = Math.floor(y); if (G.flipped) { c = 7 - c; r = 7 - r; }
  return r * 8 + c;
}
function select(i) {
  G.sel = i; G.tg = new Map();
  if (i != null) for (const m of G.legalList) if ((m & 63) === i) { const to = (m >> 6) & 63; G.tg.set(to, G.st.b[to] !== 0 || ((G.st.b[i] & 7) === 1 && (i & 7) !== (to & 7))); }
  if (i != null) Snd.play('select');
  paint();
}
function askPromo(color) {
  return new Promise(res => {
    const box = $('#promo'); box.textContent = ''; box.hidden = false;
    const done = v => { box.hidden = true; box.textContent = ''; res(v); };
    const row = h('div', { class: 'pbox' });
    for (const k of [5, 4, 3, 2]) row.append(h('button', { 'aria-label': t('promoteTo'), onclick: () => done(k),
      style: color ? { color: '#14141a', textShadow: '0 0 2px #fff' } : { color: '#fff', textShadow: '0 0 2px #000,0 0 1px #000' } }, GL[k] + VS));
    box.append(row); box.onclick = e => { if (e.target === box) done(null); };
  });
}
async function userMove(from, to) {
  const ms = G.legalList.filter(m => (m & 63) === from && ((m >> 6) & 63) === to);
  if (!ms.length) { Snd.play('illegal'); return false; }
  let m = ms[0];
  if (m >> 12) {
    let pr = 5;
    if (!S.autoq) {
      const el = pieceEls.get(from); G.busy = true; if (el) place(el, to);
      pr = await askPromo(G.st.t); G.busy = false;
      if (pr == null) { if (el) place(el, from); G.sel = null; G.tg = new Map(); paint(); return false; }
    }
    m = ms.find(x => (x >> 12) === pr) || ms[0];
  }
  playMove(m); return true;
}
boardEl.addEventListener('contextmenu', e => e.preventDefault());
boardEl.addEventListener('pointerdown', e => {
  Snd.resume();
  if (e.button === 2) { G.arr = sqAt(e); return; }
  if (e.button !== 0) return;
  const i = sqAt(e); if (i < 0) return;
  if (G.ov.length) { G.ov = []; drawOv(); }
  if (!canMove()) {
    if (G.mode === 'online' && G.net && !G.net.both && !G.spectator) toast(t('waitingOpp'));
    return;
  }
  if (G.sel != null && G.tg.has(i)) { userMove(G.sel, i); return; }
  const p = G.st.b[i];
  if (p && (p >> 3) === G.st.t) {
    const was = G.sel === i; if (!was) select(i);
    G.drag = { i, el: pieceEls.get(i), x: e.clientX, y: e.clientY, moved: false, was };
    try { boardEl.setPointerCapture(e.pointerId); } catch (err) {}
  } else if (G.sel != null) { G.sel = null; G.tg = new Map(); paint(); }
});
boardEl.addEventListener('pointermove', e => {
  const d = G.drag; if (!d || !d.el) return;
  if (!d.moved && Math.hypot(e.clientX - d.x, e.clientY - d.y) > 6) { d.moved = true; d.el.classList.add('drag'); }
  if (!d.moved) return;
  const rc = boardEl.getBoundingClientRect(), s = rc.width / 8;
  d.el.style.transform = 'translate(' + (e.clientX - rc.left - s / 2) + 'px,' + (e.clientY - rc.top - s / 2) + 'px)';
  const j = sqAt(e);
  for (let i = 0; i < 64; i++) sqEls[i].classList.toggle('hov', i === j && G.tg.has(j));
});
function endDrag(e, cancel) {
  const d = G.drag; if (!d) return; G.drag = null;
  if (d.el) d.el.classList.remove('drag');
  for (const q of sqEls) q.classList.remove('hov');
  if (d.moved) {
    const to = cancel ? -1 : sqAt(e);
    if (to >= 0 && G.tg.has(to)) userMove(d.i, to).then(ok => { if (!ok && d.el) place(d.el, d.i); });
    else { if (d.el) place(d.el, d.i); if (!cancel && to >= 0 && to !== d.i) Snd.play('illegal'); }
  } else if (d.was) { G.sel = null; G.tg = new Map(); paint(); }
}
boardEl.addEventListener('pointerup', e => {
  if (e.button === 2) {
    const j = sqAt(e), a = G.arr; G.arr = null;
    if (a != null && a >= 0 && j >= 0) toggleOv(a === j ? { t: 'm', a } : { t: 'a', a, b: j });
    return;
  }
  endDrag(e, false);
});
boardEl.addEventListener('pointercancel', e => endDrag(e, true));

/* ---------- Tema ve dil uygulama ---------- */
function applyTheme() {
  const r = document.documentElement;
  r.dataset.board = S.board; r.dataset.piece = S.piece; r.dataset.coords = S.coords ? '1' : '0';
  const dark = S.bg === 'dark' || (S.bg === 'auto' && !(window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches));
  r.dataset.mode = dark ? 'dark' : 'light'; r.style.setProperty('--dur', ANIM[S.anim] + 's');
  const m = $('meta[name=theme-color]'); if (m) m.content = dark ? '#0b1020' : '#eef1fa';
}
function applyLang() {
  L = S.lang === 'auto' ? detect() : (I18N[S.lang] ? S.lang : 'en');
  const r = document.documentElement; r.lang = L; r.dir = L === 'ar' ? 'rtl' : 'ltr';
  document.title = t('appName'); $('#appName').textContent = t('appName');
  document.querySelectorAll('[data-i]').forEach(e => { e.textContent = t(e.dataset.i); });
  document.querySelectorAll('[data-it]').forEach(e => { e.title = t(e.dataset.it); e.setAttribute('aria-label', t(e.dataset.it)); });
  if (G.st) updateAll();
}

/* ---------- Online oda istemcisi ---------- */
async function api(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
  let j = {}; try { j = await r.json(); } catch (e) {}
  if (!r.ok) { const err = new Error(j.error || ('HTTP ' + r.status)); err.code = j.error; throw err; }
  return j;
}
const errText = e => e.code === 'nf' ? t('roomNotFound') : e instanceof TypeError ? t('connLost') : (e.code || e.message || 'Error');
let INFO = null;
async function getInfo() {
  if (!INFO) { try { INFO = await (await fetch('/api/info')).json(); } catch (e) { INFO = { urls: [], local: false, public: '' }; } }
  return INFO;
}
function shareBase(info) {
  if (!['localhost', '127.0.0.1', '[::1]', '::1'].includes(location.hostname)) return location.origin;
  return info.public || (info.urls && info.urls[0]) || location.origin;
}
function applyMoves(list) {
  let ok = list.length >= G.moves.length;
  for (let i = 0; ok && i < G.moves.length; i++) if (Chess.toUci(G.moves[i]) !== list[i]) ok = false;
  if (!ok) resetGame(Object.assign({}, G.opts, { quiet: true }));
  const n = list.length - G.moves.length;
  if (n === 1) { const m = Chess.fromUci(G.st, list[list.length - 1]); if (m != null) playMove(m, { remote: true }); }
  else if (n > 1) {
    for (let i = G.moves.length; i < list.length; i++) { const m = Chess.fromUci(G.st, list[i]); if (m == null) break; playMove(m, { remote: true, silent: true }); }
    buildPieces(cur(), false); updateAll();
  }
}
const Net = {
  es: null, errShown: false, reconnectTimer: null,
  close() {
    if (this.reconnectTimer) { clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
    if (this.es) { this.es.close(); this.es = null; }
    if (G.net && G.net.inviteModal) G.net.inviteModal.close();
    G.net = null;
    if (/^#r=/.test(location.hash)) history.replaceState(null, '', location.pathname + location.search);
    const exitBtn = $('#bExitGame'); if (exitBtn) exitBtn.style.display = 'none';
  },
  async create(side, tc) {
    try { const r = await api('/api/room', { color: side, tc: tc || S.tc || '0' }); this.open(r.code, r.token, r.color, r.tc); inviteModal(); }
    catch (e) { toast(errText(e)); }
  },
  async join(code) {
    code = String(code || '').trim().toUpperCase();
    if (!/^[A-Z0-9]{6}$/.test(code)) { toast(t('roomNotFound')); return; }
    try { const r = await api('/api/room/' + code + '/join', { token: sess.get('room.' + code, null) }); this.open(code, r.token, r.color, r.tc); }
    catch (e) { toast(errText(e)); }
  },
  open(code, token, color, tc) {
    this.close();
    if (token) sess.set('room.' + code, token);
    G.net = { code, token, both: false, wasBoth: false, game: -1, draw: null, present: { w: false, b: false }, inviteModal: null, tc: tc || '0' };
    history.replaceState(null, '', location.pathname + location.search + '#r=' + code);
    resetGame({ mode: 'online', me: color === 'b' ? 1 : 0, spectator: color === 's', flipped: color === 'b', quiet: true, tc: parseTC(tc) });
    this.connect();
  },
  connect() {
    const n = G.net; if (!n) return;
    if (this.es) { try { this.es.close(); } catch (e) {} this.es = null; }
    const es = new EventSource('/api/room/' + n.code + '/events' + (n.token ? '?t=' + encodeURIComponent(n.token) : ''));
    this.es = es;
    es.onopen = () => { this.errShown = false; };
    es.onmessage = e => { let r; try { r = JSON.parse(e.data); } catch (err) { return; } if (G.net === n) this.onState(r); };
    es.onerror = () => {
      // Sekme değiştiğinde veya bağlantı koptuğunda oda bilgisini silme, otomatik yeniden bağlan
      if (es.readyState === 2) {
        this.es = null;
        if (G.net === n && !this.reconnectTimer) {
          this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            if (G.net === n) this.connect();
          }, 1500);
        }
      } else if (!this.errShown) {
        this.errShown = true;
      }
    };
  },
  onState(r) {
    const n = G.net, first = n.game === -1;
    if (r.tc && (!n.tc || n.tc === '0')) n.tc = r.tc;
    if (n.game !== r.game) {
      n.game = r.game;
      resetGame({ mode: 'online', me: r.you === 'b' ? 1 : 0, spectator: r.you === 's', flipped: r.you === 'b', quiet: first, tc: parseTC(r.tc || n.tc) });
      if (first && r.you === 's' && r.seated.w && r.seated.b) toast(t('roomFull'));
    } else if (!G.clk && r.tc && r.tc !== '0') {
      setClock(parseTC(r.tc));
    }
    n.both = !!(r.seated.w && r.seated.b); n.present = r.present; n.draw = r.draw;
    applyMoves(r.moves);
    if (r.over && !G.over) endGame(r.result, r.reason);
    if (n.both && !n.wasBoth) { n.wasBoth = true; if (n.inviteModal) n.inviteModal.close(); if (!first || !r.moves.length) { Snd.play('notify'); } }
    updateAll();
  },
  act(type, extra) {
    const n = G.net; if (!n) return Promise.resolve();
    return api('/api/room/' + n.code + '/act', Object.assign({ token: n.token, type }, extra)).catch(e => { toast(errText(e)); });
  },
  sendMove(m) {
    const n = G.net; if (!n) return;
    api('/api/room/' + n.code + '/act', { token: n.token, type: 'move', uci: Chess.toUci(m) }).catch(e => {
      toast(errText(e)); if (this.es) this.es.close(); this.connect();
    });
  },
};

/* ---------- Pencereler ---------- */
const mhead = (title, close) => h('div', { class: 'mhead' }, h('h3', { text: title }), h('button', { class: 'ib', 'aria-label': t('close'), text: '\u2715', onclick: close }));
function seg(opts, val, on) {
  const wrap = h('div', { class: 'seg' });
  for (const [v, label] of opts) {
    const b = h('button', { class: v === val ? 'on' : '', text: label, onclick: () => { for (const c of wrap.children) c.classList.remove('on'); b.classList.add('on'); on(v); } });
    wrap.append(b);
  }
  return wrap;
}
const TCS = ['0', '1+0', '3+0', '3+2', '5+0', '10+0', '15+10', '30+0'];
const tcLabel = s => s === '0' ? t('unlimited') : s.replace('+', ' | ');
const parseTC = s => { if (!s || s === '0') return null; const a = s.split('+').map(Number); return { base: a[0] * 60, inc: a[1] }; };

function newGameModal() {
  modal((box, close) => {
    let mode = S.mode, side = S.side, level = S.level, tc = S.tc;
    const draw = () => {
      box.textContent = '';
      box.append(mhead(t('newGame'), close), seg([['ai', t('modeAi')], ['local', t('modeLocal')], ['online', t('modeOnline')]], mode, v => { mode = v; draw(); }));
      const sideBox = () => h('div', {}, h('h4', { text: t('side') }), seg([['w', t('white')], ['b', t('black')], ['r', t('random')]], side, v => { side = v; }));
      const tcBox = () => {
        const sel = h('select', { 'aria-label': t('timeCtl') }, TCS.map(x => h('option', { value: x, text: tcLabel(x), selected: x === tc })));
        sel.onchange = () => { tc = sel.value; };
        return h('div', {}, h('h4', { text: t('timeCtl') }), sel);
      };
      const start = () => {
        Object.assign(S, { mode, side, tc }); save(); close();
        if (mode === 'ai') {
          const me = side === 'w' ? 0 : side === 'b' ? 1 : (Math.random() < .5 ? 0 : 1);
          if (!activeBot) activeBot = BOTS.engine[2];
          Net.close();
          resetGame({ mode: 'ai', me, flipped: me === 1, level: activeBot.skill, tc: parseTC(tc) });
          BotChat.onStart(activeBot);
        }
        else { Net.close(); resetGame({ mode: 'local', flipped: false, tc: parseTC(tc) }); }
      };
      if (mode === 'ai') {
        const botInfo = activeBot ? activeBot.name + ' (' + activeBot.elo + ' Elo)' : 'Motor Seviye 3';
        box.append(sideBox(),
          h('div', { style: { padding: '12px', borderRadius: '14px', background: 'var(--glass)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: '12px' } },
            activeBot && activeBot.img ? h('img', { src: activeBot.img, style: { width: '48px', height: '48px', borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--acc)' } }) : false,
            h('div', {},
              h('div', { style: { fontWeight: '700', fontSize: '15px' }, text: botInfo }),
              h('div', { class: 'mut', text: 'Rakibi değiştirmek için Botlar menüsünü kullan.' })
            )
          ),
          h('button', { class: 'btn', style: { width: '100%' }, text: '🤖 Botlar Menüsünden Seç', onclick: () => { close(); botsModal(); } }),
          tcBox());
      } else if (mode === 'local') {
        box.append(
          h('div', { class: 'mut', style: { marginBottom: '6px' }, text: 'Aynı cihazda iki kişilik satranç oyunu. Sırayla hamle yapabilirsiniz.' }),
          sideBox(),
          tcBox()
        );
      } else {
        const inp = h('input', { class: 'inp', maxlength: '6', placeholder: 'ABC123', 'aria-label': t('roomCode'), autocomplete: 'off', spellcheck: 'false' });
        box.append(
          h('div', { class: 'mut', style: { marginBottom: '6px' }, text: 'Arkadaşınla online oyna. Süre ve rengini seçip oda kur veya koda katıl.' }),
          sideBox(),
          tcBox(),
          h('button', { class: 'btn pri', style: { width: '100%', marginTop: '6px' }, text: '🏠 ' + t('createRoom'), onclick: () => { Object.assign(S, { mode, side, tc }); save(); close(); Net.create(side, tc); } }),
          h('div', { style: { textAlign: 'center', color: 'var(--mute)', fontSize: '13px', margin: '8px 0' }, text: '— veya —' }),
          h('div', {}, h('h4', { text: t('joinRoom') }), h('div', { class: 'row' }, inp,
            h('button', { class: 'btn', text: t('join'), onclick: () => { close(); Net.join(inp.value); } })))
        );
        return;
      }
      box.append(h('button', { class: 'btn pri', text: t('start'), onclick: start }));
    };
    draw();
  });
}

function settingsModal() {
  modal((box, close) => {
    const draw = () => {
      box.textContent = '';
      box.append(mhead(t('settings'), close));
      const langSel = h('select', { 'aria-label': t('setLang') }, h('option', { value: 'auto', text: t('langAuto'), selected: S.lang === 'auto' }),
        Object.keys(I18N.names).map(k => h('option', { value: k, text: I18N.names[k], selected: S.lang === k })));
      langSel.onchange = () => { S.lang = langSel.value; save(); applyLang(); draw(); };
      box.append(h('div', {}, h('h4', { text: t('setLang') }), langSel));
      box.append(h('div', {}, h('h4', { text: t('setBoard') }), h('div', { class: 'grid' }, BOARDS.map(b => h('button', { class: 'tile' + (S.board === b.id ? ' on' : ''),
        onclick: () => { S.board = b.id; S.piece = b.piece; S.sound = b.sound; save(); applyTheme(); Snd.resume(); Snd.play('move'); draw(); } },
        h('div', { class: 'sw' }, [b.l, b.d, b.d, b.l].map(c => h('i', { style: { background: c } }))), t('b_' + b.id))))));
      box.append(h('div', {}, h('h4', { text: t('setPieces') }), h('div', { class: 'grid' }, PIECES.map(p => h('button', { class: 'tile' + (S.piece === p ? ' on' : ''),
        onclick: () => { S.piece = p; save(); applyTheme(); draw(); } },
        h('div', { class: 'pv', 'data-piece': p }, h('div', { class: 'pc w' }, h('span', { text: GL[2] + VS, 'data-g': GL[2] + VS })), h('div', { class: 'pc b' }, h('span', { text: GL[2] + VS, 'data-g': GL[2] + VS }))), t('p_' + p))))));
      const vol = h('input', { type: 'range', min: '0', max: '100', value: String(Math.round(S.volume * 100)), 'aria-label': t('setVolume') });
      vol.oninput = () => { S.volume = vol.value / 100; save(); };
      vol.onchange = () => { Snd.resume(); Snd.play('capture'); };
      box.append(h('div', {}, h('h4', { text: t('setSound') }), seg(SOUNDS.map(s => [s, t('s_' + s)]), S.sound, v => { S.sound = v; save(); Snd.resume(); Snd.play('capture'); })),
        h('div', { class: 'row' }, vol, h('button', { class: 'btn', text: t('test'), onclick: () => { Snd.resume(); Snd.play('check'); } })));
      box.append(h('div', {}, h('h4', { text: t('setBg') }), seg([['auto', t('bgAuto')], ['dark', t('bgDark')], ['light', t('bgLight')]], S.bg, v => { S.bg = v; save(); applyTheme(); })),
        h('div', {}, h('h4', { text: t('setAnim') }), seg([[0, t('aOff')], [1, t('aFast')], [2, t('aNormal')], [3, t('aSlow')]], S.anim, v => { S.anim = v; save(); applyTheme(); })));
      const tg = (label, key) => {
        const b = h('button', { class: 'tg' + (S[key] ? ' on' : ''), role: 'switch', 'aria-checked': String(!!S[key]), 'aria-label': label,
          onclick: () => { S[key] = !S[key]; b.classList.toggle('on', S[key]); b.setAttribute('aria-checked', String(S[key])); save(); applyTheme(); updateAll(); } });
        return h('div', { class: 'row sp' }, h('span', { text: label }), b);
      };
      box.append(tg(t('coords'), 'coords'), tg(t('legalMoves'), 'legal'), tg(t('highlights'), 'hl'), tg(t('autoQueen'), 'autoq'), tg(t('vibration'), 'vib'));
    };
    draw();
  });
}

async function connectModal() {
  const info = await getInfo(), base = shareBase(info);
  modal((box, close) => {
    box.append(mhead(t('connectTitle'), close), h('p', { class: 'mut', text: t('connectHelp') }),
      h('div', { class: 'qrbox' }, h('img', { src: '/api/qr.svg?d=' + encodeURIComponent(base), alt: 'QR' }), h('div', { class: 'url', text: base })));
    if (info.local) box.append(h('p', { class: 'mut', text: t('localOnly') }));
    box.append(h('button', { class: 'btn pri', text: t('copyLink'), onclick: async () => toast((await copyText(base)) ? t('linkCopied') : base) }));
  });
}
async function inviteModal() {
  const n = G.net; if (!n) return;
  const info = await getInfo(), url = shareBase(info) + '/#r=' + n.code;
  const m = modal((box, close) => {
    box.append(mhead(t('invite'), close),
      h('div', { class: 'qrbox' }, h('img', { src: '/api/qr.svg?d=' + encodeURIComponent(url), alt: 'QR' }), h('div', { class: 'code', text: n.code }),
        h('div', { class: 'url', text: url }), h('p', { class: 'mut', text: t('inviteHelp') }), h('div', { class: 'mut dots', text: t('waitingOpp').replace('\u2026', '') })),
      h('button', { class: 'btn pri', text: t('copyLink'), onclick: async () => toast((await copyText(url)) ? t('linkCopied') : url) }));
    if (info.local) box.append(h('p', { class: 'mut', text: t('localOnly') }));
  });
  if (G.net === n) n.inviteModal = m;
}

/* ---------- PGN ---------- */
function pgn() {
  const d = new Date(), p2 = x => String(x).padStart(2, '0'), res = G.over ? G.over.res : '*';
  const nm = c => G.mode === 'ai' ? (c === G.me ? 'Human' : 'Computer') : G.mode === 'online' && !G.spectator ? (c === G.me ? 'Human' : 'Opponent') : (c ? 'Black' : 'White');
  let s = '[Event "Chess"]\n[Site "localhost"]\n[Date "' + d.getFullYear() + '.' + p2(d.getMonth() + 1) + '.' + p2(d.getDate()) + '"]\n[White "' + nm(0) + '"]\n[Black "' + nm(1) + '"]\n[Result "' + res + '"]\n\n';
  G.sans.forEach((x, i) => { if (i % 2 === 0) s += (i / 2 + 1) + '. '; s += x + ' '; });
  return s + res;
}

/* ---------- Bağlantılar ve başlangıç ---------- */
$('#bSettings').onclick = settingsModal;
$('#bConnect').onclick = connectModal;
const pTab = $('#btnPlayTab'); if (pTab) pTab.onclick = newGameModal;
const bTab = $('#btnBotTab'); if (bTab) bTab.onclick = botsModal;
const revBtn = $('#aReview'); if (revBtn) revBtn.onclick = analysisModal;
const zTab = $('#btnPuzzleTab'); if (zTab) zTab.onclick = puzzlesModal;
const oTab = $('#btnOnlineTab'); if (oTab) oTab.onclick = () => {
  modal((box, close) => {
    let side = S.side, tc = S.tc;
    const sideBox = () => h('div', {}, h('h4', { text: t('side') }), seg([['w', t('white')], ['b', t('black')], ['r', t('random')]], side, v => { side = v; }));
    const tcBox = () => {
      const sel = h('select', { 'aria-label': t('timeCtl') }, TCS.map(x => h('option', { value: x, text: tcLabel(x), selected: x === tc })));
      sel.onchange = () => { tc = sel.value; };
      return h('div', {}, h('h4', { text: t('timeCtl') }), sel);
    };
    const inp = h('input', { class: 'inp', maxlength: '6', placeholder: 'ABC123', 'aria-label': t('roomCode'), autocomplete: 'off', spellcheck: 'false' });
    box.append(
      mhead('Online Çok Oyunculu', close),
      h('p', { class: 'mut', text: 'Arkadaşınla veya farklı bir cihazla oynamak için süre ve renk seçip oda kurun veya koda katılın.' }),
      sideBox(),
      tcBox(),
      h('button', { class: 'btn pri', style: { width: '100%', marginTop: '8px' }, text: '🏠 ' + t('createRoom'), onclick: () => { Object.assign(S, { mode: 'online', side, tc }); save(); close(); Net.create(side, tc); } }),
      h('div', { style: { textAlign: 'center', color: 'var(--mute)', fontSize: '13px', margin: '8px 0' }, text: '— veya —' }),
      h('div', {}, h('h4', { text: t('joinRoom') }), h('div', { class: 'row' }, inp,
        h('button', { class: 'btn', text: t('join'), onclick: () => { close(); Net.join(inp.value); } })))
    );
  });
};
$('#bFull').onclick = () => { if (document.fullscreenElement) document.exitFullscreen(); else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {}); };
$('#aNew').onclick = newGameModal; $('#aFlip').onclick = flip; $('#aUndo').onclick = undo; $('#aHint').onclick = doHint; $('#aInvite').onclick = inviteModal;
$('#aPgn').onclick = async () => toast((await copyText(pgn())) ? t('copied') : 'PGN');
$('#aDraw').onclick = () => { if (G.mode === 'online') { Net.act('draw_offer'); toast(t('drawSent')); } else ask(t('drawConfirm'), () => endGame('1/2-1/2', 'agreement')); };
$('#aResign').onclick = () => ask(t('confirmResign'), () => {
  if (G.mode === 'online') Net.act('resign'); else endGame(G.mode === 'ai' ? (G.me === 0 ? '0-1' : '1-0') : (G.st.t === 0 ? '0-1' : '1-0'), 'resign');
});
$('#nFirst').onclick = () => goto(0); $('#nPrev').onclick = () => goto(G.vi - 1);
$('#nNext').onclick = () => goto(G.vi + 1); $('#nLast').onclick = () => goto(G.moves.length);
addEventListener('keydown', e => {
  Snd.resume();
  if (/^(INPUT|SELECT|TEXTAREA)$/.test((e.target && e.target.tagName) || '')) return;
  if (e.key === 'Escape') { if (modals.length) modals[modals.length - 1].close(); else { G.sel = null; G.tg = new Map(); G.ov = []; G.hint = null; paint(); drawOv(); } }
  else if (modals.length) return;
  else if (e.key === 'ArrowLeft') goto(G.vi - 1);
  else if (e.key === 'ArrowRight') goto(G.vi + 1);
  else if (e.key === 'Home') goto(0);
  else if (e.key === 'End') goto(G.moves.length);
  else if (e.key === 'f' || e.key === 'F') flip();
  else if ((e.key === 'z' || e.key === 'Z') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); undo(); }
});
addEventListener('pointerdown', () => Snd.resume());
function checkHash() {
  const m = /^#r=([A-Za-z0-9]{6})$/.exec(location.hash);
  if (m && !(G.net && G.net.code === m[1].toUpperCase())) Net.join(m[1]);
}
addEventListener('hashchange', checkHash);
if (window.matchMedia) { const mq = matchMedia('(prefers-color-scheme: dark)'); if (mq.addEventListener) mq.addEventListener('change', applyTheme); }

// Sekme değişimi ve odak koruması (Online maçta bağlantı kopmasın)
document.addEventListener('visibilitychange', () => {
  if (!document.hidden && G.mode === 'online' && G.net && G.net.code) {
    if (!Net.es || Net.es.readyState !== 1) Net.connect();
  }
});
window.addEventListener('focus', () => {
  if (G.mode === 'online' && G.net && G.net.code) {
    if (!Net.es || Net.es.readyState !== 1) Net.connect();
  }
});

// Sağ alttaki çıkış butonu
const exitBtnEl = $('#bExitGame');
if (exitBtnEl) {
  exitBtnEl.onclick = () => {
    ask('Mevcut oyundan ve odadan çıkmak istediğinize emin misiniz?', () => {
      if (G.mode === 'online') {
        if (!G.over && G.net && G.net.both) {
          try { Net.act('resign'); } catch (e) {}
        }
        Net.close();
      }
      exitBtnEl.style.display = 'none';
      hideResult();
      if (coachAudio) { coachAudio.pause(); coachAudio = null; }
      resetGame({ mode: 'ai', me: 0, flipped: false, level: (activeBot ? activeBot.skill : 3), tc: parseTC(S.tc) });
      toast('Odadan çıkıldı.');
    });
  };
}

applyLang(); applyTheme(); FX.size(); initWorker();
if (!activeBot && typeof BOTS !== 'undefined' && BOTS.engine) activeBot = BOTS.engine[2] || BOTS.engine[0];
resetGame({ mode: 'ai', me: 0, flipped: false, level: activeBot ? activeBot.skill : 2, tc: parseTC(S.tc), quiet: true });
checkHash();
})();
"""
ENGINE_JS = r"""/* Satranç motoru: kurallar, SAN/FEN ve alfa-beta yapay zeka.
   Sayfada ve Web Worker içinde aynı dosya çalışır.
   Kareler: 0 = a8 ... 63 = h1. Taş: tip (1 P,2 N,3 B,4 R,5 Q,6 K) | (siyah ? 8 : 0)
   Hamle: from | to<<6 | promosyon<<12 */
(function (G) {
'use strict';
const FILES = 'abcdefgh', LET = ' PNBRQK';
const KN = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
const KG = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];
const DG = [[-1,-1],[-1,1],[1,-1],[1,1]], OR = [[-1,0],[1,0],[0,-1],[0,1]];
const P = 1, N = 2, B = 3, R = 4, Q = 5, K = 6;
const PV = [0, 100, 320, 330, 500, 900, 0];
const CM = new Uint8Array(64).fill(15);
CM[60] = 12; CM[63] = 14; CM[56] = 13; CM[4] = 3; CM[7] = 11; CM[0] = 7;
const START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
const sqName = i => FILES[i & 7] + (8 - (i >> 3));
const sqIdx = s => (8 - +s[1]) * 8 + FILES.indexOf(s[0]);

function fromFEN(fen) {
  const a = fen.trim().split(/\s+/);
  const b = new Int8Array(64); let i = 0;
  for (const ch of a[0]) {
    if (ch === '/') continue;
    if (ch >= '1' && ch <= '8') { i += +ch; continue; }
    const lo = ch === ch.toLowerCase();
    b[i++] = LET.indexOf(ch.toUpperCase()) | (lo ? 8 : 0);
  }
  let c = 0;
  for (const x of (a[2] || '-')) c |= x === 'K' ? 1 : x === 'Q' ? 2 : x === 'k' ? 4 : x === 'q' ? 8 : 0;
  return { b, t: a[1] === 'b' ? 1 : 0, c, ep: a[3] && a[3] !== '-' ? sqIdx(a[3]) : -1, half: +a[4] || 0, full: +a[5] || 1 };
}
function toFEN(st) {
  let s = '';
  for (let r = 0; r < 8; r++) {
    let e = 0;
    for (let c = 0; c < 8; c++) {
      const p = st.b[r * 8 + c];
      if (!p) { e++; continue; }
      if (e) { s += e; e = 0; }
      const ch = LET[p & 7];
      s += (p >> 3) ? ch.toLowerCase() : ch;
    }
    if (e) s += e;
    if (r < 7) s += '/';
  }
  const c = (st.c & 1 ? 'K' : '') + (st.c & 2 ? 'Q' : '') + (st.c & 4 ? 'k' : '') + (st.c & 8 ? 'q' : '');
  return s + ' ' + (st.t ? 'b' : 'w') + ' ' + (c || '-') + ' ' + (st.ep >= 0 ? sqName(st.ep) : '-') + ' ' + st.half + ' ' + st.full;
}
const startState = () => fromFEN(START);

function attacked(b, sq, by) {
  const r = sq >> 3, c = sq & 7, o = by << 3;
  const pr = by === 0 ? r + 1 : r - 1;
  if (pr >= 0 && pr < 8) {
    if (c > 0 && b[pr * 8 + c - 1] === (o | P)) return true;
    if (c < 7 && b[pr * 8 + c + 1] === (o | P)) return true;
  }
  for (let d = 0; d < 8; d++) {
    let nr = r + KN[d][0], nc = c + KN[d][1];
    if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8 && b[nr * 8 + nc] === (o | N)) return true;
    nr = r + KG[d][0]; nc = c + KG[d][1];
    if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8 && b[nr * 8 + nc] === (o | K)) return true;
  }
  for (let k = 0; k < 2; k++) {
    const D = k ? OR : DG, t1 = k ? R : B;
    for (let d = 0; d < 4; d++) {
      let nr = r + D[d][0], nc = c + D[d][1];
      while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
        const p = b[nr * 8 + nc];
        if (p) { if ((p >> 3) === by && ((p & 7) === t1 || (p & 7) === Q)) return true; break; }
        nr += D[d][0]; nc += D[d][1];
      }
    }
  }
  return false;
}
function inCheck(b, color) {
  const k = b.indexOf((color << 3) | K);
  return k >= 0 && attacked(b, k, color ^ 1);
}

function gen(st, qs) {
  const b = st.b, t = st.t, res = [];
  for (let i = 0; i < 64; i++) {
    const p = b[i];
    if (!p || (p >> 3) !== t) continue;
    const k = p & 7, r = i >> 3, c = i & 7;
    if (k === P) {
      const d = t === 0 ? -1 : 1, start = t === 0 ? 6 : 1, last = t === 0 ? 0 : 7, nr = r + d;
      if (nr < 0 || nr > 7) continue;
      const add = to => {
        if (nr === last) for (let pr = 5; pr >= 2; pr--) res.push(i | to << 6 | pr << 12);
        else res.push(i | to << 6);
      };
      let to = nr * 8 + c;
      if (!b[to]) {
        if (!qs || nr === last) add(to);
        if (!qs && r === start && !b[to + d * 8]) res.push(i | (to + d * 8) << 6);
      }
      for (let dc = -1; dc <= 1; dc += 2) {
        const nc = c + dc;
        if (nc < 0 || nc > 7) continue;
        to = nr * 8 + nc;
        if ((b[to] && (b[to] >> 3) !== t) || to === st.ep) add(to);
      }
    } else if (k === N || k === K) {
      const D = k === N ? KN : KG;
      for (let d = 0; d < 8; d++) {
        const nr = r + D[d][0], nc = c + D[d][1];
        if (nr < 0 || nr > 7 || nc < 0 || nc > 7) continue;
        const to = nr * 8 + nc, q = b[to];
        if (q ? (q >> 3) !== t : !qs) res.push(i | to << 6);
      }
      if (k === K && !qs) {
        const base = t === 0 ? 56 : 0;
        if (i === base + 4 && (st.c & (t === 0 ? 3 : 12)) && !attacked(b, i, t ^ 1)) {
          const ks = t === 0 ? 1 : 4, qq = t === 0 ? 2 : 8, rook = (t << 3) | R, o = t ^ 1;
          if ((st.c & ks) && b[base + 7] === rook && !b[base + 5] && !b[base + 6] &&
              !attacked(b, base + 5, o) && !attacked(b, base + 6, o)) res.push(i | (base + 6) << 6);
          if ((st.c & qq) && b[base] === rook && !b[base + 1] && !b[base + 2] && !b[base + 3] &&
              !attacked(b, base + 3, o) && !attacked(b, base + 2, o)) res.push(i | (base + 2) << 6);
        }
      }
    } else {
      const D = k === B ? DG : k === R ? OR : DG.concat(OR);
      for (let d = 0; d < D.length; d++) {
        let nr = r + D[d][0], nc = c + D[d][1];
        while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
          const to = nr * 8 + nc, q = b[to];
          if (!q) { if (!qs) res.push(i | to << 6); }
          else { if ((q >> 3) !== t) res.push(i | to << 6); break; }
          nr += D[d][0]; nc += D[d][1];
        }
      }
    }
  }
  return res;
}

function make(st, m) {
  const f = m & 63, to = (m >> 6) & 63, pr = m >> 12, b = st.b.slice();
  let p = b[f]; const k = p & 7, t = st.t, cap = b[to] !== 0;
  let ep = -1;
  if (k === P) {
    if (to === st.ep && !cap && (f & 7) !== (to & 7)) b[to + (t === 0 ? 8 : -8)] = 0;
    if (Math.abs(to - f) === 16) ep = (f + to) >> 1;
    if (pr) p = (t << 3) | pr;
  }
  if (k === K && Math.abs(to - f) === 2) {
    if (to > f) { b[f + 1] = b[f + 3]; b[f + 3] = 0; } else { b[f - 1] = b[f - 4]; b[f - 4] = 0; }
  }
  b[to] = p; b[f] = 0;
  return { b, t: t ^ 1, c: st.c & CM[f] & CM[to], ep, half: (k === P || cap) ? 0 : st.half + 1, full: st.full + t };
}
function legal(st) {
  const out = [], ms = gen(st);
  for (let i = 0; i < ms.length; i++) if (!inCheck(make(st, ms[i]).b, st.t)) out.push(ms[i]);
  return out;
}
const toUci = m => sqName(m & 63) + sqName((m >> 6) & 63) + ((m >> 12) ? LET[m >> 12].toLowerCase() : '');
function fromUci(st, u) {
  if (typeof u !== 'string') return null;
  const ms = legal(st);
  for (const m of ms) if (toUci(m) === u) return m;
  return null;
}

function san(st, m, leg) {
  leg = leg || legal(st);
  const f = m & 63, to = (m >> 6) & 63, pr = m >> 12, p = st.b[f], k = p & 7;
  let s;
  if (k === K && Math.abs(to - f) === 2) s = to > f ? 'O-O' : 'O-O-O';
  else {
    const cap = st.b[to] !== 0 || (k === P && (f & 7) !== (to & 7));
    s = '';
    if (k === P) { if (cap) s += FILES[f & 7]; }
    else {
      s += LET[k];
      const oth = leg.filter(x => ((x >> 6) & 63) === to && st.b[x & 63] === p && (x & 63) !== f);
      if (oth.length) {
        if (oth.every(o => (o & 7) !== (f & 7))) s += FILES[f & 7];
        else if (oth.every(o => ((o & 63) >> 3) !== (f >> 3))) s += 8 - (f >> 3);
        else s += FILES[f & 7] + (8 - (f >> 3));
      }
    }
    if (cap) s += 'x';
    s += sqName(to);
    if (pr) s += '=' + LET[pr];
  }
  const ns = make(st, m);
  if (inCheck(ns.b, ns.t)) s += legal(ns).length ? '+' : '#';
  return s;
}

function insufficient(b) {
  const pcs = [];
  for (let i = 0; i < 64; i++) if (b[i] && (b[i] & 7) !== K) pcs.push([i, b[i] & 7]);
  if (!pcs.length) return true;
  if (pcs.some(x => x[1] === P || x[1] === R || x[1] === Q)) return false;
  if (pcs.length === 1) return true;
  if (pcs.every(x => x[1] === B)) return new Set(pcs.map(x => ((x[0] >> 3) + (x[0] & 7)) & 1)).size === 1;
  return false;
}
function posKey(st) {
  let s = '';
  for (let i = 0; i < 64; i++) s += String.fromCharCode(48 + st.b[i]);
  let ep = -1;
  if (st.ep >= 0) {
    const er = st.ep >> 3, ec = st.ep & 7, pr = st.t === 0 ? er + 1 : er - 1;
    for (let dc = -1; dc <= 1; dc += 2) {
      const cc = ec + dc;
      if (cc >= 0 && cc < 8 && pr >= 0 && pr < 8 && st.b[pr * 8 + cc] === ((st.t << 3) | P)) ep = st.ep;
    }
  }
  return s + st.t + st.c + ep;
}
function status(st, keys) {
  if (!legal(st).length) {
    if (inCheck(st.b, st.t)) return { over: 1, res: st.t === 0 ? '0-1' : '1-0', why: 'checkmate' };
    return { over: 1, res: '1/2-1/2', why: 'stalemate' };
  }
  if (insufficient(st.b)) return { over: 1, res: '1/2-1/2', why: 'insufficient' };
  if (st.half >= 100) return { over: 1, res: '1/2-1/2', why: 'fifty' };
  if (keys) {
    const k = posKey(st); let n = 0;
    for (const x of keys) if (x === k) n++;
    if (n >= 3) return { over: 1, res: '1/2-1/2', why: 'repetition' };
  }
  return { over: 0 };
}
function perft(st, d) {
  if (!d) return 1;
  let n = 0;
  for (const m of legal(st)) n += d === 1 ? 1 : perft(make(st, m), d - 1);
  return n;
}

/* ---------------- Yapay zeka ---------------- */
const T = s => s.trim().split(/[\s,]+/).map(Number);
const PST = [null,
  T(`0 0 0 0 0 0 0 0  50 50 50 50 50 50 50 50  10 10 20 30 30 20 10 10  5 5 10 25 25 10 5 5
     0 0 0 20 20 0 0 0  5 -5 -10 0 0 -10 -5 5  5 10 10 -20 -20 10 10 5  0 0 0 0 0 0 0 0`),
  T(`-50 -40 -30 -30 -30 -30 -40 -50  -40 -20 0 0 0 0 -20 -40  -30 0 10 15 15 10 0 -30  -30 5 15 20 20 15 5 -30
     -30 0 15 20 20 15 0 -30  -30 5 10 15 15 10 5 -30  -40 -20 0 5 5 0 -20 -40  -50 -40 -30 -30 -30 -30 -40 -50`),
  T(`-20 -10 -10 -10 -10 -10 -10 -20  -10 0 0 0 0 0 0 -10  -10 0 5 10 10 5 0 -10  -10 5 5 10 10 5 5 -10
     -10 0 10 10 10 10 0 -10  -10 10 10 10 10 10 10 -10  -10 5 0 0 0 0 5 -10  -20 -10 -10 -10 -10 -10 -10 -20`),
  T(`0 0 0 0 0 0 0 0  5 10 10 10 10 10 10 5  -5 0 0 0 0 0 0 -5  -5 0 0 0 0 0 0 -5
     -5 0 0 0 0 0 0 -5  -5 0 0 0 0 0 0 -5  -5 0 0 0 0 0 0 -5  0 0 0 5 5 0 0 0`),
  T(`-20 -10 -10 -5 -5 -10 -10 -20  -10 0 0 0 0 0 0 -10  -10 0 5 5 5 5 0 -10  -5 0 5 5 5 5 0 -5
     0 0 5 5 5 5 0 -5  -10 5 5 5 5 5 0 -10  -10 0 5 0 0 0 0 -10  -20 -10 -10 -5 -5 -10 -10 -20`),
  T(`-30 -40 -40 -50 -50 -40 -40 -30  -30 -40 -40 -50 -50 -40 -40 -30  -30 -40 -40 -50 -50 -40 -40 -30
     -30 -40 -40 -50 -50 -40 -40 -30  -20 -30 -30 -40 -40 -30 -30 -20  -10 -20 -20 -20 -20 -20 -20 -10
     20 20 0 0 0 0 20 20  20 30 10 0 0 10 30 20`)];
const KEND = T(`-50 -40 -30 -20 -20 -30 -40 -50  -30 -20 -10 0 0 -10 -20 -30  -30 -10 20 30 30 20 -10 -30
  -30 -10 30 40 40 30 -10 -30  -30 -10 30 40 40 30 -10 -30  -30 -10 20 30 30 20 -10 -30
  -30 -30 0 0 0 0 -30 -30  -50 -30 -30 -30 -30 -30 -30 -50`);

function evaluate(st) {
  const b = st.b; let mat = 0, s = 0, wb = 0, bb = 0;
  for (let i = 0; i < 64; i++) { const k = b[i] & 7; if (k > 1 && k < 6) mat += PV[k]; }
  const end = mat < 2400;
  for (let i = 0; i < 64; i++) {
    const p = b[i]; if (!p) continue;
    const k = p & 7, w = (p >> 3) === 0, x = w ? i : i ^ 56;
    const v = PV[k] + (k === K ? (end ? KEND[x] : PST[K][x]) : PST[k][x]);
    if (k === B) { if (w) wb++; else bb++; }
    s += w ? v : -v;
  }
  if (wb > 1) s += 30; if (bb > 1) s -= 30;
  return (st.t === 0 ? s : -s) + 8;
}

const INF = 1e6, MATE = 100000;
let nodes = 0, deadline = 0, stop = false, canStop = false, killers = [];
function order(st, ms, pv, ply) {
  const b = st.b, kl = killers[ply];
  const sc = ms.map(m => {
    const f = m & 63, to = (m >> 6) & 63, v = b[to];
    let s = 0;
    if (v) s = 10000 + 10 * PV[v & 7] - PV[b[f] & 7];
    else if ((b[f] & 7) === P && (f & 7) !== (to & 7)) s = 10900;
    if (m >> 12) s += 8000 + PV[m >> 12];
    if (m === pv) s = 1e6; else if (!v && kl && (kl[0] === m || kl[1] === m)) s = 5000;
    return [s, m];
  });
  sc.sort((a, c) => c[0] - a[0]);
  return sc.map(x => x[1]);
}
function timeUp() {
  if (canStop && (++nodes & 1023) === 0 && Date.now() > deadline) stop = true;
  return stop;
}
function qsearch(st, alpha, beta) {
  if (timeUp()) return 0;
  const sp = evaluate(st);
  if (sp >= beta) return beta;
  if (sp > alpha) alpha = sp;
  for (const m of order(st, gen(st, true), 0, 0)) {
    const ns = make(st, m);
    if (inCheck(ns.b, st.t)) continue;
    const s = -qsearch(ns, -beta, -alpha);
    if (stop) return 0;
    if (s >= beta) return beta;
    if (s > alpha) alpha = s;
  }
  return alpha;
}
function search(st, depth, alpha, beta, ply) {
  if (timeUp()) return 0;
  const chk = inCheck(st.b, st.t);
  if (chk && ply < 40) depth++;
  if (depth <= 0 || ply > 60) return qsearch(st, alpha, beta);
  if (st.half >= 100) return 0;
  let any = false;
  for (const m of order(st, gen(st), null, ply)) {
    const ns = make(st, m);
    if (inCheck(ns.b, st.t)) continue;
    any = true;
    const s = -search(ns, depth - 1, -beta, -alpha, ply + 1);
    if (stop) return 0;
    if (s >= beta) {
      if (!st.b[(m >> 6) & 63]) { const kl = killers[ply] || (killers[ply] = [0, 0]); if (kl[0] !== m) { kl[1] = kl[0]; kl[0] = m; } }
      return beta;
    }
    if (s > alpha) alpha = s;
  }
  if (!any) return chk ? -MATE + ply : 0;
  return alpha;
}
const LV = [null, { d: 1, t: 300, n: 150 }, { d: 2, t: 600, n: 60 }, { d: 3, t: 1200, n: 15 },
  { d: 6, t: 1800, n: 0 }, { d: 10, t: 3500, n: 0 }];

function bestMove(st, level, keys, ms) {
  const cfg = LV[level] || LV[3], root = legal(st);
  if (!root.length) return null;
  if (root.length === 1) return { m: root[0], score: 0, depth: 0 };
  nodes = 0; stop = false; killers = [];
  const counts = new Map();
  if (keys) for (const k of keys) counts.set(k, (counts.get(k) || 0) + 1);
  const rep = ns => (counts.get(posKey(ns)) || 0) >= 2;
  if (cfg.n) {
    canStop = false;
    let best = root[0], bs = -INF;
    for (const m of root) {
      const ns = make(st, m);
      let s = rep(ns) ? 0 : -search(ns, cfg.d - 1, -INF, INF, 1);
      s += (Math.random() * 2 - 1) * cfg.n;
      if (s > bs) { bs = s; best = m; }
    }
    return { m: best, score: bs, depth: cfg.d };
  }
  deadline = Date.now() + (ms || cfg.t);
  let best = root[0], bestScore = 0, done = 0;
  for (let d = 1; d <= cfg.d; d++) {
    canStop = d > 1; stop = false;
    let alpha = -INF, ib = null, is = -INF;
    for (const m of order(st, root, best, 0)) {
      const ns = make(st, m);
      const s = rep(ns) ? 0 : -search(ns, d - 1, -INF, -alpha, 1);
      if (stop) break;
      if (s > is) { is = s; ib = m; }
      if (s > alpha) alpha = s;
    }
    if (stop) break;
    best = ib; bestScore = is; done = d;
    if (Math.abs(is) > MATE - 100 || Date.now() > deadline) break;
  }
  return { m: best, score: bestScore, depth: done };
}

G.Chess = { FILES, START, sqName, sqIdx, fromFEN, toFEN, startState, attacked, inCheck, gen, make, legal,
  toUci, fromUci, san, insufficient, posKey, status, perft, bestMove, evaluate };

if (typeof WorkerGlobalScope !== 'undefined' && typeof self !== 'undefined' && self instanceof WorkerGlobalScope) {
  self.onmessage = e => {
    const d = e.data;
    let r = null;
    try { r = bestMove(fromFEN(d.fen), d.level, d.keys, d.time); } catch (err) { r = null; }
    self.postMessage({ id: d.id, m: r ? r.m : -1, score: r ? r.score : 0, depth: r ? r.depth : 0 });
  };
}
})(typeof self !== 'undefined' ? self : globalThis);
"""
I18N_JS = r"""/* Diller: en (taban), tr, de, fr, es, ru, ar, zh. Eksik anahtar İngilizceye düşer. */
window.I18N = {
  names: { en: 'English', tr: 'Türkçe', de: 'Deutsch', fr: 'Français', es: 'Español', ru: 'Русский', ar: 'العربية', zh: '中文' },
  en: {
    appName: 'Chess', newGame: 'New game', settings: 'Settings', connect: 'Play on another device', undo: 'Undo', hint: 'Hint',
    flip: 'Flip board', resign: 'Resign', draw: 'Draw', pgn: 'Copy PGN', copied: 'Copied!', fullscreen: 'Full screen',
    close: 'Close', cancel: 'Cancel', start: 'Start', yes: 'Yes', no: 'No', ok: 'OK',
    white: 'White', black: 'Black', you: 'You', computer: 'Computer', opponent: 'Opponent', spectator: 'Spectating',
    waitingOpp: 'Waiting for your opponent…', oppLeft: 'Opponent disconnected',
    toMove: '{c} to move', check: 'Check!', thinking: 'Computer is thinking…',
    youWon: 'You won!', youLost: 'You lost', drawn: 'Draw', whiteWins: 'White wins', blackWins: 'Black wins',
    w_checkmate: 'by checkmate', w_stalemate: 'stalemate', w_insufficient: 'insufficient material', w_fifty: '50-move rule',
    w_repetition: 'threefold repetition', w_agreement: 'by agreement', w_resign: 'by resignation', w_timeout: 'on time',
    modeAi: 'Computer', modeLocal: 'Two players', modeOnline: 'Online', level: 'Difficulty',
    lv1: 'Beginner', lv2: 'Casual', lv3: 'Club', lv4: 'Strong', lv5: 'Master', side: 'Play as', random: 'Random',
    timeCtl: 'Time control', unlimited: 'Unlimited',
    createRoom: 'Create room', joinRoom: 'Join with code', roomCode: 'Room code', join: 'Join', invite: 'Invite a friend',
    inviteHelp: 'Scan the QR code or share the link. The game starts as soon as your friend joins.',
    copyLink: 'Copy link', linkCopied: 'Link copied', roomNotFound: 'Room not found', connLost: 'Connection lost, reconnecting…',
    drawOffered: 'Your opponent offers a draw', drawSent: 'Draw offer sent', accept: 'Accept', decline: 'Decline',
    rematch: 'Rematch', review: 'Review', roomFull: 'Room is full, you are spectating', drawConfirm: 'Agree to a draw?',
    connectTitle: 'Play on another device',
    connectHelp: 'Open this address on a phone or computer on the same network, or scan the QR code.',
    localOnly: 'The server runs in local-only mode (--local), other devices cannot connect.',
    setBoard: 'Board', setPieces: 'Pieces', setSound: 'Sound', setVolume: 'Volume', setBg: 'Appearance',
    bgAuto: 'Auto', bgDark: 'Dark', bgLight: 'Light', setAnim: 'Animations', aOff: 'Off', aFast: 'Fast', aNormal: 'Normal', aSlow: 'Slow',
    setLang: 'Language', langAuto: 'Automatic (device)', coords: 'Coordinates', legalMoves: 'Show legal moves',
    highlights: 'Highlight last move', autoQueen: 'Always promote to queen', vibration: 'Vibration', test: 'Test',
    promoteTo: 'Promote to', confirmResign: 'Resign this game?', yourTurn: 'Your move',
    b_wood: 'Classic wood', b_emerald: 'Emerald', b_ice: 'Ice', b_night: 'Night', b_violet: 'Violet', b_marble: 'Marble', b_glass: 'Glass', b_neon: 'Neon',
    p_classic: 'Classic', p_flat: 'Flat', p_gold: 'Gold', p_glass: 'Glass', p_neon: 'Neon',
    s_wood: 'Wood', s_glass: 'Glass', s_synth: 'Synth', s_soft: 'Soft', s_off: 'Silent',
  },
  tr: {
    appName: 'Satranç', newGame: 'Yeni oyun', settings: 'Ayarlar', connect: 'Başka cihazdan oyna', undo: 'Geri al', hint: 'İpucu',
    flip: 'Tahtayı çevir', resign: 'Pes et', draw: 'Beraberlik', pgn: 'PGN kopyala', copied: 'Kopyalandı!', fullscreen: 'Tam ekran',
    close: 'Kapat', cancel: 'Vazgeç', start: 'Başla', yes: 'Evet', no: 'Hayır', ok: 'Tamam',
    white: 'Beyaz', black: 'Siyah', you: 'Sen', computer: 'Bilgisayar', opponent: 'Rakip', spectator: 'İzliyorsun',
    waitingOpp: 'Rakip bekleniyor…', oppLeft: 'Rakibin bağlantısı koptu',
    toMove: 'Sıra: {c}', check: 'Şah!', thinking: 'Bilgisayar düşünüyor…',
    youWon: 'Kazandın!', youLost: 'Kaybettin', drawn: 'Berabere', whiteWins: 'Beyaz kazandı', blackWins: 'Siyah kazandı',
    w_checkmate: 'şah-mat', w_stalemate: 'pat', w_insufficient: 'yetersiz materyal', w_fifty: '50 hamle kuralı',
    w_repetition: 'üç kez tekrar', w_agreement: 'anlaşarak', w_resign: 'pes ederek', w_timeout: 'süre bitti',
    modeAi: 'Bilgisayar', modeLocal: 'İki kişilik', modeOnline: 'Online', level: 'Zorluk',
    lv1: 'Acemi', lv2: 'Rahat', lv3: 'Kulüp', lv4: 'Güçlü', lv5: 'Usta', side: 'Rengin', random: 'Rastgele',
    timeCtl: 'Süre', unlimited: 'Süresiz',
    createRoom: 'Oda kur', joinRoom: 'Kodla katıl', roomCode: 'Oda kodu', join: 'Katıl', invite: 'Arkadaşını davet et',
    inviteHelp: 'QR kodu okut ya da bağlantıyı paylaş. Arkadaşın katılır katılmaz oyun başlar.',
    copyLink: 'Bağlantıyı kopyala', linkCopied: 'Bağlantı kopyalandı', roomNotFound: 'Oda bulunamadı', connLost: 'Bağlantı koptu, yeniden deneniyor…',
    drawOffered: 'Rakibin beraberlik teklif ediyor', drawSent: 'Beraberlik teklifi gönderildi', accept: 'Kabul et', decline: 'Reddet',
    rematch: 'Rövanş', review: 'İncele', roomFull: 'Oda dolu, izleyici olarak katıldın', drawConfirm: 'Beraberliği kabul ediyor musunuz?',
    connectTitle: 'Başka cihazdan oyna',
    connectHelp: 'Aynı ağdaki telefon ya da bilgisayarda bu adresi aç veya QR kodu okut.',
    localOnly: 'Sunucu yalnızca yerel modda (--local), diğer cihazlar bağlanamaz.',
    setBoard: 'Tahta', setPieces: 'Taşlar', setSound: 'Ses', setVolume: 'Ses düzeyi', setBg: 'Görünüm',
    bgAuto: 'Otomatik', bgDark: 'Koyu', bgLight: 'Açık', setAnim: 'Animasyonlar', aOff: 'Kapalı', aFast: 'Hızlı', aNormal: 'Normal', aSlow: 'Yavaş',
    setLang: 'Dil', langAuto: 'Otomatik (cihaz dili)', coords: 'Koordinatlar', legalMoves: 'Geçerli hamleleri göster',
    highlights: 'Son hamleyi vurgula', autoQueen: 'Hep vezir yap', vibration: 'Titreşim', test: 'Dene',
    promoteTo: 'Terfi et', confirmResign: 'Oyundan çekilmek istiyor musun?', yourTurn: 'Sıra sende',
    b_wood: 'Klasik ahşap', b_emerald: 'Zümrüt', b_ice: 'Buz', b_night: 'Gece', b_violet: 'Mor', b_marble: 'Mermer', b_glass: 'Cam', b_neon: 'Neon',
    p_classic: 'Klasik', p_flat: 'Düz', p_gold: 'Altın', p_glass: 'Cam', p_neon: 'Neon',
    s_wood: 'Ahşap', s_glass: 'Cam', s_synth: 'Sentezleyici', s_soft: 'Yumuşak', s_off: 'Sessiz',
  },
  de: {
    appName: 'Schach', newGame: 'Neues Spiel', settings: 'Einstellungen', connect: 'Auf anderem Gerät spielen', undo: 'Zurück', hint: 'Tipp',
    flip: 'Brett drehen', resign: 'Aufgeben', draw: 'Remis', pgn: 'PGN kopieren', copied: 'Kopiert!', fullscreen: 'Vollbild',
    close: 'Schließen', cancel: 'Abbrechen', start: 'Start', yes: 'Ja', no: 'Nein', ok: 'OK',
    white: 'Weiß', black: 'Schwarz', you: 'Du', computer: 'Computer', opponent: 'Gegner', spectator: 'Du schaust zu',
    waitingOpp: 'Warte auf Gegner…', oppLeft: 'Gegner getrennt',
    toMove: '{c} ist am Zug', check: 'Schach!', thinking: 'Computer denkt nach…',
    youWon: 'Du hast gewonnen!', youLost: 'Du hast verloren', drawn: 'Remis', whiteWins: 'Weiß gewinnt', blackWins: 'Schwarz gewinnt',
    w_checkmate: 'durch Schachmatt', w_stalemate: 'Patt', w_insufficient: 'zu wenig Material', w_fifty: '50-Züge-Regel',
    w_repetition: 'dreifache Wiederholung', w_agreement: 'durch Einigung', w_resign: 'durch Aufgabe', w_timeout: 'auf Zeit',
    modeAi: 'Computer', modeLocal: 'Zwei Spieler', modeOnline: 'Online', level: 'Schwierigkeit',
    lv1: 'Anfänger', lv2: 'Locker', lv3: 'Verein', lv4: 'Stark', lv5: 'Meister', side: 'Spiele als', random: 'Zufall',
    timeCtl: 'Bedenkzeit', unlimited: 'Unbegrenzt',
    createRoom: 'Raum erstellen', joinRoom: 'Mit Code beitreten', roomCode: 'Raumcode', join: 'Beitreten', invite: 'Freund einladen',
    inviteHelp: 'QR-Code scannen oder Link teilen. Das Spiel startet, sobald dein Freund beitritt.',
    copyLink: 'Link kopieren', linkCopied: 'Link kopiert', roomNotFound: 'Raum nicht gefunden', connLost: 'Verbindung verloren, neuer Versuch…',
    drawOffered: 'Dein Gegner bietet Remis an', drawSent: 'Remisangebot gesendet', accept: 'Annehmen', decline: 'Ablehnen',
    rematch: 'Revanche', review: 'Ansehen', roomFull: 'Raum voll, du schaust zu', drawConfirm: 'Remis vereinbaren?',
    connectTitle: 'Auf anderem Gerät spielen',
    connectHelp: 'Öffne diese Adresse auf einem Gerät im selben Netzwerk oder scanne den QR-Code.',
    localOnly: 'Server läuft nur lokal (--local), andere Geräte können sich nicht verbinden.',
    setBoard: 'Brett', setPieces: 'Figuren', setSound: 'Ton', setVolume: 'Lautstärke', setBg: 'Darstellung',
    bgAuto: 'Auto', bgDark: 'Dunkel', bgLight: 'Hell', setAnim: 'Animationen', aOff: 'Aus', aFast: 'Schnell', aNormal: 'Normal', aSlow: 'Langsam',
    setLang: 'Sprache', langAuto: 'Automatisch (Gerät)', coords: 'Koordinaten', legalMoves: 'Mögliche Züge zeigen',
    highlights: 'Letzten Zug markieren', autoQueen: 'Immer Dame', vibration: 'Vibration', test: 'Test',
    promoteTo: 'Umwandeln in', confirmResign: 'Partie aufgeben?', yourTurn: 'Du bist dran',
  },
  fr: {
    appName: 'Échecs', newGame: 'Nouvelle partie', settings: 'Réglages', connect: 'Jouer sur un autre appareil', undo: 'Annuler', hint: 'Indice',
    flip: "Retourner l'échiquier", resign: 'Abandonner', draw: 'Nulle', pgn: 'Copier le PGN', copied: 'Copié !', fullscreen: 'Plein écran',
    close: 'Fermer', cancel: 'Annuler', start: 'Commencer', yes: 'Oui', no: 'Non', ok: 'OK',
    white: 'Blancs', black: 'Noirs', you: 'Vous', computer: 'Ordinateur', opponent: 'Adversaire', spectator: 'Vous observez',
    waitingOpp: "En attente de l'adversaire…", oppLeft: 'Adversaire déconnecté',
    toMove: 'Aux {c} de jouer', check: 'Échec !', thinking: "L'ordinateur réfléchit…",
    youWon: 'Vous avez gagné !', youLost: 'Vous avez perdu', drawn: 'Partie nulle', whiteWins: 'Les Blancs gagnent', blackWins: 'Les Noirs gagnent',
    w_checkmate: 'par échec et mat', w_stalemate: 'pat', w_insufficient: 'matériel insuffisant', w_fifty: 'règle des 50 coups',
    w_repetition: 'triple répétition', w_agreement: 'par accord', w_resign: 'par abandon', w_timeout: 'au temps',
    modeAi: 'Ordinateur', modeLocal: 'Deux joueurs', modeOnline: 'En ligne', level: 'Difficulté',
    lv1: 'Débutant', lv2: 'Détendu', lv3: 'Club', lv4: 'Fort', lv5: 'Maître', side: 'Jouer les', random: 'Aléatoire',
    timeCtl: 'Cadence', unlimited: 'Illimité',
    createRoom: 'Créer un salon', joinRoom: 'Rejoindre avec un code', roomCode: 'Code du salon', join: 'Rejoindre', invite: 'Inviter un ami',
    inviteHelp: "Scannez le QR code ou partagez le lien. La partie commence dès que votre ami rejoint.",
    copyLink: 'Copier le lien', linkCopied: 'Lien copié', roomNotFound: 'Salon introuvable', connLost: 'Connexion perdue, nouvelle tentative…',
    drawOffered: 'Votre adversaire propose nulle', drawSent: 'Proposition envoyée', accept: 'Accepter', decline: 'Refuser',
    rematch: 'Revanche', review: 'Revoir', roomFull: 'Salon complet, vous observez', drawConfirm: 'Accepter la nulle ?',
    connectTitle: 'Jouer sur un autre appareil',
    connectHelp: 'Ouvrez cette adresse sur un appareil du même réseau ou scannez le QR code.',
    localOnly: 'Le serveur est en mode local (--local), les autres appareils ne peuvent pas se connecter.',
    setBoard: 'Échiquier', setPieces: 'Pièces', setSound: 'Son', setVolume: 'Volume', setBg: 'Apparence',
    bgAuto: 'Auto', bgDark: 'Sombre', bgLight: 'Clair', setAnim: 'Animations', aOff: 'Non', aFast: 'Rapide', aNormal: 'Normal', aSlow: 'Lent',
    setLang: 'Langue', langAuto: "Automatique (appareil)", coords: 'Coordonnées', legalMoves: 'Afficher les coups légaux',
    highlights: 'Surligner le dernier coup', autoQueen: 'Toujours en dame', vibration: 'Vibration', test: 'Tester',
    promoteTo: 'Promouvoir en', confirmResign: 'Abandonner la partie ?', yourTurn: 'À vous de jouer',
  },
  es: {
    appName: 'Ajedrez', newGame: 'Nueva partida', settings: 'Ajustes', connect: 'Jugar en otro dispositivo', undo: 'Deshacer', hint: 'Pista',
    flip: 'Girar tablero', resign: 'Rendirse', draw: 'Tablas', pgn: 'Copiar PGN', copied: '¡Copiado!', fullscreen: 'Pantalla completa',
    close: 'Cerrar', cancel: 'Cancelar', start: 'Empezar', yes: 'Sí', no: 'No', ok: 'Aceptar',
    white: 'Blancas', black: 'Negras', you: 'Tú', computer: 'Ordenador', opponent: 'Rival', spectator: 'Observando',
    waitingOpp: 'Esperando al rival…', oppLeft: 'Rival desconectado',
    toMove: 'Juegan {c}', check: '¡Jaque!', thinking: 'El ordenador piensa…',
    youWon: '¡Ganaste!', youLost: 'Perdiste', drawn: 'Tablas', whiteWins: 'Ganan las blancas', blackWins: 'Ganan las negras',
    w_checkmate: 'por jaque mate', w_stalemate: 'ahogado', w_insufficient: 'material insuficiente', w_fifty: 'regla de 50 jugadas',
    w_repetition: 'triple repetición', w_agreement: 'por acuerdo', w_resign: 'por abandono', w_timeout: 'por tiempo',
    modeAi: 'Ordenador', modeLocal: 'Dos jugadores', modeOnline: 'En línea', level: 'Dificultad',
    lv1: 'Principiante', lv2: 'Casual', lv3: 'Club', lv4: 'Fuerte', lv5: 'Maestro', side: 'Jugar con', random: 'Aleatorio',
    timeCtl: 'Tiempo', unlimited: 'Sin límite',
    createRoom: 'Crear sala', joinRoom: 'Unirse con código', roomCode: 'Código de sala', join: 'Unirse', invite: 'Invitar a un amigo',
    inviteHelp: 'Escanea el código QR o comparte el enlace. La partida empieza cuando tu amigo se una.',
    copyLink: 'Copiar enlace', linkCopied: 'Enlace copiado', roomNotFound: 'Sala no encontrada', connLost: 'Conexión perdida, reintentando…',
    drawOffered: 'Tu rival ofrece tablas', drawSent: 'Oferta de tablas enviada', accept: 'Aceptar', decline: 'Rechazar',
    rematch: 'Revancha', review: 'Revisar', roomFull: 'Sala llena, estás observando', drawConfirm: '¿Aceptar tablas?',
    connectTitle: 'Jugar en otro dispositivo',
    connectHelp: 'Abre esta dirección en un dispositivo de la misma red o escanea el código QR.',
    localOnly: 'El servidor está en modo local (--local), otros dispositivos no pueden conectarse.',
    setBoard: 'Tablero', setPieces: 'Piezas', setSound: 'Sonido', setVolume: 'Volumen', setBg: 'Apariencia',
    bgAuto: 'Auto', bgDark: 'Oscuro', bgLight: 'Claro', setAnim: 'Animaciones', aOff: 'No', aFast: 'Rápido', aNormal: 'Normal', aSlow: 'Lento',
    setLang: 'Idioma', langAuto: 'Automático (dispositivo)', coords: 'Coordenadas', legalMoves: 'Mostrar jugadas legales',
    highlights: 'Resaltar última jugada', autoQueen: 'Coronar siempre dama', vibration: 'Vibración', test: 'Probar',
    promoteTo: 'Coronar a', confirmResign: '¿Rendirte en esta partida?', yourTurn: 'Tu turno',
  },
  ru: {
    appName: 'Шахматы', newGame: 'Новая игра', settings: 'Настройки', connect: 'Играть на другом устройстве', undo: 'Отмена', hint: 'Подсказка',
    flip: 'Повернуть доску', resign: 'Сдаться', draw: 'Ничья', pgn: 'Копировать PGN', copied: 'Скопировано!', fullscreen: 'Во весь экран',
    close: 'Закрыть', cancel: 'Отмена', start: 'Начать', yes: 'Да', no: 'Нет', ok: 'ОК',
    white: 'Белые', black: 'Чёрные', you: 'Вы', computer: 'Компьютер', opponent: 'Соперник', spectator: 'Вы наблюдаете',
    waitingOpp: 'Ждём соперника…', oppLeft: 'Соперник отключился',
    toMove: 'Ход: {c}', check: 'Шах!', thinking: 'Компьютер думает…',
    youWon: 'Вы победили!', youLost: 'Вы проиграли', drawn: 'Ничья', whiteWins: 'Победа белых', blackWins: 'Победа чёрных',
    w_checkmate: 'мат', w_stalemate: 'пат', w_insufficient: 'недостаточно материала', w_fifty: 'правило 50 ходов',
    w_repetition: 'троекратное повторение', w_agreement: 'по соглашению', w_resign: 'сдача', w_timeout: 'по времени',
    modeAi: 'Компьютер', modeLocal: 'Вдвоём', modeOnline: 'Онлайн', level: 'Сложность',
    lv1: 'Новичок', lv2: 'Лёгкий', lv3: 'Клубный', lv4: 'Сильный', lv5: 'Мастер', side: 'Играть за', random: 'Случайно',
    timeCtl: 'Контроль времени', unlimited: 'Без ограничения',
    createRoom: 'Создать комнату', joinRoom: 'Войти по коду', roomCode: 'Код комнаты', join: 'Войти', invite: 'Пригласить друга',
    inviteHelp: 'Отсканируйте QR-код или поделитесь ссылкой. Игра начнётся, когда друг присоединится.',
    copyLink: 'Копировать ссылку', linkCopied: 'Ссылка скопирована', roomNotFound: 'Комната не найдена', connLost: 'Связь потеряна, переподключение…',
    drawOffered: 'Соперник предлагает ничью', drawSent: 'Предложение ничьей отправлено', accept: 'Принять', decline: 'Отклонить',
    rematch: 'Реванш', review: 'Разбор', roomFull: 'Комната занята, вы наблюдаете', drawConfirm: 'Согласиться на ничью?',
    connectTitle: 'Играть на другом устройстве',
    connectHelp: 'Откройте этот адрес на устройстве в той же сети или отсканируйте QR-код.',
    localOnly: 'Сервер работает только локально (--local), другие устройства не подключатся.',
    setBoard: 'Доска', setPieces: 'Фигуры', setSound: 'Звук', setVolume: 'Громкость', setBg: 'Оформление',
    bgAuto: 'Авто', bgDark: 'Тёмное', bgLight: 'Светлое', setAnim: 'Анимации', aOff: 'Выкл', aFast: 'Быстро', aNormal: 'Обычно', aSlow: 'Медленно',
    setLang: 'Язык', langAuto: 'Автоматически (устройство)', coords: 'Координаты', legalMoves: 'Показывать ходы',
    highlights: 'Подсвечивать последний ход', autoQueen: 'Всегда в ферзя', vibration: 'Вибрация', test: 'Проверить',
    promoteTo: 'Превратить в', confirmResign: 'Сдаться?', yourTurn: 'Ваш ход',
  },
  ar: {
    appName: 'شطرنج', newGame: 'لعبة جديدة', settings: 'الإعدادات', connect: 'العب على جهاز آخر', undo: 'تراجع', hint: 'تلميح',
    flip: 'اقلب الرقعة', resign: 'استسلام', draw: 'تعادل', pgn: 'نسخ PGN', copied: 'تم النسخ!', fullscreen: 'ملء الشاشة',
    close: 'إغلاق', cancel: 'إلغاء', start: 'ابدأ', yes: 'نعم', no: 'لا', ok: 'حسنًا',
    white: 'الأبيض', black: 'الأسود', you: 'أنت', computer: 'الحاسوب', opponent: 'الخصم', spectator: 'أنت تشاهد',
    waitingOpp: 'بانتظار الخصم…', oppLeft: 'انقطع اتصال الخصم',
    toMove: 'الدور على {c}', check: 'كش!', thinking: 'الحاسوب يفكر…',
    youWon: 'لقد فزت!', youLost: 'لقد خسرت', drawn: 'تعادل', whiteWins: 'فاز الأبيض', blackWins: 'فاز الأسود',
    w_checkmate: 'كش مات', w_stalemate: 'تعادل بالجمود', w_insufficient: 'مواد غير كافية', w_fifty: 'قاعدة 50 نقلة',
    w_repetition: 'تكرار ثلاث مرات', w_agreement: 'بالاتفاق', w_resign: 'بالاستسلام', w_timeout: 'انتهى الوقت',
    modeAi: 'الحاسوب', modeLocal: 'لاعبان', modeOnline: 'عبر الشبكة', level: 'الصعوبة',
    lv1: 'مبتدئ', lv2: 'مريح', lv3: 'نادي', lv4: 'قوي', lv5: 'أستاذ', side: 'العب بـ', random: 'عشوائي',
    timeCtl: 'الوقت', unlimited: 'بلا حد',
    createRoom: 'إنشاء غرفة', joinRoom: 'انضم بالرمز', roomCode: 'رمز الغرفة', join: 'انضم', invite: 'ادعُ صديقًا',
    inviteHelp: 'امسح رمز QR أو شارك الرابط. تبدأ اللعبة فور انضمام صديقك.',
    copyLink: 'نسخ الرابط', linkCopied: 'تم نسخ الرابط', roomNotFound: 'الغرفة غير موجودة', connLost: 'انقطع الاتصال، جارٍ إعادة المحاولة…',
    drawOffered: 'خصمك يعرض التعادل', drawSent: 'تم إرسال عرض التعادل', accept: 'قبول', decline: 'رفض',
    rematch: 'إعادة المباراة', review: 'مراجعة', roomFull: 'الغرفة ممتلئة، أنت مشاهد', drawConfirm: 'الموافقة على التعادل؟',
    connectTitle: 'العب على جهاز آخر',
    connectHelp: 'افتح هذا العنوان على جهاز في الشبكة نفسها أو امسح رمز QR.',
    localOnly: 'الخادم يعمل محليًا فقط (--local) ولا يمكن للأجهزة الأخرى الاتصال.',
    setBoard: 'الرقعة', setPieces: 'القطع', setSound: 'الصوت', setVolume: 'مستوى الصوت', setBg: 'المظهر',
    bgAuto: 'تلقائي', bgDark: 'داكن', bgLight: 'فاتح', setAnim: 'الحركات', aOff: 'إيقاف', aFast: 'سريع', aNormal: 'عادي', aSlow: 'بطيء',
    setLang: 'اللغة', langAuto: 'تلقائي (لغة الجهاز)', coords: 'الإحداثيات', legalMoves: 'إظهار النقلات المتاحة',
    highlights: 'تمييز آخر نقلة', autoQueen: 'الترقية إلى وزير دائمًا', vibration: 'الاهتزاز', test: 'تجربة',
    promoteTo: 'رقِّ إلى', confirmResign: 'هل تريد الاستسلام؟', yourTurn: 'دورك',
  },
  zh: {
    appName: '国际象棋', newGame: '新游戏', settings: '设置', connect: '在其他设备上玩', undo: '悔棋', hint: '提示',
    flip: '翻转棋盘', resign: '认输', draw: '和棋', pgn: '复制 PGN', copied: '已复制！', fullscreen: '全屏',
    close: '关闭', cancel: '取消', start: '开始', yes: '是', no: '否', ok: '确定',
    white: '白方', black: '黑方', you: '你', computer: '电脑', opponent: '对手', spectator: '观战中',
    waitingOpp: '等待对手加入…', oppLeft: '对手已断开',
    toMove: '轮到{c}', check: '将军！', thinking: '电脑思考中…',
    youWon: '你赢了！', youLost: '你输了', drawn: '和棋', whiteWins: '白方获胜', blackWins: '黑方获胜',
    w_checkmate: '将死', w_stalemate: '逼和', w_insufficient: '子力不足', w_fifty: '50 步规则',
    w_repetition: '三次重复', w_agreement: '协议和棋', w_resign: '认输', w_timeout: '超时',
    modeAi: '电脑', modeLocal: '双人', modeOnline: '在线', level: '难度',
    lv1: '入门', lv2: '轻松', lv3: '俱乐部', lv4: '强', lv5: '大师', side: '执', random: '随机',
    timeCtl: '用时', unlimited: '不限时',
    createRoom: '创建房间', joinRoom: '输入代码加入', roomCode: '房间代码', join: '加入', invite: '邀请好友',
    inviteHelp: '扫描二维码或分享链接，好友加入后立即开始。',
    copyLink: '复制链接', linkCopied: '链接已复制', roomNotFound: '房间不存在', connLost: '连接中断，正在重连…',
    drawOffered: '对手提议和棋', drawSent: '已发送和棋提议', accept: '接受', decline: '拒绝',
    rematch: '再来一局', review: '复盘', roomFull: '房间已满，你正在观战', drawConfirm: '同意和棋？',
    connectTitle: '在其他设备上玩',
    connectHelp: '在同一网络的手机或电脑上打开此地址，或扫描二维码。',
    localOnly: '服务器仅限本机访问（--local），其他设备无法连接。',
    setBoard: '棋盘', setPieces: '棋子', setSound: '音效', setVolume: '音量', setBg: '外观',
    bgAuto: '自动', bgDark: '深色', bgLight: '浅色', setAnim: '动画', aOff: '关', aFast: '快', aNormal: '正常', aSlow: '慢',
    setLang: '语言', langAuto: '自动（设备语言）', coords: '坐标', legalMoves: '显示可走位置',
    highlights: '高亮上一步', autoQueen: '总是升后', vibration: '振动', test: '试听',
    promoteTo: '升变为', confirmResign: '确定认输吗？', yourTurn: '轮到你',
  },
};
"""
ICON_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6b566"/><stop offset="1" stop-color="#a86a1c"/></linearGradient></defs><rect width="512" height="512" rx="112" fill="#0b1020"/><rect x="40" y="40" width="432" height="432" rx="84" fill="url(#g)"/><g fill="#1b1206"><circle cx="256" cy="150" r="52"/><path d="M200 230h112l30 110H170z"/><rect x="150" y="350" width="212" height="40" rx="14"/><rect x="120" y="396" width="272" height="34" rx="14"/></g></svg>"""
MANIFEST = r"""{"name":"Satranç Pro","short_name":"Satranç","start_url":"/","display":"standalone","background_color":"#0b1020","theme_color":"#0b1020","icons":[{"src":"/icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any"}]}"""

# =====================================================================
#  SATRANÇ MOTORU (sunucu tarafı doğrulama)  büyük harf = Beyaz
#  Kareler: 0 = a8 ... 63 = h1
# =====================================================================
FILES = "abcdefgh"
KN = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
KG = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
DIAG = [(-1,-1),(-1,1),(1,-1),(1,1)]
ORTH = [(-1,0),(1,0),(0,-1),(0,1)]

def color_of(p):
    if p == '.': return None
    return 'w' if p.isupper() else 'b'

def other(c): return 'b' if c == 'w' else 'w'
def sq_name(i): return FILES[i % 8] + str(8 - i // 8)

class State:
    __slots__ = ('board','turn','castling','ep','half','full')
    def __init__(self, board, turn, castling, ep, half, full):
        self.board = board; self.turn = turn; self.castling = castling
        self.ep = ep; self.half = half; self.full = full

def start_state():
    b = list("rnbqkbnr" + "pppppppp" + "." * 32 + "PPPPPPPP" + "RNBQKBNR")
    return State(b, 'w', "KQkq", None, 0, 1)

def attacked(b, sq, by):
    r, c = divmod(sq, 8)
    pr = r + 1 if by == 'w' else r - 1
    pawn = 'P' if by == 'w' else 'p'
    if 0 <= pr < 8:
        if c > 0 and b[pr*8 + c - 1] == pawn: return True
        if c < 7 and b[pr*8 + c + 1] == pawn: return True
    kn = 'N' if by == 'w' else 'n'
    for dr, dc in KN:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and b[nr*8 + nc] == kn: return True
    kg = 'K' if by == 'w' else 'k'
    for dr, dc in KG:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and b[nr*8 + nc] == kg: return True
    for dirs, pcs in ((DIAG, 'bq'), (ORTH, 'rq')):
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = b[nr*8 + nc]
                if p != '.':
                    if color_of(p) == by and p.lower() in pcs: return True
                    break
                nr += dr; nc += dc
    return False

def in_check(b, color):
    return attacked(b, b.index('K' if color == 'w' else 'k'), other(color))

def gen_moves(st):
    b = st.board; t = st.turn; res = []
    for i, p in enumerate(b):
        if p == '.' or color_of(p) != t: continue
        r, c = divmod(i, 8); k = p.upper()
        if k == 'P':
            d = -1 if t == 'w' else 1
            start = 6 if t == 'w' else 1
            last = 0 if t == 'w' else 7
            nr = r + d
            if not (0 <= nr < 8): continue
            def add(to):
                if nr == last:
                    for pr in 'qrbn': res.append((i, to, pr))
                else:
                    res.append((i, to, ''))
            to = nr*8 + c
            if b[to] == '.':
                add(to)
                if r == start and b[to + d*8] == '.':
                    res.append((i, to + d*8, ''))
            for dc in (-1, 1):
                nc = c + dc
                if 0 <= nc < 8:
                    to = nr*8 + nc
                    if (b[to] != '.' and color_of(b[to]) != t) or to == st.ep:
                        add(to)
        elif k == 'N' or k == 'K':
            for dr, dc in (KN if k == 'N' else KG):
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    to = nr*8 + nc
                    if color_of(b[to]) != t: res.append((i, to, ''))
            if k == 'K':
                base = 56 if t == 'w' else 0
                if i == base + 4:
                    opp = other(t)
                    if not attacked(b, i, opp):
                        rook = 'R' if t == 'w' else 'r'
                        ks = 'K' if t == 'w' else 'k'
                        qs = 'Q' if t == 'w' else 'q'
                        if (ks in st.castling and b[base+7] == rook and b[base+5] == '.'
                                and b[base+6] == '.' and not attacked(b, base+5, opp)
                                and not attacked(b, base+6, opp)):
                            res.append((i, base+6, ''))
                        if (qs in st.castling and b[base] == rook and b[base+1] == '.'
                                and b[base+2] == '.' and b[base+3] == '.'
                                and not attacked(b, base+3, opp)
                                and not attacked(b, base+2, opp)):
                            res.append((i, base+2, ''))
        else:
            dirs = (DIAG if k == 'B' else ORTH if k == 'R' else DIAG + ORTH)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    to = nr*8 + nc
                    q = b[to]
                    if q == '.':
                        res.append((i, to, ''))
                    else:
                        if color_of(q) != t: res.append((i, to, ''))
                        break
                    nr += dr; nc += dc
    return res

RIGHTS = {60:'KQ', 63:'K', 56:'Q', 4:'kq', 7:'k', 0:'q'}

def apply_move(st, m):
    f, t, pr = m
    b = st.board[:]
    p = b[f]; k = p.upper(); cap = b[t] != '.'
    half = 0 if (k == 'P' or cap) else st.half + 1
    ep = None
    if k == 'P':
        if t == st.ep and not cap and f % 8 != t % 8:
            b[t + (8 if st.turn == 'w' else -8)] = '.'
        if abs(t - f) == 16: ep = (f + t) // 2
        if pr: p = pr.upper() if st.turn == 'w' else pr.lower()
    if k == 'K' and abs(t - f) == 2:
        if t > f: b[f+1] = b[f+3]; b[f+3] = '.'
        else:     b[f-1] = b[f-4]; b[f-4] = '.'
    b[t] = p; b[f] = '.'
    cast = st.castling
    for sq in (f, t):
        for ch in RIGHTS.get(sq, ''): cast = cast.replace(ch, '')
    full = st.full + (1 if st.turn == 'b' else 0)
    return State(b, other(st.turn), cast, ep, half, full)

def legal_moves(st):
    res = []
    for m in gen_moves(st):
        ns = apply_move(st, m)
        if not in_check(ns.board, st.turn): res.append(m)
    return res

def insufficient(b):
    pcs = [(i, p) for i, p in enumerate(b) if p != '.' and p.lower() != 'k']
    if not pcs: return True
    if any(p.lower() in 'pqr' for _, p in pcs): return False
    if len(pcs) == 1: return True
    if all(p.lower() == 'b' for _, p in pcs):
        return len({(i // 8 + i % 8) % 2 for i, _ in pcs}) == 1
    return False

def pos_key(st):
    ep = None
    if st.ep is not None and any(m[1] == st.ep and st.board[m[0]].upper() == 'P' for m in gen_moves(st)):
        ep = st.ep
    return (''.join(st.board), st.turn, st.castling, ep)

def uci_of(m): return sq_name(m[0]) + sq_name(m[1]) + m[2]

def find_move(st, u):
    if not isinstance(u, str) or not re.fullmatch(r'[a-h][1-8][a-h][1-8][qrbn]?', u): return None
    for m in legal_moves(st):
        if uci_of(m) == u: return m
    return None

def san(st, m, legal):
    f, t, pr = m; p = st.board[f]; k = p.upper()
    if k == 'K' and abs(t - f) == 2:
        s = 'O-O' if t > f else 'O-O-O'
    else:
        cap = st.board[t] != '.' or (k == 'P' and f % 8 != t % 8)
        s = ''
        if k == 'P':
            if cap: s += FILES[f % 8]
        else:
            s += k
            others = [x for x in legal if x[1] == t and st.board[x[0]] == p and x[0] != f]
            if others:
                if all(o[0] % 8 != f % 8 for o in others): s += FILES[f % 8]
                elif all(o[0] // 8 != f // 8 for o in others): s += str(8 - f // 8)
                else: s += FILES[f % 8] + str(8 - f // 8)
        if cap: s += 'x'
        s += sq_name(t)
        if pr: s += '=' + pr.upper()
    ns = apply_move(st, m)
    if in_check(ns.board, ns.turn):
        s += '#' if not legal_moves(ns) else '+'
    return s

# =====================================================================
#  QR KOD ÜRETİCİ (bayt kipi, hata düzeltme M, sürüm 1-10)  Nayuki algoritması
# =====================================================================
_ECC = (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26)
_BLK = (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5)

def _raw_modules(v):
    r = (16 * v + 128) * v + 64
    if v >= 2:
        n = v // 7 + 2
        r -= (25 * n - 10) * n - 55
        if v >= 7: r -= 36
    return r

def _data_cw(v): return _raw_modules(v) // 8 - _ECC[v] * _BLK[v]

def _gf_mul(x, y):
    z = 0
    for i in range(7, -1, -1):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z

def _rs_div(deg):
    res = [0] * (deg - 1) + [1]; root = 1
    for _ in range(deg):
        for j in range(deg):
            res[j] = _gf_mul(res[j], root)
            if j + 1 < deg: res[j] ^= res[j + 1]
        root = _gf_mul(root, 2)
    return res

def _rs_rem(data, div):
    res = [0] * len(div)
    for b in data:
        f = b ^ res.pop(0); res.append(0)
        for i, c in enumerate(div): res[i] ^= _gf_mul(c, f)
    return res

def qr_matrix(text):
    data = text.encode('utf-8')
    ver = next((v for v in range(1, 11) if len(data) * 8 + 4 + (8 if v < 10 else 16) <= _data_cw(v) * 8), None)
    if ver is None: raise ValueError("too long")
    bits = []
    def put(val, n): bits.extend((val >> i) & 1 for i in range(n - 1, -1, -1))
    put(4, 4); put(len(data), 8 if ver < 10 else 16)
    for b in data: put(b, 8)
    cap = _data_cw(ver) * 8
    put(0, min(4, cap - len(bits)))
    put(0, -len(bits) % 8)
    pad = 0xEC
    while len(bits) < cap: put(pad, 8); pad ^= 0xEC ^ 0x11
    cw = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    nb, el, raw = _BLK[ver], _ECC[ver], _raw_modules(ver) // 8
    ns, sl = nb - raw % nb, raw // nb
    div = _rs_div(el); blocks = []; k = 0
    for i in range(nb):
        dl = sl - el + (0 if i < ns else 1)
        dat = cw[k:k + dl]; k += dl
        ecc = _rs_rem(dat, div)
        if i < ns: dat = dat + [0]
        blocks.append(dat + ecc)
    inter = []
    for i in range(len(blocks[0])):
        for j, blk in enumerate(blocks):
            if i != sl - el or j >= ns: inter.append(blk[i])
    size = ver * 4 + 17
    mod = [[False] * size for _ in range(size)]
    fn = [[False] * size for _ in range(size)]
    def setf(x, y, d):
        mod[y][x] = d; fn[y][x] = True
    for i in range(size):
        setf(6, i, i % 2 == 0); setf(i, 6, i % 2 == 0)
    for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size: setf(x, y, max(abs(dx), abs(dy)) not in (2, 4))
    if ver > 1:
        n = ver // 7 + 2
        step = (ver * 4 + n * 2 + 1) // (n * 2 - 2) * 2
        pos = list(reversed([size - 7 - i * step for i in range(n - 1)] + [6]))
        for i, cy in enumerate(pos):
            for j, cx in enumerate(pos):
                if (i == 0 and j == 0) or (i == 0 and j == n - 1) or (i == n - 1 and j == 0): continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3): setf(cx + dx, cy + dy, max(abs(dx), abs(dy)) != 1)
    def fmt_bits(mask):
        d = (0 << 3) | mask  # M = 00
        rem = d
        for _ in range(10): rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bs = ((d << 10) | rem) ^ 0x5412
        g = lambda i: (bs >> i) & 1
        for i in range(6): setf(8, i, g(i) == 1)
        setf(8, 7, g(6) == 1); setf(8, 8, g(7) == 1); setf(7, 8, g(8) == 1)
        for i in range(9, 15): setf(14 - i, 8, g(i) == 1)
        for i in range(8): setf(size - 1 - i, 8, g(i) == 1)
        for i in range(8, 15): setf(8, size - 15 + i, g(i) == 1)
        setf(8, size - 8, True)
    fmt_bits(0)
    if ver >= 7:
        rem = ver
        for _ in range(12): rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        bs = (ver << 12) | rem
        for i in range(18):
            a, b = size - 11 + i % 3, i // 3
            setf(a, b, ((bs >> i) & 1) == 1); setf(b, a, ((bs >> i) & 1) == 1)
    i = 0
    for right in range(size - 1, 0, -2):
        if right == 6: right = 5
        for vert in range(size):
            for j in range(2):
                x = right - j
                y = size - 1 - vert if ((right + 1) & 2) == 0 else vert
                if not fn[y][x] and i < len(inter) * 8:
                    mod[y][x] = ((inter[i >> 3] >> (7 - (i & 7))) & 1) == 1; i += 1
    def mask_fn(m, x, y):
        return [(x + y) % 2 == 0, y % 2 == 0, x % 3 == 0, (x + y) % 3 == 0, (x // 3 + y // 2) % 2 == 0,
                x * y % 2 + x * y % 3 == 0, (x * y % 2 + x * y % 3) % 2 == 0, ((x + y) % 2 + x * y % 3) % 2 == 0][m]
    def apply_mask(m):
        for y in range(size):
            for x in range(size):
                if not fn[y][x] and mask_fn(m, x, y): mod[y][x] = not mod[y][x]
    def penalty():
        res = 0
        lines = [[mod[y][x] for x in range(size)] for y in range(size)] + [[mod[y][x] for y in range(size)] for x in range(size)]
        for ln in lines:
            run = 1
            for k in range(1, size + 1):
                if k < size and ln[k] == ln[k - 1]: run += 1
                else:
                    if run >= 5: res += 3 + run - 5
                    run = 1
            s = ''.join('1' if v else '0' for v in ln)
            for pat in ('10111010000', '00001011101'):
                p = s.find(pat)
                while p >= 0: res += 40; p = s.find(pat, p + 1)
        for y in range(size - 1):
            for x in range(size - 1):
                if mod[y][x] == mod[y][x + 1] == mod[y + 1][x] == mod[y + 1][x + 1]: res += 3
        dark = sum(v for row in mod for v in row); tot = size * size
        return res + ((abs(dark * 20 - tot * 10) + tot - 1) // tot - 1) * 10
    best, bp = 0, None
    for m in range(8):
        apply_mask(m); fmt_bits(m)
        p = penalty()
        if bp is None or p < bp: best, bp = m, p
        apply_mask(m)
    apply_mask(best); fmt_bits(best)
    return mod

def qr_svg(text):
    m = qr_matrix(text); n = len(m); q = 3
    d = ''.join('M%d,%dh1v1h-1z' % (x + q, y + q) for y in range(n) for x in range(n) if m[y][x])
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" shape-rendering="crispEdges">'
            '<rect width="100%%" height="100%%" fill="#fff"/><path d="%s" fill="#000"/></svg>') % (n + 2 * q, n + 2 * q, d)

def qr_terminal(text):
    m = qr_matrix(text); n = len(m); q = 2
    g = lambda x, y: 0 <= x < n and 0 <= y < n and m[y][x]
    out = []
    for y in range(-q, n + q, 2):
        row = ''.join(('█' if g(x, y) and g(x, y + 1) else '▀' if g(x, y) else '▄' if g(x, y + 1) else ' ') for x in range(-q, n + q))
        out.append('\x1b[47;30m' + row + '\x1b[0m')
    return '\n'.join(out)

# =====================================================================
#  ODALAR (sunucu hamleleri doğrular, istemciye güvenilmez)
# =====================================================================
ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
ROOMS = {}; ROOMS_LOCK = threading.Lock()
MAX_ROOMS = 150

class Room:
    def __init__(self, code, tc='0'):
        self.code = code; self.tc = tc or '0'; self.lock = threading.RLock()
        self.seats = {'w': None, 'b': None}; self.listeners = []
        self.created = self.touched = time.time(); self.game = 0
        self.reset()
    def reset(self):
        self.game += 1; self.st = start_state(); self.moves = []; self.keys = [pos_key(self.st)]
        self.result = None; self.reason = None; self.draw = None; self.rematch = set()
    def seat_of(self, token):
        if isinstance(token, str) and token:
            for c in 'wb':
                if self.seats[c] and hmac.compare_digest(self.seats[c], token): return c
        return 's'
    def present(self):
        return {c: any(self.seat_of(tk) == c for _, tk in self.listeners) for c in 'wb'}
    def snapshot(self, seat):
        return {'code': self.code, 'you': seat, 'game': self.game, 'moves': self.moves, 'turn': self.st.turn, 'tc': self.tc,
                'over': self.result is not None, 'result': self.result, 'reason': self.reason, 'draw': self.draw,
                'seated': {c: self.seats[c] is not None for c in 'wb'}, 'present': self.present(), 'rematch': sorted(self.rematch)}
    def push(self, q, seat):
        data = ('data: ' + json.dumps(self.snapshot(seat), separators=(',', ':')) + '\n\n').encode()
        try: q.put_nowait(data)
        except queue.Full: pass
    def broadcast(self):
        self.touched = time.time()
        for q, tk in list(self.listeners): self.push(q, self.seat_of(tk))
    def listen(self, token):
        with self.lock:
            q = queue.Queue(maxsize=64)
            self.listeners.append((q, token)); self.broadcast(); return q
    def unlisten(self, q):
        with self.lock:
            self.listeners = [x for x in self.listeners if x[0] is not q]; self.broadcast()
    def join(self, token):
        with self.lock:
            s = self.seat_of(token)
            if s in 'wb': return s, token
            for c in 'wb':
                if self.seats[c] is None:
                    tok = secrets.token_urlsafe(18); self.seats[c] = tok; self.broadcast(); return c, tok
            return 's', None
    def finish(self, res, why): self.result, self.reason, self.draw = res, why, None
    def act(self, token, d):
        with self.lock:
            seat = self.seat_of(token); typ = d.get('type')
            if seat == 's': raise ApiError(403, 'spectator')
            if typ == 'move':
                if self.result: raise ApiError(409, 'over')
                if not (self.seats['w'] and self.seats['b']): raise ApiError(409, 'wait')
                if seat != self.st.turn: raise ApiError(409, 'turn')
                m = find_move(self.st, d.get('uci'))
                if m is None: raise ApiError(400, 'illegal')
                self.st = apply_move(self.st, m); self.moves.append(uci_of(m)); self.keys.append(pos_key(self.st)); self.draw = None
                if not legal_moves(self.st):
                    if in_check(self.st.board, self.st.turn): self.finish('1-0' if seat == 'w' else '0-1', 'checkmate')
                    else: self.finish('1/2-1/2', 'stalemate')
                elif insufficient(self.st.board): self.finish('1/2-1/2', 'insufficient')
                elif self.st.half >= 100: self.finish('1/2-1/2', 'fifty')
                elif self.keys.count(self.keys[-1]) >= 3: self.finish('1/2-1/2', 'repetition')
            elif typ == 'timeout':
                if not self.result:
                    winner = other(self.st.turn)
                    self.finish('1-0' if winner == 'w' else '0-1', 'timeout')
            elif typ == 'resign':
                if self.result: raise ApiError(409, 'over')
                self.finish('0-1' if seat == 'w' else '1-0', 'resign')
            elif typ == 'draw_offer':
                if self.result: raise ApiError(409, 'over')
                self.draw = seat
            elif typ == 'draw_accept':
                if self.result or not self.draw or self.draw == seat: raise ApiError(409, 'nodraw')
                self.finish('1/2-1/2', 'agreement')
            elif typ == 'draw_decline':
                self.draw = None
            elif typ == 'rematch':
                if not self.result: raise ApiError(409, 'notover')
                self.rematch.add(seat)
                if len(self.rematch) == 2:
                    self.seats['w'], self.seats['b'] = self.seats['b'], self.seats['w']
                    self.reset()
            else: raise ApiError(400, 'bad')
            self.broadcast()

class ApiError(Exception):
    def __init__(self, status, code): self.status, self.code = status, code

def cleanup_loop():
    while True:
        time.sleep(60); now = time.time()
        with ROOMS_LOCK:
            for code, r in list(ROOMS.items()):
                idle = now - r.touched
                if idle > 6 * 3600 or (not r.listeners and idle > 1800):
                    for q, _ in r.listeners:
                        try: q.put_nowait(None)
                        except queue.Full: pass
                    del ROOMS[code]

# =====================================================================
#  HTTP SUNUCUSU
# =====================================================================
ASSETS = {
    '/': ('text/html; charset=utf-8', INDEX_HTML),
    '/app.css': ('text/css; charset=utf-8', APP_CSS),
    '/app.js': ('application/javascript; charset=utf-8', APP_JS),
    '/engine.js': ('application/javascript; charset=utf-8', ENGINE_JS),
    '/i18n.js': ('application/javascript; charset=utf-8', I18N_JS),
    '/icon.svg': ('image/svg+xml', ICON_SVG),
    '/favicon.ico': ('image/svg+xml', ICON_SVG),
    '/manifest.webmanifest': ('application/manifest+json', MANIFEST),
}
CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self' ws: wss:; "
       "worker-src 'self' blob:; manifest-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")


import subprocess, shutil

# ---------- Cross-Platform Tespit ----------
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX   = platform.system() == 'Linux'
IS_MAC     = platform.system() == 'Darwin'
MACHINE    = platform.machine().lower()  # 'x86_64', 'amd64', 'aarch64', 'arm64'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Proje ana dizini: satranc.py 'server/' altındaysa bir üst dizin (Chess/)
if os.path.isdir(os.path.join(SCRIPT_DIR, '..', 'engines')) or os.path.isdir(os.path.join(SCRIPT_DIR, '..', 'assets')):
    APP_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
elif os.path.isdir(os.path.join(SCRIPT_DIR, 'engines')) or os.path.isdir(os.path.join(SCRIPT_DIR, 'assets')):
    APP_DIR = SCRIPT_DIR
else:
    APP_DIR = SCRIPT_DIR
    for cand in [os.getcwd(), os.path.abspath(os.path.join(os.getcwd(), '..')), os.path.expanduser('~/İndirilenler/Chess')]:
        if os.path.isdir(os.path.join(cand, 'engines')) or os.path.isdir(os.path.join(cand, 'assets')):
            APP_DIR = cand
            break

# ---------- Stockfish Binary Tespiti (Cross-Platform) ----------
def _find_stockfish():
    """Platforma uygun Stockfish binary'sini bulur."""
    candidates = []
    engines_dirs = [
        os.path.join(APP_DIR, 'engines'),
        os.path.join(APP_DIR, 'motorlar'),
        os.path.join(APP_DIR, 'stockfish-windows'),
        os.path.join(APP_DIR, 'stockfish-linux'),
        os.path.join(APP_DIR, 'stockfish'),
    ]

    if IS_WINDOWS:
        # Windows: .exe uzantılı binary'ler
        for ed in engines_dirs:
            candidates.extend([
                os.path.join(ed, 'stockfish-windows-x86-64-universal.exe'),
                os.path.join(ed, 'stockfish-windows-x86-64.exe'),
                os.path.join(ed, 'stockfish.exe'),
            ])
        w = shutil.which('stockfish.exe') or shutil.which('stockfish')
        if w: candidates.append(w)
    elif IS_LINUX:
        for ed in engines_dirs:
            if MACHINE in ('x86_64', 'amd64'):
                candidates.extend([
                    os.path.join(ed, 'stockfish-linux-x86-64-universal'),
                    os.path.join(ed, 'stockfish'),
                ])
            elif MACHINE in ('aarch64', 'arm64'):
                candidates.extend([
                    os.path.join(ed, 'stockfish-linux-aarch64'),
                    os.path.join(ed, 'stockfish'),
                ])
            else:
                candidates.append(os.path.join(ed, 'stockfish'))
        w = shutil.which('stockfish')
        if w: candidates.append(w)
    elif IS_MAC:
        for ed in engines_dirs:
            candidates.extend([
                os.path.join(ed, 'stockfish-macos-arm64'),
                os.path.join(ed, 'stockfish'),
            ])
        w = shutil.which('stockfish')
        if w: candidates.append(w)
    else:
        w = shutil.which('stockfish')
        if w: candidates.append(w)

    for p in candidates:
        if p and os.path.isfile(p):
            if IS_WINDOWS or os.access(p, os.X_OK):
                return p
    return None

SF_PATH = _find_stockfish()

class StockfishEngine:
    """Stockfish motor yöneticisi — timeout korumalı, drain mekanizmalı, isready handshake'li."""
    QUERY_TIMEOUT = 12      # Tek hamle sorgusu için max süre (sn)
    ANALYSIS_TIMEOUT = 12    # Analiz modunda hamle başı max süre (sn)

    def __init__(self, binary):
        self.binary = binary
        self.lock = threading.Lock()
        self.proc = None
        self.q = queue.Queue()
        self.reader_thread = None
        self.start()

    def _reader(self):
        try:
            p = self.proc
            if p and p.stdout:
                for line in iter(p.stdout.readline, ''):
                    self.q.put(line)
        except Exception:
            pass

    def _drain(self):
        while not self.q.empty():
            try: self.q.get_nowait()
            except queue.Empty: break

    def start(self):
        if not self.binary: return
        self._kill_proc()
        try:
            self._drain()
            popen_kwargs = dict(
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )
            # Windows'ta konsol penceresi açılmasını engelle
            if IS_WINDOWS:
                popen_kwargs['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            self.proc = subprocess.Popen([self.binary], **popen_kwargs)
            self.reader_thread = threading.Thread(target=self._reader, daemon=True)
            self.reader_thread.start()
            self._send('uci')
            self._read_until('uciok', timeout=10)
            threads = max(1, os.cpu_count() or 1)
            self._send(f'setoption name Threads value {threads}')
            self._send('setoption name Hash value 256')
            self._sync()
        except Exception:
            self._kill_proc()

    def _kill_proc(self):
        if self.proc:
            try: self.proc.kill()
            except Exception: pass
            try: self.proc.wait(timeout=2)
            except Exception: pass
            self.proc = None
        self._drain()

    def _send(self, cmd):
        if self.proc and self.proc.stdin:
            try:
                self.proc.stdin.write(cmd + '\n')
                self.proc.stdin.flush()
            except (BrokenPipeError, OSError):
                self._kill_proc()

    def _readline(self, timeout=10):
        """Kuyruktan güvenli satır okuma — tamponlama ve select takılmalarını kökten önler."""
        try:
            return self.q.get(timeout=max(0.01, timeout))
        except queue.Empty:
            return ''

    def _read_until(self, marker, timeout=10):
        """Belirli bir marker satırı gelene kadar oku. Timeout varsa False döner."""
        import time as _t
        deadline = _t.monotonic() + timeout
        while _t.monotonic() < deadline:
            remaining = max(0.05, deadline - _t.monotonic())
            line = self._readline(timeout=remaining)
            if not line:
                if self.proc and self.proc.poll() is not None:
                    self._kill_proc()
                    return False
                continue
            if marker in line:
                return True
        return False

    def _sync(self):
        """isready/readyok handshake — motorun hazır olduğunu garanti eder ve eski çıktıyı temizler."""
        self._send('isready')
        if not self._read_until('readyok', timeout=10):
            self._kill_proc()
            return False
        return True

    def _ensure_alive(self):
        """Motor sürecinin yaşadığını doğrula, ölmüşse yeniden başlat."""
        if not self.proc or self.proc.poll() is not None:
            self._kill_proc()
            self.start()
        return self.proc is not None

    def query(self, fen, skill=20, elo=None, movetime=180, depth=None, pure=False, hint=False, **kwargs):
        with self.lock:
            if not self._ensure_alive():
                return None
            try:
                self._drain()
                if not self._sync():
                    self.start()
                    if not self.proc: return None

                threads = max(1, os.cpu_count() or 1)
                self._send(f'setoption name Threads value {threads}')

                if pure or hint:
                    # Saf güç & İpucu: Maksimum NNUE, sınırlandırma yok, süper güçlü Stockfish 19
                    self._send('setoption name Skill Level value 20')
                    self._send('setoption name UCI_LimitStrength value false')
                    self._send('setoption name Hash value 128')
                else:
                    self._send('setoption name Hash value 64')
                    if elo and int(elo) >= 1320:
                        self._send('setoption name UCI_LimitStrength value true')
                        clamped_elo = max(1320, min(3190, int(elo)))
                        self._send(f'setoption name UCI_Elo value {clamped_elo}')
                    else:
                        self._send('setoption name UCI_LimitStrength value false')
                        self._send(f'setoption name Skill Level value {max(0, min(20, int(skill)))}')

                if not self._sync():
                    self.start()
                    if not self.proc: return None

                self._send(f'position fen {fen}')
                if pure or hint:
                    actual_movetime = max(800, int(movetime))
                    self._send(f'go movetime {actual_movetime}')
                elif depth and int(depth) > 0:
                    actual_movetime = max(350, int(movetime))
                    self._send(f'go depth {depth} movetime {actual_movetime}')
                else:
                    actual_movetime = max(200, int(movetime))
                    self._send(f'go movetime {actual_movetime}')

                bestmove, score, is_mate = None, 0.0, False
                import time as _t
                timeout = self.QUERY_TIMEOUT + (actual_movetime / 1000.0) + 3
                deadline = _t.monotonic() + timeout
                while _t.monotonic() < deadline:
                    remaining = max(0.1, deadline - _t.monotonic())
                    line = self._readline(timeout=remaining)
                    if not line:
                        if self.proc and self.proc.poll() is not None:
                            self._kill_proc()
                            return None
                        continue
                    line = line.strip()
                    if line.startswith('info ') and 'score' in line:
                        toks = line.split()
                        if 'score' in toks:
                            idx = toks.index('score')
                            if idx + 2 < len(toks):
                                if toks[idx+1] == 'cp':
                                    score = int(toks[idx+2]) / 100.0
                                    is_mate = False
                                elif toks[idx+1] == 'mate':
                                    score = int(toks[idx+2])
                                    is_mate = True
                    if line.startswith('bestmove'):
                        parts = line.split()
                        if len(parts) > 1 and parts[1] != '(none)':
                            bestmove = parts[1]
                        break
                else:
                    # Timeout — motoru durdur
                    self._send('stop')
                    self._read_until('bestmove', timeout=3)
                    return None
                return {'bestmove': bestmove, 'score': score, 'is_mate': is_mate}
            except Exception:
                self._kill_proc()
                return None

    def analyze_game(self, fens, uci_moves):
        with self.lock:
            if not self._ensure_alive():
                return {'moves': [], 'summary': {}}
            try:
                if not self._sync():
                    self.start()
                    if not self.proc: return {'moves': [], 'summary': {}}

                threads = max(1, min(8, os.cpu_count() or 1))
                self._send(f'setoption name Threads value {threads}')
                self._send('setoption name Hash value 256')
                self._send('setoption name Skill Level value 20')
                self._send('setoption name UCI_LimitStrength value false')
                self._send('setoption name MultiPV value 1')
                if not self._sync():
                    self.start()
                    if not self.proc: return {'moves': [], 'summary': {}}

                import time as _t, math

                # Standart Açılış Kitabı Hamleleri (Sadece bilinen teorik hamleler 'Kitap' sayılır)
                OPENING_BOOK = {
                    '': {'e2e4', 'd2d4', 'c2c4', 'g1f3', 'g2g3', 'b2b3', 'f2f4', 'b1c3'},
                    'e2e4': {'e7e5', 'c7c5', 'e7e6', 'c7c6', 'd7d6', 'g7g6', 'd7d5', 'g8f6', 'b8c6'},
                    'd2d4': {'d7d5', 'g8f6', 'e7e6', 'c7c5', 'f7f5', 'g7g6', 'd7d6', 'c7c6'},
                    'c2c4': {'e7e5', 'c7c5', 'g8f6', 'e7e6', 'c7c6'},
                    'g1f3': {'d7d5', 'g8f6', 'c7c5', 'e7e6', 'g7g6'},
                    'e2e4 e7e5': {'g1f3', 'f1c4', 'b1c3', 'f2f4', 'd2d4', 'c2c3'},
                    'e2e4 c7c5': {'g1f3', 'b1c3', 'c2c3', 'd2d4', 'g2g3', 'f2f4'},
                    'e2e4 e7e6': {'d2d4', 'd2d3', 'g1f3', 'b1c3'},
                    'e2e4 c7c6': {'d2d4', 'b1c3', 'g1f3', 'c2c4'},
                    'd2d4 d7d5': {'c2c4', 'g1f3', 'c1f4', 'e2e3', 'c1g5', 'b1c3'},
                    'd2d4 g8f6': {'c2c4', 'g1f3', 'c1g5', 'c1f4', 'e2e3', 'g2g3'},
                    'e2e4 e7e5 g1f3': {'b8c6', 'g8f6', 'd7d6', 'd7d5', 'f7f5'},
                    'e2e4 e7e5 g1f3 b8c6': {'f1b5', 'f1c4', 'd2d4', 'b1c3', 'c2c3'},
                    'e2e4 c7c5 g1f3': {'d7d6', 'b8c6', 'e7e6', 'g7g6', 'a7a6'},
                    'e2e4 c7c5 g1f3 d7d6': {'d2d4', 'f1b5', 'c2c3'},
                    'e2e4 c7c5 g1f3 b8c6': {'d2d4', 'f1b5', 'b1c3'},
                }

                total_moves = len(uci_moves)
                if not total_moves or not fens:
                    return {'moves': [], 'summary': {}}

                # 1. Aşama: Her bir FEN pozisyonunu Stockfish 19 ile analiz et
                pos_evals = []
                for f_idx, fen in enumerate(fens):
                    self._send(f'position fen {fen}')
                    if not self._sync():
                        self.start()
                        if not self.proc: return {'moves': [], 'summary': {}}

                    # Pozisyon başına derin Stockfish 19 analizi (220ms)
                    self._send('go movetime 220')
                    bestmove, score_val, is_mate, mate_in = None, 0.0, False, None
                    best_depth = 0
                    deadline = _t.monotonic() + 4.0
                    while _t.monotonic() < deadline:
                        remaining = max(0.02, deadline - _t.monotonic())
                        line = self._readline(timeout=remaining)
                        if not line:
                            if self.proc and self.proc.poll() is not None:
                                self._kill_proc()
                                return {'moves': [], 'summary': {}}
                            continue
                        line = line.strip()
                        if line.startswith('info ') and 'score' in line:
                            toks = line.split()
                            if 'depth' in toks:
                                d_idx = toks.index('depth')
                                if d_idx + 1 < len(toks):
                                    try: best_depth = int(toks[d_idx + 1])
                                    except: pass
                            if 'score' in toks:
                                idx_sc = toks.index('score')
                                if idx_sc + 2 < len(toks):
                                    if toks[idx_sc+1] == 'cp':
                                        score_val = int(toks[idx_sc+2]) / 100.0
                                        is_mate = False
                                        mate_in = None
                                    elif toks[idx_sc+1] == 'mate':
                                        m_val = int(toks[idx_sc+2])
                                        score_val = (100.0 - abs(m_val)) if m_val > 0 else (-100.0 + abs(m_val))
                                        is_mate = True
                                        mate_in = m_val
                        if line.startswith('bestmove'):
                            parts = line.split()
                            if len(parts) > 1 and parts[1] != '(none)':
                                bestmove = parts[1]
                            break
                    else:
                        self._send('stop')
                        self._read_until('bestmove', timeout=1.5)

                    pos_evals.append({
                        'bestmove': bestmove,
                        'score': score_val,
                        'is_mate': is_mate,
                        'mate_in': mate_in,
                        'depth': best_depth
                    })

                # 2. Aşama: Oynanan her hamlenin centipawn kaybını ve kategorisini hesapla
                move_results = []
                white_scores_graph = []

                if pos_evals:
                    white_scores_graph.append(round(pos_evals[0]['score'], 2))

                history_seq = []
                for idx, played in enumerate(uci_moves):
                    is_white = (idx % 2 == 0)
                    cur_pos = pos_evals[idx] if idx < len(pos_evals) else {'bestmove': None, 'score': 0.0, 'is_mate': False, 'mate_in': None, 'depth': 0}
                    next_pos = pos_evals[idx + 1] if (idx + 1) < len(pos_evals) else cur_pos

                    bestmove = cur_pos['bestmove']
                    best_depth = cur_pos['depth']
                    eval_before = cur_pos['score']
                    opp_eval_after = next_pos['score']
                    eval_after = -opp_eval_after

                    norm_white_score = eval_after if is_white else -eval_after
                    white_scores_graph.append(round(norm_white_score, 2))

                    is_match = (played and bestmove and played == bestmove)

                    if is_match:
                        loss = 0.0
                        diff = 0.0
                    else:
                        diff = eval_after - eval_before
                        if diff > 0: diff = 0.0
                        loss = max(0.0, -diff)

                    seq_key = ' '.join(history_seq)
                    is_book_move = (seq_key in OPENING_BOOK and played in OPENING_BOOK[seq_key] and loss <= 0.25)
                    history_seq.append(played)

                    if is_book_move:
                        cat = 'book'
                    elif is_match or loss <= 0.05:
                        if abs(eval_after) >= 3.0 and cur_pos['score'] <= 1.0:
                            cat = 'brilliant'
                        elif abs(eval_after) >= 2.0 and loss == 0:
                            cat = 'great'
                        else:
                            cat = 'best'
                    elif loss <= 0.20:
                        cat = 'excellent'
                    elif loss <= 0.55:
                        cat = 'good'
                    elif loss <= 1.25:
                        cat = 'inaccuracy'
                    elif loss <= 2.60:
                        if eval_before >= 1.8 and eval_after < 0.4:
                            cat = 'miss'
                        else:
                            cat = 'mistake'
                    else:
                        if eval_before >= 2.5 and eval_after <= 0.0:
                            cat = 'miss'
                        else:
                            cat = 'blunder'

                    if idx < 14: phase = 'opening'
                    elif idx < total_moves * 0.7: phase = 'middlegame'
                    else: phase = 'endgame'

                    move_results.append({
                        'idx': idx,
                        'played': played,
                        'best': bestmove,
                        'score': round(norm_white_score, 2),
                        'eval_before': round(eval_before, 2),
                        'eval_after': round(eval_after, 2),
                        'is_mate': next_pos['is_mate'],
                        'mate_in': next_pos['mate_in'],
                        'diff': round(diff, 2),
                        'loss': round(loss, 2),
                        'category': cat,
                        'phase': phase,
                        'depth': best_depth
                    })

                # 3. Aşama: Doğruluk Yüzdeleri ve Elo Derecesi
                w_moves = [m for i, m in enumerate(move_results) if i % 2 == 0]
                b_moves = [m for i, m in enumerate(move_results) if i % 2 == 1]

                def calc_player_stats(moves):
                    if not moves:
                        return {'accuracy': 75.0, 'rating': 1500, 'counts': {}, 'phase_ratings': {}}
                    all_cats = ['brilliant', 'great', 'best', 'excellent', 'good', 'book', 'inaccuracy', 'mistake', 'miss', 'blunder']
                    counts = {c: sum(1 for m in moves if m['category'] == c) for c in all_cats}

                    acc_sum = 0.0
                    for m in moves:
                        cpl = m['loss'] * 100.0
                        m_acc = max(0.0, min(100.0, 103.1668 * math.exp(-0.04354 * (cpl / 10.0)) - 3.1668))
                        acc_sum += m_acc

                    acc = round(acc_sum / len(moves), 1)

                    if acc >= 96: base_rating = 2500 + (acc - 96) * 75
                    elif acc >= 90: base_rating = 2100 + (acc - 90) * 65
                    elif acc >= 80: base_rating = 1600 + (acc - 80) * 50
                    elif acc >= 65: base_rating = 1100 + (acc - 65) * 33
                    elif acc >= 50: base_rating = 750 + (acc - 50) * 23
                    else: base_rating = max(350, 350 + acc * 8)

                    blunders = counts.get('blunder', 0)
                    misses = counts.get('miss', 0)
                    mistakes = counts.get('mistake', 0)
                    penalty = (blunders * 110) + (misses * 60) + (mistakes * 25)
                    rating = int(max(350, min(2850, base_rating - penalty)))

                    phase_ratings = {}
                    for ph in ['opening', 'middlegame', 'endgame']:
                        ph_m = [m for m in moves if m['phase'] == ph]
                        if ph_m:
                            bads = sum(1 for m in ph_m if m['category'] in ('blunder', 'miss', 'mistake'))
                            goods = sum(1 for m in ph_m if m['category'] in ('brilliant', 'great', 'best', 'excellent', 'book'))
                            if bads == 0 and goods >= len(ph_m) * 0.7:
                                phase_ratings[ph] = 'best'
                            elif bads == 0:
                                phase_ratings[ph] = 'great'
                            elif bads <= 1:
                                phase_ratings[ph] = 'inaccuracy'
                            else:
                                phase_ratings[ph] = 'blunder'

                    return {'accuracy': acc, 'rating': rating, 'counts': counts, 'phase_ratings': phase_ratings}

                w_stats = calc_player_stats(w_moves)
                b_stats = calc_player_stats(b_moves)

                diff_acc = abs(w_stats['accuracy'] - b_stats['accuracy'])
                if max(w_stats['accuracy'], b_stats['accuracy']) > 94:
                    game_desc = 'USTALIK'
                elif diff_acc <= 6:
                    game_desc = 'DENGELİ'
                elif sum(m['category'] in ('blunder', 'miss') for m in move_results) >= 3:
                    game_desc = 'ÇILGIN'
                else:
                    game_desc = 'SERT'

                summary = {
                    'white': w_stats,
                    'black': b_stats,
                    'game_desc': game_desc,
                    'total_moves': total_moves,
                    'scores': white_scores_graph
                }
                return {'moves': move_results, 'summary': summary}
            except Exception:
                self._kill_proc()
                return {'moves': [], 'summary': {}}

if sys.stdout.isatty():
    os.system('cls' if IS_WINDOWS else 'clear')

SF_ENGINE = StockfishEngine(SF_PATH) if SF_PATH else None
if SF_ENGINE:
    print(f"  ★ Stockfish 19 aktif: {SF_PATH}")
else:
    _pname = platform.system() + '/' + platform.machine()
    print(f"  ℹ Stockfish bulunamadı ({_pname}) — bot olmadan devam edilecek.")
    if IS_WINDOWS:
        print("    → engines/ klasörüne Stockfish exe dosyasını koyun.")
    elif IS_LINUX:
        print("    → engines/ klasörüne Linux Stockfish dosyasını koyun veya 'sudo apt install stockfish'.")

PIPER_VOICE = None
TTS_RAM_CACHE = {}

def _try_load_piper():
    """Piper TTS ses motorunu yüklemeyi dener.
    Eksikse kullanıcıya net kurulum önerisi sunar ve oyunu kesintisiz başlatır."""
    global PIPER_VOICE
    model_candidates = [
        (os.path.join(APP_DIR, 'engines', 'piper-turkish-tts', 'model.onnx'),
         os.path.join(APP_DIR, 'engines', 'piper-turkish-tts', 'config.json')),
        (os.path.join(APP_DIR, 'piper-turkish-tts', 'model.onnx'),
         os.path.join(APP_DIR, 'piper-turkish-tts', 'config.json')),
    ]
    model_p, config_p = None, None
    for mp, cp in model_candidates:
        if os.path.isfile(mp) and os.path.isfile(cp):
            model_p, config_p = mp, cp
            break
    if not model_p:
        return

    # 1) Proje venv'ini sys.path'e dahil etmeyi dene
    venv_candidates = [
        os.path.join(SCRIPT_DIR, 'venv'),
        os.path.join(APP_DIR, 'server', 'venv'),
        os.path.join(APP_DIR, 'venv'),
    ]
    venv_dir = None
    for vd in venv_candidates:
        if os.path.isdir(vd):
            venv_dir = vd
            break

    if venv_dir:
        if IS_WINDOWS:
            venv_site = os.path.join(venv_dir, 'Lib', 'site-packages')
        else:
            import glob
            sp = glob.glob(os.path.join(venv_dir, 'lib', 'python*', 'site-packages'))
            venv_site = sp[0] if sp else None

        if venv_site and os.path.isdir(venv_site) and venv_site not in sys.path:
            sys.path.insert(0, venv_site)

    # 2) PiperVoice yüklemesini dene
    try:
        from piper import PiperVoice
        PIPER_VOICE = PiperVoice.load(model_p, config_path=config_p, use_cuda=False)
        print(f"  ★ Piper Türkçe Ses Modeli aktif: {model_p}")
        return
    except ImportError:
        # Linux'ta sorma (zaten venv/local dosyalarda mevcut)
        if not IS_WINDOWS:
            return

        # Windows'ta kullanıcıya temiz E/H onayı sor
        if sys.stdin.isatty():
            try:
                ans = input("\n  💡 Sesli Koç Analizi için 'piper-tts' kütüphanesi eksik. Kurulsun mu? [E/H]: ").strip().lower()
                if ans in ('e', 'evet', 'y', 'yes'):
                    print("  ⏳ piper-tts kuruluyor, lütfen bekleyin...")
                    py_exe = sys.executable or 'python'
                    ret = subprocess.run([py_exe, '-m', 'pip', 'install', 'piper-tts'])
                    if ret.returncode == 0:
                        try:
                            from piper import PiperVoice
                            PIPER_VOICE = PiperVoice.load(model_p, config_path=config_p, use_cuda=False)
                            print(f"  ★ Piper Türkçe Ses Modeli kuruldu ve aktif: {model_p}\n")
                            return
                        except Exception as e:
                            print(f"  ℹ Model başlatılamadı: {e}\n")
                    else:
                        print("  ⚠ Kurulum yapılamadı. Sesli koç olmadan devam ediliyor.\n")
                else:
                    print("  ℹ Kurulum atlandı. Sesli koç olmadan devam ediliyor.\n")
            except (EOFError, KeyboardInterrupt):
                print("\n  ℹ Kurulum atlandı. Sesli koç olmadan devam ediliyor.\n")
    except Exception as e:
        print(f"  ℹ Piper TTS yükleme uyarısı: {e}")

_try_load_piper()


CFG = {'names': set(), 'port': 0, 'local': False, 'public': ''}
HITS = defaultdict(deque); HITS_LOCK = threading.Lock()
SSE_COUNT = defaultdict(int); SSE_LOCK = threading.Lock()

def rate_ok(ip, key, limit, window=60):
    now = time.time(); k = (ip, key)
    with HITS_LOCK:
        d = HITS[k]
        while d and now - d[0] > window: d.popleft()
        if len(d) >= limit: return False
        d.append(now); return True

def host_ok(hostheader):
    if not hostheader: return False
    h = hostheader.strip().lower()
    if h.startswith('['): h = h[1:h.find(']')] if ']' in h else ''
    elif h.count(':') == 1: h = h.rsplit(':', 1)[0]
    if h in CFG['names']: return True
    try: ipaddress.ip_address(h); return True   # IP adresleri DNS-rebinding'e açık değildir
    except ValueError: return False

class Handler(BaseHTTPRequestHandler):
    server_version = 'Satranc/' + VERSION
    sys_version = ''
    def log_message(self, *a): pass
    def ip(self): return self.client_address[0]
    def sec(self):
        self.send_header('Content-Security-Policy', CSP); self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer'); self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin'); self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    def reply(self, code, ctype, body, cache='no-cache'):
        if isinstance(body, str): body = body.encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', cache); self.send_header('Connection', 'close'); self.sec(); self.end_headers()
        if self.command != 'HEAD': self.wfile.write(body)
    def jreply(self, code, obj): self.reply(code, 'application/json', json.dumps(obj), 'no-store')
    def guard(self, post=False):
        if not host_ok(self.headers.get('Host')):
            self.jreply(421, {'error': 'host'}); return False
        if post:
            org = self.headers.get('Origin')
            if org and urlsplit(org).netloc.lower() != (self.headers.get('Host') or '').lower():
                self.jreply(403, {'error': 'origin'}); return False
            if not (self.headers.get('Content-Type') or '').lower().startswith('application/json'):
                self.jreply(415, {'error': 'type'}); return False
            if not rate_ok(self.ip(), 'post', 240):
                self.jreply(429, {'error': 'rate'}); return False
        return True
    def body(self):
        try: n = int(self.headers.get('Content-Length') or 0)
        except ValueError: raise ApiError(400, 'bad')
        if n < 0 or n > 131072: raise ApiError(413, 'big')
        try: d = json.loads(self.rfile.read(n) or b'{}')
        except (ValueError, UnicodeDecodeError): raise ApiError(400, 'json')
        if not isinstance(d, dict): raise ApiError(400, 'json')
        return d
    def room(self, code):
        with ROOMS_LOCK: r = ROOMS.get(code)
        if r is None: raise ApiError(404, 'nf')
        return r
    do_HEAD = lambda self: self.do_GET()
    def do_GET(self):
        if not self.guard(): return
        u = urlsplit(self.path); p = u.path
        try:
            if p in ASSETS: ct, body = ASSETS[p]; return self.reply(200, ct, body)
            if p.startswith('/bot/') or p.startswith('/sprite/') or p.startswith('/assets/'):
                clean = os.path.normpath(p.lstrip('/'))
                candidates = [
                    os.path.join(APP_DIR, 'assets', clean),
                    os.path.join(APP_DIR, clean),
                ]
                if clean.startswith('assets/'):
                    candidates.insert(0, os.path.join(APP_DIR, clean))
                    candidates.insert(1, os.path.join(APP_DIR, 'assets', clean[len('assets/'):]))

                full_p = None
                for cand in candidates:
                    if os.path.isfile(cand):
                        full_p = cand
                        break

                if full_p:
                    ext = os.path.splitext(full_p)[1].lower()
                    mimes = {'.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp'}
                    ct = mimes.get(ext, 'application/octet-stream')
                    with open(full_p, 'rb') as f: data = f.read()
                    return self.reply(200, ct, data, 'public, max-age=86400')
            if p == '/api/info':
                return self.jreply(200, {'v': VERSION, 'urls': CFG['urls'], 'public': CFG['public'], 'local': CFG['local'], 'stockfish': bool(SF_ENGINE)})
            if p == '/api/qr.svg':
                d = (parse_qs(u.query).get('d') or [''])[0]
                if not re.fullmatch(r'https?://[\x21-\x7e]{4,190}', d): raise ApiError(400, 'bad')
                return self.reply(200, 'image/svg+xml', qr_svg(d), 'public, max-age=3600')
            m = re.fullmatch(r'/api/room/([A-Z0-9]{6})/events', p)
            if m:
                tok = (parse_qs(u.query).get('t') or [''])[0][:64]
                return self.sse(self.room(m.group(1)), tok)
            raise ApiError(404, 'nf')
        except ApiError as e: self.jreply(e.status, {'error': e.code})
        except (BrokenPipeError, ConnectionResetError): pass
    def sse(self, room, tok):
        ip = self.ip()
        with SSE_LOCK:
            if SSE_COUNT[ip] >= 16: raise ApiError(429, 'rate')
            SSE_COUNT[ip] += 1
        q = None
        try:
            self.send_response(200); self.send_header('Content-Type', 'text/event-stream'); self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Accel-Buffering', 'no'); self.send_header('Connection', 'close'); self.sec(); self.end_headers()
            self.wfile.write(b'retry: 2000\n\n'); self.wfile.flush()
            q = room.listen(tok)
            while True:
                try: item = q.get(timeout=15)
                except queue.Empty: item = b': ping\n\n'
                if item is None: break
                self.wfile.write(item); self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError): pass
        finally:
            if q is not None: room.unlisten(q)
            with SSE_LOCK: SSE_COUNT[ip] -= 1
    def do_POST(self):
        if not self.guard(True): return
        p = urlsplit(self.path).path
        try:
            d = self.body()
            if p == '/api/bot/move':
                fen = d.get('fen')
                skill = int(d.get('level', 10))
                elo = d.get('elo')
                tm = int(d.get('time', 150))
                depth = d.get('depth')
                pure = bool(d.get('pure', False))
                hint = bool(d.get('hint', False))
                if SF_ENGINE and fen:
                    res = SF_ENGINE.query(fen, skill=skill, elo=elo, movetime=tm, depth=depth, pure=pure, hint=hint)
                    if res: return self.jreply(200, {'uci': res['bestmove'], 'score': res['score'], 'is_mate': res['is_mate']})
                return self.jreply(200, {'uci': None})
            if p == '/api/tts':
                text = (d.get('text') or '').strip()
                if not text: raise ApiError(400, 'empty')
                # Emojileri ve sembolleri kesin olarak temizle (Piper saçmalamasın)
                text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
                text = re.sub(r'[💡🎯⚔🏆👍✓📖✕★!?#—]', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                if not text: raise ApiError(400, 'empty')
                if PIPER_VOICE:
                    if text in TTS_RAM_CACHE:
                        return self.reply(200, 'audio/wav', TTS_RAM_CACHE[text], 'no-cache')
                    buf = io.BytesIO()
                    with wave.open(buf, 'wb') as wav:
                        wav.setnchannels(1)
                        wav.setsampwidth(2)
                        wav.setframerate(PIPER_VOICE.config.sample_rate)
                        from piper.config import SynthesisConfig
                        # Tane tane, net ve insansı konuşma hızı
                        syn_cfg = SynthesisConfig(length_scale=1.08)
                        for chunk in PIPER_VOICE.synthesize(text, syn_config=syn_cfg):
                            wav.writeframes(chunk.audio_int16_bytes)
                    wav_data = buf.getvalue()
                    TTS_RAM_CACHE[text] = wav_data
                    return self.reply(200, 'audio/wav', wav_data, 'no-cache')
                raise ApiError(503, 'no_piper')
            if p == '/api/eval':
                fen = d.get('fen')
                if SF_ENGINE and fen:
                    res = SF_ENGINE.query(fen, movetime=120)
                    if res: return self.jreply(200, {'score': res['score'], 'is_mate': res['is_mate'], 'bestmove': res['bestmove']})
                return self.jreply(200, {'score': 0.0, 'is_mate': False})
            if p == '/api/analyze/game':
                fens = d.get('fens', [])
                moves = d.get('moves', [])
                if SF_ENGINE and fens and moves:
                    res = SF_ENGINE.analyze_game(fens, moves)
                    return self.jreply(200, res)
                return self.jreply(200, {'moves': [], 'summary': {}})
            if p == '/api/room':
                if not rate_ok(self.ip(), 'mk', 12): raise ApiError(429, 'rate')
                col = d.get('color')
                tc = str(d.get('tc', '0') or '0')
                if col not in ('w', 'b', 'r'): col = 'r'
                if col == 'r': col = secrets.choice('wb')
                with ROOMS_LOCK:
                    if len(ROOMS) >= MAX_ROOMS: raise ApiError(503, 'full')
                    code = ''.join(secrets.choice(ALPHA) for _ in range(6))
                    while code in ROOMS: code = ''.join(secrets.choice(ALPHA) for _ in range(6))
                    r = Room(code, tc=tc); ROOMS[code] = r
                tok = secrets.token_urlsafe(18); r.seats[col] = tok
                return self.jreply(200, {'code': code, 'token': tok, 'color': col, 'tc': tc})
            m = re.fullmatch(r'/api/room/([A-Z0-9]{6})/(join|act)', p)
            if m:
                r = self.room(m.group(1)); tok = d.get('token') if isinstance(d.get('token'), str) else None
                if m.group(2) == 'join':
                    if not rate_ok(self.ip(), 'join', 60): raise ApiError(429, 'rate')
                    c, t = r.join(tok); return self.jreply(200, {'color': c, 'token': t})
                r.act(tok, d); return self.jreply(200, {'ok': True})
            raise ApiError(404, 'nf')
        except ApiError as e: self.jreply(e.status, {'error': e.code})
        except (BrokenPipeError, ConnectionResetError): pass

class Server(ThreadingHTTPServer):
    daemon_threads = True; allow_reuse_address = True; request_queue_size = 64

def lan_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('10.255.255.255', 1)); ips.append(s.getsockname()[0]); s.close()
    except Exception: pass
    try:
        for ai in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET): ips.append(ai[4][0])
    except Exception: pass
    out = []
    for i in ips:
        if i not in out and not i.startswith('127.') and not i.startswith('169.254.'): out.append(i)
    return out

def main():
    ap = argparse.ArgumentParser(prog='satranc.sh', description=tx('Satranç Pro - yerel ağ üzerinde çok oyunculu satranç', 'Satranç Pro - multiplayer chess on your network'))
    ap.add_argument('--port', type=int, default=8765, help=tx('başlangıç portu (varsayılan 8765)', 'first port to try (default 8765)'))
    ap.add_argument('--local', action='store_true', help=tx('yalnızca bu bilgisayar (başka cihaz bağlanamaz)', 'this computer only (no other devices)'))
    ap.add_argument('--no-browser', action='store_true', help=tx('tarayıcıyı otomatik açma', "don't open the browser"))
    ap.add_argument('--url', default='', help=tx('dışarıdan erişim adresi (ör. tünel): https://ornek.trycloudflare.com', 'public URL, e.g. a tunnel: https://example.trycloudflare.com'))
    a = ap.parse_args()
    host = '127.0.0.1' if a.local else '0.0.0.0'
    srv = None
    for port in range(a.port, a.port + 40):
        try: srv = Server((host, port), Handler); break
        except OSError: continue
    if srv is None: print(tx('Boş port bulunamadı.', 'No free port found.')); sys.exit(1)
    pub = ''
    if a.url:
        u = urlsplit(a.url)
        if u.scheme in ('http', 'https') and u.hostname: pub = '%s://%s' % (u.scheme, u.netloc); CFG['names'].add(u.hostname.lower())
        else: print(tx('Geçersiz --url yoksayıldı.', 'Invalid --url ignored.'))
    hn = socket.gethostname().lower()
    CFG['names'].update({'localhost', hn, hn + '.local', hn.split('.')[0]})
    ips = [] if a.local else lan_ips()
    CFG.update(port=port, local=a.local, public=pub, urls=['http://%s:%d' % (i, port) for i in ips])
    threading.Thread(target=cleanup_loop, daemon=True).start()
    local_url = 'http://localhost:%d' % port
    share = pub or (CFG['urls'][0] if CFG['urls'] else local_url)
    print('\n  \x1b[1m♞  Satranç Pro %s\x1b[0m\n' % VERSION)
    print('  ' + tx('Bu bilgisayar : ', 'This computer : ') + local_url)
    for u in CFG['urls']: print('  ' + tx('Yerel ağ      : ', 'Local network : ') + u)
    if pub: print('  ' + tx('Genel adres   : ', 'Public URL    : ') + pub)
    if a.local: print('  ' + tx('(--local: diğer cihazlar bağlanamaz)', '(--local: other devices cannot connect)'))
    if not a.local and sys.stdout.isatty() and share != local_url:
        try: print('\n' + qr_terminal(share) + '\n\n  ' + tx('Telefonla QR kodu okutun: ', 'Scan with your phone: ') + share)
        except Exception: pass
    print('\n  ' + tx('Durdurmak için Ctrl+C. Güvenlik duvarı sorun çıkarırsa %d portuna izin verin.' % port,
                        'Press Ctrl+C to stop. If a firewall blocks you, allow port %d.' % port) + '\n')
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(local_url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: print('\n  ' + tx('Görüşürüz!', 'Goodbye!'))
    finally: srv.server_close(); os._exit(0)

if __name__ == '__main__':
    main()
