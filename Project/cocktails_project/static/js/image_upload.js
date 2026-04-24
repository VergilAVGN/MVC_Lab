const input = document.getElementById('imageInput');
const dropZone = document.getElementById('dropZone');
const preview = document.getElementById('preview');
const btn = document.getElementById('uploadBtn');
const imageWrapper = document.getElementById('imageWrapper');

if (input && dropZone && preview && btn) {

    btn.onclick = () => input.click();

    input.onchange = () => {
        const file = input.files[0];
        if (file) {
            preview.src = URL.createObjectURL(file);
            if (imageWrapper) imageWrapper.style.display = 'block';
        }
    };

    dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.classList.add('active');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('active');
    });

    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('active');

        const file = e.dataTransfer.files[0];
        input.files = e.dataTransfer.files;

        preview.src = URL.createObjectURL(file);
        if (imageWrapper) imageWrapper.style.display = 'block';
    });

    document.addEventListener('paste', function (e) {
        const items = e.clipboardData.items;

        for (let item of items) {
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();

                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);

                input.files = dataTransfer.files;

                preview.src = URL.createObjectURL(file);
                if (imageWrapper) imageWrapper.style.display = 'block';
            }
        }
    });
}
const removeBtn = document.getElementById('removeImageBtn');
const removeInput = document.getElementById('removeImageInput');

if (removeBtn) {
    removeBtn.addEventListener('click', () => {
        if (input) {
            input.value = "";
            if (input.files) input.files = new DataTransfer().files;
        }
        if (preview) preview.src = "";
        if (imageWrapper) imageWrapper.style.display = 'none';
        if (removeInput) removeInput.value = "1";
    });
}