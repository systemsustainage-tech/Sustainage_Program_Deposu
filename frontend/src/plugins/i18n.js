import { reactive } from 'vue'

const state = reactive({
  locale: 'tr',
  messages: {}
})

export const t = (key) => {
  const keys = key.split('.')
  let value = state.messages
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k]
    } else {
      return key // Fallback to key if not found
    }
  }
  
  return typeof value === 'string' ? value : key
}

const i18n = {
  install(app) {
    // Define $t
    app.config.globalProperties.$t = t

    // Load translations
    fetch('/api/v1/translations')
      .then(res => res.json())
      .then(data => {
        state.locale = data.lang
        state.messages = data.translations
        console.log('Translations loaded:', state.locale)
      })
      .catch(err => console.error('Failed to load translations:', err))
  }
}

export default i18n
