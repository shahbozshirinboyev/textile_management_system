document.addEventListener('DOMContentLoaded', function() {
    const imageInputs = document.querySelectorAll('input[type="file"]');

    function getPreviewSize(previewElement, inputName) {
        const defaultSize = inputName === 'image'
            ? { width: 100, height: 100 }
            : { width: 100, height: 20 };

        if (!previewElement) {
            return defaultSize;
        }

        return {
            width: parseInt(previewElement.dataset.previewWidth, 10) || defaultSize.width,
            height: parseInt(previewElement.dataset.previewHeight, 10) || defaultSize.height,
        };
    }

    function setImageSize(img, size) {
        img.style.maxWidth = `${size.width}px`;
        img.style.maxHeight = `${size.height}px`;
        img.style.width = 'auto';
        img.style.height = 'auto';
    }

    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const readonlyPreview = document.getElementById(`${input.name}-preview`);
                    if (readonlyPreview) {
                        readonlyPreview.innerHTML = '';

                        const img = document.createElement('img');
                        img.src = event.target.result;
                        setImageSize(img, getPreviewSize(readonlyPreview, input.name));
                        readonlyPreview.appendChild(img);
                        return;
                    }

                    const previewContainer = input.parentElement.querySelector('.image-preview-container');
                    if (!previewContainer) {
                        const container = document.createElement('div');
                        container.className = 'image-preview-container';
                        container.style.marginTop = '5px';

                        const img = document.createElement('img');
                        img.src = event.target.result;
                        setImageSize(img, { width: 80, height: 20 });

                        container.appendChild(img);
                        input.parentElement.appendChild(container);
                    } else {
                        const img = previewContainer.querySelector('img');
                        img.src = event.target.result;
                        setImageSize(img, { width: 80, height: 20 });
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });
});
