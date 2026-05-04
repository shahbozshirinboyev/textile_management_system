document.addEventListener('DOMContentLoaded', function() {
    const imageInputs = document.querySelectorAll('input[type="file"]');
    
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const previewContainer = input.parentElement.querySelector('.image-preview-container');
                    if (!previewContainer) {
                        const container = document.createElement('div');
                        container.className = 'image-preview-container';
                        container.style.marginTop = '10px';
                        
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        img.style.maxWidth = '100px';
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
