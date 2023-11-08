console.log('JavaScript файл успешно загруженapp!');
document.addEventListener('DOMContentLoaded', function() {
  const copyEmailBtns = document.querySelectorAll('.copy-email-btn');

  copyEmailBtns.forEach(function(btn) {
    const email = btn.dataset.email;

    btn.addEventListener('click', function() {
      navigator.clipboard.writeText(email)
        .then(() => {
          alert('Адрес электронной почты скопирован!');
        })
        .catch((error) => {
          console.error('Ошибка при копировании адреса электронной почты:', error);
        });
    });
  });
});
