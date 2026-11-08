(() => {
  if (typeof window.__setCursorPosition === 'function') return;

  function mountTarget() {
    return document.body || document.documentElement;
  }

  const style = document.createElement('style');
  style.textContent = `
    #pw-video-cursor-root {
      position: fixed; left: 0; top: 0; width: 100%; height: 100%;
      pointer-events: none; z-index: 2147483647;
    }
    #pw-cursor-highlight {
      position: absolute; width: 64px; height: 64px;
      margin-left: -32px; margin-top: -32px; border-radius: 50%;
      background: rgba(255, 255, 0, 0.35); pointer-events: none;
    }
    #pw-cursor-arrow {
      position: absolute; width: 32px; height: 32px;
      pointer-events: none;
    }
    .pw-ripple {
      position: absolute; width: 32px; height: 32px;
      margin-left: -16px; margin-top: -16px; border-radius: 50%;
      border: 2px solid rgba(255, 220, 0, 0.9); pointer-events: none;
      animation: pw-ripple-anim 0.55s ease-out forwards;
    }
    @keyframes pw-ripple-anim {
      from { transform: scale(0.35); opacity: 1; }
      to { transform: scale(2.8); opacity: 0; }
    }
    #pw-callout {
      position: absolute; padding: 8px 12px; font: 16pt sans-serif;
      pointer-events: none; opacity: 0; transition: opacity 2s ease;
      max-width: 360px; box-sizing: border-box;
    }
  `;
  (document.head || mountTarget()).appendChild(style);

  const root = document.createElement('div');
  root.id = 'pw-video-cursor-root';

  const highlight = document.createElement('div');
  highlight.id = 'pw-cursor-highlight';

  const arrow = document.createElement('div');
  arrow.id = 'pw-cursor-arrow';
  arrow.innerHTML = `<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 3 L5 24 L12 18 L17 27 L21 25 L15 16 L25 16 Z"
      fill="white" stroke="black" stroke-width="1.5" stroke-linejoin="round"/>
  </svg>`;

  root.appendChild(highlight);
  root.appendChild(arrow);
  mountTarget().appendChild(root);

  let cursorX = 120;
  let cursorY = 120;

  function applyCursor() {
    highlight.style.left = cursorX + 'px';
    highlight.style.top = cursorY + 'px';
    arrow.style.left = cursorX + 'px';
    arrow.style.top = cursorY + 'px';
  }
  applyCursor();

  window.__setCursorPosition = (x, y) => {
    cursorX = x;
    cursorY = y;
    applyCursor();
  };

  window.__playRipple = (x, y) => {
    const ripple = document.createElement('div');
    ripple.className = 'pw-ripple';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    root.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  };

  window.ShowCallout = (text, bgColor, textColor, fade) => {
    bgColor = bgColor || '#ffff00';
    textColor = textColor || '#000000';
    fade = fade !== false;
    let callout = document.getElementById('pw-callout');
    if (!callout) {
      callout = document.createElement('div');
      callout.id = 'pw-callout';
      root.appendChild(callout);
    }
    callout.textContent = text;
    callout.style.background = bgColor;
    callout.style.color = textColor;
    callout.style.left = Math.min(cursorX + 24, window.innerWidth - 240) + 'px';
    callout.style.top = Math.max(cursorY - 56, 12) + 'px';
    callout.style.opacity = '1';
    if (fade) {
      window.setTimeout(() => { callout.style.opacity = '0'; }, 3500);
    }
  };
})();
