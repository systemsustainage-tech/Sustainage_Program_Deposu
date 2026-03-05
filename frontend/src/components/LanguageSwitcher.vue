
<script setup>
import { useI18n } from 'vue-i18n';
import { ref, watch } from 'vue';

const { locale } = useI18n();
const currentLang = ref(locale.value);

const languages = [
  { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' }
];

const changeLanguage = async (lang) => {
  currentLang.value = lang;
  locale.value = lang;
  localStorage.setItem('lang', lang);
  document.documentElement.lang = lang;
  
  // Optional: Notify backend about language change if user is logged in
  try {
      await fetch(`/set_language/${lang}`);
  } catch (e) {
      console.warn("Backend language sync failed", e);
  }
};

watch(locale, (newLang) => {
    currentLang.value = newLang;
});
</script>

<template>
  <div class="dropdown">
    <button class="btn btn-outline-light dropdown-toggle btn-sm" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
      <i class="bi bi-globe me-1"></i> {{ currentLang.toUpperCase() }}
    </button>
    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="languageDropdown">
      <li v-for="lang in languages" :key="lang.code">
        <a class="dropdown-item" href="#" @click.prevent="changeLanguage(lang.code)" :class="{ active: currentLang === lang.code }">
          <span class="me-2">{{ lang.flag }}</span> {{ lang.label }}
        </a>
      </li>
    </ul>
  </div>
</template>
