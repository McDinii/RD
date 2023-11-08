document.addEventListener("DOMContentLoaded", function() {
    console.log('JavaScript файл успешно загружен1!');
    const copyEmailBtns = document.querySelectorAll('.copy-email-btn');

    copyEmailBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const email = btn.dataset.email;

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(email)
                    .then(() => {
                    alert('Адрес электронной почты скопирован!');
                    })
                    .catch((error) => {
                    console.error('Ошибка при копировании адреса электронной почты:', error);
                    });
            } else {
            const textArea = document.createElement('textarea');
            textArea.value = email;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('Адрес электронной почты скопирован!');
            }
        });
    });
});
