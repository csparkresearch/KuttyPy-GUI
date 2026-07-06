/**
 * Semicircle analog gauge — needle and value arc share the same polar angles.
 */

const CX = 100;
const CY = 92;
const R = 72;
const NEEDLE_R = R - 10;
/** Math-style degrees: 0=right, 90=down; arc runs along the bottom 270°. */
const START = 135;
const SWEEP = 270;

function polar(angleDeg, radius = R) {
  const rad = (angleDeg * Math.PI) / 180;
  return {
    x: CX + radius * Math.cos(rad),
    y: CY + radius * Math.sin(rad),
  };
}

function arcPath(r, a0, a1) {
  if (a1 <= a0) return '';
  const p0 = polar(a0, r);
  const p1 = polar(a1, r);
  const large = a1 - a0 > 180 ? 1 : 0;
  return `M ${p0.x} ${p0.y} A ${r} ${r} 0 ${large} 1 ${p1.x} ${p1.y}`;
}

function formatValue(v, lo, hi) {
  const span = Math.abs(hi - lo);
  if (span < 1) return v.toFixed(3);
  if (span < 20) return v.toFixed(2);
  if (span < 200) return v.toFixed(1);
  return Math.round(v).toString();
}

function hexToRgb(hex) {
  const h = hex.replace('#', '');
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

function rgbToHex(r, g, b) {
  return `#${[r, g, b]
    .map((x) => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, '0'))
    .join('')}`;
}

function mixHex(hex, target, t) {
  const [r0, g0, b0] = hexToRgb(hex);
  const [r1, g1, b1] = hexToRgb(target);
  return rgbToHex(r0 + (r1 - r0) * t, g0 + (g1 - g0) * t, b0 + (b1 - b0) * t);
}

function hexAlpha(hex, alpha) {
  const [r, g, b] = hexToRgb(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function createAnalogGauge(label, unit, min, max, { traceColor: initialTraceColor } = {}) {
  const uid = `g${Math.random().toString(36).slice(2, 9)}`;
  const root = document.createElement('div');
  root.className = 'analog-gauge';
  root.innerHTML = `
    <div class="gauge-face" aria-hidden="true">
      <svg viewBox="0 0 200 118" class="gauge-svg">
        <defs>
          <linearGradient id="${uid}-track" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#1e3a5f"/>
            <stop offset="50%" stop-color="#334155"/>
            <stop offset="100%" stop-color="#1e3a5f"/>
          </linearGradient>
          <linearGradient id="${uid}-fill" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#0ea5e9"/>
            <stop offset="55%" stop-color="#38bdf8"/>
            <stop offset="100%" stop-color="#22d3ee"/>
          </linearGradient>
          <filter id="${uid}-glow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="2" result="b"/>
            <feMerge>
              <feMergeNode in="b"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <path class="gauge-track" d="${arcPath(R, START, START + SWEEP)}" stroke="url(#${uid}-track)"/>
        <path class="gauge-value-arc" d="" stroke="url(#${uid}-fill)" filter="url(#${uid}-glow)"/>
        <g class="gauge-ticks"></g>
        <circle class="gauge-hub-outer" cx="${CX}" cy="${CY}" r="9"/>
        <circle class="gauge-hub" cx="${CX}" cy="${CY}" r="5.5"/>
        <line class="gauge-needle" x1="${CX}" y1="${CY}" x2="${CX}" y2="${CY}"/>
      </svg>
    </div>
    <div class="gauge-readout">
      <span class="gauge-label">${label}</span>
      <div class="gauge-value-row">
        <span class="gauge-value">—</span>
        <span class="gauge-unit">${unit}</span>
      </div>
      <span class="gauge-range"></span>
    </div>
  `;

  const ticksG = root.querySelector('.gauge-ticks');
  const valueArc = root.querySelector('.gauge-value-arc');
  const needle = root.querySelector('.gauge-needle');
  const hub = root.querySelector('.gauge-hub');
  const labelEl = root.querySelector('.gauge-label');
  const valueEl = root.querySelector('.gauge-value');
  const rangeEl = root.querySelector('.gauge-range');
  const fillGrad = root.querySelector(`#${uid}-fill`);
  const fillStops = fillGrad ? fillGrad.querySelectorAll('stop') : [];
  let lo = min;
  let hi = max;
  let traceColor = null;
  let traceActive = true;

  function buildTicks() {
    ticksG.innerHTML = '';
    const majors = 5;
    for (let i = 0; i <= majors; i++) {
      const t = i / majors;
      const angle = START + t * SWEEP;
      const outer = polar(angle, R + 2);
      const inner = polar(angle, R - (i % majors === 0 ? 10 : 5));
      const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      tick.setAttribute('x1', inner.x);
      tick.setAttribute('y1', inner.y);
      tick.setAttribute('x2', outer.x);
      tick.setAttribute('y2', outer.y);
      tick.setAttribute('class', i === 0 || i === majors ? 'gauge-tick-major' : 'gauge-tick-minor');
      ticksG.appendChild(tick);

      if (i === 0 || i === majors || i === Math.floor(majors / 2)) {
        const val = lo + t * (hi - lo);
        const lp = polar(angle, R - 18);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', lp.x);
        text.setAttribute('y', lp.y);
        text.setAttribute('class', 'gauge-tick-label');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.textContent = formatValue(val, lo, hi);
        ticksG.appendChild(text);
      }
    }
    rangeEl.textContent = `${formatValue(lo, lo, hi)} – ${formatValue(hi, lo, hi)} ${unit}`;
  }

  function setRange(minVal, maxVal) {
    lo = Number(minVal);
    hi = Number(maxVal);
    if (!Number.isFinite(lo) || !Number.isFinite(hi) || lo === hi) {
      hi = lo + 1;
    }
    buildTicks();
  }

  function valueToAngle(v) {
    const clamped = Math.max(lo, Math.min(hi, v));
    const t = (clamped - lo) / (hi - lo);
    return START + t * SWEEP;
  }

  function setNeedle(angleDeg) {
    const tip = polar(angleDeg, NEEDLE_R);
    needle.setAttribute('x1', CX);
    needle.setAttribute('y1', CY);
    needle.setAttribute('x2', tip.x);
    needle.setAttribute('y2', tip.y);
  }

  function update(value) {
    const v = Number(value);
    if (!Number.isFinite(v)) {
      valueEl.textContent = '—';
      valueArc.setAttribute('d', '');
      setNeedle(START);
      return;
    }
    const angle = valueToAngle(v);
    valueArc.setAttribute('d', arcPath(R - 6, START, angle));
    setNeedle(angle);
    valueEl.textContent = formatValue(v, lo, hi);
  }

  setRange(min, max);
  update(NaN);
  if (initialTraceColor) {
    setTraceColor(initialTraceColor);
    setTraceActive(true);
  }

  function setLabel(text) {
    labelEl.textContent = text;
  }

  function applyTraceColor(color) {
    traceColor = color;
    root.dataset.traceColor = color;
    root.style.borderColor = color;
    root.style.boxShadow = `inset 0 0 18px ${hexAlpha(color, 0.12)}`;
    valueEl.style.color = color;
    labelEl.style.color = color;

    if (fillStops.length >= 3) {
      fillStops[0].setAttribute('stop-color', mixHex(color, '#000000', 0.35));
      fillStops[1].setAttribute('stop-color', color);
      fillStops[2].setAttribute('stop-color', mixHex(color, '#ffffff', 0.25));
    }

    valueArc.setAttribute('stroke', color);
    needle.setAttribute('stroke', color);
    hub.setAttribute('stroke', color);
  }

  function setTraceColor(color) {
    applyTraceColor(color);
  }

  function setTraceActive(active) {
    traceActive = active;
    root.classList.toggle('gauge-trace-active', active);
    root.classList.toggle('gauge-trace-off', !active);
    if (active && traceColor) {
      applyTraceColor(traceColor);
    } else if (!active) {
      root.style.borderColor = 'rgba(51, 65, 85, 0.6)';
      root.style.boxShadow = 'none';
      valueEl.style.color = '#64748b';
      labelEl.style.color = '#64748b';
      valueArc.setAttribute('stroke', '#475569');
      needle.setAttribute('stroke', '#64748b');
      hub.setAttribute('stroke', '#64748b');
    }
  }

  function isTraceActive() {
    return traceActive;
  }

  return {
    el: root,
    update,
    setRange,
    setLabel,
    setTraceColor,
    setTraceActive,
    isTraceActive,
  };
}
