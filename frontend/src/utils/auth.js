export function redirectToLogin() {
  const state = crypto.randomUUID();
  localStorage.setItem('oauth_state', state);

  const params = new URLSearchParams({
    client_id: import.meta.env.VITE_CLIENT_ID,
    redirect_uri: import.meta.env.VITE_CALLBACK_URL,
    response_type: 'code',
    scope: 'openid profile email',
    state,
  });

  window.location.href = `${import.meta.env.VITE_AUTH_URL}?${params.toString()}`;
}