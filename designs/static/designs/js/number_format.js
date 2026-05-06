document.addEventListener('DOMContentLoaded', function() {
    function cleanNumber(value) {
        return value.replace(/\s+/g, '').replace(/,/g, '');
    }

    function groupThousands(value) {
        return value.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function formatLive(value, decimalPlaces) {
        value = cleanNumber(value).replace(/[^\d.-]/g, '');

        const isNegative = value.startsWith('-');
        value = value.replace(/-/g, '');

        const parts = value.split('.');
        const integerPart = groupThousands(parts[0] || '');
        let formatted = `${isNegative ? '-' : ''}${integerPart}`;

        if (decimalPlaces > 0 && parts.length > 1) {
            formatted += `.${parts.slice(1).join('').slice(0, decimalPlaces)}`;
        }

        return formatted;
    }

    function formatFixed(value, decimalPlaces) {
        value = cleanNumber(value);
        if (!value) {
            return '';
        }

        const number = Number(value);
        if (Number.isNaN(number)) {
            return value;
        }

        if (decimalPlaces === 0) {
            return groupThousands(String(Math.trunc(number)));
        }

        const fixed = number.toFixed(decimalPlaces);
        const parts = fixed.split('.');
        return `${groupThousands(parts[0])}.${parts[1]}`;
    }

    function initializeNumberInput(input) {
        if (input.dataset.numberFormatInitialized) {
            return;
        }

        input.dataset.numberFormatInitialized = 'true';
        const decimalPlaces = Number(input.dataset.decimalPlaces || 0);

        input.value = formatFixed(input.value, decimalPlaces);

        input.addEventListener('input', function() {
            const cursorAtEnd = input.selectionStart === input.value.length;
            input.value = formatLive(input.value, decimalPlaces);
            if (cursorAtEnd) {
                input.setSelectionRange(input.value.length, input.value.length);
            }
        });

        input.addEventListener('blur', function() {
            input.value = formatFixed(input.value, decimalPlaces);
        });
    }

    function initializeNumberInputs(context) {
        context.querySelectorAll('.spaced-number-input').forEach(initializeNumberInput);
    }

    initializeNumberInputs(document);

    document.addEventListener('formset:added', function(event) {
        initializeNumberInputs(event.target);
    });
});
