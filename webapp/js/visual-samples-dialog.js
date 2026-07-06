/**
 * Sample programs browser — loads Blockly XML from codeblocks/.
 */

const MANIFEST_URL = 'codeblocks/manifest.json';
const PREVIEW_EXTS = ['.png', '.jpg', '.jpeg', '.webp', '.gif'];

let manifestPromise = null;

async function loadManifest() {
  if (!manifestPromise) {
    manifestPromise = fetch(MANIFEST_URL)
      .then((r) => {
        if (!r.ok) throw new Error('Could not load samples list');
        return r.json();
      });
  }
  return manifestPromise;
}

function codeblocksUrl(relativePath) {
  return `codeblocks/${relativePath.split('/').map(encodeURIComponent).join('/')}`;
}

function previewCandidates(xmlPath, previewPath) {
  if (previewPath) return [codeblocksUrl(previewPath)];
  const base = xmlPath.replace(/\.xml$/i, '');
  return PREVIEW_EXTS.map((ext) => codeblocksUrl(`${base}${ext}`));
}

function createSamplePreview() {
  let popup = null;
  let timer = null;
  let activeBtn = null;
  let loadId = 0;

  function ensurePopup() {
    if (!popup) {
      popup = document.createElement('div');
      popup.className = 'visual-samples-preview';
      popup.hidden = true;
      popup.innerHTML = '<img alt="" loading="lazy">';
      document.body.appendChild(popup);
    }
    return popup;
  }

  function hide() {
    clearTimeout(timer);
    timer = null;
    activeBtn = null;
    loadId += 1;
    if (popup) {
      popup.hidden = true;
      const img = popup.querySelector('img');
      if (img) img.removeAttribute('src');
    }
  }

  function positionNear(btn) {
    const el = ensurePopup();
    const rect = btn.getBoundingClientRect();
    const margin = 10;
    el.hidden = false;
    const pw = el.offsetWidth || 280;
    const ph = el.offsetHeight || 200;
    let left = rect.right + margin;
    let top = rect.top;
    if (left + pw > window.innerWidth - margin) {
      left = Math.max(margin, rect.left - pw - margin);
    }
    if (top + ph > window.innerHeight - margin) {
      top = Math.max(margin, window.innerHeight - ph - margin);
    }
    if (top < margin) top = margin;
    el.style.left = `${left}px`;
    el.style.top = `${top}px`;
  }

  async function loadPreview(btn, urls) {
    const id = loadId;
    const img = ensurePopup().querySelector('img');
    for (const url of urls) {
      const loaded = await new Promise((resolve) => {
        const probe = new Image();
        probe.onload = () => resolve(url);
        probe.onerror = () => resolve(null);
        probe.src = url;
      });
      if (id !== loadId || btn !== activeBtn) return;
      if (loaded) {
        img.src = loaded;
        positionNear(btn);
        return;
      }
    }
    if (id === loadId) hide();
  }

  function show(btn, xmlPath, previewPath) {
    clearTimeout(timer);
    timer = setTimeout(() => {
      activeBtn = btn;
      loadId += 1;
      loadPreview(btn, previewCandidates(xmlPath, previewPath));
    }, 160);
  }

  function destroy() {
    hide();
    popup?.remove();
    popup = null;
  }

  return { show, hide, destroy };
}

/**
 * @param {{ onPick: (path: string) => void|Promise<void> }} opts
 */
export function openSamplesDialog({ onPick }) {
  const overlay = document.createElement('div');
  overlay.className = 'visual-samples-overlay';
  overlay.innerHTML = `
    <div class="visual-samples-dialog" role="dialog" aria-modal="true" aria-labelledby="vsd-title">
      <header class="visual-samples-header">
        <img class="visual-samples-header-icon" src="images/VisualCoding.png" width="32" height="32" alt="">
        <h2 id="vsd-title">Sample programs</h2>
        <button type="button" class="visual-samples-close" aria-label="Close">×</button>
      </header>
      <p class="visual-samples-hint">Hover a sample for a preview. Click to load it into the workspace.</p>
      <div class="visual-samples-body" aria-live="polite">Loading…</div>
    </div>
  `;
  document.body.appendChild(overlay);

  const body = overlay.querySelector('.visual-samples-body');
  const preview = createSamplePreview();
  let closed = false;

  function close() {
    if (closed) return;
    closed = true;
    preview.destroy();
    overlay.remove();
  }

  overlay.querySelector('.visual-samples-close')?.addEventListener('click', close);
  overlay.addEventListener('click', (ev) => {
    if (ev.target === overlay) close();
  });

  document.addEventListener('keydown', function onKey(ev) {
    if (ev.key === 'Escape') {
      document.removeEventListener('keydown', onKey);
      close();
    }
  });

  loadManifest()
    .then((data) => {
      body.innerHTML = '';
      const categories = data?.categories || [];
      if (!categories.length) {
        body.textContent = 'No samples found.';
        return;
      }

      for (const cat of categories) {
        const section = document.createElement('section');
        section.className = 'visual-samples-category';
        const heading = document.createElement('h3');
        heading.textContent = cat.name;
        section.appendChild(heading);

        const list = document.createElement('div');
        list.className = 'visual-samples-list';
        for (const sample of cat.samples || []) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'visual-samples-item';
          btn.textContent = sample.title;
          btn.title = sample.preview ? 'Preview available' : sample.path;
          btn.dataset.samplePath = sample.path;
          if (sample.preview) btn.classList.add('visual-samples-item--has-preview');

          btn.addEventListener('mouseenter', () => {
            preview.show(btn, sample.path, sample.preview);
          });
          btn.addEventListener('mouseleave', () => preview.hide());
          btn.addEventListener('focus', () => {
            preview.show(btn, sample.path, sample.preview);
          });
          btn.addEventListener('blur', () => preview.hide());

          btn.addEventListener('click', async () => {
            close();
            await onPick(sample.path);
          });
          list.appendChild(btn);
        }
        section.appendChild(list);
        body.appendChild(section);
      }
    })
    .catch((err) => {
      body.textContent = err.message || 'Failed to load samples';
    });
}

export async function fetchSampleXml(relativePath) {
  const res = await fetch(codeblocksUrl(relativePath));
  if (!res.ok) throw new Error(`Could not load ${relativePath}`);
  return res.text();
}
