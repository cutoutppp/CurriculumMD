# -*- coding: utf-8 -*-
"""
Builder script to generate the 5-Level Radial Structure Map with Drill-down Sub-circles
and Full Realtime Catalog Search for index.html
"""

import sys

html_template = '''<!DOCTYPE html>
<html lang="th" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>แผนภาพโครงสร้างหลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน</title>
  <meta name="description" content="แผนภาพและระบบสืบค้นโครงสร้างหลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน (กลุ่มสาระ สาระ มาตรฐาน และตัวชี้วัด)">

  <!-- Google Fonts: IBM Plex Sans Thai, Prompt & Space Grotesk -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&family=Prompt:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@0.344.0/dist/umd/lucide.min.js"></script>

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"IBM Plex Sans Thai"', 'Prompt', 'system-ui', 'sans-serif'],
            heading: ['Prompt', 'sans-serif'],
            mono: ['"Space Grotesk"', 'monospace']
          },
          colors: {
            brand: {
              navy: '#0d3d70',
              deep: '#071f3a',
              accent: '#10b981'
            }
          }
        }
      }
    }
  </script>

  <style>
    :root {
      --bg: #0b1120;
      --bg-card: rgba(15, 23, 42, 0.88);
      --ink: #f8fafc;
      --ink-soft: #94a3b8;
      --line: rgba(51, 65, 85, 0.5);
      --line-strong: rgba(71, 85, 105, 0.8);
      --navy-deep: #071f3a;
      --navy: #0d3d70;
      --teal: #10b981;
      --amber: #f59e0b;
      --sky: #38bdf8;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at 50% 0%, #172554 0%, #0b1120 40%, #030712 100%);
      color: var(--ink);
      font-family: "IBM Plex Sans Thai", system-ui, sans-serif;
      overflow-x: hidden;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    /* Glass Panels */
    .glass-panel {
      background: rgba(15, 23, 42, 0.90);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(51, 65, 85, 0.6);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    /* Interactive Graph Stage */
    .graph-stage {
      position: relative;
      height: clamp(620px, 75vh, 920px);
      min-height: 620px;
      overflow: hidden;
      border-radius: 24px;
      border: 1px solid rgba(51, 65, 85, 0.6);
      background:
        radial-gradient(circle at center, rgba(16, 185, 129, 0.04) 0%, transparent 60%),
        radial-gradient(circle at center, rgba(56, 189, 248, 0.03) 0%, transparent 40%),
        linear-gradient(180deg, #090e17 0%, #030712 100%);
      box-shadow: inset 0 0 60px rgba(0,0,0,0.6), 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      cursor: grab;
      touch-action: none;
      user-select: none;
    }
    .graph-stage:active { cursor: grabbing; }

    #graphSvg, #sunburstSvg {
      width: 100%;
      height: 100%;
      display: block;
    }
    #graphSvg.hidden, #sunburstSvg.hidden {
      display: none !important;
    }

    /* Concentric Guideline Rings */
    .graph-ring {
      fill: none;
      stroke: rgba(255, 255, 255, 0.08);
      stroke-dasharray: 4 6;
      stroke-width: 1px;
    }
    .graph-ring-label {
      font-size: 11px;
      fill: rgba(148, 163, 184, 0.7);
      font-family: 'IBM Plex Sans Thai', sans-serif;
      text-anchor: middle;
      pointer-events: none;
      font-weight: 500;
      letter-spacing: 0.03em;
    }

    /* SVG Edges */
    .graph-edge {
      fill: none;
      stroke-linecap: round;
      transition: stroke 200ms ease, stroke-width 200ms ease, opacity 200ms ease;
      pointer-events: none;
    }

    /* SVG Nodes */
    .node {
      cursor: pointer;
      transition: opacity 200ms ease;
    }
    .node .node-visible-shape {
      transition: r 180ms ease, fill 180ms ease, stroke 180ms ease, filter 180ms ease;
    }
    .node:hover .node-visible-shape {
      filter: drop-shadow(0 0 10px currentColor);
    }

    /* Node Hit Area (Invisible large circle for effortless clicking) */
    .node-hit-area {
      fill: transparent;
      pointer-events: all;
      cursor: pointer;
    }

    /* Labels */
    .node-label-bg {
      font-size: 11px;
      fill: none;
      stroke: #030712;
      stroke-width: 3.5px;
      stroke-linejoin: round;
      pointer-events: all;
      cursor: pointer;
      user-select: none;
      font-family: "IBM Plex Sans Thai", sans-serif;
    }
    .node-label-fg {
      font-size: 11px;
      fill: #f1f5f9;
      pointer-events: all;
      cursor: pointer;
      user-select: none;
      font-family: "IBM Plex Sans Thai", sans-serif;
      font-weight: 500;
    }

    /* Dimming & Highlighting in Focus Mode */
    .is-dimmed {
      opacity: 0.12 !important;
    }
    .edge-dimmed {
      opacity: 0.03 !important;
    }
    .edge-highlighted {
      opacity: 0.95 !important;
      stroke-width: 2.2px !important;
      filter: drop-shadow(0 0 4px currentColor);
    }
    .node-highlighted .node-visible-shape {
      filter: drop-shadow(0 0 14px currentColor) !important;
    }

    /* Selected Node Halo Animation */
    @keyframes haloPulse {
      0% { transform: scale(1); opacity: 0.9; }
      50% { transform: scale(1.15); opacity: 0.5; }
      100% { transform: scale(1); opacity: 0.9; }
    }
    .selected-halo {
      animation: haloPulse 2s ease-in-out infinite;
      transform-origin: center;
      transform-box: fill-box;
      filter: drop-shadow(0 0 8px #10b981);
      pointer-events: none;
    }

    /* Center Drill Return Indicator */
    .center-drill-halo {
      animation: haloPulse 2.5s ease-in-out infinite;
      transform-origin: center;
      transform-box: fill-box;
      stroke-dasharray: 4 4;
      pointer-events: none;
    }

    /* Radar Wheel & Grade Slices */
    .radar-cell {
      cursor: pointer;
      transition: opacity 180ms ease, filter 180ms ease, stroke-width 180ms ease;
      stroke: #030712;
      stroke-width: 1px;
    }
    .radar-cell:hover {
      filter: brightness(1.3) drop-shadow(0 0 10px currentColor);
      stroke: #ffffff;
      stroke-width: 1.8px;
    }
    .radar-axis-badge {
      cursor: pointer;
      transition: transform 150ms ease, filter 150ms ease;
    }
    .radar-axis-badge:hover {
      filter: brightness(1.25);
    }
    .radar-axis-bg {
      fill: #0f172a;
      stroke: #334155;
      stroke-width: 1.2px;
      rx: 6px;
    }
    .radar-axis-badge:hover .radar-axis-bg {
      fill: #1e293b;
      stroke: #38bdf8;
    }
    .radar-axis-text {
      font-family: 'IBM Plex Sans Thai', sans-serif;
      font-size: 11px;
      font-weight: 700;
      fill: #f8fafc;
      text-anchor: middle;
      dominant-baseline: central;
      pointer-events: none;
    }
    .radar-subject-label {
      font-family: 'IBM Plex Sans Thai', sans-serif;
      font-size: 11px;
      font-weight: 700;
      fill: #cbd5e1;
      text-anchor: middle;
      dominant-baseline: central;
      cursor: pointer;
      transition: fill 150ms ease;
    }
    .radar-subject-label:hover {
      fill: #38bdf8;
    }

    /* Sunburst Slices */
    .sunburst-slice {
      cursor: pointer;
      transition: opacity 180ms ease, filter 180ms ease, stroke-width 180ms ease;
      stroke: #030712;
      stroke-width: 1px;
    }
    .sunburst-slice:hover {
      filter: brightness(1.28) drop-shadow(0 0 10px currentColor);
      stroke: #ffffff;
      stroke-width: 1.8px;
    }
    .sunburst-label {
      font-family: 'IBM Plex Sans Thai', sans-serif;
      font-size: 10px;
      font-weight: 600;
      fill: #ffffff;
      pointer-events: none;
      user-select: none;
      text-anchor: middle;
      dominant-baseline: central;
    }
    .sunburst-label-bg {
      font-family: 'IBM Plex Sans Thai', sans-serif;
      font-size: 10px;
      font-weight: 600;
      fill: none;
      stroke: #030712;
      stroke-width: 2.8px;
      stroke-linejoin: round;
      pointer-events: none;
      user-select: none;
      text-anchor: middle;
      dominant-baseline: central;
    }

    /* Toast animation */
    @keyframes toastSlide {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    .toast-animate {
      animation: toastSlide 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
  </style>
</head>
<body class="selection:bg-emerald-500/30 selection:text-emerald-200">

  <!-- Toast Notification Container -->
  <div id="toast-container" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- App Shell -->
  <div class="min-h-screen flex flex-col">

    <!-- Topbar (Editorial Header) -->
    <header class="border-b border-slate-800/80 bg-slate-950/90 sticky top-0 z-40 backdrop-blur-md px-4 sm:px-6 lg:px-8 py-3.5">
      <div class="max-w-[1720px] mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <!-- Brand & Title -->
        <div class="flex items-start space-x-3.5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-sky-500 flex items-center justify-center text-white shadow-lg shadow-emerald-950 shrink-0 mt-0.5">
            <i data-lucide="network" class="w-5 h-5"></i>
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-mono text-[11px] tracking-wider text-emerald-400 uppercase font-semibold">โครงสร้างหลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน</span>
              <span class="px-1.5 py-0.2 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">พ.ศ. ๒๕๕๑ (ฉบับปรับปรุง ๒๕๖๐)</span>
            </div>
            <h1 class="text-lg sm:text-xl font-bold font-heading text-white tracking-tight">
              แผนภาพโครงสร้างหลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน
            </h1>
            <p class="text-xs text-slate-400 max-w-2xl mt-0.5">
              ๘ กลุ่มสาระการเรียนรู้ • ๓๑ สาระ • ๕๕ มาตรฐาน • ๒,๐๕๖ ตัวชี้วัด
            </p>
          </div>
        </div>

        <!-- Top Actions -->
        <div class="flex items-center space-x-2 shrink-0">
          <!-- View Mode Toggle -->
          <div class="bg-slate-900 border border-slate-800 p-1 rounded-xl flex items-center space-x-1">
            <button id="btn-view-map" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white transition flex items-center space-x-1.5 shadow-sm">
              <i data-lucide="orbit" class="w-3.5 h-3.5"></i>
              <span>แผนภาพโครงข่าย</span>
            </button>
            <button id="btn-view-sunburst" class="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5">
              <i data-lucide="pie-chart" class="w-3.5 h-3.5"></i>
              <span>วงกลมแบ่งตามชั้น</span>
            </button>
            <button id="btn-view-catalog" class="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5">
              <i data-lucide="table-properties" class="w-3.5 h-3.5"></i>
              <span>ตารางสืบค้น</span>
            </button>
          </div>

          <button id="btn-open-help" class="px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium transition flex items-center space-x-1.5">
            <i data-lucide="help-circle" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>วิธีใช้</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Summary Metrics Strip (6 Key Cards with 31 Strands) -->
    <section class="max-w-[1720px] mx-auto w-full px-4 sm:px-6 lg:px-8 pt-4 pb-2">
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 sm:gap-3">
        <!-- 1. Learning Areas -->
        <div class="glass-panel p-3 rounded-2xl border-l-4 border-l-pink-500 hover:border-slate-700 transition">
          <span class="text-[11px] font-medium text-slate-400 block mb-0.5">กลุ่มสาระการเรียนรู้</span>
          <div class="flex items-baseline space-x-1.5">
            <span class="text-xl sm:text-2xl font-bold font-mono text-white">8</span>
            <span class="text-[10px] text-pink-400">กลุ่มสาระฯ</span>
          </div>
        </div>

        <!-- 2. Strands (สาระ) -->
        <div class="glass-panel p-3 rounded-2xl border-l-4 border-l-cyan-500 hover:border-slate-700 transition">
          <span class="text-[11px] font-medium text-slate-400 block mb-0.5">สาระการเรียนรู้</span>
          <div class="flex items-baseline space-x-1.5">
            <span class="text-xl sm:text-2xl font-bold font-mono text-cyan-400">31</span>
            <span class="text-[10px] text-cyan-300">สาระ</span>
          </div>
        </div>

        <!-- 3. Standards -->
        <div class="glass-panel p-3 rounded-2xl border-l-4 border-l-blue-500 hover:border-slate-700 transition">
          <span class="text-[11px] font-medium text-slate-400 block mb-0.5">มาตรฐานการเรียนรู้</span>
          <div class="flex items-baseline space-x-1.5">
            <span class="text-xl sm:text-2xl font-bold font-mono text-white">55</span>
            <span class="text-[10px] text-blue-400">มาตรฐาน</span>
          </div>
        </div>

        <!-- 4. Total KPIs -->
        <div class="glass-panel p-3 rounded-2xl border-l-4 border-l-emerald-500 hover:border-slate-700 transition">
          <span class="text-[11px] font-medium text-slate-400 block mb-0.5">ตัวชี้วัดทั้งหมด</span>
          <div class="flex items-baseline space-x-1.5">
            <span class="text-xl sm:text-2xl font-bold font-mono text-emerald-400" id="stat-total-kpi">2,056</span>
            <span class="text-[10px] text-emerald-400">ตัวชี้วัด</span>
          </div>
        </div>

        <!-- 5. Formative & Summative -->
        <div class="glass-panel p-3 rounded-2xl border-l-4 border-l-amber-500 hover:border-slate-700 transition">
          <span class="text-[11px] font-medium text-slate-400 block mb-0.5">ระหว่างทาง / ปลายทาง</span>
          <div class="flex items-baseline space-x-1.5">
            <span class="text-base sm:text-lg font-bold font-mono text-sky-400">1,285</span>
            <span class="text-slate-500 text-xs">/</span>
            <span class="text-base sm:text-lg font-bold font-mono text-amber-400">771</span>
          </div>
        </div>

        <!-- 6. School Courses -->
        <div class="glass-panel p-3 rounded-2xl border-l-4 border-l-purple-500 hover:border-slate-700 transition">
          <span class="text-[11px] font-medium text-slate-400 block mb-0.5">วิชาโรงเรียนพัฒนานิคม</span>
          <div class="flex items-baseline space-x-1.5">
            <span class="text-xl sm:text-2xl font-bold font-mono text-purple-400">548</span>
            <span class="text-[10px] text-purple-300">วิชา (ม.1–6)</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Main View 1: 3-Panel Interactive Structure Map View (Default) -->
    <main id="main-map-view" class="max-w-[1720px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-3 flex-1 flex flex-col">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5 flex-1 items-start">

        <!-- Left Column: Details & Action Info Panel (3 cols) -->
        <aside id="infoPanel" class="lg:col-span-3 glass-panel rounded-3xl p-4 sm:p-5 flex flex-col max-h-[820px] overflow-hidden">
          <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span class="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">ข้อมูลรายละเอียด</span>
            </div>
            <button id="btn-panel-reset" class="text-[11px] font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-950/60 hover:bg-emerald-900/60 px-2.5 py-1 rounded-full border border-emerald-500/30 transition flex items-center space-x-1">
              <i data-lucide="rotate-ccw" class="w-3 h-3"></i>
              <span>กลับภาพรวม</span>
            </button>
          </div>

          <!-- Dynamic Info Content Container -->
          <div id="infoContent" class="overflow-y-auto pr-1 flex-1 space-y-4 text-xs leading-relaxed">
            <!-- Injected via JavaScript -->
          </div>
        </aside>

        <!-- Center Column: Interactive Graph Stage with Breadcrumb Header (6 cols) -->
        <section class="lg:col-span-6 relative flex flex-col">
          
          <!-- Drill-down Breadcrumb Navigation Bar -->
          <div class="rounded-t-2xl bg-slate-900/95 border-t border-x border-slate-800 px-4 py-2.5 flex items-center justify-between text-xs backdrop-blur z-20">
            <div id="drillBreadcrumb" class="flex items-center space-x-1.5 overflow-x-auto text-slate-400 font-mono text-[11px] pr-2">
              <!-- Rendered via JS -->
            </div>
            <button id="btn-drill-up" class="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium transition flex items-center space-x-1.5 shrink-0 hidden">
              <i data-lucide="arrow-left" class="w-3.5 h-3.5 text-emerald-400"></i>
              <span>ย้อนกลับ</span>
            </button>
          </div>

          <!-- Circular View Sub-mode Selector Bar -->
          <div id="sunburstModeBar" class="hidden bg-slate-950/95 border-x border-b border-slate-800/90 px-4 py-2 flex items-center justify-between text-xs backdrop-blur z-20">
            <div class="flex items-center space-x-2">
              <span class="text-slate-400 text-[11px] font-medium flex items-center gap-1">
                <i data-lucide="layers" class="w-3.5 h-3.5 text-emerald-400"></i>
                <span class="text-slate-300 font-semibold">การจัดชั้น:</span>
              </span>
              <div class="bg-slate-900 border border-slate-700/80 p-0.5 rounded-lg flex items-center space-x-0.5">
                <button id="btn-sunburst-grade" class="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-600 text-white transition flex items-center space-x-1 shadow-sm">
                  <i data-lucide="graduation-cap" class="w-3 h-3"></i>
                  <span>แบ่งตามชั้น (ป.๑-ม.๖)</span>
                </button>
                <button id="btn-sunburst-radar" class="px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1">
                  <i data-lucide="target" class="w-3 h-3"></i>
                  <span>วงแหวน ๑๐ ชั้นเรียน (Radar)</span>
                </button>
                <button id="btn-sunburst-subj" class="px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1">
                  <i data-lucide="book-open" class="w-3 h-3"></i>
                  <span>แบ่งตามกลุ่มสาระ (๘ วิชา)</span>
                </button>
              </div>
            </div>
            <span id="sunburstModeDesc" class="text-[11px] text-slate-400 font-mono hidden sm:inline">
              วงในแบ่ง ๑๐ ระดับชั้น (ป.๑ - ม.๖) ➔ ๘ วิชา ➔ ตัวชี้วัด
            </span>
          </div>

          <!-- Floating Toolbar -->
          <div class="absolute top-14 right-3.5 z-20 flex items-center space-x-1.5">
            <button id="btn-toggle-focus" class="px-2.5 py-1.5 rounded-xl bg-slate-900/90 text-emerald-400 border border-emerald-500/50 text-xs font-medium backdrop-blur shadow-md hover:bg-slate-800 transition flex items-center space-x-1.5">
              <i data-lucide="crosshair" class="w-3.5 h-3.5"></i>
              <span>โหมดโฟกัส</span>
            </button>
            <button id="btn-toggle-labels" class="px-2.5 py-1.5 rounded-xl bg-slate-900/90 text-slate-200 border border-slate-700 text-xs font-medium backdrop-blur shadow-md hover:bg-slate-800 transition flex items-center space-x-1.5">
              <i data-lucide="tag" class="w-3.5 h-3.5 text-amber-400"></i>
              <span id="label-toggle-text">ซ่อนป้ายชื่อ</span>
            </button>
            <button id="btn-reset-view" class="p-1.5 rounded-xl bg-slate-900/90 text-slate-200 border border-slate-700 text-xs font-medium backdrop-blur shadow-md hover:bg-slate-800 transition" title="รีเซ็ตตำแหน่งและมุมมอง">
              <i data-lucide="maximize-2" class="w-4 h-4"></i>
            </button>
            <button id="btn-zoom-in" class="p-1.5 rounded-xl bg-slate-900/90 text-slate-200 border border-slate-700 text-xs font-medium backdrop-blur shadow-md hover:bg-slate-800 transition" title="ซูมเข้า">
              <i data-lucide="zoom-in" class="w-4 h-4"></i>
            </button>
            <button id="btn-zoom-out" class="p-1.5 rounded-xl bg-slate-900/90 text-slate-200 border border-slate-700 text-xs font-medium backdrop-blur shadow-md hover:bg-slate-800 transition" title="ซูมออก">
              <i data-lucide="zoom-out" class="w-4 h-4"></i>
            </button>
          </div>

          <!-- Stage SVG Container -->
          <div class="graph-stage rounded-t-none" id="graphStage">
            <svg id="graphSvg" viewBox="-750 -750 1500 1500" aria-label="Thailand Curriculum Structure Map" role="img"></svg>
            <svg id="sunburstSvg" viewBox="-650 -650 1300 1300" aria-label="Thailand Curriculum Sunburst Map" role="img" class="hidden w-full h-full block"></svg>

            <!-- Floating Node Tooltip on Map -->
            <div id="graphTooltip" class="absolute pointer-events-none opacity-0 transition-opacity duration-150 z-30 px-3 py-1.5 rounded-xl bg-slate-950/95 border border-slate-700 text-white shadow-2xl text-[11px] backdrop-blur -translate-x-1/2 -translate-y-full mb-2 whitespace-nowrap">
              <div id="tooltipKind" class="text-[9px] font-mono uppercase font-bold text-emerald-400"></div>
              <div id="tooltipTitle" class="font-bold text-xs text-white"></div>
              <div id="tooltipSub" class="text-[10px] text-slate-400"></div>
            </div>

            <!-- Interaction Guidance Tag -->
            <div class="absolute bottom-3 left-1/2 -translate-x-1/2 pointer-events-none px-4 py-1.5 rounded-full bg-slate-950/85 border border-slate-800 text-[11px] text-slate-300 shadow-xl backdrop-blur flex items-center space-x-2 whitespace-nowrap">
              <i data-lucide="mouse-pointer" class="w-3.5 h-3.5 text-emerald-400"></i>
              <span>คลิกเพื่อดูรายละเอียด • ดับเบิลคลิกเพื่อดูเฉพาะกลุ่ม • เลื่อนเมาส์เพื่อซูม</span>
            </div>
          </div>
        </section>

        <!-- Right Column: Control & Filter Panel (3 cols) -->
        <aside id="controlPanel" class="lg:col-span-3 glass-panel rounded-3xl p-4 sm:p-5 flex flex-col max-h-[820px] overflow-hidden">
          <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
            <div class="flex items-center space-x-2">
              <i data-lucide="sliders-horizontal" class="w-3.5 h-3.5 text-sky-400"></i>
              <span class="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">ตัวกรองและสืบค้น</span>
            </div>
            <button id="btn-clear-filters" class="text-[11px] font-medium text-slate-400 hover:text-white transition">
              ล้างทั้งหมด
            </button>
          </div>

          <div class="overflow-y-auto pr-1 flex-1 space-y-4 text-xs">
            <!-- 1. Realtime Search -->
            <div>
              <label for="searchInput" class="block text-[11px] font-semibold text-slate-300 mb-1.5">ค้นหา สาระ / ตัวชี้วัด / รหัสวิชา</label>
              <div class="relative">
                <input
                  id="searchInput"
                  type="search"
                  placeholder="เช่น การอ่าน, ท21101, ว 1.2, ม.1..."
                  class="w-full bg-slate-950/90 border border-slate-700/80 rounded-xl px-3 py-2 pl-9 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition shadow-inner"
                />
                <i data-lucide="search" class="w-4 h-4 text-slate-500 absolute left-3 top-2.5"></i>
              </div>
              <div id="searchMatchCount" class="text-[10px] text-slate-500 mt-1"></div>
              <div id="searchMatchChips" class="flex flex-wrap gap-1 mt-1.5 max-h-24 overflow-y-auto"></div>
            </div>

            <!-- 2. Subject Pills Grid (8 Subjects) -->
            <div>
              <span class="block text-[11px] font-semibold text-slate-300 mb-1.5">กลุ่มสาระการเรียนรู้ (๘ กลุ่ม)</span>
              <div id="subjectPillGrid" class="grid grid-cols-2 gap-1.5">
                <!-- Injected via JS -->
              </div>
            </div>

            <!-- 3. Grade Filter -->
            <div>
              <label for="filterGrade" class="block text-[11px] font-semibold text-slate-300 mb-1.5">ระดับชั้นการศึกษา</label>
              <select id="filterGrade" class="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ทุกระดับชั้น (ป.1 - ม.6)</option>
                <option value="มัธยมต้น (ม.1-3)">มัธยมศึกษาตอนต้น (ม.1 - ม.3)</option>
                <option value="มัธยมปลาย (ม.4-6)">มัธยมศึกษาตอนปลาย (ม.4 - ม.6)</option>
                <option value="ประถมต้น (ป.1-3)">ประถมศึกษาตอนต้น (ป.1 - ป.3)</option>
                <option value="ประถมปลาย (ป.4-6)">ประถมศึกษาตอนปลาย (ป.4 - ป.6)</option>
                <option value="ม.1">มัธยมศึกษาปีที่ 1 (ม.1)</option>
                <option value="ม.2">มัธยมศึกษาปีที่ 2 (ม.2)</option>
                <option value="ม.3">มัธยมศึกษาปีที่ 3 (ม.3)</option>
                <option value="ม.4">มัธยมศึกษาปีที่ 4 (ม.4)</option>
                <option value="ม.5">มัธยมศึกษาปีที่ 5 (ม.5)</option>
                <option value="ม.6">มัธยมศึกษาปีที่ 6 (ม.6)</option>
                <option value="ป.1">ประถมศึกษาปีที่ 1 (ป.1)</option>
                <option value="ป.2">ประถมศึกษาปีที่ 2 (ป.2)</option>
                <option value="ป.3">ประถมศึกษาปีที่ 3 (ป.3)</option>
                <option value="ป.4">ประถมศึกษาปีที่ 4 (ป.4)</option>
                <option value="ป.5">ประถมศึกษาปีที่ 5 (ป.5)</option>
                <option value="ป.6">ประถมศึกษาปีที่ 6 (ป.6)</option>
              </select>
            </div>

            <!-- 4. Term Filter (แก้ปัญหาหาเทอมช้า) -->
            <div>
              <label for="filterTerm" class="block text-[11px] font-semibold text-slate-300 mb-1.5">ภาคเรียนที่สอน (โรงเรียนพัฒนานิคม)</label>
              <select id="filterTerm" class="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ทุกภาคเรียน (เทอม 1 และ เทอม 2)</option>
                <option value="1">ภาคเรียนที่ 1 (เทอม 1)</option>
                <option value="2">ภาคเรียนที่ 2 (เทอม 2)</option>
              </select>
            </div>

            <!-- 5. Indicator Type Filter -->
            <div>
              <label for="filterType" class="block text-[11px] font-semibold text-slate-300 mb-1.5">ประเภทตัวชี้วัด (สพฐ. ๒๕๖๖)</label>
              <select id="filterType" class="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ทุกประเภท (ระหว่างทาง + ปลายทาง)</option>
                <option value="ระหว่างทาง">ตัวชี้วัดระหว่างทาง (Formative - 1,285 ข้อ)</option>
                <option value="ปลายทาง">ตัวชี้วัดปลายทาง (Summative - 771 ข้อ)</option>
              </select>
            </div>

            <!-- 6. School Mapping Filter -->
            <div>
              <label for="filterSchool" class="block text-[11px] font-semibold text-slate-300 mb-1.5">การนำไปใช้ในหลักสูตรสถานศึกษา</label>
              <select id="filterSchool" class="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ตัวชี้วัดทั้งหมดของชาติ (2,056 ข้อ)</option>
                <option value="MAPPED">เปิดสอนใน รร.พัฒนานิคม (มีรหัสวิชารองรับ)</option>
              </select>
            </div>
          </div>
        </aside>

      </div>
    </main>

    <!-- Main View 2: Catalog Table View with Integrated Realtime Search Bar -->
    <main id="main-catalog-view" class="max-w-[1720px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-3 flex-1 hidden flex flex-col">
      <div class="glass-panel rounded-3xl p-4 sm:p-6 flex flex-col space-y-4">
        
        <!-- Catalog Header & Batch Tools -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div>
            <h2 class="text-base font-bold text-white flex items-center space-x-2">
              <i data-lucide="table-properties" class="w-4 h-4 text-emerald-400"></i>
              <span>ตารางสืบค้นตัวชี้วัด</span>
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">สืบค้นตัวชี้วัดและคัดลอกตารางสำหรับเอกสาร Word</p>
          </div>

          <div class="flex items-center space-x-2">
            <button id="btn-catalog-select-all" class="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 font-medium transition flex items-center space-x-1.5">
              <i data-lucide="check-square" class="w-3.5 h-3.5"></i>
              <span>เลือกทั้งหมดที่แสดง</span>
            </button>
            <button id="btn-catalog-copy-word" class="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white transition shadow flex items-center space-x-1.5">
              <i data-lucide="clipboard-copy" class="w-3.5 h-3.5"></i>
              <span>คัดลอกตารางลง Word</span>
            </button>
            <button id="btn-catalog-copy-plan" class="px-3 py-1.5 rounded-xl border border-emerald-500/40 bg-emerald-950/40 hover:bg-emerald-900/60 text-xs text-emerald-300 font-medium transition flex items-center space-x-1.5">
              <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
              <span>คัดลอกทำแผน</span>
            </button>
          </div>
        </div>

        <!-- Integrated Search & Filter Control Bar -->
        <div class="p-3.5 rounded-2xl bg-slate-950/90 border border-slate-800 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-12 gap-2.5">
            <!-- 1. Realtime Search Input -->
            <div class="md:col-span-5 relative">
              <input
                id="catalogSearchInput"
                type="search"
                placeholder="พิมพ์ค้นหา รหัสตัวชี้วัด, สาระ, ข้อความ, หรือรหัสวิชา..."
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 pl-9 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition shadow-inner"
              />
              <i data-lucide="search" class="w-4 h-4 text-slate-500 absolute left-3 top-2.5"></i>
            </div>

            <!-- 2. Subject Filter -->
            <div class="md:col-span-3">
              <select id="catalogFilterSubject" class="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl p-2 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ทุกกลุ่มสาระการเรียนรู้ (๘ กลุ่ม)</option>
                <option value="ภาษาไทย">ภาษาไทย</option>
                <option value="คณิตศาสตร์">คณิตศาสตร์</option>
                <option value="วิทยาศาสตร์และเทคโนโลยี">วิทยาศาสตร์และเทคโนโลยี</option>
                <option value="สังคมศึกษา ศาสนา และวัฒนธรรม">สังคมศึกษา ศาสนา และวัฒนธรรม</option>
                <option value="สุขศึกษาและพลศึกษา">สุขศึกษาและพลศึกษา</option>
                <option value="ศิลปะ">ศิลปะ</option>
                <option value="การงานอาชีพ">การงานอาชีพ</option>
                <option value="ภาษาต่างประเทศ">ภาษาต่างประเทศ</option>
              </select>
            </div>

            <!-- 3. Grade Filter -->
            <div class="md:col-span-2">
              <select id="catalogFilterGrade" class="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl p-2 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ทุกระดับชั้น (ป.1 - ม.6)</option>
                <option value="มัธยมต้น (ม.1-3)">มัธยมต้น (ม.1-3)</option>
                <option value="มัธยมปลาย (ม.4-6)">มัธยมปลาย (ม.4-6)</option>
                <option value="ประถมต้น (ป.1-3)">ประถมต้น (ป.1-3)</option>
                <option value="ประถมปลาย (ป.4-6)">ประถมปลาย (ป.4-6)</option>
                <option value="ม.1">มัธยมศึกษาปีที่ 1 (ม.1)</option>
                <option value="ม.2">มัธยมศึกษาปีที่ 2 (ม.2)</option>
                <option value="ม.3">มัธยมศึกษาปีที่ 3 (ม.3)</option>
                <option value="ม.4">มัธยมศึกษาปีที่ 4 (ม.4)</option>
                <option value="ม.5">มัธยมศึกษาปีที่ 5 (ม.5)</option>
                <option value="ม.6">มัธยมศึกษาปีที่ 6 (ม.6)</option>
              </select>
            </div>

            <!-- 4. Type Filter -->
            <div class="md:col-span-2">
              <select id="catalogFilterType" class="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl p-2 focus:border-emerald-500 focus:outline-none">
                <option value="ALL">ทุกประเภทตัวชี้วัด</option>
                <option value="ระหว่างทาง">ตัวชี้วัดระหว่างทาง (Formative)</option>
                <option value="ปลายทาง">ตัวชี้วัดปลายทาง (Summative)</option>
              </select>
            </div>
          </div>

          <!-- Result Count Bar -->
          <div class="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80">
            <div id="catalogResultCount" class="font-mono text-[11px] text-emerald-400 font-semibold">
              กำลังคำนวณผลการค้นหา...
            </div>
            <div class="flex items-center space-x-2">
              <button id="btn-catalog-clear-search" class="text-[11px] text-slate-400 hover:text-white transition">
                ล้างคำค้นหา
              </button>
            </div>
          </div>
        </div>

        <!-- Catalog Table -->
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-slate-950 text-slate-400 font-mono border-b border-slate-800">
                <th class="p-3 w-10 text-center"><i data-lucide="check" class="w-3.5 h-3.5 mx-auto"></i></th>
                <th class="p-3 whitespace-nowrap">รหัสตัวชี้วัด</th>
                <th class="p-3 whitespace-nowrap">กลุ่มสาระ (สาระ)</th>
                <th class="p-3 whitespace-nowrap text-center">ประเภท</th>
                <th class="p-3 min-w-[280px]">ข้อความตัวชี้วัด</th>
                <th class="p-3 min-w-[240px]">สาระการเรียนรู้แกนกลาง</th>
                <th class="p-3 whitespace-nowrap">วิชาที่สอน (พัฒนานิคม)</th>
                <th class="p-3 w-28 text-center">การกระทำ</th>
              </tr>
            </thead>
            <tbody id="catalog-table-tbody" class="divide-y divide-slate-800/60 text-slate-300">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>

        <div id="catalogPaginationStrip" class="text-center py-2">
          <!-- Show more button if filtered > 150 -->
        </div>

      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-900/80 bg-slate-950/80 px-4 sm:px-6 lg:px-8 py-3 mt-auto">
      <div class="max-w-[1720px] mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
        <div>
          หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน พ.ศ. ๒๕๕๑ (ฉบับปรับปรุง ๒๕๖๐) • โรงเรียนพัฒนานิคม จ.ลพบุรี
        </div>
        <div class="flex items-center space-x-3">
          <span>ฐานข้อมูล ๒,๐๕๖ ตัวชี้วัด</span>
          <span>•</span>
          <a href="https://github.com/cutoutppp/CurriculumMD" target="_blank" class="hover:text-emerald-400 transition">GitHub Repository</a>
        </div>
      </div>
    </footer>

  </div>

  <!-- Help & Manual Modal -->
  <div id="helpModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 hidden">
    <div class="bg-slate-900 border border-slate-700 max-w-xl w-full rounded-2xl p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-white flex items-center space-x-2">
          <i data-lucide="help-circle" class="w-5 h-5 text-amber-400"></i>
          <span>คู่มือการใช้งาน</span>
        </h3>
        <button id="btn-close-help" class="text-slate-400 hover:text-white"><i data-lucide="x" class="w-5 h-5"></i></button>
      </div>
      <div class="space-y-3 text-xs text-slate-300 leading-relaxed max-h-[60vh] overflow-y-auto pr-1">
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
          <strong class="text-emerald-400 block mb-1">๑. มุมมองวงกลมแบ่งชั้น (Sunburst Chart) และแผนภาพโครงข่าย</strong>
          <p>• สลับระหว่าง <span class="text-white font-semibold">"แผนภาพโครงข่าย"</span> (จุดเชื่อมโยงรัศมี) และ <span class="text-cyan-400 font-semibold">"วงกลมแบ่งชั้น"</span> (วงแหวนแบ่งชั้น ๔ ระดับซ้อนกัน) ได้จากแถบมุมมองด้านบน</p>
          <p>• ในวงกลมแบ่งชั้น แต่ละชั้นคือ: ๘ กลุ่มสาระ (วงใน) ➔ ๓๑ สาระ ➔ ๕๕ มาตรฐาน ➔ ตัวชี้วัด (วงนอกสุด)</p>
          <strong class="text-emerald-400 block mt-2 mb-1">๒. การดูเฉพาะกลุ่ม (เจาะลึกวงย่อย)</strong>
          <p>• คลิกเลือกจุดใดในแผนภาพ (กลุ่มสาระ / สาระ / มาตรฐาน) แล้วกดปุ่ม <span class="text-cyan-400 font-semibold">"ดูเฉพาะ..."</span> หรือ <span class="text-white font-semibold">ดับเบิลคลิกที่โหนดนั้น</span></p>
          <p>• แผนภาพจะแสดงจุดที่เลือกเป็นศูนย์กลาง และกระจายรายการย่อยรอบวง ๓๖๐ องศา เพื่อให้อ่านรายละเอียดได้สะดวก</p>
          <p>• กดปุ่ม <span class="text-emerald-400 font-semibold">"ย้อนกลับ"</span> หรือคลิกที่แถบด้านบนเพื่อกลับสู่วงหลัก</p>
        </div>
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
          <strong class="text-sky-400 block mb-1">๒. การสืบค้นในตาราง</strong>
          <p>• สลับมาที่แท็บ <span class="text-emerald-400 font-semibold">"ตารางสืบค้น"</span> สามารถพิมพ์ค้นหาข้อความ, รหัสตัวชี้วัด (เช่น ท 1.1), หรือรหัสวิชา (เช่น ว21101) ได้ทันที</p>
          <p>• เลือกกรองตามกลุ่มสาระ, ระดับชั้น หรือประเภทตัวชี้วัดระหว่างทาง/ปลายทางได้</p>
          <p>• เลือกรายการที่ต้องการ แล้วกดปุ่ม <span class="text-emerald-400 font-semibold">"คัดลอกตารางลง Word"</span> เพื่อนำไปวางในเอกสาร</p>
        </div>
      </div>
      <div class="pt-2 text-right">
        <button id="btn-help-understood" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition">
          ปิด
        </button>
      </div>
    </div>
  </div>

  <!-- Load KPI Master Data Bundle -->
  <script src="kpi_data.js"></script>

  <!-- Interactive Map & Portal Core Script -->
  <script>
    const SVG_NS = "http://www.w3.org/2000/svg";
    const DATA = (typeof OPEN_CURRICULUM_DATA !== 'undefined' ? OPEN_CURRICULUM_DATA : (window.OPEN_CURRICULUM_DATA || {}));

    // State
    const state = {
      viewMode: 'map', // 'map', 'sunburst', or 'catalog'
      sunburstMode: 'grade', // 'grade' (ป.๑-ม.๖), 'radar' (10 concentric rings), 'subject' (๘ กลุ่มสาระ)
      drillNodeId: 'root-curriculum', // Active center of radial circle
      selectedNodeId: 'root-curriculum',
      search: '',
      subject: 'ALL',
      grade: 'ALL',
      term: 'ALL',
      type: 'ALL',
      school: 'ALL',
      focusMode: true,
      showLabels: true,
      selectedKpiCodes: new Set(),
      catalogLimit: 150
    };

    const graphState = {
      scale: 1,
      translateX: 0,
      translateY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0
    };

    const ZOOM_LIMITS = { min: 0.25, max: 8 };

    // Elements Lookup
    const el = {
      graphSvg: document.getElementById('graphSvg'),
      graphStage: document.getElementById('graphStage'),
      graphTooltip: document.getElementById('graphTooltip'),
      tooltipKind: document.getElementById('tooltipKind'),
      tooltipTitle: document.getElementById('tooltipTitle'),
      tooltipSub: document.getElementById('tooltipSub'),
      drillBreadcrumb: document.getElementById('drillBreadcrumb'),
      btnDrillUp: document.getElementById('btn-drill-up'),
      infoContent: document.getElementById('infoContent'),
      searchInput: document.getElementById('searchInput'),
      searchMatchChips: document.getElementById('searchMatchChips'),
      searchMatchCount: document.getElementById('searchMatchCount'),
      subjectPillGrid: document.getElementById('subjectPillGrid'),
      filterGrade: document.getElementById('filterGrade'),
      filterTerm: document.getElementById('filterTerm'),
      filterType: document.getElementById('filterType'),
      filterSchool: document.getElementById('filterSchool'),
      btnToggleFocus: document.getElementById('btn-toggle-focus'),
      btnToggleLabels: document.getElementById('btn-toggle-labels'),
      labelToggleText: document.getElementById('label-toggle-text'),
      btnResetView: document.getElementById('btn-reset-view'),
      btnZoomIn: document.getElementById('btn-zoom-in'),
      btnZoomOut: document.getElementById('btn-zoom-out'),
      btnPanelReset: document.getElementById('btn-panel-reset'),
      btnClearFilters: document.getElementById('btn-clear-filters'),
      mainMapView: document.getElementById('main-map-view'),
      mainCatalogView: document.getElementById('main-catalog-view'),
      btnViewMap: document.getElementById('btn-view-map'),
      btnViewSunburst: document.getElementById('btn-view-sunburst'),
      btnViewCatalog: document.getElementById('btn-view-catalog'),
      sunburstSvg: document.getElementById('sunburstSvg'),
      sunburstModeBar: document.getElementById('sunburstModeBar'),
      btnSunburstGrade: document.getElementById('btn-sunburst-grade'),
      btnSunburstRadar: document.getElementById('btn-sunburst-radar'),
      btnSunburstSubj: document.getElementById('btn-sunburst-subj'),
      sunburstModeDesc: document.getElementById('sunburstModeDesc'),
      catalogSearchInput: document.getElementById('catalogSearchInput'),
      catalogFilterSubject: document.getElementById('catalogFilterSubject'),
      catalogFilterGrade: document.getElementById('catalogFilterGrade'),
      catalogFilterType: document.getElementById('catalogFilterType'),
      catalogResultCount: document.getElementById('catalogResultCount'),
      btnCatalogClearSearch: document.getElementById('btn-catalog-clear-search'),
      catalogTbody: document.getElementById('catalog-table-tbody'),
      catalogPaginationStrip: document.getElementById('catalogPaginationStrip')
    };

    // SVG Layer Groups
    const viewportGroup = createSvgElement('g', { class: 'graph-viewport' });
    const ringsGroup = createSvgElement('g', { class: 'layer-rings' });
    const edgesGroup = createSvgElement('g', { class: 'layer-edges' });
    const haloGroup = createSvgElement('g', { class: 'layer-halo' });
    const nodesGroup = createSvgElement('g', { class: 'layer-nodes' });
    viewportGroup.append(ringsGroup, edgesGroup, haloGroup, nodesGroup);
    el.graphSvg.appendChild(viewportGroup);

    // Sunburst SVG Layer Groups
    const sunburstViewportGroup = createSvgElement('g', { class: 'sunburst-viewport' });
    const sunburstRingsGroup = createSvgElement('g', { class: 'sunburst-rings' });
    const sunburstSlicesGroup = createSvgElement('g', { class: 'sunburst-slices' });
    const sunburstLabelsGroup = createSvgElement('g', { class: 'sunburst-labels' });
    sunburstViewportGroup.append(sunburstRingsGroup, sunburstSlicesGroup, sunburstLabelsGroup);
    if (el.sunburstSvg) el.sunburstSvg.appendChild(sunburstViewportGroup);

    // Global Graph Data Store
    let graph = null;
    let sunburstData = null;
    let semesterCatalog = null;

    // Helper: Normalize Thai search text
    function normText(str) {
      if (!str) return '';
      const digits = ['๐','๑','๒','๓','๔','๕','๖','๗','๘','๙'];
      let s = str.toLowerCase();
      for (let i = 0; i < 10; i++) s = s.replaceAll(digits[i], String(i));
      return s.replace(/\\s+/g, '');
    }

    function createSvgElement(tag, attrs = {}) {
      const node = document.createElementNS(SVG_NS, tag);
      for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
      return node;
    }

    // Init
    document.addEventListener('DOMContentLoaded', async () => {
      lucide.createIcons();

      // Try load semester_catalog.json
      try {
        const res = await fetch('./semester_catalog.json');
        if (res.ok) semesterCatalog = await res.json();
      } catch (err) {
        console.warn('semester_catalog.json not loaded, falling back to kpi_data.js courses:', err);
      }

      if (DATA.kpis && DATA.kpis.length > 0) {
        DATA.kpis.forEach(k => {
          k.searchIndex = normText(`${k.code} ${k.text} ${k.standard} ${k.type || ''} ${k.standard_desc || ''} ${k.strand || ''} ${k.core_content || ''} ${(k.courses || []).join(' ')}`);
        });
        loadView(state.drillNodeId);
        populateControls();
        bindEvents();
      }
    });

    // Polar Math & SVG Arc Helpers for Sunburst
    function polarToCartesian(cx, cy, r, angleRad) {
      return {
        x: cx + r * Math.cos(angleRad),
        y: cy + r * Math.sin(angleRad)
      };
    }

    function createSunburstArc(cx, cy, rInner, rOuter, startAngle, endAngle) {
      const diff = endAngle - startAngle;
      if (diff >= Math.PI * 2 - 0.0001) {
        const p1 = polarToCartesian(cx, cy, rOuter, 0);
        const p2 = polarToCartesian(cx, cy, rOuter, Math.PI);
        const p3 = polarToCartesian(cx, cy, rInner, Math.PI);
        const p4 = polarToCartesian(cx, cy, rInner, 0);
        const innerPart = rInner > 0
          ? `M ${p4.x.toFixed(2)} ${p4.y.toFixed(2)} A ${rInner} ${rInner} 0 1 0 ${p3.x.toFixed(2)} ${p3.y.toFixed(2)} A ${rInner} ${rInner} 0 1 0 ${p4.x.toFixed(2)} ${p4.y.toFixed(2)} Z`
          : 'Z';
        return `M ${p1.x.toFixed(2)} ${p1.y.toFixed(2)} A ${rOuter} ${rOuter} 0 1 1 ${p2.x.toFixed(2)} ${p2.y.toFixed(2)} A ${rOuter} ${rOuter} 0 1 1 ${p1.x.toFixed(2)} ${p1.y.toFixed(2)} ${innerPart}`;
      }

      const pad = (rInner > 0 && diff > 0.035) ? 0.004 : 0.0;
      let a0 = startAngle + pad;
      let a1 = endAngle - pad;
      if (a1 <= a0) { a0 = startAngle; a1 = endAngle; }

      const startOuter = polarToCartesian(cx, cy, rOuter, a0);
      const endOuter = polarToCartesian(cx, cy, rOuter, a1);
      const startInner = polarToCartesian(cx, cy, rInner, a1);
      const endInner = polarToCartesian(cx, cy, rInner, a0);
      const largeArc = (a1 - a0) > Math.PI ? '1' : '0';

      if (rInner <= 0) {
        return `M ${cx} ${cy} L ${startOuter.x.toFixed(2)} ${startOuter.y.toFixed(2)} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${endOuter.x.toFixed(2)} ${endOuter.y.toFixed(2)} Z`;
      }

      return `M ${startOuter.x.toFixed(2)} ${startOuter.y.toFixed(2)} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${endOuter.x.toFixed(2)} ${endOuter.y.toFixed(2)} L ${startInner.x.toFixed(2)} ${startInner.y.toFixed(2)} A ${rInner} ${rInner} 0 ${largeArc} 0 ${endInner.x.toFixed(2)} ${endInner.y.toFixed(2)} Z`;
    }

    // Master View Loader: Re-centers on drillNodeId
    function loadView(drillNodeId, selectId = null) {
      state.drillNodeId = drillNodeId;
      graphState.scale = 1;
      graphState.translateX = 0;
      graphState.translateY = 0;
      updateViewportTransform();

      graph = buildGraphForView(drillNodeId, DATA);
      renderStaticGraph();

      sunburstData = buildSunburstForView(drillNodeId, DATA);
      renderSunburstGraph();

      renderBreadcrumb();
      applyFilters();

      const toSelect = selectId || graph.centerNode.id;
      selectNode(toSelect, false);
    }

    // Drill-down Radial Graph Engine across all 4 levels:
    // Root -> Subject -> Strand -> Standard
    function buildGraphForView(drillNodeId, DATA) {
      const subjectOrder = [
        'ภาษาไทย', 'คณิตศาสตร์', 'วิทยาศาสตร์และเทคโนโลยี', 'สังคมศึกษา ศาสนา และวัฒนธรรม',
        'สุขศึกษาและพลศึกษา', 'ศิลปะ', 'การงานอาชีพ', 'ภาษาต่างประเทศ'
      ];

      // Pre-group hierarchical tree
      const hierarchy = {};
      DATA.kpis.forEach(k => {
        k.searchIndex = normText(`${k.code} ${k.text} ${k.standard} ${k.standard_desc || ''} ${k.strand || ''} ${k.core_content || ''} ${(k.courses || []).join(' ')}`);
        const subj = k.subject;
        const strand = k.strand || 'สาระทั่วไป';
        const std = k.standard;
        if (!hierarchy[subj]) hierarchy[subj] = {};
        if (!hierarchy[subj][strand]) hierarchy[subj][strand] = {};
        if (!hierarchy[subj][strand][std]) hierarchy[subj][strand][std] = [];
        hierarchy[subj][strand][std].push(k);
      });

      const nodes = [];
      const nodeById = new Map();
      const edges = [];
      const neighborMap = new Map();

      function addNode(n) {
        nodes.push(n);
        nodeById.set(n.id, n);
        if (!neighborMap.has(n.id)) neighborMap.set(n.id, new Set([n.id]));
      }

      function addEdge(sourceId, targetId, color, width) {
        edges.push({ id: `edge-${sourceId}-${targetId}`, source: sourceId, target: targetId, color, width });
        if (!neighborMap.has(sourceId)) neighborMap.set(sourceId, new Set([sourceId]));
        if (!neighborMap.has(targetId)) neighborMap.set(targetId, new Set([targetId]));
        neighborMap.get(sourceId).add(targetId);
        neighborMap.get(targetId).add(sourceId);
      }

      let centerNode = null;
      let rings = [];

      if (!drillNodeId || drillNodeId === 'root-curriculum') {
        // ==========================================
        // 1. GLOBAL 5-LEVEL VIEW (Full Curriculum)
        // ==========================================
        centerNode = {
          id: 'root-curriculum',
          kind: 'root',
          name: 'หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน',
          code: 'CurriculumMD',
          shortLabel: 'หลักสูตรแกนกลาง',
          subLabel: 'พ.ศ. ๒๕๕๑ (ปรับปรุง ๒๕๖๐) • ๘ กลุ่มสาระ • ๓๑ สาระ • ๕๕ มาตรฐาน',
          x: 0,
          y: 0,
          size: 18,
          color: '#0d3d70'
        };
        addNode(centerNode);

        rings = [
          { r: 130, label: 'วงที่ ๑: กลุ่มสาระการเรียนรู้ (๘)' },
          { r: 260, label: 'วงที่ ๒: สาระการเรียนรู้ (๓๑ สาระ)' },
          { r: 390, label: 'วงที่ ๓: มาตรฐานการเรียนรู้ (๕๕)' },
          { r: 540, label: 'วงที่ ๔: ตัวชี้วัดแกนกลาง (๒,๐๕๖)' }
        ];

        const totalKpis = DATA.kpis.length;
        let angleCursor = -Math.PI / 2;

        subjectOrder.forEach(subj => {
          const sMeta = DATA.subject_meta[subj] || { color: '#64748b' };
          const strandsObj = hierarchy[subj] || {};
          const sKpis = DATA.kpis.filter(k => k.subject === subj);
          const sSpan = (Math.PI * 2 * sKpis.length) / totalKpis;

          const sStartAngle = angleCursor;
          const sEndAngle = angleCursor + sSpan;
          const sMidAngle = (sStartAngle + sEndAngle) / 2;

          const sNode = {
            id: `subj-${sMeta.code || subj}`,
            kind: 'subject',
            name: subj,
            code: sMeta.code || subj,
            shortLabel: subj,
            color: sMeta.color || '#3b82f6',
            kpiCount: sKpis.length,
            angle: sMidAngle,
            x: Math.round(Math.cos(sMidAngle) * 130),
            y: Math.round(Math.sin(sMidAngle) * 130),
            size: 14,
            data: {
              why: DATA.subject_overviews?.[subj]?.why || '',
              what: DATA.subject_overviews?.[subj]?.what || '',
              quality: DATA.subject_overviews?.[subj]?.quality || {}
            }
          };
          addNode(sNode);
          addEdge(centerNode.id, sNode.id, sNode.color, 2.2);

          // Strands
          let stAngleCursor = sStartAngle;
          Object.entries(strandsObj).forEach(([strandName, stdObj], stIdx) => {
            const stKpis = Object.values(stdObj).flat();
            const stSpan = (sSpan * stKpis.length) / Math.max(sKpis.length, 1);
            const stStartAngle = stAngleCursor;
            const stEndAngle = stAngleCursor + stSpan;
            const stMidAngle = (stStartAngle + stEndAngle) / 2;

            const strandMatch = strandName.match(/สาระที่\\s*([0-9๑-๙]+)\\s*(.*)/);
            const strandNum = strandMatch ? strandMatch[1] : String(stIdx + 1);
            const strandTitle = strandMatch && strandMatch[2] ? strandMatch[2].trim() : strandName;

            const stNode = {
              id: `strand-${sMeta.code}-${strandNum}`,
              kind: 'strand',
              name: strandName,
              shortLabel: `สาระที่ ${strandNum}`,
              subLabel: strandTitle,
              subject: subj,
              subjectId: sNode.id,
              kpiCount: stKpis.length,
              standardsCount: Object.keys(stdObj).length,
              color: sNode.color,
              angle: stMidAngle,
              x: Math.round(Math.cos(stMidAngle) * 260),
              y: Math.round(Math.sin(stMidAngle) * 260),
              size: 10
            };
            addNode(stNode);
            addEdge(sNode.id, stNode.id, sNode.color, 1.6);

            // Standards
            let stdAngleCursor = stStartAngle;
            Object.entries(stdObj).forEach(([stdCode, stdKpis]) => {
              const stdSpan = (stSpan * stdKpis.length) / Math.max(stKpis.length, 1);
              const stdStartAngle = stdAngleCursor;
              const stdEndAngle = stdAngleCursor + stdSpan;
              const stdMidAngle = (stdStartAngle + stdEndAngle) / 2;
              const stdDesc = DATA.standards[stdCode] || '';

              const stdNode = {
                id: `std-${stdCode.replace(/\\s+/g, '_')}`,
                kind: 'standard',
                code: stdCode,
                name: `มาตรฐาน ${stdCode}`,
                shortLabel: stdCode,
                subLabel: stdDesc,
                desc: stdDesc,
                strand: strandName,
                strandId: stNode.id,
                subject: subj,
                subjectId: sNode.id,
                kpiCount: stdKpis.length,
                color: sNode.color,
                angle: stdMidAngle,
                x: Math.round(Math.cos(stdMidAngle) * 390),
                y: Math.round(Math.sin(stdMidAngle) * 390),
                size: 7,
                formativeCount: stdKpis.filter(k => k.type === 'ระหว่างทาง').length,
                summativeCount: stdKpis.filter(k => k.type === 'ปลายทาง').length
              };
              addNode(stdNode);
              addEdge(stNode.id, stdNode.id, sNode.color, 1.2);

              // KPIs
              const kpiStep = stdSpan / Math.max(stdKpis.length, 1);
              stdKpis.forEach((k, kIdx) => {
                const kAngle = stdStartAngle + kpiStep * (kIdx + 0.5);
                const radiusOffset = (kIdx % 4) * 12;
                const kRadius = 530 + radiusOffset;

                const kNode = {
                  id: `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`,
                  kind: 'kpi',
                  code: k.code,
                  name: k.code,
                  shortLabel: k.code.split(' ').pop() || k.code,
                  fullText: k.text,
                  coreContent: k.core_content || '',
                  type: k.type,
                  grade: k.grade,
                  gradeBand: k.grade_band,
                  strand: strandName,
                  strandId: stNode.id,
                  standard: stdCode,
                  standardId: stdNode.id,
                  standardDesc: stdDesc,
                  subject: subj,
                  subjectId: sNode.id,
                  courses: k.courses || [],
                  searchIndex: k.searchIndex,
                  angle: kAngle,
                  x: Math.round(Math.cos(kAngle) * kRadius),
                  y: Math.round(Math.sin(kAngle) * kRadius),
                  size: k.type === 'ปลายทาง' ? 5 : 4,
                  color: k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8'
                };
                addNode(kNode);
                addEdge(stdNode.id, kNode.id, kNode.color, 0.75);
              });
              stdAngleCursor = stdEndAngle;
            });
            stAngleCursor = stEndAngle;
          });
          angleCursor = sEndAngle;
        });

      } else if (drillNodeId.startsWith('subj-')) {
        // ==========================================
        // 2. SUBJECT DRILL-DOWN VIEW (360° Circle)
        // ==========================================
        const targetMetaCode = drillNodeId.replace('subj-', '');
        const subjEntry = Object.entries(DATA.subject_meta).find(([name, meta]) => (meta.code || name) === targetMetaCode);
        const subjName = subjEntry ? subjEntry[0] : targetMetaCode;
        const sMeta = DATA.subject_meta[subjName] || { color: '#3b82f6' };
        const strandsObj = hierarchy[subjName] || {};
        const sKpis = DATA.kpis.filter(k => k.subject === subjName);

        centerNode = {
          id: drillNodeId,
          kind: 'subject',
          name: subjName,
          code: sMeta.code || subjName,
          shortLabel: subjName,
          subLabel: `กลุ่มสาระการเรียนรู้ (${sKpis.length} ตัวชี้วัด)`,
          color: sMeta.color,
          x: 0,
          y: 0,
          size: 24,
          isDrillCenter: true,
          data: {
            why: DATA.subject_overviews?.[subjName]?.why || '',
            what: DATA.subject_overviews?.[subjName]?.what || '',
            quality: DATA.subject_overviews?.[subjName]?.quality || {}
          }
        };
        addNode(centerNode);

        const strandEntries = Object.entries(strandsObj);
        const stdCount = strandEntries.reduce((acc, [, stdObj]) => acc + Object.keys(stdObj).length, 0);

        rings = [
          { r: 160, label: `วงที่ ๑: สาระการเรียนรู้ (${strandEntries.length} สาระ)` },
          { r: 300, label: `วงที่ ๒: มาตรฐานการเรียนรู้ (${stdCount} มาตรฐาน)` },
          { r: 470, label: `วงที่ ๓: ตัวชี้วัด (${sKpis.length} ตัวชี้วัด)` }
        ];

        let angleCursor = -Math.PI / 2;
        strandEntries.forEach(([strandName, stdObj], stIdx) => {
          const stKpis = Object.values(stdObj).flat();
          const stSpan = (Math.PI * 2 * stKpis.length) / Math.max(sKpis.length, 1);
          const stStartAngle = angleCursor;
          const stEndAngle = angleCursor + stSpan;
          const stMidAngle = (stStartAngle + stEndAngle) / 2;

          const strandMatch = strandName.match(/สาระที่\\s*([0-9๑-๙]+)\\s*(.*)/);
          const strandNum = strandMatch ? strandMatch[1] : String(stIdx + 1);
          const strandTitle = strandMatch && strandMatch[2] ? strandMatch[2].trim() : strandName;

          const stNode = {
            id: `strand-${sMeta.code}-${strandNum}`,
            kind: 'strand',
            name: strandName,
            shortLabel: `สาระที่ ${strandNum}`,
            subLabel: strandTitle,
            subject: subjName,
            subjectId: centerNode.id,
            kpiCount: stKpis.length,
            standardsCount: Object.keys(stdObj).length,
            color: sMeta.color,
            angle: stMidAngle,
            x: Math.round(Math.cos(stMidAngle) * 160),
            y: Math.round(Math.sin(stMidAngle) * 160),
            size: 13
          };
          addNode(stNode);
          addEdge(centerNode.id, stNode.id, sMeta.color, 2.4);

          // Standards
          let stdAngleCursor = stStartAngle;
          Object.entries(stdObj).forEach(([stdCode, stdKpis]) => {
            const stdSpan = (stSpan * stdKpis.length) / Math.max(stKpis.length, 1);
            const stdStartAngle = stdAngleCursor;
            const stdEndAngle = stdAngleCursor + stdSpan;
            const stdMidAngle = (stdStartAngle + stdEndAngle) / 2;
            const stdDesc = DATA.standards[stdCode] || '';

            const stdNode = {
              id: `std-${stdCode.replace(/\\s+/g, '_')}`,
              kind: 'standard',
              code: stdCode,
              name: `มาตรฐาน ${stdCode}`,
              shortLabel: stdCode,
              subLabel: stdDesc,
              desc: stdDesc,
              strand: strandName,
              strandId: stNode.id,
              subject: subjName,
              subjectId: centerNode.id,
              kpiCount: stdKpis.length,
              color: sMeta.color,
              angle: stdMidAngle,
              x: Math.round(Math.cos(stdMidAngle) * 300),
              y: Math.round(Math.sin(stdMidAngle) * 300),
              size: 10,
              formativeCount: stdKpis.filter(k => k.type === 'ระหว่างทาง').length,
              summativeCount: stdKpis.filter(k => k.type === 'ปลายทาง').length
            };
            addNode(stdNode);
            addEdge(stNode.id, stdNode.id, sMeta.color, 1.8);

            // KPIs
            const kpiStep = stdSpan / Math.max(stdKpis.length, 1);
            stdKpis.forEach((k, kIdx) => {
              const kAngle = stdStartAngle + kpiStep * (kIdx + 0.5);
              const radiusOffset = (kIdx % 4) * 14;
              const kRadius = 460 + radiusOffset;

              const kNode = {
                id: `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`,
                kind: 'kpi',
                code: k.code,
                name: k.code,
                shortLabel: k.code.split(' ').pop() || k.code,
                fullText: k.text,
                coreContent: k.core_content || '',
                type: k.type,
                grade: k.grade,
                gradeBand: k.grade_band,
                strand: strandName,
                strandId: stNode.id,
                standard: stdCode,
                standardId: stdNode.id,
                standardDesc: stdDesc,
                subject: subjName,
                subjectId: centerNode.id,
                courses: k.courses || [],
                searchIndex: k.searchIndex,
                angle: kAngle,
                x: Math.round(Math.cos(kAngle) * kRadius),
                y: Math.round(Math.sin(kAngle) * kRadius),
                size: k.type === 'ปลายทาง' ? 6 : 5,
                color: k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8'
              };
              addNode(kNode);
              addEdge(stdNode.id, kNode.id, kNode.color, 1);
            });
            stdAngleCursor = stdEndAngle;
          });
          angleCursor = stEndAngle;
        });

      } else if (drillNodeId.startsWith('strand-')) {
        // ==========================================
        // 3. STRAND DRILL-DOWN VIEW (360° Circle)
        // ==========================================
        const targetStrandKpis = DATA.kpis.filter(k => {
          const strandMatch = (k.strand || '').match(/สาระที่\\s*([0-9๑-๙]+)/);
          const strandNum = strandMatch ? strandMatch[1] : '';
          const sMeta = DATA.subject_meta[k.subject] || {};
          return `strand-${sMeta.code}-${strandNum}` === drillNodeId;
        });

        const sampleKpi = targetStrandKpis[0] || {};
        const strandName = sampleKpi.strand || 'สาระการเรียนรู้';
        const subjName = sampleKpi.subject || 'กลุ่มสาระ';
        const sMeta = DATA.subject_meta[subjName] || { color: '#10b981' };

        centerNode = {
          id: drillNodeId,
          kind: 'strand',
          name: strandName,
          code: drillNodeId,
          shortLabel: strandName,
          subLabel: `${subjName} (${targetStrandKpis.length} ตัวชี้วัด)`,
          color: sMeta.color,
          subject: subjName,
          subjectId: `subj-${sMeta.code || subjName}`,
          x: 0,
          y: 0,
          size: 24,
          isDrillCenter: true
        };
        addNode(centerNode);

        const stdGroups = {};
        targetStrandKpis.forEach(k => {
          if (!stdGroups[k.standard]) stdGroups[k.standard] = [];
          stdGroups[k.standard].push(k);
        });

        const stdEntries = Object.entries(stdGroups);
        rings = [
          { r: 200, label: `วงที่ ๑: มาตรฐานในสาระนี้ (${stdEntries.length} มาตรฐาน)` },
          { r: 420, label: `วงที่ ๒: ตัวชี้วัดทั้งหมด (${targetStrandKpis.length} ข้อ)` }
        ];

        let angleCursor = -Math.PI / 2;
        stdEntries.forEach(([stdCode, stdKpis]) => {
          const stdSpan = (Math.PI * 2 * stdKpis.length) / Math.max(targetStrandKpis.length, 1);
          const stdStartAngle = angleCursor;
          const stdEndAngle = angleCursor + stdSpan;
          const stdMidAngle = (stdStartAngle + stdEndAngle) / 2;
          const stdDesc = DATA.standards[stdCode] || '';

          const stdNode = {
            id: `std-${stdCode.replace(/\\s+/g, '_')}`,
            kind: 'standard',
            code: stdCode,
            name: `มาตรฐาน ${stdCode}`,
            shortLabel: stdCode,
            subLabel: stdDesc,
            desc: stdDesc,
            strand: strandName,
            strandId: centerNode.id,
            subject: subjName,
            subjectId: centerNode.subjectId,
            kpiCount: stdKpis.length,
            color: sMeta.color,
            angle: stdMidAngle,
            x: Math.round(Math.cos(stdMidAngle) * 200),
            y: Math.round(Math.sin(stdMidAngle) * 200),
            size: 13,
            formativeCount: stdKpis.filter(k => k.type === 'ระหว่างทาง').length,
            summativeCount: stdKpis.filter(k => k.type === 'ปลายทาง').length
          };
          addNode(stdNode);
          addEdge(centerNode.id, stdNode.id, sMeta.color, 2.2);

          // KPIs
          const kpiStep = stdSpan / Math.max(stdKpis.length, 1);
          stdKpis.forEach((k, kIdx) => {
            const kAngle = stdStartAngle + kpiStep * (kIdx + 0.5);
            const radiusOffset = (kIdx % 3) * 20;
            const kRadius = 400 + radiusOffset;

            const kNode = {
              id: `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`,
              kind: 'kpi',
              code: k.code,
              name: k.code,
              shortLabel: k.code.split(' ').pop() || k.code,
              fullText: k.text,
              coreContent: k.core_content || '',
              type: k.type,
              grade: k.grade,
              gradeBand: k.grade_band,
              strand: strandName,
              strandId: centerNode.id,
              standard: stdCode,
              standardId: stdNode.id,
              standardDesc: stdDesc,
              subject: subjName,
              subjectId: centerNode.subjectId,
              courses: k.courses || [],
              searchIndex: k.searchIndex,
              angle: kAngle,
              x: Math.round(Math.cos(kAngle) * kRadius),
              y: Math.round(Math.sin(kAngle) * kRadius),
              size: k.type === 'ปลายทาง' ? 7 : 6,
              color: k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8'
            };
            addNode(kNode);
            addEdge(stdNode.id, kNode.id, kNode.color, 1.2);
          });
          angleCursor = stdEndAngle;
        });

      } else if (drillNodeId.startsWith('std-')) {
        // ==========================================
        // 4. STANDARD DRILL-DOWN VIEW (360° Circle)
        // ==========================================
        const rawStdCode = drillNodeId.replace('std-', '').replace(/_/g, ' ');
        const stdKpis = DATA.kpis.filter(k => k.standard === rawStdCode);
        const sampleKpi = stdKpis[0] || {};
        const subjName = sampleKpi.subject || 'กลุ่มสาระ';
        const strandName = sampleKpi.strand || 'สาระ';
        const stdDesc = DATA.standards[rawStdCode] || '';
        const sMeta = DATA.subject_meta[subjName] || { color: '#3b82f6' };

        centerNode = {
          id: drillNodeId,
          kind: 'standard',
          name: `มาตรฐาน ${rawStdCode}`,
          code: rawStdCode,
          shortLabel: rawStdCode,
          subLabel: `${subjName} • ${strandName}`,
          desc: stdDesc,
          color: sMeta.color,
          subject: subjName,
          subjectId: `subj-${sMeta.code || subjName}`,
          strand: strandName,
          x: 0,
          y: 0,
          size: 26,
          isDrillCenter: true
        };
        addNode(centerNode);

        rings = [
          { r: 350, label: `วงตัวชี้วัดทั้งหมดในมาตรฐานนี้ (${stdKpis.length} ข้อ)` }
        ];

        const kpiStep = (Math.PI * 2) / Math.max(stdKpis.length, 1);
        stdKpis.forEach((k, kIdx) => {
          const kAngle = -Math.PI / 2 + kpiStep * kIdx;
          const kRadius = 350;

          const kNode = {
            id: `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`,
            kind: 'kpi',
            code: k.code,
            name: k.code,
            shortLabel: k.code.split(' ').pop() || k.code,
            fullText: k.text,
            coreContent: k.core_content || '',
            type: k.type,
            grade: k.grade,
            gradeBand: k.grade_band,
            strand: strandName,
            standard: rawStdCode,
            standardId: centerNode.id,
            standardDesc: stdDesc,
            subject: subjName,
            courses: k.courses || [],
            searchIndex: k.searchIndex,
            angle: kAngle,
            x: Math.round(Math.cos(kAngle) * kRadius),
            y: Math.round(Math.sin(kAngle) * kRadius),
            size: k.type === 'ปลายทาง' ? 8 : 7,
            color: k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8'
          };
          addNode(kNode);
          addEdge(centerNode.id, kNode.id, kNode.color, 1.5);
        });
      }

      return { centerNode, nodes, nodeById, edges, neighborMap, rings };
    }

    // Render SVG Rings, Edges, Nodes
    function renderStaticGraph() {
      // 1. Concentric Guideline Rings
      ringsGroup.replaceChildren();
      (graph.rings || []).forEach(ring => {
        ringsGroup.appendChild(createSvgElement('circle', {
          cx: '0', cy: '0', r: String(ring.r),
          class: 'graph-ring'
        }));
        const txt = createSvgElement('text', {
          x: '0', y: String(-ring.r - 6),
          class: 'graph-ring-label'
        });
        txt.textContent = ring.label;
        ringsGroup.appendChild(txt);
      });

      // 2. Edges
      edgesGroup.replaceChildren();
      const edgeFrag = document.createDocumentFragment();
      graph.edges.forEach(edge => {
        const s = graph.nodeById.get(edge.source);
        const t = graph.nodeById.get(edge.target);
        if (!s || !t) return;

        const path = createSvgElement('path', {
          d: curvedEdgePath(s, t),
          class: 'graph-edge',
          stroke: edge.color,
          'stroke-width': String(edge.width),
          opacity: '0.45',
          'data-edge-id': edge.id,
          'data-source': edge.source,
          'data-target': edge.target
        });
        edge.element = path;
        edgeFrag.appendChild(path);
      });
      edgesGroup.appendChild(edgeFrag);

      // 3. Nodes with LARGE INVISIBLE HITBOXES
      nodesGroup.replaceChildren();
      const nodeFrag = document.createDocumentFragment();

      graph.nodes.forEach(node => {
        const g = createSvgElement('g', {
          class: `node node--${node.kind} ${node.isDrillCenter ? 'node--drill-center' : ''}`,
          transform: `translate(${node.x} ${node.y})`,
          'data-node-id': node.id
        });

        // Large Transparent Hitbox for effortless clicking
        const hitRadius = Math.max(20, (node.size || 6) * 2.5);
        const hitbox = createSvgElement('circle', {
          cx: '0', cy: '0', r: String(hitRadius),
          class: 'node-hit-area'
        });
        g.appendChild(hitbox);

        // Visible Shape based on kind
        if (node.kind === 'root') {
          g.appendChild(createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size),
            fill: node.color,
            stroke: '#38bdf8',
            'stroke-width': '3',
            class: 'node-visible-shape'
          }));
        } else if (node.kind === 'grade' || node.kind === 'subject') {
          g.appendChild(createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size),
            fill: node.color,
            stroke: node.isDrillCenter ? '#10b981' : '#0f172a',
            'stroke-width': node.isDrillCenter ? '3' : '2.5',
            class: 'node-visible-shape'
          }));
        } else if (node.kind === 'strand' || node.kind === 'grade-subject') {
          g.appendChild(createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size),
            fill: node.color,
            stroke: node.isDrillCenter ? '#10b981' : '#ffffff',
            'stroke-width': node.isDrillCenter ? '3' : '1.5',
            class: 'node-visible-shape'
          }));
        } else if (node.kind === 'standard' || node.kind === 'grade-standard') {
          g.appendChild(createSvgElement('polygon', {
            points: diamondPoints(node.size),
            fill: node.color,
            stroke: node.isDrillCenter ? '#10b981' : '#0f172a',
            'stroke-width': node.isDrillCenter ? '3' : '1.5',
            class: 'node-visible-shape'
          }));
          g.appendChild(createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size),
            fill: node.color,
            stroke: node.isDrillCenter ? '#10b981' : '#0f172a',
            'stroke-width': node.isDrillCenter ? '3' : '2.5',
            class: 'node-visible-shape'
          }));
        } else if (node.kind === 'strand') {
          g.appendChild(createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size),
            fill: node.color,
            stroke: node.isDrillCenter ? '#10b981' : '#ffffff',
            'stroke-width': node.isDrillCenter ? '3' : '1.5',
            class: 'node-visible-shape'
          }));
        } else if (node.kind === 'standard') {
          g.appendChild(createSvgElement('polygon', {
            points: diamondPoints(node.size),
            fill: node.color,
            stroke: node.isDrillCenter ? '#10b981' : '#0f172a',
            'stroke-width': node.isDrillCenter ? '2.5' : '1.5',
            class: 'node-visible-shape'
          }));
        } else {
          // KPI dot
          g.appendChild(createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size),
            fill: node.color,
            stroke: '#0f172a',
            'stroke-width': '1',
            class: 'node-visible-shape'
          }));
        }

        // Special Pulsing Halo for Center Node in drill-down view
        if (node.isDrillCenter && node.id !== 'root-curriculum') {
          const centerHalo = createSvgElement('circle', {
            cx: '0', cy: '0', r: String(node.size + 10),
            fill: 'none',
            stroke: '#10b981',
            'stroke-width': '2',
            class: 'center-drill-halo'
          });
          g.appendChild(centerHalo);
        }

        // Labels
        if (node.kind !== 'kpi' || state.drillNodeId.startsWith('std-')) {
          const lblBg = createSvgElement('text', { class: 'node-label-bg' });
          const lblFg = createSvgElement('text', { class: 'node-label-fg' });
          positionNodeLabel(node, lblBg, lblFg);
          lblBg.textContent = node.shortLabel;
          lblFg.textContent = node.shortLabel;
          g.append(lblBg, lblFg);
        }

        // Direct Node Interaction
        g.addEventListener('mouseenter', (e) => {
          showTooltip(node, e);
          if (!graphState.isDragging && state.focusMode) {
            highlightHover(node.id);
          }
        });
        g.addEventListener('mouseleave', () => {
          hideTooltip();
        });

        g.addEventListener('click', (e) => {
          e.stopPropagation();
          // If clicked on current drill center, drill up!
          if (node.isDrillCenter && node.id !== 'root-curriculum') {
            drillUp();
            return;
          }
          selectNode(node.id);
        });

        // Double click to instantly drill down into sub-circle!
        g.addEventListener('dblclick', (e) => {
          e.stopPropagation();
          if (node.kind === 'subject' || node.kind === 'strand' || node.kind === 'standard') {
            drillTo(node.id);
          }
        });

        node.element = g;
        nodeFrag.appendChild(g);
      });

      nodesGroup.appendChild(nodeFrag);
      updateViewportTransform();
    }

    function curvedEdgePath(source, target) {
      const mx = (source.x + target.x) / 2;
      const my = (source.y + target.y) / 2;
      const bend = 0.65;
      const cx = mx * bend;
      const cy = my * bend;
      return `M ${source.x} ${source.y} Q ${cx} ${cy} ${target.x} ${target.y}`;
    }

    function diamondPoints(size) {
      return `0 ${-size} ${size} 0 0 ${size} ${-size} 0`;
    }

    function positionNodeLabel(node, bg, fg) {
      const isRight = node.x >= 0;
      const offset = node.size + 7;
      const anchor = node.x === 0 && node.y === 0 ? 'middle' : (isRight ? 'start' : 'end');
      const lx = node.x === 0 && node.y === 0 ? 0 : (isRight ? offset : -offset);
      const ly = node.x === 0 && node.y === 0 ? node.size + 15 : 4;

      bg.setAttribute('x', lx);
      bg.setAttribute('y', ly);
      bg.setAttribute('text-anchor', anchor);

      fg.setAttribute('x', lx);
      fg.setAttribute('y', ly);
      fg.setAttribute('text-anchor', anchor);
    }

    // Drill-down Breadcrumb Bar Renderer
    function renderBreadcrumb() {
      const parts = [];
      const current = state.drillNodeId;

      parts.push({
        id: 'root-curriculum',
        label: 'หลักสูตรแกนกลางทั้งหมด',
        icon: 'globe'
      });

      if (current.startsWith('grade-')) {
        const gCfg = GRADE_CONFIG.find(g => g.id === current || current.startsWith(g.id + '-'));
        if (gCfg) {
          parts.push({ id: gCfg.id, label: gCfg.shortLabel });
          if (current.includes('-subj-')) {
            const target = (sunburstData && sunburstData.sliceById.get(current)) || (graph && graph.nodeById.get(current));
            if (target) {
              parts.push({ id: current, label: target.shortLabel || target.name });
            }
          }
        }
      } else if (current.startsWith('subj-')) {
        const target = graph.nodeById.get(current) || { name: 'กลุ่มสาระ' };
        parts.push({ id: current, label: target.name || target.shortLabel });
      } else if (current.startsWith('strand-')) {
        const target = graph.nodeById.get(current) || { name: 'สาระ', subject: '' };
        if (target.subject) {
          const sMeta = DATA.subject_meta[target.subject] || {};
          parts.push({ id: `subj-${sMeta.code || target.subject}`, label: target.subject });
        }
        parts.push({ id: current, label: target.shortLabel || target.name });
      } else if (current.startsWith('std-')) {
        const target = graph.nodeById.get(current) || { name: 'มาตรฐาน', subject: '', strand: '' };
        if (target.subject) {
          const sMeta = DATA.subject_meta[target.subject] || {};
          parts.push({ id: `subj-${sMeta.code || target.subject}`, label: target.subject });
        }
        if (target.strand) {
          const strandMatch = target.strand.match(/สาระที่\\s*([0-9๑-๙]+)/);
          const strandNum = strandMatch ? strandMatch[1] : '1';
          const sMeta = DATA.subject_meta[target.subject] || {};
          parts.push({ id: `strand-${sMeta.code}-${strandNum}`, label: `สาระที่ ${strandNum}` });
        }
        parts.push({ id: current, label: target.code || target.shortLabel });
      }

      el.drillBreadcrumb.innerHTML = parts.map((p, idx) => {
        const isLast = idx === parts.length - 1;
        return `
          <button onclick="drillTo('${p.id}')" class="flex items-center space-x-1 transition ${isLast ? 'text-emerald-400 font-bold pointer-events-none' : 'hover:text-white text-slate-400'}">
            ${p.icon ? `<i data-lucide="${p.icon}" class="w-3 h-3 text-emerald-400"></i>` : ''}
            <span>${p.label}</span>
          </button>
          ${!isLast ? '<i data-lucide="chevron-right" class="w-3 h-3 text-slate-600"></i>' : ''}
        `;
      }).join('');

      el.btnDrillUp.classList.toggle('hidden', current === 'root-curriculum');
      lucide.createIcons();
    }

    // Drill to Node as Center
    function drillTo(nodeId) {
      loadView(nodeId, nodeId);
    }

    // Step up one level
    function drillUp() {
      const current = state.drillNodeId;
      if (current.startsWith('std-')) {
        const stdNode = graph.nodeById.get(current);
        if (stdNode && stdNode.strandId) drillTo(stdNode.strandId);
        else if (stdNode && stdNode.subjectId) drillTo(stdNode.subjectId);
        else drillTo('root-curriculum');
      } else if (current.startsWith('strand-')) {
        const strandNode = graph.nodeById.get(current);
        if (strandNode && strandNode.subjectId) drillTo(strandNode.subjectId);
        else drillTo('root-curriculum');
      } else {
        drillTo('root-curriculum');
      }
    }

    // ========================================================
    // Sunburst Radial Partition Engine (Grade-First, Radar Wheel & Subject-First)
    const GRADE_CONFIG = [
      { id: 'grade-p1', code: 'ป.1', title: 'ชั้นประถมศึกษาปีที่ ๑ (ป.๑)', shortLabel: 'ชั้น ป.๑', stage: 'ประถมศึกษาตอนต้น', color: '#10b981' },
      { id: 'grade-p2', code: 'ป.2', title: 'ชั้นประถมศึกษาปีที่ ๒ (ป.๒)', shortLabel: 'ชั้น ป.๒', stage: 'ประถมศึกษาตอนต้น', color: '#0d9488' },
      { id: 'grade-p3', code: 'ป.3', title: 'ชั้นประถมศึกษาปีที่ ๓ (ป.๓)', shortLabel: 'ชั้น ป.๓', stage: 'ประถมศึกษาตอนต้น', color: '#06b6d4' },
      { id: 'grade-p4', code: 'ป.4', title: 'ชั้นประถมศึกษาปีที่ ๔ (ป.๔)', shortLabel: 'ชั้น ป.๔', stage: 'ประถมศึกษาตอนปลาย', color: '#0284c7' },
      { id: 'grade-p5', code: 'ป.5', title: 'ชั้นประถมศึกษาปีที่ ๕ (ป.๕)', shortLabel: 'ชั้น ป.๕', stage: 'ประถมศึกษาตอนปลาย', color: '#2563eb' },
      { id: 'grade-p6', code: 'ป.6', title: 'ชั้นประถมศึกษาปีที่ ๖ (ป.๖)', shortLabel: 'ชั้น ป.๖', stage: 'ประถมศึกษาตอนปลาย', color: '#4f46e5' },
      { id: 'grade-m1', code: 'ม.1', title: 'ชั้นมัธยมศึกษาปีที่ ๑ (ม.๑)', shortLabel: 'ชั้น ม.๑', stage: 'มัธยมศึกษาตอนต้น', color: '#f59e0b' },
      { id: 'grade-m2', code: 'ม.2', title: 'ชั้นมัธยมศึกษาปีที่ ๒ (ม.๒)', shortLabel: 'ชั้น ม.๒', stage: 'มัธยมศึกษาตอนต้น', color: '#ea580c' },
      { id: 'grade-m3', code: 'ม.3', title: 'ชั้นมัธยมศึกษาปีที่ ๓ (ม.๓)', shortLabel: 'ชั้น ม.๓', stage: 'มัธยมศึกษาตอนต้น', color: '#dc2626' },
      { id: 'grade-m4-6', code: 'ม.4-6', title: 'ชั้นมัธยมศึกษาตอนปลาย (ม.๔-๖)', shortLabel: 'ชั้น ม.๔-๖', stage: 'มัธยมศึกษาตอนปลาย', color: '#8b5cf6' }
    ];

    function normalizeGradeKey(g) {
      if (!g) return 'ม.4-6';
      const s = String(g).trim();
      if (['ป.1', 'ป.2', 'ป.3', 'ป.4', 'ป.5', 'ป.6', 'ม.1', 'ม.2', 'ม.3'].includes(s)) return s;
      if (['ม.4', 'ม.5', 'ม.6', 'ม.4-6'].includes(s)) return 'ม.4-6';
      return 'ม.4-6';
    }

    function buildSunburstForView(drillNodeId, DATA) {
      const subjectOrder = [
        'ภาษาไทย', 'คณิตศาสตร์', 'วิทยาศาสตร์และเทคโนโลยี', 'สังคมศึกษา ศาสนา และวัฒนธรรม',
        'สุขศึกษาและพลศึกษา', 'ศิลปะ', 'การงานอาชีพ', 'ภาษาต่างประเทศ'
      ];

      const slices = [];
      const sliceById = new Map();
      const radarBadges = [];
      const radarSubjectHeaders = [];

      function addSlice(s) {
        slices.push(s);
        sliceById.set(s.id, s);
      }

      // =====================================================================
      // MODE 1: RADAR CONCENTRIC WHEEL (10 Concentric Rings x 8 Subjects)
      // =====================================================================
      if (state.sunburstMode === 'radar') {
        const totalKpis = DATA.kpis.length;
        const center = {
          id: 'root-curriculum',
          kind: 'root',
          name: 'หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน',
          shortLabel: 'หลักสูตร ๕๑',
          rInner: 0, rOuter: 72,
          startAngle: 0, endAngle: Math.PI * 2,
          color: '#0f172a',
          kpiCount: totalKpis
        };
        addSlice(center);

        // Grade ring radii definitions
        const gradeRadii = [
          { rIn: 78, rOut: 116 },   // ป.1
          { rIn: 120, rOut: 158 },  // ป.2
          { rIn: 162, rOut: 200 },  // ป.3
          { rIn: 204, rOut: 242 },  // ป.4
          { rIn: 246, rOut: 284 },  // ป.5
          { rIn: 288, rOut: 326 },  // ป.6
          { rIn: 330, rOut: 370 },  // ม.1
          { rIn: 374, rOut: 414 },  // ม.2
          { rIn: 418, rOut: 458 },  // ม.3
          { rIn: 462, rOut: 510 }   // ม.4-6
        ];

        // 8 Angular sectors (45 deg each, starting from -Math.PI / 2)
        const sectorSpan = (Math.PI * 2) / 8;

        // Group KPIs by (Grade, Subject)
        const cellKpis = {};
        DATA.kpis.forEach(k => {
          const gk = normalizeGradeKey(k.grade);
          const s = k.subject;
          if (!cellKpis[gk]) cellKpis[gk] = {};
          if (!cellKpis[gk][s]) cellKpis[gk][s] = [];
          cellKpis[gk][s].push(k);
        });

        GRADE_CONFIG.forEach((gCfg, gIdx) => {
          const radii = gradeRadii[gIdx];
          const gKpisCount = DATA.kpis.filter(k => normalizeGradeKey(k.grade) === gCfg.code).length;

          // Axis badge for this grade ring
          radarBadges.push({
            id: gCfg.id,
            gradeCode: gCfg.code,
            shortLabel: gCfg.shortLabel,
            title: gCfg.title,
            rMid: (radii.rIn + radii.rOut) / 2,
            angle: -Math.PI / 2,
            kpiCount: gKpisCount
          });

          subjectOrder.forEach((subj, sIdx) => {
            const startAngle = -Math.PI / 2 + sIdx * sectorSpan;
            const endAngle = startAngle + sectorSpan;
            const kpis = (cellKpis[gCfg.code] && cellKpis[gCfg.code][subj]) || [];
            const sMeta = DATA.subject_meta[subj] || { color: '#10b981', code: subj };
            const cellId = `${gCfg.id}-subj-${sMeta.code || subj}`;

            addSlice({
              id: cellId,
              kind: 'radar-cell',
              gradeId: gCfg.id,
              grade: gCfg.code,
              subject: subj,
              subjectId: sMeta.code || subj,
              name: `${subj} ชั้น ${gCfg.code}`,
              shortLabel: `${kpis.length} ตชว.`,
              rInner: radii.rIn,
              rOuter: radii.rOut,
              startAngle: startAngle,
              endAngle: endAngle,
              color: sMeta.color,
              kpiCount: kpis.length,
              kpis: kpis
            });
          });
        });

        // Subject rim headers around outer perimeter
        subjectOrder.forEach((subj, sIdx) => {
          const midAngle = -Math.PI / 2 + (sIdx + 0.5) * sectorSpan;
          const sMeta = DATA.subject_meta[subj] || { color: '#10b981', code: subj };
          radarSubjectHeaders.push({
            subject: subj,
            subjectId: sMeta.code || subj,
            shortLabel: subj.length > 12 ? subj.substring(0, 11) + '…' : subj,
            angle: midAngle,
            r: 535,
            color: sMeta.color
          });
        });

        return { slices, sliceById, radarBadges, radarSubjectHeaders, isRadar: true };
      }

      // =====================================================================
      // MODE 2: GRADE-FIRST SUNBURST (Grade Levels in Inner Ring) - DEFAULT
      // =====================================================================
      if (state.sunburstMode === 'grade') {
        // Build Grade-first tree: Grade -> Subject -> Standard -> KPIs
        const gradeTree = {};
        GRADE_CONFIG.forEach(g => { gradeTree[g.code] = {}; });

        DATA.kpis.forEach(k => {
          const gk = normalizeGradeKey(k.grade);
          const s = k.subject;
          const std = k.standard || 'ทั่วไป';
          if (!gradeTree[gk]) gradeTree[gk] = {};
          if (!gradeTree[gk][s]) gradeTree[gk][s] = {};
          if (!gradeTree[gk][s][std]) gradeTree[gk][s][std] = [];
          gradeTree[gk][s][std].push(k);
        });

        // ROOT VIEW (All 10 Grade Levels)
        if (!drillNodeId || drillNodeId === 'root-curriculum') {
          const totalKpis = DATA.kpis.length;
          let angleCursor = -Math.PI / 2;

          const r0 = 0, r1 = 80;
          const r1_in = 86, r1_out = 185;
          const r2_in = 192, r2_out = 295;
          const r3_in = 302, r3_out = 410;
          const r4_in = 416, r4_out = 530;

          const center = {
            id: 'root-curriculum',
            kind: 'root',
            name: 'หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน',
            shortLabel: 'หลักสูตร ๕๑',
            rInner: 0, rOuter: 80,
            startAngle: 0, endAngle: Math.PI * 2,
            color: '#0d3d70',
            kpiCount: totalKpis
          };
          addSlice(center);

          GRADE_CONFIG.forEach(gCfg => {
            const gCode = gCfg.code;
            const gradeSubjs = gradeTree[gCode] || {};
            const gradeKpisCount = Object.values(gradeSubjs).reduce((acc, stdDict) => {
              return acc + Object.values(stdDict).reduce((sum, list) => sum + list.length, 0);
            }, 0);

            if (gradeKpisCount === 0) return;
            const gradeSpan = (Math.PI * 2 * gradeKpisCount) / totalKpis;
            const gradeStart = angleCursor;
            const gradeEnd = angleCursor + gradeSpan;
            angleCursor = gradeEnd;

            addSlice({
              id: gCfg.id,
              kind: 'grade',
              name: gCfg.title,
              shortLabel: gCfg.shortLabel,
              code: gCfg.code,
              stage: gCfg.stage,
              gradeId: gCfg.id,
              rInner: r1_in, rOuter: r1_out,
              startAngle: gradeStart, endAngle: gradeEnd,
              color: gCfg.color,
              kpiCount: gradeKpisCount
            });

            // Layer 2: 8 Subjects under this grade
            let subjCursor = gradeStart;
            subjectOrder.forEach(subjName => {
              const stdDict = gradeSubjs[subjName];
              if (!stdDict) return;
              const subjKpisCount = Object.values(stdDict).reduce((sum, list) => sum + list.length, 0);
              if (subjKpisCount === 0) return;

              const subjSpan = (subjKpisCount / gradeKpisCount) * gradeSpan;
              const subjStart = subjCursor;
              const subjEnd = subjCursor + subjSpan;
              subjCursor = subjEnd;

              const sMeta = DATA.subject_meta[subjName] || { color: '#10b981', code: subjName };
              const subjSliceId = `${gCfg.id}-subj-${sMeta.code || subjName}`;

              addSlice({
                id: subjSliceId,
                kind: 'grade-subject',
                name: `${subjName} (${gCfg.shortLabel})`,
                shortLabel: subjName.length > 8 ? subjName.substring(0, 7) + '…' : subjName,
                subject: subjName,
                grade: gCfg.code,
                gradeId: gCfg.id,
                subjectId: sMeta.code || subjName,
                rInner: r2_in, rOuter: r2_out,
                startAngle: subjStart, endAngle: subjEnd,
                color: sMeta.color,
                kpiCount: subjKpisCount
              });

              // Layer 3: Standards under this subject in this grade
              let stdCursor = subjStart;
              Object.entries(stdDict).forEach(([stdCode, kpiList]) => {
                if (kpiList.length === 0) return;
                const stdSpan = (kpiList.length / subjKpisCount) * subjSpan;
                const stdStart = stdCursor;
                const stdEnd = stdCursor + stdSpan;
                stdCursor = stdEnd;

                const stdId = `${gCfg.id}-std-${stdCode.replace(/\\s+/g, '_')}`;

                addSlice({
                  id: stdId,
                  kind: 'grade-standard',
                  name: `มาตรฐาน ${stdCode} (${gCfg.shortLabel})`,
                  shortLabel: stdCode,
                  standardCode: stdCode,
                  subject: subjName,
                  grade: gCfg.code,
                  gradeId: gCfg.id,
                  subjectId: sMeta.code || subjName,
                  standardId: stdId,
                  rInner: r3_in, rOuter: r3_out,
                  startAngle: stdStart, endAngle: stdEnd,
                  color: sMeta.color,
                  kpiCount: kpiList.length
                });

                // Layer 4: Individual KPIs in this grade & standard
                const kpiStep = stdSpan / kpiList.length;
                kpiList.forEach((k, kIdx) => {
                  const kStart = stdStart + kIdx * kpiStep;
                  const kEnd = kStart + kpiStep;
                  const kColor = k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8';
                  const kId = `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`;

                  addSlice({
                    id: kId,
                    kind: 'kpi',
                    name: `${k.code} (${k.type || 'ตัวชี้วัด'})`,
                    shortLabel: k.code,
                    code: k.code,
                    type: k.type,
                    kpi: k,
                    subject: subjName,
                    grade: gCfg.code,
                    gradeId: gCfg.id,
                    standardId: stdId,
                    rInner: r4_in, rOuter: r4_out,
                    startAngle: kStart, endAngle: kEnd,
                    color: kColor,
                    kpiCount: 1
                  });
                });
              });
            });
          });

          return { slices, sliceById, isRadar: false };
        }

        // DRILLED INTO A SPECIFIC GRADE (e.g. 'grade-p2')
        if (drillNodeId.startsWith('grade-') && !drillNodeId.includes('-subj-')) {
          const gCfg = GRADE_CONFIG.find(g => g.id === drillNodeId) || GRADE_CONFIG[0];
          const gradeSubjs = gradeTree[gCfg.code] || {};
          const totalGradeKpis = Object.values(gradeSubjs).reduce((acc, stdDict) => {
            return acc + Object.values(stdDict).reduce((sum, list) => sum + list.length, 0);
          }, 0);

          let angleCursor = -Math.PI / 2;
          const r1_in = 95, r1_out = 220;
          const r2_in = 228, r2_out = 370;
          const r3_in = 378, r3_out = 530;

          // Center: That Grade Level
          addSlice({
            id: gCfg.id,
            kind: 'grade',
            name: gCfg.title,
            shortLabel: gCfg.shortLabel,
            code: gCfg.code,
            stage: gCfg.stage,
            rInner: 0, rOuter: 88,
            startAngle: 0, endAngle: Math.PI * 2,
            color: gCfg.color,
            kpiCount: totalGradeKpis
          });

          // Ring 1: 8 Subjects in this Grade
          subjectOrder.forEach(subjName => {
            const stdDict = gradeSubjs[subjName];
            if (!stdDict) return;
            const subjKpisCount = Object.values(stdDict).reduce((sum, list) => sum + list.length, 0);
            if (subjKpisCount === 0) return;

            const subjSpan = (subjKpisCount / totalGradeKpis) * Math.PI * 2;
            const subjStart = angleCursor;
            const subjEnd = angleCursor + subjSpan;
            angleCursor = subjEnd;

            const sMeta = DATA.subject_meta[subjName] || { color: '#10b981', code: subjName };
            const subjSliceId = `${gCfg.id}-subj-${sMeta.code || subjName}`;

            addSlice({
              id: subjSliceId,
              kind: 'grade-subject',
              name: `${subjName} (${gCfg.shortLabel})`,
              shortLabel: subjName,
              subject: subjName,
              grade: gCfg.code,
              gradeId: gCfg.id,
              subjectId: sMeta.code || subjName,
              rInner: r1_in, rOuter: r1_out,
              startAngle: subjStart, endAngle: subjEnd,
              color: sMeta.color,
              kpiCount: subjKpisCount
            });

            // Ring 2: Standards in this Grade & Subject
            let stdCursor = subjStart;
            Object.entries(stdDict).forEach(([stdCode, kpiList]) => {
              if (kpiList.length === 0) return;
              const stdSpan = (kpiList.length / subjKpisCount) * subjSpan;
              const stdStart = stdCursor;
              const stdEnd = stdCursor + stdSpan;
              stdCursor = stdEnd;

              const stdId = `${gCfg.id}-std-${stdCode.replace(/\\s+/g, '_')}`;

              addSlice({
                id: stdId,
                kind: 'grade-standard',
                name: `มาตรฐาน ${stdCode} (${gCfg.shortLabel})`,
                shortLabel: stdCode,
                standardCode: stdCode,
                subject: subjName,
                grade: gCfg.code,
                gradeId: gCfg.id,
                subjectId: sMeta.code || subjName,
                standardId: stdId,
                rInner: r2_in, rOuter: r2_out,
                startAngle: stdStart, endAngle: stdEnd,
                color: sMeta.color,
                kpiCount: kpiList.length
              });

              // Ring 3: KPIs in this Grade & Standard
              const kpiStep = stdSpan / kpiList.length;
              kpiList.forEach((k, kIdx) => {
                const kStart = stdStart + kIdx * kpiStep;
                const kEnd = kStart + kpiStep;
                const kColor = k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8';
                const kId = `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`;

                addSlice({
                  id: kId,
                  kind: 'kpi',
                  name: `${k.code} (${k.type || 'ตัวชี้วัด'})`,
                  shortLabel: k.code,
                  code: k.code,
                  type: k.type,
                  kpi: k,
                  subject: subjName,
                  grade: gCfg.code,
                  gradeId: gCfg.id,
                  standardId: stdId,
                  rInner: r3_in, rOuter: r3_out,
                  startAngle: kStart, endAngle: kEnd,
                  color: kColor,
                  kpiCount: 1
                });
              });
            });
          });

          return { slices, sliceById, isRadar: false };
        }

        // DRILLED INTO A SPECIFIC GRADE & SUBJECT (e.g. 'grade-p2-subj-tha')
        if (drillNodeId.startsWith('grade-') && drillNodeId.includes('-subj-')) {
          const parts = drillNodeId.split('-subj-');
          const gId = parts[0];
          const sCode = parts[1];
          const gCfg = GRADE_CONFIG.find(g => g.id === gId) || GRADE_CONFIG[0];
          const subjName = subjectOrder.find(s => (DATA.subject_meta[s]?.code || s) === sCode) || 'ภาษาไทย';
          const sMeta = DATA.subject_meta[subjName] || { color: '#10b981' };

          const stdDict = (gradeTree[gCfg.code] && gradeTree[gCfg.code][subjName]) || {};
          const totalSubjKpis = Object.values(stdDict).reduce((sum, list) => sum + list.length, 0);

          let angleCursor = -Math.PI / 2;
          const r1_in = 95, r1_out = 260;
          const r2_in = 270, r2_out = 530;

          // Center: That Subject in that Grade
          addSlice({
            id: drillNodeId,
            kind: 'grade-subject',
            name: `${subjName} ชั้น ${gCfg.code}`,
            shortLabel: `${subjName} (${gCfg.code})`,
            subject: subjName,
            grade: gCfg.code,
            gradeId: gCfg.id,
            subjectId: sCode,
            rInner: 0, rOuter: 88,
            startAngle: 0, endAngle: Math.PI * 2,
            color: sMeta.color,
            kpiCount: totalSubjKpis
          });

          // Ring 1: Standards in this Subject & Grade
          Object.entries(stdDict).forEach(([stdCode, kpiList]) => {
            if (kpiList.length === 0) return;
            const stdSpan = (kpiList.length / totalSubjKpis) * Math.PI * 2;
            const stdStart = angleCursor;
            const stdEnd = angleCursor + stdSpan;
            angleCursor = stdEnd;

            const stdId = `${gCfg.id}-std-${stdCode.replace(/\\s+/g, '_')}`;

            addSlice({
              id: stdId,
              kind: 'grade-standard',
              name: `มาตรฐาน ${stdCode}`,
              shortLabel: stdCode,
              standardCode: stdCode,
              subject: subjName,
              grade: gCfg.code,
              gradeId: gCfg.id,
              subjectId: sCode,
              rInner: r1_in, rOuter: r1_out,
              startAngle: stdStart, endAngle: stdEnd,
              color: sMeta.color,
              kpiCount: kpiList.length
            });

            // Ring 2: KPIs in this Standard
            const kpiStep = stdSpan / kpiList.length;
            kpiList.forEach((k, kIdx) => {
              const kStart = stdStart + kIdx * kpiStep;
              const kEnd = kStart + kpiStep;
              const kColor = k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8';
              const kId = `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`;

              addSlice({
                id: kId,
                kind: 'kpi',
                name: `${k.code} (${k.type || 'ตัวชี้วัด'})`,
                shortLabel: k.code,
                code: k.code,
                type: k.type,
                kpi: k,
                subject: subjName,
                grade: gCfg.code,
                gradeId: gCfg.id,
                rInner: r2_in, rOuter: r2_out,
                startAngle: kStart, endAngle: kEnd,
                color: kColor,
                kpiCount: 1
              });
            });
          });

          return { slices, sliceById, isRadar: false };
        }
      }

      // =====================================================================
      // MODE 3: SUBJECT-FIRST SUNBURST (8 Subjects in Inner Ring)
      // =====================================================================
      const tree = {};
      DATA.kpis.forEach(k => {
        const subj = k.subject;
        const strand = k.strand || 'สาระทั่วไป';
        const std = k.standard;
        if (!tree[subj]) tree[subj] = {};
        if (!tree[subj][strand]) tree[subj][strand] = {};
        if (!tree[subj][strand][std]) tree[subj][strand][std] = [];
        tree[subj][strand][std].push(k);
      });

      if (!drillNodeId || drillNodeId === 'root-curriculum') {
        const totalKpis = DATA.kpis.length;
        let angleCursor = -Math.PI / 2;

        const r0 = 0, r1 = 80;
        const r1_in = 86, r1_out = 175;
        const r2_in = 182, r2_out = 280;
        const r3_in = 286, r3_out = 395;
        const r4_in = 402, r4_out = 520;

        const center = {
          id: 'root-curriculum',
          kind: 'root',
          name: 'หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน',
          shortLabel: 'หลักสูตรแกนกลาง',
          rInner: 0, rOuter: 80,
          startAngle: 0, endAngle: Math.PI * 2,
          color: '#0d3d70',
          kpiCount: totalKpis
        };
        addSlice(center);

        subjectOrder.forEach(subjName => {
          if (!tree[subjName]) return;
          const sMeta = DATA.subject_meta[subjName] || { color: '#10b981', code: subjName };
          const subjKpisCount = DATA.subject_counts[subjName]?.total || 0;
          const subjSpan = (Math.PI * 2 * subjKpisCount) / totalKpis;
          const subjStart = angleCursor;
          const subjEnd = angleCursor + subjSpan;
          angleCursor = subjEnd;

          const subjId = `subj-${sMeta.code || subjName}`;
          addSlice({
            id: subjId,
            kind: 'subject',
            name: subjName,
            shortLabel: subjName,
            subject: subjName,
            subjectId: subjId,
            rInner: r1_in, rOuter: r1_out,
            startAngle: subjStart, endAngle: subjEnd,
            color: sMeta.color,
            kpiCount: subjKpisCount
          });

          let strandCursor = subjStart;
          const strands = Object.entries(tree[subjName]);
          strands.forEach(([strandName, stdDict], stIdx) => {
            const strandKpisCount = Object.values(stdDict).reduce((sum, list) => sum + list.length, 0);
            const strandSpan = (strandKpisCount / subjKpisCount) * subjSpan;
            const strandStart = strandCursor;
            const strandEnd = strandCursor + strandSpan;

            const stMatch = strandName.match(/สาระที่\\s*([0-9๑-๙]+)/);
            const stNum = stMatch ? stMatch[1] : String(stIdx + 1);
            const strandId = `strand-${sMeta.code || subjName}-${stNum}`;

            addSlice({
              id: strandId,
              kind: 'strand',
              name: strandName,
              shortLabel: `สาระที่ ${stNum}`,
              subject: subjName,
              subjectId: subjId,
              strandId: strandId,
              rInner: r2_in, rOuter: r2_out,
              startAngle: strandStart, endAngle: strandEnd,
              color: sMeta.color,
              kpiCount: strandKpisCount
            });

            let stdCursor = strandStart;
            const standards = Object.entries(stdDict);
            standards.forEach(([stdCode, kpiList]) => {
              const stdSpan = (kpiList.length / strandKpisCount) * strandSpan;
              const stdStart = stdCursor;
              const stdEnd = stdCursor + stdSpan;

              const stdId = `std-${stdCode.replace(/\\s+/g, '_')}`;

              addSlice({
                id: stdId,
                kind: 'standard',
                name: `มาตรฐาน ${stdCode}`,
                shortLabel: stdCode,
                subject: subjName,
                strand: strandName,
                subjectId: subjId,
                strandId: strandId,
                standardId: stdId,
                rInner: r3_in, rOuter: r3_out,
                startAngle: stdStart, endAngle: stdEnd,
                color: sMeta.color,
                kpiCount: kpiList.length
              });

              const kpiStep = stdSpan / kpiList.length;
              kpiList.forEach((k, kIdx) => {
                const kStart = stdStart + kIdx * kpiStep;
                const kEnd = kStart + kpiStep;
                const kColor = k.type === 'ปลายทาง' ? '#f59e0b' : '#38bdf8';
                const kId = `kpi-${k.id || k.code.replace(/\\s+/g, '_')}`;

                addSlice({
                  id: kId,
                  kind: 'kpi',
                  name: `${k.code} (${k.type || 'ตัวชี้วัด'})`,
                  shortLabel: k.code,
                  code: k.code,
                  type: k.type,
                  kpi: k,
                  subject: subjName,
                  strand: strandName,
                  subjectId: subjId,
                  strandId: strandId,
                  standardId: stdId,
                  rInner: r4_in, rOuter: r4_out,
                  startAngle: kStart, endAngle: kEnd,
                  color: kColor,
                  kpiCount: 1
                });
              });

              stdCursor = stdEnd;
            });

            strandCursor = strandEnd;
          });
        });

        return { slices, sliceById, isRadar: false };
      }

      // Default fallback
      return { slices, sliceById, isRadar: false };
    }

    // ========================================================
    // Sunburst & Radar SVG Renderer
    // ========================================================
    function renderSunburstGraph() {
      if (!sunburstData) return;

      sunburstRingsGroup.innerHTML = '';
      sunburstSlicesGroup.innerHTML = '';
      sunburstLabelsGroup.innerHTML = '';

      const fragSlices = document.createDocumentFragment();
      const fragLabels = document.createDocumentFragment();

      // If RADAR WHEEL MODE
      if (sunburstData.isRadar) {
        // 1. Concentric Ring Guidelines
        const gradeRadii = [78, 116, 120, 158, 162, 200, 204, 242, 246, 284, 288, 326, 330, 370, 374, 414, 418, 458, 462, 510];
        gradeRadii.forEach(r => {
          const ringCircle = createSvgElement('circle', {
            cx: '0', cy: '0', r: String(r),
            fill: 'none',
            stroke: '#1e293b',
            'stroke-width': '0.7',
            'stroke-dasharray': '2 3',
            'pointer-events': 'none'
          });
          sunburstRingsGroup.appendChild(ringCircle);
        });

        // 2. Radial Spoke Dividers (8 Subjects)
        for (let i = 0; i < 8; i++) {
          const angle = -Math.PI / 2 + i * (Math.PI / 4);
          const p1 = polarToCartesian(0, 0, 72, angle);
          const p2 = polarToCartesian(0, 0, 515, angle);
          const spoke = createSvgElement('line', {
            x1: String(p1.x.toFixed(1)), y1: String(p1.y.toFixed(1)),
            x2: String(p2.x.toFixed(1)), y2: String(p2.y.toFixed(1)),
            stroke: '#334155',
            'stroke-width': '1.2',
            'stroke-dasharray': '3 3',
            'pointer-events': 'none'
          });
          sunburstRingsGroup.appendChild(spoke);
        }

        // 3. Render 80 Cells
        sunburstData.slices.forEach(slice => {
          if (slice.kind === 'root') {
            const centerCircle = createSvgElement('circle', {
              cx: '0', cy: '0', r: String(slice.rOuter),
              fill: slice.color,
              stroke: '#38bdf8',
              'stroke-width': '1.5',
              class: 'sunburst-slice cursor-pointer transition-all',
              'data-slice-id': slice.id
            });
            centerCircle.addEventListener('click', (e) => {
              e.stopPropagation();
              selectNode('root-curriculum');
            });
            fragSlices.appendChild(centerCircle);

            const centerText1 = createSvgElement('text', {
              x: '0', y: '-8',
              class: 'sunburst-label',
              style: 'font-size: 13px; font-weight: 700; fill: #38bdf8;'
            });
            centerText1.textContent = 'แกนกลาง ๕๑';
            fragLabels.appendChild(centerText1);

            const centerText2 = createSvgElement('text', {
              x: '0', y: '12',
              class: 'sunburst-label',
              style: 'font-size: 10px; font-weight: 600; fill: #94a3b8;'
            });
            centerText2.textContent = '๒,๐๕๖ ตัวชี้วัด';
            fragLabels.appendChild(centerText2);
            return;
          }

          // Radar Cell Arc
          const pathD = createSunburstArc(0, 0, slice.rInner, slice.rOuter, slice.startAngle, slice.endAngle);
          const path = createSvgElement('path', {
            d: pathD,
            fill: slice.color,
            class: 'radar-cell',
            'data-slice-id': slice.id,
            style: 'fill-opacity: 0.85;'
          });

          path.addEventListener('mouseenter', (e) => {
            showTooltip(slice, e);
            if (!graphState.isDragging && state.focusMode) {
              highlightSunburstHover(slice.id);
            }
          });
          path.addEventListener('mouseleave', () => {
            hideTooltip();
            resetSunburstHover();
          });
          path.addEventListener('click', (e) => {
            e.stopPropagation();
            selectNode(slice.id);
          });

          fragSlices.appendChild(path);
          slice.element = path;

          // KPI Count inside cell
          if (slice.kpiCount > 0) {
            const midAngle = (slice.startAngle + slice.endAngle) / 2;
            const midR = (slice.rInner + slice.rOuter) / 2;
            const pos = polarToCartesian(0, 0, midR, midAngle);
            const txt = createSvgElement('text', {
              x: String(pos.x.toFixed(1)),
              y: String(pos.y.toFixed(1)),
              class: 'sunburst-label',
              style: 'font-size: 10px; font-weight: 700; fill: #ffffff; pointer-events: none;'
            });
            txt.textContent = String(slice.kpiCount);
            fragLabels.appendChild(txt);
          }
        });

        // 4. Grade Axis Badges (along top vertical axis)
        if (sunburstData.radarBadges) {
          sunburstData.radarBadges.forEach(badge => {
            const gBadge = createSvgElement('g', {
              class: 'radar-axis-badge',
              transform: `translate(0, ${-badge.rMid.toFixed(1)})`
            });

            const rect = createSvgElement('rect', {
              x: '-22', y: '-10',
              width: '44', height: '20',
              class: 'radar-axis-bg'
            });

            const label = createSvgElement('text', {
              x: '0', y: '0',
              class: 'radar-axis-text'
            });
            label.textContent = badge.gradeCode;

            gBadge.appendChild(rect);
            gBadge.appendChild(label);

            gBadge.addEventListener('click', (e) => {
              e.stopPropagation();
              selectNode(badge.id);
            });
            gBadge.addEventListener('mouseenter', (e) => {
              showTooltip({ name: badge.title, shortLabel: `${badge.kpiCount} ตัวชี้วัด`, kpiCount: badge.kpiCount }, e);
              highlightSunburstHover(badge.id);
            });
            gBadge.addEventListener('mouseleave', () => {
              hideTooltip();
              resetSunburstHover();
            });

            fragLabels.appendChild(gBadge);
          });
        }

        // 5. Subject Headers around outer rim
        if (sunburstData.radarSubjectHeaders) {
          sunburstData.radarSubjectHeaders.forEach(sh => {
            const pos = polarToCartesian(0, 0, sh.r, sh.angle);
            let rot = (sh.angle * 180) / Math.PI;
            if (rot > 90) rot -= 180;
            else if (rot < -90) rot += 180;

            const txt = createSvgElement('text', {
              x: String(pos.x.toFixed(1)),
              y: String(pos.y.toFixed(1)),
              class: 'radar-subject-label',
              transform: `rotate(${rot.toFixed(1)} ${pos.x.toFixed(1)} ${pos.y.toFixed(1)})`
            });
            txt.textContent = sh.shortLabel;
            txt.addEventListener('click', (e) => {
              e.stopPropagation();
              selectNode(`subj-${sh.subjectId}`);
            });
            txt.addEventListener('mouseenter', (e) => {
              showTooltip({ name: sh.subject, shortLabel: 'คลิกเพื่อดูวิชานี้ทุกระดับชั้น' }, e);
              highlightSunburstHover(`subj-${sh.subjectId}`);
            });
            txt.addEventListener('mouseleave', () => {
              hideTooltip();
              resetSunburstHover();
            });
            fragLabels.appendChild(txt);
          });
        }

        sunburstSlicesGroup.appendChild(fragSlices);
        sunburstLabelsGroup.appendChild(fragLabels);
        return;
      }

      // =====================================================================
      // SUNBURST PARTITION RENDERING (Grade-First or Subject-First)
      // =====================================================================
      sunburstData.slices.forEach(slice => {
        if (slice.kind === 'root') {
          const centerCircle = createSvgElement('circle', {
            cx: '0', cy: '0', r: String(slice.rOuter),
            fill: slice.color,
            stroke: '#1e293b',
            'stroke-width': '2',
            class: 'sunburst-slice cursor-pointer transition-all',
            'data-slice-id': slice.id
          });

          centerCircle.addEventListener('click', (e) => {
            e.stopPropagation();
            drillTo('root-curriculum');
          });

          fragSlices.appendChild(centerCircle);

          const centerText1 = createSvgElement('text', {
            x: '0', y: '-8',
            class: 'sunburst-label',
            style: 'font-size: 13px; font-weight: 700; fill: #38bdf8;'
          });
          centerText1.textContent = slice.shortLabel || 'หลักสูตรแกนกลาง';
          fragLabels.appendChild(centerText1);

          const centerText2 = createSvgElement('text', {
            x: '0', y: '12',
            class: 'sunburst-label',
            style: 'font-size: 10px; font-weight: 600; fill: #94a3b8;'
          });
          centerText2.textContent = `${slice.kpiCount.toLocaleString()} ตัวชี้วัด`;
          fragLabels.appendChild(centerText2);
          return;
        }

        const pathD = createSunburstArc(0, 0, slice.rInner, slice.rOuter, slice.startAngle, slice.endAngle);
        const path = createSvgElement('path', {
          d: pathD,
          fill: slice.color,
          class: 'sunburst-slice',
          'data-slice-id': slice.id
        });

        if (slice.kind === 'kpi' && state.drillNodeId === 'root-curriculum') {
          path.setAttribute('stroke-width', '0.2');
          path.setAttribute('stroke', '#030712');
        }

        path.addEventListener('mouseenter', (e) => {
          showTooltip(slice, e);
          if (!graphState.isDragging && state.focusMode) {
            highlightSunburstHover(slice.id);
          }
        });
        path.addEventListener('mouseleave', () => {
          hideTooltip();
          resetSunburstHover();
        });

        path.addEventListener('click', (e) => {
          e.stopPropagation();
          selectNode(slice.id);
        });

        path.addEventListener('dblclick', (e) => {
          e.stopPropagation();
          if (['grade', 'grade-subject', 'subject', 'strand', 'standard'].includes(slice.kind)) {
            drillTo(slice.id);
          }
        });

        fragSlices.appendChild(path);
        slice.element = path;

        const span = slice.endAngle - slice.startAngle;
        const midAngle = (slice.startAngle + slice.endAngle) / 2;
        const midR = (slice.rInner + slice.rOuter) / 2;
        const arcLength = span * midR;

        let showLabel = false;
        let labelText = slice.shortLabel || slice.name;

        if (slice.kind === 'grade' && span >= 0.12) {
          showLabel = true;
        } else if (slice.kind === 'grade-subject' && span >= 0.08 && arcLength >= 24) {
          showLabel = true;
        } else if (slice.kind === 'subject' && span >= 0.15) {
          showLabel = true;
        } else if (slice.kind === 'strand' && span >= 0.08 && arcLength >= 26) {
          showLabel = true;
        } else if ((slice.kind === 'standard' || slice.kind === 'grade-standard') && span >= 0.06 && arcLength >= 22) {
          showLabel = true;
        } else if (slice.kind === 'kpi' && span >= 0.08 && arcLength >= 32) {
          showLabel = true;
        }

        if (showLabel) {
          const pos = polarToCartesian(0, 0, midR, midAngle);
          let rot = (midAngle * 180) / Math.PI;
          if (rot > 90) rot -= 180;
          else if (rot < -90) rot += 180;

          const txt = createSvgElement('text', {
            x: String(pos.x.toFixed(1)),
            y: String(pos.y.toFixed(1)),
            class: 'sunburst-label',
            transform: `rotate(${rot.toFixed(1)} ${pos.x.toFixed(1)} ${pos.y.toFixed(1)})`
          });
          txt.textContent = labelText;
          fragLabels.appendChild(txt);
        }
      });

      sunburstSlicesGroup.appendChild(fragSlices);
      sunburstLabelsGroup.appendChild(fragLabels);
    }

    function highlightSunburstHover(sliceId) {
      if (!sunburstData) return;
      const branchNodes = getBranchNodes(sliceId);
      sunburstData.slices.forEach(s => {
        if (!s.element) return;
        if (branchNodes.has(s.id)) {
          s.element.style.opacity = '1';
          s.element.style.filter = 'brightness(1.25)';
        } else {
          s.element.style.opacity = '0.2';
          s.element.style.filter = 'none';
        }
      });
    }

    function resetSunburstHover() {
      applyVisibility();
    }

    // Floating Tooltip over SVG
    function showTooltip(node, e) {
      if (!el.graphTooltip) return;
      const kindLabels = {
        root: 'ศูนย์กลางหลักสูตรแกนกลาง',
        subject: 'กลุ่มสาระการเรียนรู้',
        strand: 'สาระการเรียนรู้ (Strand)',
        standard: 'มาตรฐานการเรียนรู้',
        kpi: node.type === 'ปลายทาง' ? 'ตัวชี้วัดปลายทาง (Summative)' : 'ตัวชี้วัดระหว่างทาง (Formative)'
      };

      el.tooltipKind.innerText = kindLabels[node.kind] || node.kind;
      el.tooltipTitle.innerText = node.name || node.code;
      if (node.isDrillCenter && node.id !== 'root-curriculum') {
        el.tooltipSub.innerText = 'จุดศูนย์กลาง (คลิกเพื่อย้อนกลับ)';
      } else if (node.kind === 'strand') {
        el.tooltipSub.innerText = `${node.subject} • ${node.standardsCount} มาตรฐาน • ${node.kpiCount} ตัวชี้วัด`;
      } else if (node.kind === 'standard') {
        el.tooltipSub.innerText = `${node.strand} • ${node.kpiCount} ตัวชี้วัด`;
      } else if (node.kind === 'kpi') {
        el.tooltipSub.innerText = `${node.grade} • ${node.standard} • ${(node.courses || []).length} วิชาใน รร.`;
      } else if (node.kind === 'subject') {
        el.tooltipSub.innerText = `${node.kpiCount} ตัวชี้วัดใน ๕๕ มาตรฐาน`;
      } else {
        el.tooltipSub.innerText = 'คลิกเพื่อดูรายละเอียด';
      }

      const rect = el.graphStage.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      el.graphTooltip.style.left = `${x}px`;
      el.graphTooltip.style.top = `${y}px`;
      el.graphTooltip.style.opacity = '1';
    }

    function hideTooltip() {
      if (el.graphTooltip) el.graphTooltip.style.opacity = '0';
    }

    // Populate Right Control Panel Buttons & Lists
    function populateControls() {
      const frag = document.createDocumentFragment();
      const allBtn = document.createElement('button');
      allBtn.className = 'subj-pill col-span-2 px-2.5 py-1.5 rounded-xl border border-emerald-500/50 bg-emerald-600/20 text-emerald-300 font-semibold text-xs transition flex items-center justify-between';
      allBtn.innerHTML = `<span>ทุกกลุ่มสาระ (๘)</span><span class="font-mono text-[10px] bg-slate-900 px-1.5 py-0.5 rounded">2,056</span>`;
      allBtn.addEventListener('click', () => setSubjectFilter('ALL', allBtn));
      frag.appendChild(allBtn);

      for (const [subjName, meta] of Object.entries(DATA.subject_meta)) {
        const count = DATA.subject_counts[subjName]?.total || 0;
        const btn = document.createElement('button');
        btn.className = 'subj-pill px-2 py-1.5 rounded-xl border border-slate-800 bg-slate-900/80 hover:border-slate-700 text-slate-300 text-xs transition flex items-center justify-between text-left';
        btn.innerHTML = `
          <div class="flex items-center space-x-1.5 truncate">
            <span class="w-2 h-2 rounded-full shrink-0" style="background-color: ${meta.color}"></span>
            <span class="truncate">${subjName}</span>
          </div>
          <span class="font-mono text-[10px] text-slate-500 ml-1">${count}</span>
        `;
        btn.addEventListener('click', () => setSubjectFilter(subjName, btn));
        frag.appendChild(btn);
      }
      el.subjectPillGrid.appendChild(frag);
    }

    function setSubjectFilter(subj, activeBtn) {
      state.subject = subj;
      document.querySelectorAll('.subj-pill').forEach(b => {
        b.className = 'subj-pill px-2 py-1.5 rounded-xl border border-slate-800 bg-slate-900/80 hover:border-slate-700 text-slate-300 text-xs transition flex items-center justify-between text-left';
      });
      if (activeBtn) {
        activeBtn.className = 'subj-pill px-2 py-1.5 rounded-xl border border-emerald-500/50 bg-emerald-600/20 text-emerald-300 font-semibold text-xs transition flex items-center justify-between text-left shadow-sm';
      }
      if (subj !== 'ALL') {
        const sMeta = DATA.subject_meta[subj] || {};
        drillTo(`subj-${sMeta.code || subj}`);
      } else {
        drillTo('root-curriculum');
      }
    }

    // Node Selection & Left Info Panel
    function selectNode(nodeId, panTo = true) {
      state.selectedNodeId = nodeId;
      updateInfoPanel(nodeId);
      applyVisibility();

      if (panTo && state.viewMode === 'map') {
        const node = graph ? graph.nodeById.get(nodeId) : null;
        if (node && node.kind !== 'root' && !node.isDrillCenter) {
          graphState.translateX = -node.x * graphState.scale * 0.4;
          graphState.translateY = -node.y * graphState.scale * 0.4;
          updateViewportTransform();
        }
      }

      if (window.innerWidth < 1024) {
        const panel = document.getElementById('infoPanel');
        if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function highlightHover(nodeId) {
      // Soft hover highlight
    }

    // Get Branch Ancestors and Descendants
    function getBranchNodes(nodeId) {
      const set = new Set();
      const node = (graph && graph.nodeById.get(nodeId)) || (sunburstData && sunburstData.sliceById.get(nodeId));
      if (!node) return set;
      set.add(node.id);

      const centerId = state.drillNodeId;
      if (node.id === centerId) {
        if (graph) graph.nodes.forEach(n => set.add(n.id));
        if (sunburstData) sunburstData.slices.forEach(s => set.add(s.id));
        return set;
      }

      set.add(centerId);
      if (node.subjectId) set.add(node.subjectId);
      if (node.strandId) set.add(node.strandId);
      if (node.standardId) set.add(node.standardId);

      if (node.gradeId) set.add(node.gradeId);

      if (node.kind === 'grade') {
        if (graph) graph.nodes.forEach(n => { if (n.grade === node.code || (n.id && n.id.startsWith(node.id))) set.add(n.id); });
        if (sunburstData) sunburstData.slices.forEach(s => { if (s.grade === node.code || s.gradeId === node.id || (s.id && s.id.startsWith(node.id))) set.add(s.id); });
      } else if (node.kind === 'grade-subject' || node.kind === 'radar-cell') {
        if (graph) graph.nodes.forEach(n => { if (n.grade === node.grade && n.subject === node.subject) set.add(n.id); });
        if (sunburstData) sunburstData.slices.forEach(s => { if (s.grade === node.grade && s.subject === node.subject) set.add(s.id); });
      } else if (node.kind === 'grade-standard') {
        if (graph) graph.nodes.forEach(n => { if (n.grade === node.grade && n.standard === node.standardCode) set.add(n.id); });
        if (sunburstData) sunburstData.slices.forEach(s => { if (s.grade === node.grade && (s.standardCode === node.standardCode || s.standard === node.standardCode)) set.add(s.id); });
      } else if (node.kind === 'subject') {
        if (graph) graph.nodes.forEach(n => { if (n.subject === node.name) set.add(n.id); });
        if (sunburstData) sunburstData.slices.forEach(s => { if (s.subject === node.name) set.add(s.id); });
      } else if (node.kind === 'strand') {
        if (graph) graph.nodes.forEach(n => { if (n.subject === node.subject && n.strand === node.name) set.add(n.id); });
        if (sunburstData) sunburstData.slices.forEach(s => { if (s.subject === node.subject && s.strand === node.name) set.add(s.id); });
      } else if (node.kind === 'standard') {
        if (graph) graph.nodes.forEach(n => { if (n.kind === 'kpi' && n.standard === node.code) set.add(n.id); });
        if (sunburstData) sunburstData.slices.forEach(s => { if (s.kind === 'kpi' && s.standard === node.code) set.add(s.id); });
      }

      return set;
    }

    function applyVisibility() {
      const activeId = state.selectedNodeId;
      const branchNodes = getBranchNodes(activeId);

      graph.nodes.forEach(node => {
        const inBranch = branchNodes.has(node.id);
        const matchesFilter = nodeMatchesFilter(node);

        if (state.focusMode && activeId !== graph.centerNode.id) {
          if (inBranch && matchesFilter) {
            node.element.classList.remove('is-dimmed');
            node.element.classList.add('node-highlighted');
          } else {
            node.element.classList.add('is-dimmed');
            node.element.classList.remove('node-highlighted');
          }
        } else {
          if (matchesFilter) {
            node.element.classList.remove('is-dimmed');
            node.element.classList.remove('node-highlighted');
          } else {
            node.element.classList.add('is-dimmed');
            node.element.classList.remove('node-highlighted');
          }
        }
      });

      graph.edges.forEach(edge => {
        const isBranchEdge = branchNodes.has(edge.source) && branchNodes.has(edge.target);
        if (state.focusMode && activeId !== graph.centerNode.id) {
          if (isBranchEdge) {
            edge.element.classList.remove('edge-dimmed');
            edge.element.classList.add('edge-highlighted');
          } else {
            edge.element.classList.add('edge-dimmed');
            edge.element.classList.remove('edge-highlighted');
          }
        } else {
          edge.element.classList.remove('edge-dimmed', 'edge-highlighted');
        }
      });

      // Update Sunburst Slices Visibility
      if (sunburstData && sunburstData.slices) {
        sunburstData.slices.forEach(slice => {
          if (!slice.element) return;
          const inBranch = branchNodes.has(slice.id);
          const matchesFilter = nodeMatchesFilter(slice);
          const isSelected = slice.id === activeId;

          const centerId = state.drillNodeId;
          if (state.focusMode && activeId !== centerId) {
            if (inBranch && matchesFilter) {
              slice.element.style.opacity = '1';
              slice.element.style.stroke = isSelected ? '#10b981' : (inBranch ? '#38bdf8' : '#030712');
              slice.element.style.strokeWidth = isSelected ? '3px' : '1.5px';
            } else {
              slice.element.style.opacity = '0.12';
              slice.element.style.stroke = '#030712';
              slice.element.style.strokeWidth = '0.5px';
            }
          } else {
            if (matchesFilter) {
              slice.element.style.opacity = '1';
              slice.element.style.stroke = isSelected ? '#10b981' : '#030712';
              slice.element.style.strokeWidth = isSelected ? '3px' : (slice.kind === 'kpi' && state.drillNodeId === 'root-curriculum' ? '0.2px' : '1px');
            } else {
              slice.element.style.opacity = '0.12';
              slice.element.style.stroke = '#030712';
              slice.element.style.strokeWidth = '0.5px';
            }
          }
        });
      }

      // Update Selected Halo
      haloGroup.replaceChildren();
      if (activeId !== graph.centerNode.id) {
        const activeNode = graph.nodeById.get(activeId);
        if (activeNode) {
          const halo = createSvgElement('circle', {
            cx: String(activeNode.x),
            cy: String(activeNode.y),
            r: String((activeNode.size || 6) + 9),
            class: 'selected-halo',
            fill: 'none',
            stroke: '#10b981',
            'stroke-width': '2.5',
            'stroke-dasharray': '5 3'
          });
          haloGroup.appendChild(halo);
        }
      }
    }

    // Filter Logic supporting Search Text, Subject, Grade, Term, Type, School
    function nodeMatchesFilter(node) {
      if (node.id === graph.centerNode.id) return true;

      // Realtime Search Text Matching
      if (state.search && state.search.trim().length > 0) {
        const qNorm = normText(state.search);
        if (node.searchIndex && !node.searchIndex.includes(qNorm)) {
          return false;
        }
      }

      // Subject Filter
      if (state.subject !== 'ALL') {
        if (node.kind === 'subject' && node.name !== state.subject) return false;
        if (node.subject && node.subject !== state.subject) return false;
      }

      // Grade Filter
      if (state.grade !== 'ALL' && node.kind === 'kpi') {
        if (state.grade.startsWith('มัธยม') || state.grade.startsWith('ประถม')) {
          if (node.gradeBand !== state.grade) return false;
        } else {
          if (node.grade !== state.grade) return false;
        }
      }

      // Type Filter
      if (state.type !== 'ALL' && node.kind === 'kpi') {
        if (node.type !== state.type) return false;
      }

      // School courses filter
      if (state.school === 'MAPPED' && node.kind === 'kpi') {
        if (!node.courses || node.courses.length === 0) return false;
      }

      // Term Filter
      if (state.term !== 'ALL' && node.kind === 'kpi') {
        const hasTerm = (node.courses || []).some(c => {
          return state.term === '1' ? c.includes('เทอม 1') || c.endsWith('1') || c.includes('1_') : c.includes('เทอม 2') || c.endsWith('2') || c.includes('2_');
        });
        if (!hasTerm) return false;
      }

      return true;
    }

    // Dynamic Left Info Panel Renderer with Drill-Down Actions
    function updateInfoPanel(nodeId) {
      const node = (state.viewMode === 'sunburst' && sunburstData && sunburstData.sliceById.get(nodeId)) ||
                   (graph && graph.nodeById.get(nodeId)) ||
                   (sunburstData && sunburstData.sliceById.get(nodeId));
      if (!node) return;

      let html = '';

      if (node.kind === 'grade') {
        const isCenter = node.id === state.drillNodeId;
        const gradeKpis = DATA.kpis.filter(k => normalizeGradeKey(k.grade) === node.code);
        const formativeCount = gradeKpis.filter(k => k.type === 'ระหว่างทาง').length;
        const summativeCount = gradeKpis.filter(k => k.type === 'ปลายทาง').length;

        // Group by subject in this grade
        const subjBreakdown = {};
        gradeKpis.forEach(k => {
          subjBreakdown[k.subject] = (subjBreakdown[k.subject] || 0) + 1;
        });

        // School courses for this grade
        const gradeCourses = [];
        const seenGradeCourses = new Set();
        gradeKpis.forEach(k => {
          (k.courses || []).forEach(c => {
            if (!seenGradeCourses.has(c)) {
              seenGradeCourses.add(c);
              gradeCourses.push({ code: c, name: c, school: 'โรงเรียนพัฒนานิคม' });
            }
          });
        });

        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-700">
              <div class="flex items-center space-x-2 mb-1.5">
                <span class="w-3 h-3 rounded-full" style="background-color: ${node.color}"></span>
                <span class="text-[10px] font-mono uppercase font-bold text-slate-400">ระดับชั้นการศึกษา</span>
              </div>
              <h2 class="text-base font-bold text-white">${node.name}</h2>
              <div class="flex items-center space-x-3 text-xs mt-2 font-mono">
                <span class="text-cyan-400 font-semibold">${node.stage}</span>
                <span class="text-slate-500">•</span>
                <span class="text-emerald-400 font-semibold">${gradeKpis.length.toLocaleString()} ตัวชี้วัด</span>
              </div>
            </div>

            <!-- Stats Grid -->
            <div class="grid grid-cols-2 gap-2 text-center font-mono">
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-sky-400 block">ระหว่างทาง</span>
                <span class="text-base font-bold text-sky-400">${formativeCount}</span>
              </div>
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-amber-400 block">ปลายทาง</span>
                <span class="text-base font-bold text-amber-400">${summativeCount}</span>
              </div>
            </div>

            <!-- Subject Distribution in this Grade -->
            <div>
              <span class="text-[11px] font-semibold text-slate-400 block mb-2">๘ กลุ่มสาระในระดับชั้นนี้:</span>
              <div class="space-y-1.5">
                ${Object.entries(subjBreakdown).sort((a,b) => b[1] - a[1]).map(([sName, cnt]) => {
                  const sMeta = DATA.subject_meta[sName] || { color: '#10b981' };
                  return `
                    <div class="flex items-center justify-between p-2 rounded-xl bg-slate-900 border border-slate-800/80 hover:border-slate-700 text-xs transition cursor-pointer" onclick="selectNode('${node.id}-subj-${sMeta.code || sName}')">
                      <div class="flex items-center space-x-2">
                        <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${sMeta.color}"></span>
                        <span class="text-slate-300 font-medium">${sName}</span>
                      </div>
                      <span class="font-mono text-emerald-400 font-bold">${cnt} ตชว.</span>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>

            <!-- School Courses for this Grade -->
            ${gradeCourses.length > 0 ? `
              <div>
                <span class="text-[11px] font-semibold text-slate-400 block mb-2">รายวิชาของโรงเรียน (${gradeCourses.length} วิชา):</span>
                <div class="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  ${gradeCourses.map(c => `
                    <div class="p-2 rounded-xl bg-slate-900 border border-slate-800/80 text-xs">
                      <div class="flex items-center justify-between">
                        <span class="font-mono font-bold text-white">${c.code}</span>
                        <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">${c.school}</span>
                      </div>
                      <p class="text-slate-300 text-[11px] mt-0.5">${c.name}</p>
                    </div>
                  `).join('')}
                </div>
              </div>
            ` : ''}

            <!-- Action Buttons -->
            <div class="space-y-2 pt-2">
              ${!isCenter ? `
                <button onclick="drillTo('${node.id}')" class="w-full py-2.5 rounded-xl font-bold bg-emerald-600 hover:bg-emerald-500 text-white text-xs transition shadow-lg flex items-center justify-center space-x-2">
                  <i data-lucide="zoom-in" class="w-4 h-4"></i>
                  <span>เจาะลึกเฉพาะชั้น ${node.code}</span>
                </button>
              ` : ''}
              <button onclick="downloadGradeWord('${node.code}')" class="w-full py-2 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs transition flex items-center justify-center space-x-2">
                <i data-lucide="file-down" class="w-3.5 h-3.5 text-cyan-400"></i>
                <span>ดาวน์โหลดเอกสารชั้น ${node.code} (.docx)</span>
              </button>
            </div>
          </div>
        `;
      } else if (node.kind === 'grade-subject' || node.kind === 'radar-cell') {
        const isCenter = node.id === state.drillNodeId;
        const cellKpis = DATA.kpis.filter(k => normalizeGradeKey(k.grade) === node.grade && k.subject === node.subject);
        const formativeCount = cellKpis.filter(k => k.type === 'ระหว่างทาง').length;
        const summativeCount = cellKpis.filter(k => k.type === 'ปลายทาง').length;
        const sMeta = DATA.subject_meta[node.subject] || { color: '#10b981' };

        // Unique standards
        const uniqueStds = [...new Set(cellKpis.map(k => k.standard))];

        // School courses matching this grade & subject
        const matchCourses = [];
        const seenMatchCourses = new Set();
        cellKpis.forEach(k => {
          (k.courses || []).forEach(c => {
            if (!seenMatchCourses.has(c)) {
              seenMatchCourses.add(c);
              matchCourses.push({ code: c, name: c, school: 'โรงเรียนพัฒนานิคม' });
            }
          });
        });

        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-700">
              <div class="flex items-center space-x-2 mb-1.5">
                <span class="w-3 h-3 rounded-full" style="background-color: ${sMeta.color}"></span>
                <span class="text-[10px] font-mono uppercase font-bold text-slate-400">กลุ่มสาระการเรียนรู้</span>
              </div>
              <h2 class="text-base font-bold text-white">${node.subject}</h2>
              <div class="flex items-center space-x-3 text-xs mt-2 font-mono">
                <span class="text-cyan-400 font-semibold">ชั้น ${node.grade}</span>
                <span class="text-slate-500">•</span>
                <span class="text-emerald-400 font-semibold">${cellKpis.length} ตัวชี้วัด</span>
              </div>
            </div>

            <!-- Stats Grid -->
            <div class="grid grid-cols-2 gap-2 text-center font-mono">
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-sky-400 block">ระหว่างทาง</span>
                <span class="text-base font-bold text-sky-400">${formativeCount}</span>
              </div>
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-amber-400 block">ปลายทาง</span>
                <span class="text-base font-bold text-amber-400">${summativeCount}</span>
              </div>
            </div>

            <!-- Standards list -->
            <div>
              <span class="text-[11px] font-semibold text-slate-400 block mb-2">มาตรฐานในระดับชั้นนี้ (${uniqueStds.length} มาตรฐาน):</span>
              <div class="space-y-1.5">
                ${uniqueStds.map(stdCode => {
                  const countInStd = cellKpis.filter(k => k.standard === stdCode).length;
                  return `
                    <div class="flex items-center justify-between p-2 rounded-xl bg-slate-900 border border-slate-800/80 text-xs">
                      <span class="font-mono text-cyan-400 font-bold">มาตรฐาน ${stdCode}</span>
                      <span class="font-mono text-slate-400">${countInStd} ตัวชี้วัด</span>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>

            <!-- School courses -->
            ${matchCourses.length > 0 ? `
              <div>
                <span class="text-[11px] font-semibold text-slate-400 block mb-2">รายวิชาที่สอนในโรงเรียน (${matchCourses.length} วิชา):</span>
                <div class="space-y-1.5">
                  ${matchCourses.map(c => `
                    <div class="p-2 rounded-xl bg-slate-900 border border-slate-800/80 text-xs">
                      <div class="flex items-center justify-between">
                        <span class="font-mono font-bold text-white">${c.code}</span>
                        <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">${c.school}</span>
                      </div>
                      <p class="text-slate-300 text-[11px] mt-0.5">${c.name}</p>
                    </div>
                  `).join('')}
                </div>
              </div>
            ` : ''}

            <!-- Action Buttons -->
            <div class="space-y-2 pt-2">
              ${!isCenter ? `
                <button onclick="drillTo('${node.id}')" class="w-full py-2.5 rounded-xl font-bold bg-emerald-600 hover:bg-emerald-500 text-white text-xs transition shadow-lg flex items-center justify-center space-x-2">
                  <i data-lucide="zoom-in" class="w-4 h-4"></i>
                  <span>เจาะลึกเฉพาะ ${node.subject} (${node.grade})</span>
                </button>
              ` : ''}
              <button onclick="downloadGradeWord('${node.grade}')" class="w-full py-2 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs transition flex items-center justify-center space-x-2">
                <i data-lucide="file-down" class="w-3.5 h-3.5 text-cyan-400"></i>
                <span>ดาวน์โหลดเอกสาร (.docx)</span>
              </button>
            </div>
          </div>
        `;
      } else if (node.kind === 'grade-standard') {
        const stdKpis = DATA.kpis.filter(k => normalizeGradeKey(k.grade) === node.grade && k.standard === node.standardCode);
        const formativeCount = stdKpis.filter(k => k.type === 'ระหว่างทาง').length;
        const summativeCount = stdKpis.filter(k => k.type === 'ปลายทาง').length;

        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-700">
              <span class="text-[10px] font-mono uppercase font-bold text-slate-400">มาตรฐานการเรียนรู้</span>
              <h2 class="text-base font-bold text-white mt-1">มาตรฐาน ${node.standardCode}</h2>
              <div class="flex items-center space-x-3 text-xs mt-2 font-mono">
                <span class="text-cyan-400 font-semibold">${node.subject}</span>
                <span class="text-slate-500">•</span>
                <span class="text-emerald-400 font-semibold">ชั้น ${node.grade} (${stdKpis.length} ตัวชี้วัด)</span>
              </div>
            </div>

            <!-- Stats Grid -->
            <div class="grid grid-cols-2 gap-2 text-center font-mono">
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-sky-400 block">ระหว่างทาง</span>
                <span class="text-base font-bold text-sky-400">${formativeCount}</span>
              </div>
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-amber-400 block">ปลายทาง</span>
                <span class="text-base font-bold text-amber-400">${summativeCount}</span>
              </div>
            </div>

            <!-- KPIs in this standard -->
            <div>
              <span class="text-[11px] font-semibold text-slate-400 block mb-2">ตัวชี้วัดในมาตรฐานนี้:</span>
              <div class="space-y-2">
                ${stdKpis.map(k => `
                  <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800/80 hover:border-slate-700 transition cursor-pointer" onclick="selectNode('kpi-${k.id || k.code.replace(/\\s+/g, '_')}')">
                    <div class="flex items-center justify-between mb-1">
                      <span class="font-mono text-xs font-bold text-emerald-400">${k.code}</span>
                      <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ${k.type === 'ปลายทาง' ? 'bg-amber-950/80 text-amber-400 border border-amber-800/60' : 'bg-sky-950/80 text-sky-400 border border-sky-800/60'}">${k.type || 'ตัวชี้วัด'}</span>
                    </div>
                    <p class="text-slate-300 text-xs">${k.kpi_text}</p>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        `;
      } else if (node.kind === 'root') {
        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-brand-navy/60 border border-slate-700/80">
              <span class="text-[10px] font-mono tracking-wider text-emerald-400 uppercase font-bold">โครงสร้างหลักสูตรแกนกลาง</span>
              <h2 class="text-base font-bold text-white mt-1">หลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน</h2>
              <p class="text-slate-300 text-xs mt-1">พุทธศักราช ๒๕๕๑ (ฉบับปรับปรุง ๒๕๖๐) • ๘ กลุ่มสาระ • ๓๑ สาระ • ๕๕ มาตรฐาน • ๒,๐๕๖ ตัวชี้วัด</p>
            </div>

            <div class="grid grid-cols-2 gap-2 text-center font-mono">
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-slate-400 block">กลุ่มสาระการเรียนรู้</span>
                <span class="text-base font-bold text-white">๘ กลุ่ม</span>
              </div>
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-cyan-400 block">สาระการเรียนรู้</span>
                <span class="text-base font-bold text-cyan-400">๓๑ สาระ</span>
              </div>
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-slate-400 block">มาตรฐานการเรียนรู้</span>
                <span class="text-base font-bold text-white">๕๕ มาตรฐาน</span>
              </div>
              <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[10px] text-emerald-400 block">ตัวชี้วัดทั้งหมด</span>
                <span class="text-base font-bold text-emerald-400">๒,๐๕๖ ข้อ</span>
              </div>
            </div>

            <div>
              <span class="text-[11px] font-semibold text-slate-400 block mb-2">เลือกกลุ่มสาระการเรียนรู้:</span>
              <div class="space-y-1.5">
                ${Object.entries(DATA.subject_meta).map(([name, meta]) => `
                  <button onclick="drillTo('subj-${meta.code || name}')" class="w-full px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-left transition flex items-center justify-between text-xs group">
                    <div class="flex items-center space-x-2">
                      <span class="w-2.5 h-2.5 rounded-full" style="background-color:${meta.color}"></span>
                      <span class="text-white group-hover:text-emerald-400 transition font-medium">${name}</span>
                    </div>
                    <span class="font-mono text-[10px] text-slate-500">${DATA.subject_counts[name]?.total || 0} ตัวชี้วัด ➔</span>
                  </button>
                `).join('')}
              </div>
            </div>
          </div>
        `;
      } else if (node.kind === 'subject') {
        const isCenter = node.id === state.drillNodeId;
        const subjectStrands = DATA.kpis.filter(k => k.subject === node.name);
        const uniqueStrands = [...new Set(subjectStrands.map(k => k.strand))];

        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-700">
              <div class="flex items-center space-x-2 mb-1.5">
                <span class="w-3 h-3 rounded-full" style="background-color: ${node.color}"></span>
                <span class="text-[10px] font-mono uppercase font-bold text-slate-400">กลุ่มสาระการเรียนรู้</span>
              </div>
              <h2 class="text-base font-bold text-white">${node.name}</h2>
              <div class="flex items-center space-x-3 text-xs mt-2 font-mono">
                <span class="text-cyan-400 font-semibold">${uniqueStrands.length} สาระ</span>
                <span class="text-slate-500">•</span>
                <span class="text-white">${node.kpiCount || subjectStrands.length} ตัวชี้วัด</span>
              </div>
            </div>

            <!-- Drill-down / Return Action -->
            <div class="space-y-1.5">
              ${!isCenter ? `
                <button onclick="drillTo('${node.id}')" class="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition shadow-md flex items-center justify-center space-x-1.5">
                  <i data-lucide="zoom-in" class="w-3.5 h-3.5"></i>
                  <span>ดูเฉพาะกลุ่มสาระ${node.name}</span>
                </button>
              ` : `
                <button onclick="drillUp()" class="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition flex items-center justify-center space-x-1.5">
                  <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
                  <span>ย้อนกลับภาพรวม</span>
                </button>
              `}
            </div>

            <!-- List of Strands in Subject -->
            <div>
              <span class="text-[11px] font-semibold text-slate-300 block mb-2">สาระการเรียนรู้ในกลุ่มนี้ (${uniqueStrands.length} สาระ):</span>
              <div class="space-y-1.5">
                ${uniqueStrands.map((stName, idx) => {
                  const stMatch = stName.match(/สาระที่\\s*([0-9๑-๙]+)/);
                  const stNum = stMatch ? stMatch[1] : String(idx + 1);
                  const sMeta = DATA.subject_meta[node.name] || {};
                  const stId = `strand-${sMeta.code}-${stNum}`;
                  return `
                    <button onclick="drillTo('${stId}')" class="w-full p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500 text-left transition flex items-center justify-between group">
                      <div>
                        <span class="text-xs font-semibold text-cyan-300 group-hover:text-cyan-200 block">${stName}</span>
                      </div>
                      <span class="font-mono text-[10px] text-slate-500">ดูสาระนี้ ➔</span>
                    </button>
                  `;
                }).join('')}
              </div>
            </div>

            <!-- Why Learn -->
            ${node.data?.why ? `
              <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <strong class="text-emerald-400 block text-[10px] uppercase font-mono mb-1">ทำไมต้องเรียนกลุ่มสาระนี้</strong>
                <p class="text-slate-300 text-[11px] leading-relaxed max-h-32 overflow-y-auto">${node.data.why.slice(0, 300)}...</p>
              </div>
            ` : ''}
          </div>
        `;
      } else if (node.kind === 'strand') {
        const isCenter = node.id === state.drillNodeId;
        const strandKpis = DATA.kpis.filter(k => k.strand === node.name && (!node.subject || k.subject === node.subject));
        const strandStandards = [...new Set(strandKpis.map(k => k.standard))];
        const formativeCount = strandKpis.filter(k => k.type === 'ระหว่างทาง').length;
        const summativeCount = strandKpis.filter(k => k.type === 'ปลายทาง').length;

        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-slate-900 border border-cyan-500/40">
              <span class="text-[10px] font-mono tracking-wider text-cyan-400 uppercase font-bold">สาระการเรียนรู้</span>
              <h2 class="text-base font-bold text-white mt-1">${node.name}</h2>
              <p class="text-slate-400 text-xs mt-0.5">กลุ่มสาระการเรียนรู้${node.subject}</p>
            </div>

            <div class="grid grid-cols-3 gap-1.5 text-center font-mono">
              <div class="p-2 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[9px] text-slate-400 block">มาตรฐาน</span>
                <span class="text-sm font-bold text-white">${strandStandards.length}</span>
              </div>
              <div class="p-2 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[9px] text-sky-400 block">ระหว่างทาง</span>
                <span class="text-sm font-bold text-sky-400">${formativeCount}</span>
              </div>
              <div class="p-2 rounded-xl bg-slate-900 border border-slate-800">
                <span class="text-[9px] text-amber-400 block">ปลายทาง</span>
                <span class="text-sm font-bold text-amber-400">${summativeCount}</span>
              </div>
            </div>

            <!-- Drill-down / Return Action -->
            <div class="space-y-1.5">
              ${!isCenter ? `
                <button onclick="drillTo('${node.id}')" class="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition shadow-md flex items-center justify-center space-x-1.5">
                  <i data-lucide="zoom-in" class="w-3.5 h-3.5"></i>
                  <span>ดูเฉพาะ${node.shortLabel}</span>
                </button>
              ` : `
                <button onclick="drillUp()" class="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition flex items-center justify-center space-x-1.5">
                  <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
                  <span>ย้อนกลับ</span>
                </button>
              `}
            </div>

            <!-- List of Standards in Strand -->
            <div>
              <span class="text-[11px] font-semibold text-slate-300 block mb-2">มาตรฐานในสาระนี้:</span>
              <div class="space-y-2">
                ${strandStandards.map(stdCode => {
                  const stdDesc = DATA.standards[stdCode] || '';
                  const stdId = `std-${stdCode.replace(/\\s+/g, '_')}`;
                  return `
                    <button onclick="drillTo('${stdId}')" class="w-full p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500 text-left transition group">
                      <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-bold text-white group-hover:text-emerald-400 transition">${stdCode}</span>
                        <span class="font-mono text-[10px] text-cyan-400">ดูมาตรฐานนี้ ➔</span>
                      </div>
                      <p class="text-[11px] text-slate-400 leading-snug line-clamp-2">${stdDesc || 'ไม่มีคำอธิบาย'}</p>
                    </button>
                  `;
                }).join('')}
              </div>
            </div>

            <!-- Word Copy -->
            <button onclick="copyStrandWordTable('${node.id}')" class="w-full py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-md flex items-center justify-center space-x-1.5">
              <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i>
              <span>คัดลอกตัวชี้วัดในสาระนี้ (${strandKpis.length} ข้อ) ลง Word</span>
            </button>
          </div>
        `;
      } else if (node.kind === 'standard') {
        const isCenter = node.id === state.drillNodeId;
        const stdKpis = DATA.kpis.filter(k => k.standard === node.code);

        html = `
          <div class="space-y-4 animate-fadeIn">
            <div class="p-4 rounded-2xl bg-slate-900 border border-blue-500/40">
              <span class="text-[10px] font-mono tracking-wider text-blue-400 uppercase font-bold">มาตรฐานการเรียนรู้</span>
              <h2 class="text-base font-bold text-white mt-1">${node.code}</h2>
              <p class="text-slate-400 text-xs mt-0.5">${node.strand || ''} • กลุ่มสาระ${node.subject || ''}</p>
              <p class="text-slate-200 text-xs leading-relaxed mt-2.5 pt-2 border-t border-slate-800">${node.desc || DATA.standards[node.code] || 'ไม่มีคำอธิบาย'}</p>
            </div>

            <div class="flex items-center justify-between px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs">
              <span class="text-slate-400">ตัวชี้วัดทั้งหมด</span>
              <span class="text-white font-bold">${stdKpis.length} ข้อ</span>
            </div>

            <!-- Drill-down / Return Action -->
            <div class="space-y-1.5">
              ${!isCenter ? `
                <button onclick="drillTo('${node.id}')" class="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition shadow-md flex items-center justify-center space-x-1.5">
                  <i data-lucide="zoom-in" class="w-3.5 h-3.5"></i>
                  <span>ดูเฉพาะมาตรฐาน ${node.code}</span>
                </button>
              ` : `
                <button onclick="drillUp()" class="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition flex items-center justify-center space-x-1.5">
                  <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
                  <span>ย้อนกลับ</span>
                </button>
              `}
            </div>

            <!-- KPIs List -->
            <div>
              <span class="text-[11px] font-semibold text-slate-300 block mb-2">ตัวชี้วัดในมาตรฐานนี้:</span>
              <div class="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                ${stdKpis.map(k => `
                  <button onclick="selectNode('kpi-${k.id || k.code.replace(/\\s+/g, '_')}')" class="w-full p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-left transition flex items-center justify-between group">
                    <div>
                      <span class="font-mono font-bold text-xs ${k.type === 'ปลายทาง' ? 'text-amber-400' : 'text-sky-400'}">${k.code}</span>
                      <span class="text-[11px] text-slate-300 block truncate max-w-[180px]">${k.text}</span>
                    </div>
                    <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-950 text-slate-400">${k.grade}</span>
                  </button>
                `).join('')}
              </div>
            </div>

            <button onclick="copyStandardWordTable('${node.id}')" class="w-full py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-md flex items-center justify-center space-x-1.5">
              <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i>
              <span>คัดลอกตารางมาตรฐาน ${node.code} ลง Word</span>
            </button>
          </div>
        `;
      } else {
        // KPI Node (ตัวชี้วัด)
        const typeBadge = node.type === 'ปลายทาง'
          ? `<span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 text-[10px] font-mono font-bold">ตัวชี้วัดปลายทาง (Summative)</span>`
          : `<span class="px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/40 text-[10px] font-mono font-bold">ตัวชี้วัดระหว่างทาง (Formative)</span>`;

        const coursesHtml = (node.courses && node.courses.length > 0)
          ? node.courses.map(c => `
              <div class="p-1.5 rounded-lg bg-slate-950/70 border border-slate-800 text-[11px] font-mono text-purple-300 flex items-center justify-between">
                <span>${c}</span>
                <span class="text-[9px] text-slate-500">มัธยม</span>
              </div>
            `).join('')
          : '<div class="text-slate-500 text-[11px] italic">ไม่มีรายวิชาระบุเฉพาะ</div>';

        html = `
          <div class="space-y-3.5 animate-fadeIn">
            <!-- Header Card -->
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-700">
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-[10px] font-mono text-slate-400">ตัวชี้วัด</span>
                ${typeBadge}
              </div>
              <h2 class="text-lg font-bold font-mono text-white tracking-tight">${node.code}</h2>
              <p class="text-slate-400 text-[11px] mt-0.5">กลุ่มสาระ${node.subject} • ${node.strand} • ${node.gradeBand || node.grade}</p>
            </div>

            <!-- Standard -->
            <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <strong class="text-blue-400 block text-[10px] uppercase font-mono mb-1">มาตรฐาน ${node.standard}</strong>
              <p class="text-slate-300 leading-relaxed text-[11px]">${node.standardDesc || '-'}</p>
            </div>

            <!-- Indicator Text -->
            <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <strong class="text-amber-400 block text-[10px] uppercase font-mono mb-1">ข้อความตัวชี้วัด</strong>
              <p class="text-slate-100 font-medium leading-relaxed text-xs">${node.fullText}</p>
            </div>

            <!-- Core Content -->
            <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <strong class="text-emerald-400 block text-[10px] uppercase font-mono mb-1">สาระการเรียนรู้แกนกลาง</strong>
              <p class="text-slate-300 leading-relaxed text-[11px] whitespace-pre-line">${node.coreContent || 'ไม่มีสาระแกนกลางเฉพาะ'}</p>
            </div>

            <!-- School Courses -->
            <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <strong class="text-purple-400 block text-[10px] uppercase font-mono mb-1">วิชาโรงเรียนพัฒนานิคมที่สอน</strong>
              <div class="space-y-1 mt-1.5">${coursesHtml}</div>
            </div>

            <!-- Action Buttons -->
            <div class="space-y-1.5 pt-1">
              <button onclick="copyKpiWordTable('${node.id}')" class="w-full py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-md flex items-center justify-center space-x-1.5">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i>
                <span>คัดลอกตารางลง Word</span>
              </button>

              <div class="grid grid-cols-2 gap-1.5">
                <button onclick="copyKpiPlanTemplate('${node.id}')" class="py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium transition flex items-center justify-center space-x-1">
                  <i data-lucide="book-open" class="w-3 h-3 text-sky-400"></i>
                  <span>คัดลอกทำแผน</span>
                </button>
                <button onclick="copyToClipboard('${node.code}', 'คัดลอกรหัส ${node.code} แล้ว')" class="py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium transition flex items-center justify-center space-x-1">
                  <i data-lucide="copy" class="w-3 h-3 text-amber-400"></i>
                  <span>คัดลอกรหัส</span>
                </button>
              </div>
            </div>
          </div>
        `;
      }

      el.infoContent.innerHTML = html;
      lucide.createIcons();
    }

    // Filter Application & Autocomplete Search Matches
    function applyFilters() {
      const q = el.searchInput.value.trim();
      state.search = q;
      state.grade = el.filterGrade.value;
      state.term = el.filterTerm.value;
      state.type = el.filterType.value;
      state.school = el.filterSchool.value;

      // Sync catalog inputs if catalog is visible
      if (el.catalogSearchInput && el.catalogSearchInput.value !== q) {
        el.catalogSearchInput.value = q;
      }
      if (el.catalogFilterGrade && el.catalogFilterGrade.value !== state.grade) {
        el.catalogFilterGrade.value = state.grade;
      }
      if (el.catalogFilterType && el.catalogFilterType.value !== state.type) {
        el.catalogFilterType.value = state.type;
      }

      // Update search match chips on Map view
      if (q.length > 0) {
        const qNorm = normText(q);
        const matches = DATA.kpis.filter(k => k.searchIndex?.includes(qNorm));
        el.searchMatchCount.innerText = `ตรงกับเงื่อนไข ${matches.length} รายการ`;

        el.searchMatchChips.innerHTML = matches.slice(0, 10).map(m => `
          <button onclick="jumpToKpi('${m.code}', '${m.subject}', '${m.standard}')" class="px-2 py-0.5 rounded-md bg-slate-800 hover:bg-emerald-600 text-[11px] font-mono text-slate-200 transition">
            ${m.code}
          </button>
        `).join('');
      } else {
        el.searchMatchCount.innerText = '';
        el.searchMatchChips.innerHTML = '';
      }

      applyVisibility();

      // If in Catalog view, also update table
      if (state.viewMode === 'catalog') {
        renderCatalogTable();
      }
    }

    // Jump to specific KPI (Drill down to its view if needed)
    function jumpToKpi(kpiCode, subject, standard) {
      const sMeta = DATA.subject_meta[subject] || {};
      const stdId = `std-${standard.replace(/\\s+/g, '_')}`;
      drillTo(stdId);
      setTimeout(() => {
        const targetNode = graph.nodes.find(n => n.kind === 'kpi' && n.code === kpiCode);
        if (targetNode) selectNode(targetNode.id);
      }, 50);
    }

    // Catalog Table View Renderer with Instant Search Filtering
    function renderCatalogTable() {
      // Filter directly from 2,056 Master KPIs
      const filtered = DATA.kpis.filter(k => {
        // Search text filter
        if (state.search && state.search.trim().length > 0) {
          const qNorm = normText(state.search);
          if (!k.searchIndex?.includes(qNorm)) return false;
        }

        // Subject filter
        if (state.subject !== 'ALL' && k.subject !== state.subject) return false;

        // Grade filter
        if (state.grade !== 'ALL') {
          if (state.grade.startsWith('มัธยม') || state.grade.startsWith('ประถม')) {
            if (k.grade_band !== state.grade) return false;
          } else {
            if (k.grade !== state.grade) return false;
          }
        }

        // Type filter
        if (state.type !== 'ALL' && k.type !== state.type) return false;

        return true;
      });

      // Update Result Count Badge
      const totalMaster = DATA.kpis.length;
      if (el.catalogResultCount) {
        if (state.search || state.subject !== 'ALL' || state.grade !== 'ALL' || state.type !== 'ALL') {
          el.catalogResultCount.innerHTML = `พบ <span class="text-white font-bold">${filtered.length}</span> รายการ จากทั้งหมด ${totalMaster} ข้อ`;
        } else {
          el.catalogResultCount.innerHTML = `แสดงทั้งหมด <span class="text-white font-bold">${totalMaster}</span> ตัวชี้วัด`;
        }
      }

      const limit = state.catalogLimit || 150;
      const sliced = filtered.slice(0, limit);
      let rows = '';

      sliced.forEach(k => {
        const isChecked = state.selectedKpiCodes.has(k.code);
        const typeColor = k.type === 'ปลายทาง' ? 'text-amber-400' : 'text-sky-400';
        const typeBg = k.type === 'ปลายทาง' ? 'bg-amber-500/10 border-amber-500/30' : 'bg-sky-500/10 border-sky-500/30';
        const courses = (k.courses || []).slice(0, 2).join(', ');

        rows += `
          <tr class="hover:bg-slate-900/80 transition">
            <td class="p-3 text-center">
              <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleKpiSelect('${k.code}')" class="rounded border-slate-700 bg-slate-900 text-emerald-600 focus:ring-0">
            </td>
            <td class="p-3 font-mono font-bold text-white whitespace-nowrap">${k.code}</td>
            <td class="p-3 whitespace-nowrap">
              <span class="text-slate-200 font-medium">${k.subject}</span>
              <span class="text-slate-400 block text-[10px]">${k.strand || ''}</span>
            </td>
            <td class="p-3 text-center whitespace-nowrap">
              <span class="px-2 py-0.5 rounded-full border text-[10px] font-mono font-bold ${typeColor} ${typeBg}">${k.type}</span>
            </td>
            <td class="p-3 leading-relaxed text-slate-200">${k.text}</td>
            <td class="p-3 text-slate-400 leading-relaxed text-[11px]">${(k.core_content || '-').slice(0, 100)}</td>
            <td class="p-3 text-[11px] font-mono text-purple-300 whitespace-nowrap">${courses || '<span class="text-slate-600">-</span>'}</td>
            <td class="p-3 text-center whitespace-nowrap">
              <button onclick="jumpToKpi('${k.code}', '${k.subject}', '${k.standard}'); switchToMapView();" class="px-2.5 py-1 rounded-lg bg-emerald-950/80 hover:bg-emerald-800/80 border border-emerald-500/40 text-emerald-300 font-medium transition text-[11px]">
                ดูในแผนภาพ
              </button>
            </td>
          </tr>
        `;
      });

      el.catalogTbody.innerHTML = rows || `
        <tr>
          <td colspan="8" class="p-8 text-center text-slate-500">
            <i data-lucide="search-x" class="w-8 h-8 mx-auto mb-2 text-slate-600"></i>
            <div>ไม่พบตัวชี้วัดที่ตรงกับคำค้นหา "${state.search}"</div>
            <button onclick="clearCatalogSearch()" class="mt-2 text-xs text-emerald-400 hover:underline">ล้างคำค้นหาทั้งหมด</button>
          </td>
        </tr>
      `;

      // Pagination / Show All button
      if (filtered.length > limit) {
        el.catalogPaginationStrip.innerHTML = `
          <button onclick="expandCatalogLimit()" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition shadow">
            แสดงทั้งหมดที่เหลืออีก ${filtered.length - limit} รายการ
          </button>
        `;
      } else {
        el.catalogPaginationStrip.innerHTML = '';
      }

      lucide.createIcons();
    }

    function expandCatalogLimit() {
      state.catalogLimit = 5000;
      renderCatalogTable();
    }

    function clearCatalogSearch() {
      state.search = '';
      state.subject = 'ALL';
      state.grade = 'ALL';
      state.type = 'ALL';
      if (el.searchInput) el.searchInput.value = '';
      if (el.catalogSearchInput) el.catalogSearchInput.value = '';
      if (el.catalogFilterSubject) el.catalogFilterSubject.value = 'ALL';
      if (el.catalogFilterGrade) el.catalogFilterGrade.value = 'ALL';
      if (el.catalogFilterType) el.catalogFilterType.value = 'ALL';
      applyFilters();
      renderCatalogTable();
    }

    function toggleKpiSelect(code) {
      if (state.selectedKpiCodes.has(code)) state.selectedKpiCodes.delete(code);
      else state.selectedKpiCodes.add(code);
    }

    // Double-Layer Pointer Drag & Click Event Handlers
    function bindEvents() {
      let pointerStart = { x: 0, y: 0, time: 0 };
      let isPointerDown = false;
      let hasDragged = false;
      let targetNodeId = null;

      // Wheel Zoom
      el.graphStage.addEventListener('wheel', (e) => {
        e.preventDefault();
        const rect = el.graphSvg.getBoundingClientRect();
        const pointerX = e.clientX - rect.left;
        const pointerY = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const svgX = (pointerX - centerX - graphState.translateX) / graphState.scale;
        const svgY = (pointerY - centerY - graphState.translateY) / graphState.scale;

        const intensity = Math.exp(-e.deltaY * 0.0022);
        const nextScale = Math.max(ZOOM_LIMITS.min, Math.min(ZOOM_LIMITS.max, graphState.scale * intensity));

        graphState.translateX = pointerX - centerX - svgX * nextScale;
        graphState.translateY = pointerY - centerY - svgY * nextScale;
        graphState.scale = nextScale;
        updateViewportTransform();
      }, { passive: false });

      // Pointer Down
      el.graphStage.addEventListener('pointerdown', (e) => {
        if (e.button !== undefined && e.button !== 0) return;
        isPointerDown = true;
        hasDragged = false;
        pointerStart = { x: e.clientX, y: e.clientY, time: Date.now() };

        const clickable = e.target.closest('.node, .sunburst-slice, .radar-cell, [data-slice-id], [data-node-id]');
        targetNodeId = clickable ? (clickable.getAttribute('data-node-id') || clickable.getAttribute('data-slice-id')) : null;

        graphState.dragStartX = e.clientX - graphState.translateX;
        graphState.dragStartY = e.clientY - graphState.translateY;

        // Only capture pointer for background panning; do not capture when clicking a node/slice
        if (!clickable) {
          try { el.graphStage.setPointerCapture(e.pointerId); } catch (_) {}
        }
      });

      // Pointer Move
      el.graphStage.addEventListener('pointermove', (e) => {
        if (!isPointerDown) return;
        const dx = e.clientX - pointerStart.x;
        const dy = e.clientY - pointerStart.y;
        const dist = Math.hypot(dx, dy);

        if (dist > 5) {
          hasDragged = true;
          graphState.isDragging = true;
          graphState.translateX = e.clientX - graphState.dragStartX;
          graphState.translateY = e.clientY - graphState.dragStartY;
          updateViewportTransform();
        }
      });

      // Pointer Up
      el.graphStage.addEventListener('pointerup', (e) => {
        if (!isPointerDown) return;
        isPointerDown = false;
        graphState.isDragging = false;

        try {
          if (el.graphStage.hasPointerCapture(e.pointerId)) {
            el.graphStage.releasePointerCapture(e.pointerId);
          }
        } catch (_) {}

        // If moved less than 6px, guaranteed click!
        const dx = e.clientX - pointerStart.x;
        const dy = e.clientY - pointerStart.y;
        const dist = Math.hypot(dx, dy);

        if (dist <= 6) {
          const clickable = e.target.closest('.node, .sunburst-slice, .radar-cell, [data-slice-id], [data-node-id]');
          const id = (clickable ? (clickable.getAttribute('data-node-id') || clickable.getAttribute('data-slice-id')) : null) || targetNodeId;
          if (id) {
            selectNode(id);
          }
        }
      });

      // Drill Up button
      el.btnDrillUp.addEventListener('click', drillUp);

      // Toolbar buttons
      el.btnToggleFocus.addEventListener('click', () => {
        state.focusMode = !state.focusMode;
        el.btnToggleFocus.classList.toggle('bg-emerald-600/20', state.focusMode);
        applyVisibility();
      });

      el.btnToggleLabels.addEventListener('click', () => {
        state.showLabels = !state.showLabels;
        el.labelToggleText.innerText = state.showLabels ? 'ซ่อนป้ายชื่อ' : 'แสดงป้ายชื่อ';
        document.querySelectorAll('.node-label-bg, .node-label-fg').forEach(lbl => {
          lbl.style.display = state.showLabels ? '' : 'none';
        });
      });

      el.btnResetView.addEventListener('click', () => {
        graphState.scale = 1;
        graphState.translateX = 0;
        graphState.translateY = 0;
        updateViewportTransform();
      });

      el.btnZoomIn.addEventListener('click', () => {
        graphState.scale = Math.min(ZOOM_LIMITS.max, graphState.scale * 1.3);
        updateViewportTransform();
      });

      el.btnZoomOut.addEventListener('click', () => {
        graphState.scale = Math.max(ZOOM_LIMITS.min, graphState.scale / 1.3);
        updateViewportTransform();
      });

      el.btnPanelReset.addEventListener('click', () => {
        drillTo('root-curriculum');
      });

      // Filter Inputs on Right Map Panel
      el.searchInput.addEventListener('input', applyFilters);
      el.filterGrade.addEventListener('change', applyFilters);
      el.filterTerm.addEventListener('change', applyFilters);
      el.filterType.addEventListener('change', applyFilters);
      el.filterSchool.addEventListener('change', applyFilters);

      el.btnClearFilters.addEventListener('click', () => {
        clearCatalogSearch();
      });

      // Catalog Search Inputs (แก้ปัญหาค้นหาในตารางไม่ได้!)
      el.catalogSearchInput.addEventListener('input', (e) => {
        state.search = e.target.value;
        if (el.searchInput) el.searchInput.value = e.target.value;
        renderCatalogTable();
      });

      el.catalogFilterSubject.addEventListener('change', (e) => {
        state.subject = e.target.value;
        renderCatalogTable();
      });

      el.catalogFilterGrade.addEventListener('change', (e) => {
        state.grade = e.target.value;
        if (el.filterGrade) el.filterGrade.value = e.target.value;
        renderCatalogTable();
      });

      el.catalogFilterType.addEventListener('change', (e) => {
        state.type = e.target.value;
        if (el.filterType) el.filterType.value = e.target.value;
        renderCatalogTable();
      });

      el.btnCatalogClearSearch.addEventListener('click', clearCatalogSearch);

      // View Switcher
      el.btnViewMap.addEventListener('click', switchToMapView);
      if (el.btnViewSunburst) el.btnViewSunburst.addEventListener('click', switchToSunburstView);
      el.btnViewCatalog.addEventListener('click', switchToCatalogView);

      // Sub-mode switchers for Circular View (Sunburst & Radar)
      if (el.btnSunburstGrade) {
        el.btnSunburstGrade.addEventListener('click', () => {
          state.sunburstMode = 'grade';
          el.btnSunburstGrade.className = 'px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-600 text-white transition flex items-center space-x-1 shadow-sm';
          if (el.btnSunburstRadar) el.btnSunburstRadar.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1';
          if (el.btnSunburstSubj) el.btnSunburstSubj.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1';
          if (el.sunburstModeDesc) el.sunburstModeDesc.textContent = 'วงในแบ่ง ๑๐ ระดับชั้น (ป.๑ - ม.๖) ➔ ๘ วิชา ➔ ตัวชี้วัด';
          loadView('root-curriculum', 'root-curriculum');
        });
      }

      if (el.btnSunburstRadar) {
        el.btnSunburstRadar.addEventListener('click', () => {
          state.sunburstMode = 'radar';
          el.btnSunburstRadar.className = 'px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-600 text-white transition flex items-center space-x-1 shadow-sm';
          if (el.btnSunburstGrade) el.btnSunburstGrade.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1';
          if (el.btnSunburstSubj) el.btnSunburstSubj.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1';
          if (el.sunburstModeDesc) el.sunburstModeDesc.textContent = '๑๐ วงแหวนระดับชั้น (ป.๑ ในสุด ถึง ม.๖ นอกสุด) x ๘ กลุ่มสาระ';
          loadView('root-curriculum', 'root-curriculum');
        });
      }

      if (el.btnSunburstSubj) {
        el.btnSunburstSubj.addEventListener('click', () => {
          state.sunburstMode = 'subject';
          el.btnSunburstSubj.className = 'px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-600 text-white transition flex items-center space-x-1 shadow-sm';
          if (el.btnSunburstGrade) el.btnSunburstGrade.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1';
          if (el.btnSunburstRadar) el.btnSunburstRadar.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-400 hover:text-white transition flex items-center space-x-1';
          if (el.sunburstModeDesc) el.sunburstModeDesc.textContent = 'วงในแบ่ง ๘ กลุ่มสาระการเรียนรู้ ➔ สาระ ➔ มาตรฐาน ➔ ตัวชี้วัด';
          loadView('root-curriculum', 'root-curriculum');
        });
      }

      // Help Modal
      const helpModal = document.getElementById('helpModal');
      document.getElementById('btn-open-help').addEventListener('click', () => helpModal.classList.remove('hidden'));
      document.getElementById('btn-close-help').addEventListener('click', () => helpModal.classList.add('hidden'));
      document.getElementById('btn-help-understood').addEventListener('click', () => helpModal.classList.add('hidden'));

      // Catalog Table Batch Buttons
      document.getElementById('btn-catalog-select-all').addEventListener('click', () => {
        const filtered = DATA.kpis.filter(k => {
          if (state.search && !k.searchIndex?.includes(normText(state.search))) return false;
          if (state.subject !== 'ALL' && k.subject !== state.subject) return false;
          if (state.grade !== 'ALL' && k.grade !== state.grade) return false;
          if (state.type !== 'ALL' && k.type !== state.type) return false;
          return true;
        });
        filtered.forEach(k => state.selectedKpiCodes.add(k.code));
        renderCatalogTable();
        showToast(`เลือกตัวชี้วัด ${state.selectedKpiCodes.size} รายการ`);
      });

      document.getElementById('btn-catalog-copy-word').addEventListener('click', () => {
        copyBatchTable();
      });

      document.getElementById('btn-catalog-copy-plan').addEventListener('click', () => {
        copyBatchPlan();
      });
    }

    function switchToMapView() {
      state.viewMode = 'map';
      el.mainMapView.classList.remove('hidden');
      el.mainCatalogView.classList.add('hidden');
      el.graphSvg.style.display = 'block';
      el.graphSvg.classList.remove('hidden');
      if (el.sunburstSvg) {
        el.sunburstSvg.style.display = 'none';
        el.sunburstSvg.classList.add('hidden');
      }
      if (el.sunburstModeBar) {
        el.sunburstModeBar.classList.add('hidden');
        el.sunburstModeBar.classList.remove('flex');
      }
      el.btnViewMap.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white transition flex items-center space-x-1.5 shadow-sm';
      if (el.btnViewSunburst) el.btnViewSunburst.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5';
      el.btnViewCatalog.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5';
      updateViewportTransform();
      applyVisibility();
    }

    function switchToSunburstView() {
      state.viewMode = 'sunburst';
      el.mainMapView.classList.remove('hidden');
      el.mainCatalogView.classList.add('hidden');
      el.graphSvg.style.display = 'none';
      el.graphSvg.classList.add('hidden');
      if (el.sunburstSvg) {
        el.sunburstSvg.style.display = 'block';
        el.sunburstSvg.classList.remove('hidden');
      }
      if (el.sunburstModeBar) {
        el.sunburstModeBar.classList.remove('hidden');
        el.sunburstModeBar.classList.add('flex');
      }
      if (el.btnViewSunburst) el.btnViewSunburst.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white transition flex items-center space-x-1.5 shadow-sm';
      el.btnViewMap.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5';
      el.btnViewCatalog.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5';
      updateViewportTransform();
      applyVisibility();
    }

    function switchToCatalogView() {
      state.viewMode = 'catalog';
      el.mainMapView.classList.add('hidden');
      el.mainCatalogView.classList.remove('hidden');
      el.graphSvg.style.display = 'none';
      el.graphSvg.classList.add('hidden');
      if (el.sunburstSvg) {
        el.sunburstSvg.style.display = 'none';
        el.sunburstSvg.classList.add('hidden');
      }
      if (el.sunburstModeBar) {
        el.sunburstModeBar.classList.add('hidden');
        el.sunburstModeBar.classList.remove('flex');
      }
      el.btnViewCatalog.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white transition flex items-center space-x-1.5 shadow-sm';
      el.btnViewMap.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5';
      if (el.btnViewSunburst) el.btnViewSunburst.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center space-x-1.5';
      renderCatalogTable();
    }

    function updateViewportTransform() {
      const transformStr = `translate(${graphState.translateX} ${graphState.translateY}) scale(${graphState.scale})`;
      viewportGroup.setAttribute('transform', transformStr);
      if (typeof sunburstViewportGroup !== 'undefined' && sunburstViewportGroup) {
        sunburstViewportGroup.setAttribute('transform', transformStr);
      }
    }

    // 1-Click Clipboard Actions for Teachers
    function copyKpiWordTable(kpiId) {
      const k = DATA.kpis.find(item => `kpi-${item.id || item.code.replace(/\\s+/g, '_')}` === kpiId) || graph.nodeById.get(kpiId);
      if (!k) return;

      const code = k.code;
      const stdCode = k.standard;
      const stdDesc = k.standard_desc || k.standardDesc || DATA.standards[stdCode] || '';
      const fullText = k.text || k.fullText || '';
      const coreContent = k.core_content || k.coreContent || '';
      const type = k.type;
      const courses = k.courses || [];

      const tsv = `รหัสตัวชี้วัด\\tมาตรฐานการเรียนรู้\\tข้อความตัวชี้วัด\\tสาระการเรียนรู้แกนกลาง\\tประเภทตัวชี้วัด\\tวิชาที่เปิดสอน\\n` +
        `${code}\\tมาตรฐาน ${stdCode}: ${stdDesc}\\t${fullText}\\t${coreContent.replace(/\\n/g, ' ')}\\tตัวชี้วัด${type}\\t${courses.join('; ')}\\n`;

      const typeColor = type === 'ปลายทาง' ? '#d97706' : '#2563eb';
      const htmlTable = `
        <table border="1" cellpadding="0" cellspacing="0" style="border-collapse:collapse; width:100%; font-family:Sarabun, sans-serif; font-size:14px; line-height:1.5;">
          <thead>
            <tr style="background-color:#f1f5f9; text-align:left;">
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รหัสตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">มาตรฐานการเรียนรู้</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ข้อความตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">สาระการเรียนรู้แกนกลาง</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ประเภท</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รายวิชาที่นำไปใช้</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="padding:6px 10px; border:1px solid #cbd5e1; font-weight:bold; white-space:nowrap; vertical-align:top;">${code}</td>
              <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;"><strong>มาตรฐาน ${stdCode}:</strong> ${stdDesc}</td>
              <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${fullText}</td>
              <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${coreContent.replace(/\\n/g, ' ')}</td>
              <td style="padding:6px 10px; border:1px solid #cbd5e1; color:${typeColor}; font-weight:bold; white-space:nowrap; vertical-align:top;">ตัวชี้วัด${type}</td>
              <td style="padding:6px 10px; border:1px solid #cbd5e1; font-size:12px; vertical-align:top;">${courses.join('; ')}</td>
            </tr>
          </tbody>
        </table>
      `;

      copyRichTable(tsv, htmlTable, `คัดลอกตาราง ${code} แล้ว`);
    }

    function copyStandardWordTable(stdId) {
      const rawStdCode = stdId.replace('std-', '').replace(/_/g, ' ');
      const stdKpis = DATA.kpis.filter(k => k.standard === rawStdCode);
      if (stdKpis.length === 0) return;
      const stdDesc = DATA.standards[rawStdCode] || '';

      let tsv = `รหัสตัวชี้วัด\\tมาตรฐานการเรียนรู้\\tข้อความตัวชี้วัด\\tสาระการเรียนรู้แกนกลาง\\tประเภทตัวชี้วัด\\tวิชาที่เปิดสอน\\n`;
      let htmlRows = '';

      stdKpis.forEach(k => {
        tsv += `${k.code}\\tมาตรฐาน ${rawStdCode}: ${stdDesc}\\t${k.text}\\t${(k.core_content || '').replace(/\\n/g, ' ')}\\tตัวชี้วัด${k.type}\\t${(k.courses || []).join('; ')}\\n`;
        const typeColor = k.type === 'ปลายทาง' ? '#d97706' : '#2563eb';
        htmlRows += `
          <tr>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; font-weight:bold; white-space:nowrap; vertical-align:top;">${k.code}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;"><strong>มาตรฐาน ${rawStdCode}:</strong> ${stdDesc}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${k.text}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${(k.core_content || '').replace(/\\n/g, ' ')}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; color:${typeColor}; font-weight:bold; white-space:nowrap; vertical-align:top;">ตัวชี้วัด${k.type}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; font-size:12px; vertical-align:top;">${(k.courses || []).join('; ')}</td>
          </tr>
        `;
      });

      const htmlTable = `
        <table border="1" cellpadding="0" cellspacing="0" style="border-collapse:collapse; width:100%; font-family:Sarabun, sans-serif; font-size:14px; line-height:1.5;">
          <thead>
            <tr style="background-color:#f1f5f9; text-align:left;">
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รหัสตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">มาตรฐานการเรียนรู้</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ข้อความตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">สาระการเรียนรู้แกนกลาง</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ประเภท</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รายวิชาที่นำไปใช้</th>
            </tr>
          </thead>
          <tbody>${htmlRows}</tbody>
        </table>
      `;

      copyRichTable(tsv, htmlTable, `คัดลอกตารางมาตรฐาน ${rawStdCode} แล้ว`);
    }

    function copyStrandWordTable(strandId) {
      const strandKpis = DATA.kpis.filter(k => {
        const strandMatch = (k.strand || '').match(/สาระที่\\s*([0-9๑-๙]+)/);
        const strandNum = strandMatch ? strandMatch[1] : '';
        const sMeta = DATA.subject_meta[k.subject] || {};
        return `strand-${sMeta.code}-${strandNum}` === strandId;
      });
      if (strandKpis.length === 0) return;

      const sample = strandKpis[0];
      let tsv = `รหัสตัวชี้วัด\\tมาตรฐานการเรียนรู้\\tข้อความตัวชี้วัด\\tสาระการเรียนรู้แกนกลาง\\tประเภทตัวชี้วัด\\tวิชาที่เปิดสอน\\n`;
      let htmlRows = '';

      strandKpis.forEach(k => {
        const stdDesc = DATA.standards[k.standard] || '';
        tsv += `${k.code}\\tมาตรฐาน ${k.standard}: ${stdDesc}\\t${k.text}\\t${(k.core_content || '').replace(/\\n/g, ' ')}\\tตัวชี้วัด${k.type}\\t${(k.courses || []).join('; ')}\\n`;
        const typeColor = k.type === 'ปลายทาง' ? '#d97706' : '#2563eb';
        htmlRows += `
          <tr>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; font-weight:bold; white-space:nowrap; vertical-align:top;">${k.code}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;"><strong>มาตรฐาน ${k.standard}:</strong> ${stdDesc}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${k.text}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${(k.core_content || '').replace(/\\n/g, ' ')}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; color:${typeColor}; font-weight:bold; white-space:nowrap; vertical-align:top;">ตัวชี้วัด${k.type}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; font-size:12px; vertical-align:top;">${(k.courses || []).join('; ')}</td>
          </tr>
        `;
      });

      const htmlTable = `
        <table border="1" cellpadding="0" cellspacing="0" style="border-collapse:collapse; width:100%; font-family:Sarabun, sans-serif; font-size:14px; line-height:1.5;">
          <thead>
            <tr style="background-color:#f1f5f9; text-align:left;">
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รหัสตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">มาตรฐานการเรียนรู้</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ข้อความตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">สาระการเรียนรู้แกนกลาง</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ประเภท</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รายวิชาที่นำไปใช้</th>
            </tr>
          </thead>
          <tbody>${htmlRows}</tbody>
        </table>
      `;

      copyRichTable(tsv, htmlTable, `คัดลอกตาราง ${sample.strand} แล้ว`);
    }

    function copyKpiPlanTemplate(kpiId) {
      const k = DATA.kpis.find(item => `kpi-${item.id || item.code.replace(/\\s+/g, '_')}` === kpiId) || graph.nodeById.get(kpiId);
      if (!k) return;

      const code = k.code;
      const stdCode = k.standard;
      const stdDesc = k.standard_desc || k.standardDesc || DATA.standards[stdCode] || '';
      const fullText = k.text || k.fullText || '';
      const coreContent = k.core_content || k.coreContent || '';
      const type = k.type;

      let planText = `กลุ่มสาระการเรียนรู้${k.subject} • ${k.strand || ''}\\n`;
      planText += `มาตรฐาน ${stdCode}: ${stdDesc}\\n`;
      planText += `ตัวชี้วัด ${code}: ${fullText} [ตัวชี้วัด${type}]\\n`;
      if (coreContent) {
        planText += `สาระการเรียนรู้แกนกลาง: ${coreContent.replace(/\\n/g, ' ')}\\n`;
      }
      copyToClipboard(planText, `คัดลอกข้อมูลแผน ${code} แล้ว`);
    }

    function copyBatchTable() {
      const selected = Array.from(state.selectedKpiCodes).map(code => DATA.kpis.find(k => k.code === code)).filter(Boolean);
      if (selected.length === 0) {
        showToast('กรุณาเลือกตัวชี้วัดในตารางอย่างน้อย 1 ข้อ');
        return;
      }

      let tsv = `รหัสตัวชี้วัด\\tมาตรฐานการเรียนรู้\\tข้อความตัวชี้วัด\\tสาระการเรียนรู้แกนกลาง\\tประเภทตัวชี้วัด\\tวิชาที่เปิดสอน\\n`;
      let htmlRows = '';

      selected.forEach(k => {
        const stdDesc = DATA.standards[k.standard] || '';
        tsv += `${k.code}\\tมาตรฐาน ${k.standard}: ${stdDesc}\\t${k.text}\\t${(k.core_content || '').replace(/\\n/g, ' ')}\\tตัวชี้วัด${k.type}\\t${(k.courses || []).join('; ')}\\n`;
        const typeColor = k.type === 'ปลายทาง' ? '#d97706' : '#2563eb';
        htmlRows += `
          <tr>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; font-weight:bold; white-space:nowrap; vertical-align:top;">${k.code}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;"><strong>มาตรฐาน ${k.standard}:</strong> ${stdDesc}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${k.text}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; vertical-align:top;">${(k.core_content || '').replace(/\\n/g, ' ')}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; color:${typeColor}; font-weight:bold; white-space:nowrap; vertical-align:top;">ตัวชี้วัด${k.type}</td>
            <td style="padding:6px 10px; border:1px solid #cbd5e1; font-size:12px; vertical-align:top;">${(k.courses || []).join('; ')}</td>
          </tr>
        `;
      });

      const htmlTable = `
        <table border="1" cellpadding="0" cellspacing="0" style="border-collapse:collapse; width:100%; font-family:Sarabun, sans-serif; font-size:14px; line-height:1.5;">
          <thead>
            <tr style="background-color:#f1f5f9; text-align:left;">
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รหัสตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">มาตรฐานการเรียนรู้</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ข้อความตัวชี้วัด</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">สาระการเรียนรู้แกนกลาง</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">ประเภท</th>
              <th style="padding:8px 10px; border:1px solid #cbd5e1;">รายวิชาที่นำไปใช้</th>
            </tr>
          </thead>
          <tbody>${htmlRows}</tbody>
        </table>
      `;

      copyRichTable(tsv, htmlTable, `คัดลอกตาราง (${selected.length} รายการ) แล้ว`);
    }

    function copyBatchPlan() {
      const selected = Array.from(state.selectedKpiCodes).map(code => DATA.kpis.find(k => k.code === code)).filter(Boolean);
      if (selected.length === 0) return;

      let planText = `มาตรฐานการเรียนรู้และตัวชี้วัด / สาระแกนกลาง (${selected.length} ข้อ):\\n\\n`;
      selected.forEach(k => {
        const stdDesc = DATA.standards[k.standard] || '';
        planText += `มาตรฐาน ${k.standard}: ${stdDesc}\\n`;
        planText += `• ตัวชี้วัด ${k.code}: ${k.text} [ตัวชี้วัด${k.type}]\\n`;
        if (k.core_content) planText += `  สาระการเรียนรู้แกนกลาง: ${k.core_content.replace(/\\n/g, ' ')}\\n`;
        planText += `\\n`;
      });

      copyToClipboard(planText, `คัดลอกข้อมูลแผน (${selected.length} ข้อ) แล้ว`);
    }

    // Rich Table Clipboard
    function copyRichTable(tsvText, htmlText, successMsg) {
      if (navigator.clipboard && window.ClipboardItem) {
        const textBlob = new Blob([tsvText], { type: 'text/plain' });
        const htmlBlob = new Blob([htmlText], { type: 'text/html' });
        navigator.clipboard.write([
          new ClipboardItem({ 'text/plain': textBlob, 'text/html': htmlBlob })
        ]).then(() => showToast(successMsg)).catch(() => copyToClipboard(tsvText, successMsg));
      } else {
        copyToClipboard(tsvText, successMsg);
      }
    }

    function copyToClipboard(text, successMsg = 'คัดลอกแล้ว') {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => showToast(successMsg)).catch(() => fallbackCopy(text, successMsg));
      } else {
        fallbackCopy(text, successMsg);
      }
    }

    function fallbackCopy(text, successMsg) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-999999px';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {
        document.execCommand('copy');
        showToast(successMsg);
      } catch (err) {
        alert('กรุณาคัดลอกข้อความด้วยตนเอง');
      }
      ta.remove();
    }

    function showToast(message) {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const t = document.createElement('div');
      t.className = 'toast-animate bg-slate-900 border border-emerald-500/60 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center space-x-2 text-xs pointer-events-auto';
      t.innerHTML = `
        <div class="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
          <i data-lucide="check" class="w-3 h-3"></i>
        </div>
        <span class="font-medium">${message}</span>
      `;
      container.appendChild(t);
      lucide.createIcons();
      setTimeout(() => {
        t.style.transition = 'opacity 0.25s ease-out, transform 0.25s ease-out';
        t.style.opacity = '0';
        t.style.transform = 'translateY(15px)';
        setTimeout(() => t.remove(), 250);
      }, 2400);
    }

    // Expose interactive functions globally for HTML string event handlers
    window.selectNode = selectNode;
    window.drillTo = drillTo;
    window.drillUp = drillUp;
    window.downloadGradeWord = downloadGradeWord;
    window.downloadSubjectWord = downloadSubjectWord;
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print('Generated index.html with Drill-down & Realtime Catalog Search. Length:', len(html_template))
