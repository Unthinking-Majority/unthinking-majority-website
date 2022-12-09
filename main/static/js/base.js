let file_inputs = document.querySelector('.file-input');

if (file_inputs) {
    file_inputs.onchange = function () {
        let file_name = this.files.item(0).name;
        this.labels.forEach(label => {
            label.querySelector('.file-label').innerText = file_name;
        });
    };
}