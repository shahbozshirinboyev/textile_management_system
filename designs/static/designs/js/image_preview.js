document.addEventListener('DOMContentLoaded', function() {
    const imageInputs = document.querySelectorAll('input[type="file"]');

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
                        img.width = 100;
                        img.height = input.name === 'image' ? 100 : 20;
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
                        img.style.maxWidth = '80px';
                        img.style.maxHeight = '20px';

                        container.appendChild(img);
                        input.parentElement.appendChild(container);
                    } else {
                        const img = previewContainer.querySelector('img');
                        img.src = event.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });
});
