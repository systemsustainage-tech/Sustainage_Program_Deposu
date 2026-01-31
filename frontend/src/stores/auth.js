import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const isAuthenticated = ref(!!user.value);
  const router = useRouter();

  function login(userData) {
    user.value = userData;
    isAuthenticated.value = true;
    localStorage.setItem('user', JSON.stringify(userData));
  }

  function logout() {
    user.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem('user');
    // Optional: Call backend logout endpoint
    fetch('/api/v1/logout', { method: 'POST' }).catch(() => {});
  }

  return { user, isAuthenticated, login, logout };
});
