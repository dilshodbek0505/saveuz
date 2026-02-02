(() => {
    'use strict';

    function qs(selector, root = document) {
        return root.querySelector(selector);
    }

    function qsa(selector, root = document) {
        return Array.from(root.querySelectorAll(selector));
    }

    function updateAddModeTabs() {
        const tabs = qs('.add-mode-tabs');
        if (!tabs) return;
        const checked = qs('input[name="add_mode"]:checked');
        const value = checked ? checked.value : 'manual';
        qsa('.add-mode-tab', tabs).forEach((btn) => {
            const active = btn.dataset.value === value;
            btn.classList.toggle('is-active', active);
            btn.setAttribute('aria-selected', active ? 'true' : 'false');
        });
    }

    function initAddModeTabs() {
        const field = qs('#id_add_mode');
        if (!field || qs('.add-mode-tabs')) return;
        const inputs = qsa('input[type="radio"][name="add_mode"]', field);
        if (!inputs.length) return;

        const tabs = document.createElement('div');
        tabs.className = 'add-mode-tabs';
        tabs.setAttribute('role', 'tablist');
        tabs.setAttribute('aria-label', 'Способ добавления');

        inputs.forEach((input) => {
            const label = input.closest('label');
            const labelText = label ? label.textContent.trim() : input.value;
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'add-mode-tab';
            btn.setAttribute('role', 'tab');
            btn.dataset.value = input.value;
            btn.textContent = labelText;
            btn.addEventListener('click', () => {
                input.checked = true;
                input.dispatchEvent(new Event('change', { bubbles: true }));
                updateAddModeTabs();
            });
            tabs.appendChild(btn);
        });

        field.classList.add('add-mode-hidden');
        field.insertAdjacentElement('afterend', tabs);
    }

    function setFieldState(el, required, readonly) {
        if (!el) return;
        el.required = !!required;
        if (readonly !== undefined) {
            el.readOnly = !!readonly;
        }
    }

    function toggleAddMode() {
        const checked = qs('input[name="add_mode"]:checked');
        const mode = checked ? checked.value : 'manual';

        const commonSection = qs('.common-product-section');
        const manualSection = qs('.manual-fields-section');

        if (commonSection) {
            commonSection.classList.toggle('is-hidden', mode !== 'common');
            commonSection.classList.toggle('hidden', mode !== 'common');
        }
        if (manualSection) {
            manualSection.classList.toggle('is-hidden', mode !== 'manual');
            manualSection.classList.toggle('hidden', mode !== 'manual');
        }

        setFieldState(qs('#id_name'), mode === 'manual', mode !== 'manual');
        setFieldState(qs('#id_description'), mode === 'manual', mode !== 'manual');
        setFieldState(qs('#id_category'), mode === 'manual', mode !== 'manual');
        setFieldState(qs('#id_common_product'), mode === 'common', false);

        updateAddModeTabs();
    }

    function initHandlers() {
        qsa('input[name="add_mode"]').forEach((input) => {
            input.addEventListener('change', toggleAddMode);
        });

        const commonSelect = qs('#id_common_product');
        if (commonSelect) {
            commonSelect.addEventListener('change', () => {
                if (commonSelect.value) {
                    const commonInput = qs('input[name="add_mode"][value="common"]');
                    if (commonInput) {
                        commonInput.checked = true;
                        commonInput.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        initAddModeTabs();
        initHandlers();
        toggleAddMode();
    });
})();
