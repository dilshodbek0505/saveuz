(function($) {
    'use strict';

    if (!$ || !$.fn) {
        return;
    }

    $(document).ready(function() {
        function updateAddModeTabs() {
            const $tabs = $('.add-mode-tabs');
            if (!$tabs.length) return;
            const currentValue = $('input[name="add_mode"]:checked').val();
            $tabs.find('.add-mode-tab').each(function() {
                const $btn = $(this);
                const value = $btn.data('value');
                const active = value === currentValue;
                $btn.toggleClass('is-active', active).attr('aria-selected', active ? 'true' : 'false');
            });
        }

        function initAddModeTabs() {
            const $field = $('#id_add_mode');
            if (!$field.length || $('.add-mode-tabs').length) return;

            const $inputs = $field.find('input[type="radio"][name="add_mode"]');
            if (!$inputs.length) return;

            const $tabs = $('<div class="add-mode-tabs" role="tablist" aria-label="Способ добавления"></div>');
            $inputs.each(function() {
                const $input = $(this);
                const value = $input.val();
                const labelText = $input.parent().text().trim();
                const $btn = $('<button type="button" class="add-mode-tab" role="tab"></button>');
                $btn.text(labelText);
                $btn.attr('data-value', value);
                $tabs.append($btn);
            });

            $field.addClass('add-mode-hidden').after($tabs);

            $tabs.on('click', '.add-mode-tab', function() {
                const value = $(this).data('value');
                $inputs.filter('[value="' + value + '"]').prop('checked', true).trigger('change');
                updateAddModeTabs();
            });
        }

        // Функция для переключения режимов
        function toggleAddMode() {
            const addMode = $('input[name="add_mode"]:checked').val();
            const commonProductSection = $('.common-product-section');
            const manualFieldsSection = $('.manual-fields-section');
            
            if (addMode === 'common') {
                // Показываем секцию общей базы, скрываем ручные поля
                commonProductSection.removeClass('hidden');
                manualFieldsSection.addClass('hidden');
                
                // Делаем поля ручного ввода необязательными и readonly
                $('#id_name').prop('required', false).prop('readonly', true);
                $('#id_description').prop('required', false).prop('readonly', true);
                $('#id_category').prop('required', false).prop('readonly', true);
                
                // Делаем common_product обязательным
                $('#id_common_product').prop('required', true);
                
            } else if (addMode === 'manual') {
                // Скрываем секцию общей базы, показываем ручные поля
                commonProductSection.addClass('hidden');
                manualFieldsSection.removeClass('hidden');
                
                // Делаем поля ручного ввода обязательными и редактируемыми
                $('#id_name').prop('required', true).prop('readonly', false);
                $('#id_description').prop('required', true).prop('readonly', false);
                $('#id_category').prop('required', true).prop('readonly', false);
                
                // Делаем common_product необязательным
                $('#id_common_product').prop('required', false);
            }

            updateAddModeTabs();
        }

        // Обработчик изменения режима
        $('input[name="add_mode"]').on('change', function() {
            toggleAddMode();
        });

        // Инициализация при загрузке страницы
        initAddModeTabs();
        toggleAddMode();

        // Обновление информации о продукте при выборе common_product
        $('#id_common_product').on('change', function() {
            const productId = $(this).val();
            if (productId) {
                // Автоматически переключаемся на режим "из общей базы"
                $('input[name="add_mode"][value="common"]').prop('checked', true);
                toggleAddMode();
                
                // Заполняем поля данными из выбранного продукта (для визуального отображения)
                // Данные будут взяты из common_product автоматически при сохранении
                const selectedOption = $(this).find('option:selected');
                const productText = selectedOption.text();
                
                // Можно добавить AJAX запрос для получения полной информации о продукте
                // и заполнения информационного блока
            } else {
                // Если продукт не выбран, переключаемся на ручной режим
                if (!$('#id_name').val() && !$('#id_description').val()) {
                    $('input[name="add_mode"][value="manual"]').prop('checked', true);
                    toggleAddMode();
                }
            }
        });

        updateAddModeTabs();
    });

})(django.jQuery);
