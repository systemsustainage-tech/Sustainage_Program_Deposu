<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const router = useRouter();
const authStore = useAuthStore();

import { t as $t } from '../plugins/i18n';

const handleLogin = async () => {
  error.value = '';
  loading.value = true;
  
  try {
    const response = await fetch('/api/v1/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    });

    const data = await response.json();

    if (response.ok && data.success) {
      // Login successful
      authStore.login(data.user);
      router.push('/');
    } else {
      error.value = data.error || $t('login_failed');
    }
  } catch (err) {
    console.error('Login error:', err);
    error.value = $t('server_error');
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">{{ $t('login_title') }}</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">{{ $t('username') }}</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username" 
                  v-model="username"
                  required
                  autofocus
                >
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">{{ $t('password') }}</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="password"
                  required
                >
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ loading ? $t('logging_in') : $t('login_button') }}
                </button>
              </div>
            </form>
          </div>
          <div class="card-footer text-center text-muted">
            <small>{{ $t('copyright_sustainage') }}</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 80vh;
  display: flex;
  align-items: center;
}
</style>
