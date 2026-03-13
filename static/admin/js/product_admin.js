(() => {
    'use strict';

    const DEBOUNCE_MS = 2500;
    const LANGS = ['uz', 'ru', 'en'];

    function qs(selector, root = document) {
        return root.querySelector(selector);
    }

    function qsa(selector, root = document) {
        return Array.from(root.querySelectorAll(selector));
    }

    function getCsrfToken() {
        const input = qs('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : '';
    }

    function getTranslateUrl() {
        const form = qs('.manual-fields-section') ? qs('.manual-fields-section').closest('form') : null;
        if (form && form.action) {
            const base = form.action.replace(/\/add\/?$|\/\d+\/change\/?$/, '');
            return base + (base.endsWith('/') ? '' : '/') + 'translate/';
        }
        const path = window.location.pathname || '';
        if (path.indexOf('/admin/main/product') !== -1) {
            const base = path.replace(/\/add\/?$|\/\d+\/change\/?$/, '');
            return base + (base.endsWith('/') ? '' : '/') + 'translate/';
        }
        return '';
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

    function initTranslationManual() {
        let manualSection = qs('.manual-fields-section');
        if (!manualSection && qs('#id_name') && qs('#id_category')) {
            manualSection = qs('#id_name').closest('fieldset');
        }
        if (!manualSection || qs('.translation-manual-block', manualSection)) return;

        const translateUrl = getTranslateUrl();
        if (!translateUrl) return;

        const nameIds = ['id_name', 'id_name_uz', 'id_name_ru', 'id_name_en'];
        const descIds = ['id_description', 'id_description_uz', 'id_description_ru', 'id_description_en'];
        const rowSelectors = ['.form-row', '.field', '[class*="field-"]'];
        nameIds.concat(descIds).forEach((id) => {
            const el = qs('#' + id);
            if (!el) return;
            let row = null;
            for (const sel of rowSelectors) {
                row = el.closest(sel);
                if (row && row.closest('.manual-fields-section')) break;
            }
            if (row) row.classList.add('translation-hidden-row');
        });

        const defaultLang = 'uz';
        const block = document.createElement('div');
        block.className = 'translation-manual-block';
        block.innerHTML =
            '<div class="translation-manual-row">' +
            '<label class="translation-manual-label">Til (asosiy)</label>' +
            '<select id="translation_source_lang" class="translation-manual-select">' +
            '<option value="uz">O\'zbek</option><option value="ru">Русский</option><option value="en">English</option>' +
            '</select>' +
            '</div>' +
            '<div class="translation-manual-row">' +
            '<label class="translation-manual-label" for="translation_name_input">Nomi</label>' +
            '<input type="text" id="translation_name_input" class="translation-manual-input" placeholder="Mahsulot nomi">' +
            '</div>' +
            '<div class="translation-manual-row">' +
            '<label class="translation-manual-label" for="translation_desc_input">Tarif</label>' +
            '<textarea id="translation_desc_input" class="translation-manual-textarea" rows="3" placeholder="Qisqacha tarif"></textarea>' +
            '<span class="translation-manual-hint">Tarjima 3–4 s dan keyin avtomatik amalga oshiriladi.</span>' +
            '</div>' +
            '<div class="translation-manual-row">' +
            '<button type="button" class="translation-manual-btn-unfold" id="translation_btn_modal">Tarjimalari ko\'rish</button>' +
            '</div>';
        manualSection.insertBefore(block, manualSection.firstChild);

        const sourceLangSelect = qs('#translation_source_lang', block);
        const nameInput = qs('#translation_name_input', block);
        const descInput = qs('#translation_desc_input', block);
        const btnModal = qs('#translation_btn_modal', block);

        let nameDebounceTimer = null;
        let descDebounceTimer = null;
        let nameLoading = false;
        let descLoading = false;
        let namePending = false;
        let descPending = false;

        function setButtonLoading(loading) {
            if (!btnModal) return;
            btnModal.disabled = loading;
            btnModal.classList.toggle('is-loading', loading);
            btnModal.textContent = loading ? 'Yuklanmoqda…' : 'Tarjimalari ko\'rish';
        }

        function updateButtonState() {
            const loading = nameLoading || descLoading;
            setButtonLoading(loading);
        }

        function getFieldEl(fieldBase, lang) {
            const id = 'id_' + fieldBase + '_' + lang;
            let el = qs('#' + id);
            if (el) return el;
            const name = fieldBase + '_' + lang;
            el = qs('input[name="' + name + '"], textarea[name="' + name + '"]');
            return el || null;
        }

        function getMainFieldEl(fieldBase) {
            let el = qs('#id_' + fieldBase);
            if (el) return el;
            el = qs('input[name="' + fieldBase + '"], textarea[name="' + fieldBase + '"]');
            return el || null;
        }

        function fillNameFields(data) {
            if (!data) return;
            LANGS.forEach((lang) => {
                const el = getFieldEl('name', lang);
                if (el) el.value = data[lang] || '';
            });
            const idName = getMainFieldEl('name');
            if (idName) idName.value = data[defaultLang] || '';
        }

        function fillDescFields(data) {
            if (!data) return;
            LANGS.forEach((lang) => {
                const el = getFieldEl('description', lang);
                if (el) el.value = data[lang] || '';
            });
            const idDesc = getMainFieldEl('description');
            if (idDesc) idDesc.value = data[defaultLang] || '';
        }

        function doTranslateName() {
            namePending = false;
            const text = (nameInput && nameInput.value) ? nameInput.value.trim() : '';
            const src = sourceLangSelect ? sourceLangSelect.value : defaultLang;
            if (!text) {
                fillNameFields({ uz: '', ru: '', en: '' });
                updateButtonState();
                return;
            }
            nameLoading = true;
            updateButtonState();
            fetch(translateUrl, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ text, source_lang: src }),
            })
                .then((r) => r.ok ? r.json() : Promise.reject(r))
                .then(fillNameFields)
                .catch(() => fillNameFields({ uz: text, ru: '', en: '' }))
                .finally(() => {
                    nameLoading = false;
                    updateButtonState();
                });
        }

        function doTranslateDesc() {
            descPending = false;
            const text = (descInput && descInput.value) ? descInput.value.trim() : '';
            const src = sourceLangSelect ? sourceLangSelect.value : defaultLang;
            if (!text) {
                fillDescFields({ uz: '', ru: '', en: '' });
                updateButtonState();
                return;
            }
            descLoading = true;
            updateButtonState();
            fetch(translateUrl, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ text, source_lang: src }),
            })
                .then((r) => r.ok ? r.json() : Promise.reject(r))
                .then(fillDescFields)
                .catch(() => fillDescFields({ uz: text, ru: '', en: '' }))
                .finally(() => {
                    descLoading = false;
                    updateButtonState();
                });
        }

        function scheduleName() {
            if (nameDebounceTimer) clearTimeout(nameDebounceTimer);
            const hasText = (nameInput && nameInput.value && nameInput.value.trim()) !== '';
            if (hasText) {
                namePending = true;
                updateButtonState();
            }
            nameDebounceTimer = setTimeout(doTranslateName, DEBOUNCE_MS);
        }

        function scheduleDesc() {
            if (descDebounceTimer) clearTimeout(descDebounceTimer);
            const hasText = (descInput && descInput.value && descInput.value.trim()) !== '';
            if (hasText) {
                descPending = true;
                updateButtonState();
            }
            descDebounceTimer = setTimeout(doTranslateDesc, DEBOUNCE_MS);
        }

        function syncSourceToHidden() {
            const src = sourceLangSelect ? sourceLangSelect.value : defaultLang;
            const nameVal = (nameInput && nameInput.value) ? nameInput.value.trim() : '';
            const descVal = (descInput && descInput.value) ? descInput.value.trim() : '';
            const nameEl = qs('#id_name_' + src);
            const descEl = qs('#id_description_' + src);
            if (nameEl) nameEl.value = nameVal;
            if (descEl) descEl.value = descVal;
            const idName = qs('#id_name');
            const idDesc = qs('#id_description');
            if (idName) idName.value = nameVal;
            if (idDesc) idDesc.value = descVal;
        }

        if (nameInput) {
            nameInput.addEventListener('input', () => { syncSourceToHidden(); scheduleName(); });
            nameInput.addEventListener('change', () => { syncSourceToHidden(); scheduleName(); });
        }
        if (descInput) {
            descInput.addEventListener('input', () => { syncSourceToHidden(); scheduleDesc(); });
            descInput.addEventListener('change', () => { syncSourceToHidden(); scheduleDesc(); });
        }
        if (sourceLangSelect) {
            sourceLangSelect.addEventListener('change', syncSourceToHidden);
        }

        function getFormNames() {
            const uz = getFieldEl('name', 'uz');
            const ru = getFieldEl('name', 'ru');
            const en = getFieldEl('name', 'en');
            return {
                uz: (uz && uz.value) ? uz.value : '',
                ru: (ru && ru.value) ? ru.value : '',
                en: (en && en.value) ? en.value : '',
            };
        }

        function getFormDescs() {
            const uz = getFieldEl('description', 'uz');
            const ru = getFieldEl('description', 'ru');
            const en = getFieldEl('description', 'en');
            return {
                uz: (uz && uz.value) ? uz.value : '',
                ru: (ru && ru.value) ? ru.value : '',
                en: (en && en.value) ? en.value : '',
            };
        }

        function setFormNames(obj) {
            LANGS.forEach((lang) => {
                if (obj[lang] === undefined) return;
                const el = getFieldEl('name', lang);
                if (el) el.value = obj[lang];
            });
            const main = getMainFieldEl('name');
            if (main) main.value = obj[defaultLang] != null ? obj[defaultLang] : (getFieldEl('name', 'uz') && getFieldEl('name', 'uz').value);
        }

        function setFormDescs(obj) {
            LANGS.forEach((lang) => {
                if (obj[lang] === undefined) return;
                const el = getFieldEl('description', lang);
                if (el) el.value = obj[lang];
            });
            const main = getMainFieldEl('description');
            if (main) main.value = obj[defaultLang] != null ? obj[defaultLang] : (getFieldEl('description', 'uz') && getFieldEl('description', 'uz').value);
        }

        function callTranslateApi(text, sourceLang) {
            if (!(text && text.trim())) return Promise.resolve({ uz: '', ru: '', en: '' });
            return fetch(translateUrl, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ text: text.trim(), source_lang: sourceLang }),
            })
                .then((r) => r.ok ? r.json() : Promise.reject(r))
                .then((data) => (data && typeof data === 'object' ? data : { uz: '', ru: '', en: '' }))
                .catch(() => ({ uz: text.trim(), ru: '', en: '' }));
        }

        function openTranslationsModal() {
            const src = sourceLangSelect ? sourceLangSelect.value : defaultLang;
            const nameText = (nameInput && nameInput.value) ? nameInput.value.trim() : '';
            const descText = (descInput && descInput.value) ? descInput.value.trim() : '';
            const needName = nameText.length > 0;
            const needDesc = descText.length > 0;

            let overlay = qs('.translation-modal-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'translation-modal-overlay';
                overlay.setAttribute('aria-hidden', 'true');
                document.body.appendChild(overlay);
            }
            overlay.innerHTML =
                '<div class="translation-modal" role="dialog" aria-labelledby="translation-modal-title">' +
                '<div class="translation-modal-header">' +
                '<h2 id="translation-modal-title" class="translation-modal-title">Tarjimalar</h2>' +
                '<button type="button" class="translation-modal-close" aria-label="Yopish">&times;</button>' +
                '</div>' +
                '<div class="translation-modal-tabs">' +
                LANGS.map((lang, i) => '<button type="button" class="translation-modal-tab' + (i === 2 ? ' is-active' : '') + '" data-lang="' + lang + '">' + (lang === 'uz' ? 'UZ' : lang === 'ru' ? 'RU' : 'EN') + '</button>').join('') +
                '</div>' +
                '<div class="translation-modal-body">' +
                (needName || needDesc ? '<div class="translation-modal-loading" id="translation-modal-loading">Tarjima yuklanmoqda…</div>' : '') +
                '<div class="translation-modal-content" id="translation-modal-content" style="' + ((needName || needDesc) ? 'opacity:0.5;pointer-events:none;' : '') + '">' +
                LANGS.map((lang) => {
                    const active = lang === 'en' ? ' is-active' : '';
                    return '<div class="translation-modal-pane' + active + '" data-lang="' + lang + '">' +
                        '<label class="translation-modal-label">Nomi</label>' +
                        '<textarea class="translation-modal-textarea translation-modal-name" data-lang="' + lang + '" rows="2"></textarea>' +
                        '<label class="translation-modal-label">Tarif</label>' +
                        '<textarea class="translation-modal-textarea translation-modal-desc" data-lang="' + lang + '" rows="4"></textarea>' +
                        '</div>';
                }).join('') +
                '</div>' +
                '</div>' +
                '<div class="translation-modal-footer">' +
                '<button type="button" class="translation-modal-btn-save">Saqlash</button>' +
                '</div>' +
                '</div>';
            overlay.classList.add('is-open');
            overlay.setAttribute('aria-hidden', 'false');

            const loadingEl = qs('#translation-modal-loading', overlay);
            const contentEl = qs('#translation-modal-content', overlay);

            function applyToModal(names, descs) {
                LANGS.forEach((lang) => {
                    const nameTa = qs('.translation-modal-name[data-lang="' + lang + '"]', overlay);
                    const descTa = qs('.translation-modal-desc[data-lang="' + lang + '"]', overlay);
                    if (nameTa) nameTa.value = (names && names[lang]) ? names[lang] : '';
                    if (descTa) descTa.value = (descs && descs[lang]) ? descs[lang] : '';
                });
                if (loadingEl) loadingEl.style.display = 'none';
                if (contentEl) { contentEl.style.opacity = '1'; contentEl.style.pointerEvents = ''; }
            }

            if (!needName && !needDesc) {
                const names = getFormNames();
                const descs = getFormDescs();
                applyToModal(names, descs);
            } else {
                const namePromise = needName ? callTranslateApi(nameText, src) : Promise.resolve(null);
                const descPromise = needDesc ? callTranslateApi(descText, src) : Promise.resolve(null);
                Promise.all([namePromise, descPromise]).then(([nameData, descData]) => {
                    if (nameData) fillNameFields(nameData);
                    if (descData) fillDescFields(descData);
                    const names = nameData ? { uz: nameData.uz || '', ru: nameData.ru || '', en: nameData.en || '' } : getFormNames();
                    const descs = descData ? { uz: descData.uz || '', ru: descData.ru || '', en: descData.en || '' } : getFormDescs();
                    applyToModal(names, descs);
                });
            }

            const closeBtn = qs('.translation-modal-close', overlay);
            const saveBtn = qs('.translation-modal-btn-save', overlay);
            const tabs = qsa('.translation-modal-tab', overlay);
            const panes = qsa('.translation-modal-pane', overlay);

            function showPane(lang) {
                tabs.forEach((t) => t.classList.toggle('is-active', t.dataset.lang === lang));
                panes.forEach((p) => p.classList.toggle('is-active', p.dataset.lang === lang));
            }

            tabs.forEach((t) => {
                t.addEventListener('click', () => showPane(t.dataset.lang));
            });

            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    overlay.classList.remove('is-open');
                    overlay.setAttribute('aria-hidden', 'true');
                });
            }
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.classList.remove('is-open');
                    overlay.setAttribute('aria-hidden', 'true');
                }
            });

            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    const newNames = { uz: '', ru: '', en: '' };
                    const newDescs = { uz: '', ru: '', en: '' };
                    qsa('.translation-modal-name', overlay).forEach((ta) => {
                        newNames[ta.dataset.lang] = ta.value;
                    });
                    qsa('.translation-modal-desc', overlay).forEach((ta) => {
                        newDescs[ta.dataset.lang] = ta.value;
                    });
                    setFormNames(newNames);
                    setFormDescs(newDescs);
                    overlay.classList.remove('is-open');
                    overlay.setAttribute('aria-hidden', 'true');
                });
            }
        }

        if (btnModal) {
            btnModal.addEventListener('click', (e) => {
                e.preventDefault();
                if (nameLoading || descLoading) return;
                openTranslationsModal();
            });
        }

        const idName = qs('#id_name');
        const idDesc = qs('#id_description');
        if (nameInput && idName && idName.value) nameInput.value = idName.value;
        if (descInput && idDesc && idDesc.value) descInput.value = idDesc.value;
    }

    function getSubcategoriesUrl(form) {
        if (form && form.action) {
            const base = form.action.replace(/\/add\/?$|\/\d+\/change\/?$/, '');
            return (base.endsWith('/') ? base : base + '/') + 'get-subcategories/';
        }
        const path = window.location.pathname || '';
        const base = path.replace(/\/add\/?$|\/\d+\/change\/?$/, '');
        return (base.endsWith('/') ? base : base + '/') + 'get-subcategories/';
    }

    function initSubcategoryByCategory() {
        const form = qs('#product_form') || qs('form[id*="product"]') || qs('#changelist-form') || document.querySelector('form');
        if (!form) return;
        if (form.dataset.subcategoryInited === 'true') return;
        const subcategorySelect = form.querySelector('#id_subcategory') || form.querySelector('select[name="subcategory"]');
        if (!subcategorySelect) return;

        function getCategoryValue() {
            const categoryField = form.querySelector('#id_category') || form.querySelector('select[name="category"]') || form.querySelector('input[name="category"]') || form.querySelector('[name="category"]');
            if (!categoryField) return '';
            if (categoryField.tagName === 'SELECT') return (categoryField.value || '').trim();
            return (categoryField.value || '').trim();
        }

        function setSubcategoryOptions(categoryId) {
            if (!categoryId) {
                subcategorySelect.innerHTML = '<option value="">---------</option>';
                subcategorySelect.disabled = false;
                return;
            }
            const url = getSubcategoriesUrl(form) + '?category_id=' + encodeURIComponent(categoryId);
            const currentValue = subcategorySelect.value;
            subcategorySelect.disabled = true;
            subcategorySelect.innerHTML = '<option value="">---------</option>';
            fetch(url, { credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
                .then((r) => r.ok ? r.json() : Promise.reject(r))
                .then((data) => {
                    const list = data.subcategories || [];
                    list.forEach((s) => {
                        const opt = document.createElement('option');
                        opt.value = s.id;
                        opt.textContent = s.name;
                        subcategorySelect.appendChild(opt);
                    });
                    if (currentValue && list.some((s) => String(s.id) === String(currentValue))) {
                        subcategorySelect.value = currentValue;
                    } else {
                        subcategorySelect.value = '';
                    }
                })
                .catch(() => {})
                .finally(() => {
                    subcategorySelect.disabled = false;
                });
        }

        function onCategoryChange() {
            setSubcategoryOptions(getCategoryValue());
        }

        form.addEventListener('change', (e) => {
            const t = e.target;
            if (t && (t.name === 'category' || t.id === 'id_category')) onCategoryChange();
        });
        form.addEventListener('input', (e) => {
            const t = e.target;
            if (t && (t.name === 'category' || t.id === 'id_category')) onCategoryChange();
        });

        subcategorySelect.addEventListener('focus', () => {
            const categoryId = getCategoryValue();
            if (categoryId && subcategorySelect.options.length <= 1) setSubcategoryOptions(categoryId);
        });

        form.dataset.subcategoryInited = 'true';

        if (getCategoryValue()) {
            setSubcategoryOptions(getCategoryValue());
        }
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
        initTranslationManual();
        initSubcategoryByCategory();
        setTimeout(initSubcategoryByCategory, 400);
        const initialCommon = qs('#id_common_product');
        if (initialCommon && initialCommon.value) {
            updateCommonProductInfo(initialCommon.value);
        }
    });
})();
