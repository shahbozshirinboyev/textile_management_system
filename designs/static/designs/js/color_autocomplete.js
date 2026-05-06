document.addEventListener('DOMContentLoaded', function() {
    function labelContainerForSelect(select) {
        const row = select.closest('tr');
        if (!row) {
            return null;
        }

        let container = row.querySelector('.color-label-preview');
        if (container) {
            return container;
        }

        const cell = row.querySelector('.field-color_label_preview');
        if (!cell) {
            return null;
        }

        cell.innerHTML = '';
        container = document.createElement('span');
        container.className = 'color-label-preview';
        cell.appendChild(container);
        return container;
    }

    function updateColorLabel(select) {
        const option = select.options[select.selectedIndex];
        const imageUrl = option ? option.dataset.imageUrl : '';
        const container = labelContainerForSelect(select);

        if (!container) {
            return;
        }

        container.innerHTML = '';

        if (!imageUrl) {
            container.textContent = 'No label';
            return;
        }

        const image = document.createElement('img');
        image.src = imageUrl;
        image.alt = '';
        image.width = 206;
        image.height = 56;
        container.appendChild(image);
    }

    function initializeColorSelect(select) {
        if (select.name.includes('__prefix__')) {
            return;
        }

        if (select.dataset.colorLabelInitialized) {
            return;
        }

        select.dataset.colorLabelInitialized = 'true';
        updateColorLabel(select);
    }

    function initializeColorSelects(context) {
        context.querySelectorAll('select.color-image-select').forEach(initializeColorSelect);
    }

    document.addEventListener('change', function(event) {
        if (event.target.matches('select.color-image-select')) {
            updateColorLabel(event.target);
        }
    });

    initializeColorSelects(document);

    document.addEventListener('formset:added', function(event) {
        initializeColorSelects(event.target);
    });
});
