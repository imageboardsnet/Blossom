document.addEventListener('DOMContentLoaded', function () {
    const copyButtons = document.querySelectorAll('.ui.action.input .ui.button');
    const inputFields = document.querySelectorAll('.ui.action.input input');

    copyButtons.forEach(function (copyButton, index) {
        copyButton.addEventListener('click', function () {
            inputFields[index].select();
            navigator.clipboard.writeText(inputFields[index].value);
        });
    });
});