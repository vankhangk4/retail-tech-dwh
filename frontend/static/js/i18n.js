(function () {
    'use strict';

    const STORAGE_KEY = 'dwh_ui_lang';
    const LEGACY_STORAGE_KEYS = ['dwh_settings_ui_lang'];
    const SUPPORTED_LANGUAGES = new Set(['vi', 'en']);

    const BASE_COPY = {
        vi: {
            language: {
                vietnamese: 'Tiếng Việt',
                english: 'English',
            },
            common: {
                close: 'Đóng',
                processing: 'Đang xử lý',
                notAvailable: 'Chưa xác định',
                systemWide: 'Toàn hệ thống',
                active: 'Hoạt động',
                inactive: 'Tắt',
                noLimit: 'Không giới hạn',
                unknown: 'Chưa xác định',
                back: 'Quay lại',
                confirm: 'Xác nhận',
                keepCurrent: 'Giữ nguyên',
            },
            roles: {
                superadmin: 'Quản trị hệ thống',
                admin: 'Quản trị chi nhánh',
                viewer: 'Người xem báo cáo',
            },
            sidebar: {
                brandMeta: 'Trung tâm vận hành cho hệ thống Data Warehouse đa chi nhánh',
                scopePrefix: 'Phạm vi dữ liệu',
                scopeAll: 'Toàn hệ thống',
                scopeBranchMode: 'Phạm vi chi nhánh',
                groupOperations: 'Vận hành',
                groupAnalytics: 'Phân tích',
                groupAdmin: 'Quản trị',
                groupAccount: 'Tài khoản',
                primaryNavAria: 'Điều hướng chính',
                overviewTitle: 'Tổng quan',
                overviewMeta: 'Chỉ báo vận hành',
                etlTitle: 'Vận hành ETL',
                etlMeta: 'Nạp dữ liệu và ETL',
                analysisTitle: 'Phân tích',
                analysisMeta: 'Truy cập 5 báo cáo phân tích',
                manageTitle: 'Quản lý chi nhánh',
                manageMeta: 'Người dùng theo chi nhánh',
                adminTitle: 'Quản trị hệ thống',
                adminMeta: 'Chi nhánh, người dùng, giám sát ETL',
                settingsTitle: 'Thiết lập',
                settingsMeta: 'Thông tin và bảo mật',
                healthLoading: 'Đang kiểm tra kết nối API',
                healthHealthy: 'Kết nối API ổn định',
                healthCheck: 'Cần kiểm tra kết nối API',
                signOut: 'Đăng xuất',
            },
        },
        en: {
            language: {
                vietnamese: 'Vietnamese',
                english: 'English',
            },
            common: {
                close: 'Close',
                processing: 'Processing',
                notAvailable: 'Not available',
                systemWide: 'System-wide',
                active: 'Active',
                inactive: 'Disabled',
                noLimit: 'No limit',
                unknown: 'Not available',
                back: 'Back',
                confirm: 'Confirm',
                keepCurrent: 'Keep current values',
            },
            roles: {
                superadmin: 'System Administrator',
                admin: 'Branch Administrator',
                viewer: 'Report Viewer',
            },
            sidebar: {
                brandMeta: 'Operations hub for the multi-branch Data Warehouse platform',
                scopePrefix: 'Data scope',
                scopeAll: 'System-wide',
                scopeBranchMode: 'Branch scope',
                groupOperations: 'Operations',
                groupAnalytics: 'Analytics',
                groupAdmin: 'Administration',
                groupAccount: 'Account',
                primaryNavAria: 'Primary navigation',
                overviewTitle: 'Overview',
                overviewMeta: 'Operational signals',
                etlTitle: 'ETL Operations',
                etlMeta: 'Data upload and ETL',
                analysisTitle: 'Analytics',
                analysisMeta: 'Access 5 analytical reports',
                manageTitle: 'Branch Management',
                manageMeta: 'Users by branch',
                adminTitle: 'System Administration',
                adminMeta: 'Branches, users, and ETL monitoring',
                settingsTitle: 'Settings',
                settingsMeta: 'Profile and security',
                healthLoading: 'Checking API connection',
                healthHealthy: 'API connection is healthy',
                healthCheck: 'Check API connection',
                signOut: 'Sign out',
            },
        },
    };

    function isPlainObject(value) {
        return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
    }

    function deepMerge(target, source) {
        const output = { ...target };
        Object.entries(source || {}).forEach(([key, value]) => {
            if (isPlainObject(value) && isPlainObject(output[key])) {
                output[key] = deepMerge(output[key], value);
                return;
            }
            output[key] = value;
        });
        return output;
    }

    function mergeCopy(pageCopy = {}) {
        return {
            vi: deepMerge(BASE_COPY.vi, pageCopy.vi || {}),
            en: deepMerge(BASE_COPY.en, pageCopy.en || {}),
        };
    }

    function normalizeLanguage(value) {
        return SUPPORTED_LANGUAGES.has(value) ? value : 'vi';
    }

    function loadLanguage(defaultLanguage = 'vi') {
        try {
            const direct = localStorage.getItem(STORAGE_KEY);
            if (direct) {
                return normalizeLanguage(direct);
            }

            for (const key of LEGACY_STORAGE_KEYS) {
                const legacyValue = localStorage.getItem(key);
                if (!legacyValue) continue;
                const normalizedLegacy = normalizeLanguage(legacyValue);
                localStorage.setItem(STORAGE_KEY, normalizedLegacy);
                return normalizedLegacy;
            }
        } catch (error) {
            // Ignore storage failures and use the default language.
        }

        const htmlLanguage = document.documentElement.lang || document.body?.dataset.uiLang || defaultLanguage;
        return normalizeLanguage(htmlLanguage);
    }

    function saveLanguage(value) {
        try {
            localStorage.setItem(STORAGE_KEY, normalizeLanguage(value));
        } catch (error) {
            // Ignore storage failures and keep the in-memory language only.
        }
    }

    function resolvePath(source, path) {
        return String(path || '')
            .split('.')
            .reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined), source);
    }

    function interpolate(value, params = {}) {
        return String(value).replace(/\{(\w+)\}/g, (_, key) => {
            return params[key] === undefined || params[key] === null ? '' : String(params[key]);
        });
    }

    function translateStatic(root, translate) {
        root.querySelectorAll('[data-i18n]').forEach((element) => {
            element.textContent = translate(element.dataset.i18n);
        });

        root.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
            element.placeholder = translate(element.dataset.i18nPlaceholder);
        });

        root.querySelectorAll('[data-i18n-title]').forEach((element) => {
            element.title = translate(element.dataset.i18nTitle);
        });

        root.querySelectorAll('[data-i18n-aria-label]').forEach((element) => {
            element.setAttribute('aria-label', translate(element.dataset.i18nAriaLabel));
        });

        root.querySelectorAll('[data-i18n-alt]').forEach((element) => {
            element.alt = translate(element.dataset.i18nAlt);
        });
    }

    function setRuntimeCopy(element, key = '', params = {}) {
        if (!element) return;
        if (!key) {
            delete element.dataset.i18nRuntimeKey;
            delete element.dataset.i18nRuntimeParams;
            return;
        }
        element.dataset.i18nRuntimeKey = key;
        element.dataset.i18nRuntimeParams = JSON.stringify(params || {});
    }

    function applyRuntimeCopy(root, translate) {
        root.querySelectorAll('[data-i18n-runtime-key]').forEach((element) => {
            let params = {};
            try {
                params = JSON.parse(element.dataset.i18nRuntimeParams || '{}');
            } catch (error) {
                params = {};
            }
            element.textContent = translate(element.dataset.i18nRuntimeKey, params);
        });
    }

    function getLocale(language) {
        return language === 'en' ? 'en-US' : 'vi-VN';
    }

    function createPageI18n({ copy, defaultLanguage = 'vi', documentTitleKey = '', languageSelect = null, root = document } = {}) {
        const mergedCopy = mergeCopy(copy);
        let currentLanguage = loadLanguage(defaultLanguage);
        const listeners = new Set();

        function translate(path, params = {}) {
            const value = resolvePath(mergedCopy[currentLanguage], path) ?? path;
            return typeof value === 'string' ? interpolate(value, params) : value;
        }

        function applyStaticCopy() {
            document.documentElement.lang = currentLanguage;
            if (document.body) {
                document.body.dataset.uiLang = currentLanguage;
            }
            if (documentTitleKey) {
                document.title = translate(documentTitleKey);
            }
            translateStatic(root, translate);
            if (languageSelect) {
                languageSelect.value = currentLanguage;
            }
        }

        function setLanguage(value, { notify = true } = {}) {
            currentLanguage = normalizeLanguage(value || defaultLanguage);
            saveLanguage(currentLanguage);
            applyStaticCopy();
            if (notify) {
                listeners.forEach((listener) => listener(currentLanguage));
            }
            return currentLanguage;
        }

        function onChange(listener) {
            listeners.add(listener);
            return () => listeners.delete(listener);
        }

        if (languageSelect) {
            languageSelect.addEventListener('change', (event) => {
                setLanguage(event.target.value);
            });
        }

        applyStaticCopy();

        return {
            t: translate,
            getLanguage: () => currentLanguage,
            getLocale: () => getLocale(currentLanguage),
            setLanguage,
            onChange,
            applyStaticCopy,
            formatInteger(value, options = {}) {
                return new Intl.NumberFormat(getLocale(currentLanguage), options).format(Number(value || 0));
            },
            formatCurrency(value) {
                const formatted = new Intl.NumberFormat(getLocale(currentLanguage), {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }).format(Number(value || 0));
                return currentLanguage === 'en' ? `VND ${formatted}` : `${formatted} VNĐ`;
            },
            formatDateTime(value) {
                if (!value) return '—';
                const date = new Date(value);
                if (Number.isNaN(date.getTime())) return '—';
                return date.toLocaleString(getLocale(currentLanguage));
            },
            formatFileSize(bytes) {
                const size = Number(bytes || 0);
                if (size >= 1024 * 1024) {
                    return `${(size / 1024 / 1024).toFixed(1)} MB`;
                }
                return `${(size / 1024).toFixed(1)} KB`;
            },
            roleLabel(role) {
                return translate(`roles.${role}`);
            },
            setRuntimeCopy,
            applyRuntimeCopy() {
                applyRuntimeCopy(root, translate);
            },
        };
    }

    window.DWHI18n = {
        STORAGE_KEY,
        mergeCopy,
        createPageI18n,
        normalizeLanguage,
        loadLanguage,
        saveLanguage,
        setRuntimeCopy,
        applyRuntimeCopy,
    };
})();
