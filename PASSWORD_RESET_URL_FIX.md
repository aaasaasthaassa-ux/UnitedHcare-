# Password Reset URL - Quick Reference

## The Issue You Encountered

You tried to visit:
```
❌ WRONG: http://127.0.0.1:8000/accounts/password_reset/MTI/czbj6k-bf78c4
Error: 404 Page Not Found
```

---

## The Correct URL

The correct URL path for password reset is:
```
✅ CORRECT: http://127.0.0.1:8000/accounts/reset/<uidb64>/<token>/
Example: http://127.0.0.1:8000/accounts/reset/MTI/czbj6k-fccedaf3eac7eac28291b4dfa3af4a1d/
```

---

## URL Pattern Reference

### Django Built-in Auth URLs

| Purpose | URL Pattern | Name |
|---------|-----------|------|
| Request Reset | `/accounts/password_reset/` | `password_reset` |
| Reset Done | `/accounts/password_reset/done/` | `password_reset_done` |
| **Reset Form** | **`/accounts/reset/<uidb64>/<token>/`** | **`password_reset_confirm`** ← USE THIS |
| Reset Complete | `/accounts/reset/done/` | `password_reset_complete` |

---

## Why Was It Wrong?

### URL Paths:
- `/accounts/password_reset/` — For requesting reset (form page)
- `/accounts/reset/` — For confirming reset (with token) ← **This is what you need**

### The Difference:
```
/accounts/password_reset/               ← Request email form
/accounts/password_reset/<uid>/<token>/ ← WRONG - doesn't exist
/accounts/reset/<uid>/<token>/          ← CORRECT - password reset form
```

---

## How to Get the Correct Link

### Method 1: From Console Output

When you request password reset, Django prints the email to console:

```
Look in terminal for:
http://127.0.0.1:8000/accounts/reset/MTI/czbj6k-fccedaf3eac7eac28291b4dfa3af4a1d/
```

### Method 2: Generate Programmatically

```python
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

user = User.objects.get(email='adarsh03kazee@gmail.com')
uid = urlsafe_base64_encode(force_bytes(user.pk))
token = default_token_generator.make_token(user)
reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
full_url = f"http://127.0.0.1:8000{reset_url}"
# Result: http://127.0.0.1:8000/accounts/reset/MTI/czbj6k-fccedaf3eac7eac28291b4dfa3af4a1d/
```

---

## Complete Password Reset Flow (Corrected)

```
1. User clicks "Forgot Password?"
   ↓ Goes to: http://127.0.0.1:8000/accounts/password_reset/

2. User enters email
   ↓ POST to same URL

3. Django validates email exists
   ↓ Generates token and prints to console

4. User copies link from console
   ↓ Link: http://127.0.0.1:8000/accounts/reset/MTI/czbj6k-fccedaf3eac7eac28291b4dfa3af4a1d/

5. User visits reset link
   ↓ Goes to: http://127.0.0.1:8000/accounts/reset/<uid>/<token>/

6. Django validates token
   ✅ If valid: Shows password_reset_confirm.html (reset form)
   ❌ If invalid: Shows error message

7. User enters new password
   ↓ POST to same URL

8. Password saved
   ↓ Redirect to: http://127.0.0.1:8000/accounts/reset/done/

9. Success page shown
   ✅ password_reset_complete.html
```

---

## Templates vs URLs

**Templates** (in `templates/registration/`):
- `password_reset_form.html` — Request form (shows when you go to `/accounts/password_reset/`)
- `password_reset_done.html` — Confirmation (shows after form submitted)
- `password_reset_confirm.html` — Reset form (shows when you go to `/accounts/reset/<uid>/<token>/`)
- `password_reset_complete.html` — Success (shows after password saved)

**URLs**:
```
/accounts/password_reset/           → password_reset_form.html
/accounts/password_reset/done/      → password_reset_done.html
/accounts/reset/<uid>/<token>/      → password_reset_confirm.html ← The one with token
/accounts/reset/done/               → password_reset_complete.html
```

---

## Email Template

The email template correctly generates the reset link:

```html
{% url 'password_reset_confirm' uidb64=uid token=token %}
```

This reverses to: `/accounts/reset/<uid>/<token>/` ✅

---

## Summary

| Item | Value |
|------|-------|
| Request Form URL | `/accounts/password_reset/` |
| Email in Console | Contains full link |
| Correct Link Path | `/accounts/reset/<uidb64>/<token>/` |
| Wrong Path | ~~`/accounts/password_reset/<uidb64>/<token>/`~~ |
| Template | `password_reset_confirm.html` |
| Status | ✅ Working correctly |

---

## Test Now

Visit the correct URL:
```
http://127.0.0.1:8000/accounts/reset/MTI/czbjbq-fccedaf3eac7eac28291b4dfa3af4a1d/
```

(Copy from your console output, not this example)

You should see the "Create New Password" form. If you see 404 error, you have the wrong URL format.

---

**Everything is working correctly! The URL pattern is just different than expected.** ✅
