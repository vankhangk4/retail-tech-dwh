// ============================================================
// theme.js — Theme switcher (light / dark / auto)
// Persists choice in localStorage under STORAGE_KEY.
// Exposes window.DWHTheme.
// ============================================================

(function () {
    'use strict';

    const STORAGE_KEY = 'dwh_ui_theme';
    const SUPPORTED = new Set(['light', 'dark', 'auto']);
    const DEFAULT = 'auto';

    function normalize(value) {
        return SUPPORTED.has(value) ? value : DEFAULT;
    }

    function read() {
        try {
            return normalize(localStorage.getItem(STORAGE_KEY) || DEFAULT);
        } catch (_) {
            return DEFAULT;
        }
    }

    function write(value) {
        try {
            localStorage.setItem(STORAGE_KEY, normalize(value));
        } catch (_) {
            // storage unavailable — ignore
        }
    }

    function apply(value) {
        const next = normalize(value);
        document.documentElement.setAttribute('data-theme', next);
        return next;
    }

    function effective(value) {
        const v = normalize(value);
        if (v !== 'auto') return v;
        const mq = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
        return mq && mq.matches ? 'dark' : 'light';
    }

    const listeners = new Set();

    function notify(value) {
        const eff = effective(value);
        listeners.forEach((fn) => {
            try { fn(value, eff); } catch (_) { /* swallow */ }
        });
    }

    function set(value) {
        const next = apply(value);
        write(next);
        notify(next);
        return next;
    }

    function get() {
        return read();
    }

    function onChange(fn) {
        if (typeof fn !== 'function') return () => {};
        listeners.add(fn);
        return () => listeners.delete(fn);
    }

    // Re-broadcast when OS preference changes and we're in auto mode.
    if (window.matchMedia) {
        const mq = window.matchMedia('(prefers-color-scheme: dark)');
        const handler = () => {
            if (read() === 'auto') notify('auto');
        };
        if (mq.addEventListener) {
            mq.addEventListener('change', handler);
        } else if (mq.addListener) {
            mq.addListener(handler);
        }
    }

    // Ensure attribute is present (the pre-paint inline script normally sets it,
    // but this is a safety net in case the inline script was removed).
    if (!document.documentElement.getAttribute('data-theme')) {
        apply(read());
    }

    window.DWHTheme = {
        STORAGE_KEY,
        SUPPORTED: Array.from(SUPPORTED),
        DEFAULT,
        get,
        set,
        effective: () => effective(read()),
        onChange,
    };
})();
