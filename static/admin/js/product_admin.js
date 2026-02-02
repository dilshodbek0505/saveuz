(function($) {
    'use strict';

    $(document).ready(function() {
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
        }

        // Обработчик изменения режима
        $('input[name="add_mode"]').on('change', function() {
            toggleAddMode();
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

        // Улучшение UX: предупреждение при переключении режима с заполненными данными
        let previousMode = $('input[name="add_mode"]:checked').val();
        $('input[name="add_mode"]').on('change', function() {
            const newMode = $(this).val();
            const hasManualData = $('#id_name').val() || $('#id_description').val() || $('#id_category').val();
            const hasCommonProduct = $('#id_common_product').val();
            
            // Если режим не изменился, ничего не делаем
            if (newMode === previousMode) {
                return;
            }
            
            if (newMode === 'common' && hasManualData && !hasCommonProduct) {
                if (!confirm('Вы переключаетесь на режим "Из общей базы". ' +
                           'Заполненные вручную данные (название, описание, категория) будут скрыты. ' +
                           'Продолжить?')) {
                    // Возвращаемся к предыдущему режиму
                    $('input[name="add_mode"][value="' + previousMode + '"]').prop('checked', true);
                    return false;
                }
            } else if (newMode === 'manual' && hasCommonProduct) {
                if (!confirm('Вы переключаетесь на режим "Вручную". ' +
                           'Выбранный продукт из общей базы будет сброшен. ' +
                           'Продолжить?')) {
                    // Возвращаемся к предыдущему режиму
                    $('input[name="add_mode"][value="' + previousMode + '"]').prop('checked', true);
                    return false;
                }
                // Очищаем common_product при переключении на ручной режим
                $('#id_common_product').val('');
            }
            
            previousMode = newMode;
            toggleAddMode();
        });
    });

})(django.jQuery);
