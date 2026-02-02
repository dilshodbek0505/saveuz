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

    function setFieldsState(ids, required, readonly) {
        ids.forEach((id) => {
            setFieldState(qs('#' + id), required, readonly);
        });
    }

    function updateCommonProductInfo(productId) {
        const info = qs('#common-product-info');
        if (!info) return;
        const baseUrl = info.getAttribute('data-url');
        if (!baseUrl || !productId) {
            info.classList.remove('is-filled');
            info.classList.add('is-empty');
            info.innerHTML = '' +
                '<div class="common-product-info__layout">' +
                '<div class="common-product-info__image is-empty">Фото</div>' +
                '<div class="common-product-info__content">' +
                '<div class="common-product-info__title">Выберите продукт из общей базы</div>' +
                '<div class="common-product-info__text">Чтобы увидеть информацию и фото</div>' +
                '</div>' +
                '</div>';
            return;
        }

        fetch(baseUrl + '?id=' + encodeURIComponent(productId), { credentials: 'same-origin' })
            .then((response) => response.ok ? response.json() : Promise.reject(response))
            .then((data) => {
                info.classList.remove('is-empty');
                info.classList.add('is-filled');
                const imageStyle = data.image_url
                    ? 'style="background-image:url(' + data.image_url + ');"'
                    : '';
                const name = data.name || '';
                const desc = (data.description || '').slice(0, 180);
                const category = data.category || '-';
                info.innerHTML = '' +
                    '<div class="common-product-info__layout">' +
                    '<div class="common-product-info__image" ' + imageStyle + '></div>' +
                    '<div class="common-product-info__content">' +
                    '<div class="common-product-info__title">' + name + '</div>' +
                    '<div class="common-product-info__text">' + desc + '</div>' +
                    '<div class="common-product-info__meta">Категория: ' + category + '</div>' +
                    '</div>' +
                    '</div>';
            })
            .catch(() => {
                info.classList.remove('is-filled');
                info.classList.add('is-empty');
            });
    }

    function toggleAddMode() {
        const checked = qs('input[name="add_mode"]:checked');
        const mode = checked ? checked.value : 'manual';

        const commonSection = qs('.common-product-section');
        const manualSection = qs('.manual-fields-section');
        const imagesInline = qs('.product-images-inline');

        if (commonSection) {
            commonSection.classList.toggle('is-hidden', mode !== 'common');
            commonSection.classList.toggle('hidden', mode !== 'common');
        }
        if (manualSection) {
            manualSection.classList.toggle('is-hidden', mode !== 'manual');
            manualSection.classList.toggle('hidden', mode !== 'manual');
        }
        if (imagesInline) {
            const hideImages = mode === 'common';
            imagesInline.classList.toggle('is-hidden', hideImages);
            imagesInline.classList.toggle('hidden', hideImages);
            qsa('input, select, textarea, button', imagesInline).forEach((el) => {
                el.disabled = hideImages;
            });
        }

        setFieldsState(
            [
                'id_name',
                'id_name_ru',
                'id_name_uz',
                'id_name_en',
                'id_description',
                'id_description_ru',
                'id_description_uz',
                'id_description_en',
                'id_category',
            ],
            mode === 'manual',
            mode !== 'manual'
        );
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
                updateCommonProductInfo(commonSelect.value);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        initAddModeTabs();
        initHandlers();
        toggleAddMode();
        const initialCommon = qs('#id_common_product');
        if (initialCommon && initialCommon.value) {
            updateCommonProductInfo(initialCommon.value);
        }
    });
})();
