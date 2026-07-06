/** True on Chrome (or Chromium) on Android — not desktop Linux with mobile UA. */
export function isAndroidChrome() {
  const ua = navigator.userAgent;
  return /Android/i.test(ua) && /Chrome\//i.test(ua) && !/CrOS/i.test(ua);
}
