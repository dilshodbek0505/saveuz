(function($) {
    'use strict';

    if (!$ || !$.fn) {
        return;
    }

    $(document).ready(function() {
        function updateAddModeTabs() {
            const list = $('.add-mode-selector');
            list.attr('role', 'tablist');
            list.find('li').removeClass('is-active');
            list.find('label').removeClass('is-active').attr('role', 'tab');
            list.find('input:checked').each(function() {
                const $li = $(this).closest('li');
                const $label = $(this).closest('label');
                $li.addClass('is-active');
                $label.addClass('is-active').attr('aria-selected', 'true');
            });
            list.find('input:not(:checked)').each(function() {
                $(this).closest('label').attr('aria-selected', 'false');
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

        // Клик по табу (li/label) должен переключать input
        $('.add-mode-selector').on('click', 'li, label', function(event) {
            const $li = $(this).closest('li');
            let $input = $li.find('input[type="radio"]').first();
            if (!$input.length) {
                const labelFor = $(this).attr('for');
                $input = labelFor ? $('#' + labelFor) : $input;
            }
            if ($input && $input.length) {
                $input.prop('checked', true).trigger('change');
                event.preventDefault();
            }
        });

        // Инициализация при загрузке страницы
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
