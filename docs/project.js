const route = new URLSearchParams(window.location.search);
if (route.get('view') === 'tutorial') {
  const language = route.get('lang') || 'en';
  window.location.replace(`tutorial/?lang=${encodeURIComponent(language)}`);
}

const dialog = document.querySelector('#lightbox');
const dialogImage = dialog.querySelector('img');
const themeToggle = document.querySelector('#theme-toggle');

themeToggle.addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('pec-theme', next);
  themeToggle.setAttribute('aria-label', `Switch to ${next === 'dark' ? 'light' : 'dark'} theme`);
});

document.querySelectorAll('[data-lightbox]').forEach((button) => {
  button.addEventListener('click', () => {
    dialogImage.src = button.dataset.lightbox;
    dialog.showModal();
  });
});

dialog.querySelector('.lightbox-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => {
  if (event.target === dialog) dialog.close();
});

document.querySelector('#copy-citation').addEventListener('click', async (event) => {
  await navigator.clipboard.writeText(document.querySelector('#bibtex').textContent);
  event.currentTarget.textContent = 'Copied';
  window.setTimeout(() => { event.currentTarget.textContent = 'Copy'; }, 1400);
});
