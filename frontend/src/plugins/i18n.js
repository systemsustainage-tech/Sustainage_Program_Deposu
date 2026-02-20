import { createI18n } from 'vue-i18n'
import tr from '../locales/tr.json'
import en from '../locales/en.json'
import de from '../locales/de.json'

// Readable fallback function
const missingHandler = (locale, key, vm, values) => {
  if (!key) return ''
  // active_surveys -> Active surveys
  return key.replace(/_/g, ' ').replace(/-/g, ' ').trim().replace(/^\w/, c => c.toUpperCase())
}

const i18n = createI18n({
  legacy: false, // Vue 3 Composition API mode
  globalInjection: true, // Inject $t globally for templates
  locale: localStorage.getItem('lang') || 'tr',
  fallbackLocale: 'en',
  messages: {
    tr,
    en,
    de
  },
  missing: missingHandler,
  silentTranslationWarn: true,
  missingWarn: false,
  fallbackWarn: false
})

// Dynamic update from backend
// This allows the backend to override/update translations without rebuilding frontend
// Adding timestamp to bypass browser cache as requested
fetch('/api/v1/translations?v=' + new Date().getTime())
  .then(res => res.json())
  .then(data => {
    if (data && data.translations && data.lang) {
      // Update messages for the language returned by backend
      // Using mergeLocaleMessage to support lazy-loaded additions if any
      i18n.global.mergeLocaleMessage(data.lang, data.translations)
      
      // Sync locale if different
      if (i18n.global.locale.value !== data.lang) {
          i18n.global.locale.value = data.lang
          localStorage.setItem('lang', data.lang)
      }
      console.log('Translations updated from backend for:', data.lang)
    }
  })
  .catch(err => console.error('Failed to update translations:', err))

export default i18n
