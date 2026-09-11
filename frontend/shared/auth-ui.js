// NER SafeRoute — shared UI helpers for the login pages (validation, loading
// state, success feedback). No network/auth logic lives here — each page's
// own <script> still owns the Supabase/backend calls.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isValidEmail(email) {
  return EMAIL_RE.test(email.trim());
}

function passwordStrength(pw) {
  if (!pw) return { score: 0, label: '' };
  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 10) score++;
  if (/[0-9]/.test(pw) && /[a-zA-Z]/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  if (score <= 1) return { score: 1, label: 'Weak' };
  if (score <= 2) return { score: 2, label: 'Fair' };
  return { score: 3, label: 'Strong' };
}

// Wires live validation on an email <input>: toggles .invalid/.valid on its
// .input-group wrapper and fills the adjacent .field-msg as the user types.
function wireEmailField(inputEl, onChange) {
  const group = inputEl.closest('.input-group');
  const msgEl = group.querySelector('.field-msg');

  function check(showError) {
    const val = inputEl.value.trim();
    const valid = val === '' ? null : isValidEmail(val);
    group.classList.remove('invalid', 'valid');
    if (valid === false && showError) {
      group.classList.add('invalid');
      if (msgEl) msgEl.textContent = 'Enter a valid email address';
    } else if (valid === true) {
      group.classList.add('valid');
    }
    if (onChange) onChange(valid === true);
  }

  inputEl.addEventListener('input', () => check(false));
  inputEl.addEventListener('blur', () => check(true));
  return check;
}

// Wires live validation on a password <input>: same invalid/valid + field-msg
// pattern as wireEmailField, so an invalid password can be surfaced on a
// forced check (e.g. a click-time validation attempt) too.
function wirePasswordField(inputEl, minLength, onChange) {
  const group = inputEl.closest('.input-group');
  const msgEl = group.querySelector('.field-msg');

  function check(showError) {
    const val = inputEl.value;
    const valid = val === '' ? null : val.length >= minLength;
    group.classList.remove('invalid', 'valid');
    if (valid === false && showError) {
      group.classList.add('invalid');
      if (msgEl) msgEl.textContent = `Password must be at least ${minLength} characters`;
    } else if (valid === true) {
      group.classList.add('valid');
    }
    if (onChange) onChange(valid === true);
  }

  inputEl.addEventListener('input', () => check(false));
  inputEl.addEventListener('blur', () => check(true));
  return check;
}

// Briefly shakes a button to signal a rejected click (e.g. submit attempted
// with an invalid form) — visible feedback instead of a silent no-op.
function triggerShake(btn) {
  btn.classList.remove('shake');
  void btn.offsetWidth; // restart the animation if already mid-shake
  btn.classList.add('shake');
  setTimeout(() => btn.classList.remove('shake'), 420);
}

// Wires a password strength meter under a password <input>. Expects a
// sibling `.pw-strength` block with `.pw-strength-bars span` x3 and a
// `.pw-strength-label`.
function wirePasswordStrength(inputEl, meterEl) {
  const bars = meterEl.querySelectorAll('.pw-strength-bars span');
  const label = meterEl.querySelector('.pw-strength-label');

  inputEl.addEventListener('input', () => {
    const pw = inputEl.value;
    if (!pw) { meterEl.classList.remove('show'); return; }
    meterEl.classList.add('show');
    const { score, label: text } = passwordStrength(pw);
    bars.forEach((bar, i) => {
      bar.className = '';
      if (i < score) bar.classList.add(score === 1 ? 'on-weak' : score === 2 ? 'on-fair' : 'on-strong');
    });
    label.textContent = text ? `Password strength: ${text}` : '';
  });
}

function setButtonLoading(btn, loading, loadingText) {
  const textEl = btn.querySelector('.btn-text');
  const spinnerEl = btn.querySelector('.spinner');
  const arrowEl = btn.querySelector('.btn-arrow');
  if (loading) {
    btn.dataset.originalText = btn.dataset.originalText || (textEl ? textEl.textContent : '');
    if (textEl && loadingText) textEl.textContent = loadingText;
    if (spinnerEl) spinnerEl.hidden = false;
    if (arrowEl) arrowEl.hidden = true;
    btn.disabled = true;
  } else {
    if (textEl && btn.dataset.originalText) textEl.textContent = btn.dataset.originalText;
    if (spinnerEl) spinnerEl.hidden = true;
    if (arrowEl) arrowEl.hidden = false;
  }
}

function showSuccess(el, message) {
  el.innerHTML = '';
  const spinner = document.createElement('span');
  spinner.className = 'spinner';
  spinner.style.borderTopColor = '#1e8a3c';
  const text = document.createElement('span');
  text.textContent = message;
  el.appendChild(spinner);
  el.appendChild(text);
  el.style.display = 'flex';
}
