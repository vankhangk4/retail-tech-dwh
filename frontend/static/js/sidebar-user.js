// ============================================================
// sidebar-user.js — Loads the user's profile (avatar + display name)
// and syncs it into the sidebar partial on pages that don't already
// fetch the profile (e.g. dashboard).
//
// Skipped if the page is the settings page — settings.js owns the
// profile lifecycle there and would race this loader.
// ============================================================

(function () {
    'use strict';

    // Settings page handles its own loading; bail out.
    if (window.location.pathname.replace(/\/+$/, '') === '/settings') return;

    const sidebarAvatarImg = document.getElementById('sidebarAvatarImg');
    const sidebarAvatarInitial = document.getElementById('sidebarAvatarInitial');
    if (!sidebarAvatarImg && !sidebarAvatarInitial) return;

    async function loadProfile() {
        try {
            const response = await fetch('/api/me/profile', {
                credentials: 'same-origin',
                headers: { 'Accept': 'application/json' },
            });
            if (!response.ok) return;
            const data = await response.json();

            if (data.avatar_data && sidebarAvatarImg) {
                sidebarAvatarImg.src = data.avatar_data;
                sidebarAvatarImg.classList.remove('is-hidden');
                sidebarAvatarInitial?.classList.add('is-hidden');
            } else if (sidebarAvatarInitial) {
                const name = data.display_name || data.username;
                if (name) sidebarAvatarInitial.textContent = name[0].toUpperCase();
            }
        } catch (_) {
            // Silent — leave the server-rendered initial in place.
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadProfile);
    } else {
        loadProfile();
    }
})();
