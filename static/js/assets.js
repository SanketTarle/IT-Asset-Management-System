/**
 * Assets Module Scripts
 * Handles image previews, dynamic form validation, and filter resets
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Image Preview
    const imageInput = document.getElementById('assetImageInput');
    const imagePreview = document.getElementById('assetImagePreview');
    const previewContainer = document.getElementById('assetImagePreviewContainer');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (evt) {
                    imagePreview.src = evt.target.result;
                    if (previewContainer) {
                        previewContainer.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 2. Auto-sync current value with purchase price if current value is empty
    const purchasePriceInput = document.getElementById('purchase_price');
    const currentValueInput = document.getElementById('current_value');

    if (purchasePriceInput && currentValueInput) {
        purchasePriceInput.addEventListener('blur', function () {
            if (!currentValueInput.value || parseFloat(currentValueInput.value) === 0) {
                currentValueInput.value = this.value;
            }
        });
    }

    // 3. Quick Filter Clear
    const clearFilterBtn = document.getElementById('clearFiltersBtn');
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function () {
            window.location.href = '/assets/';
        });
    }
});

