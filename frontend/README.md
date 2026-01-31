# Frontend Setup Guide

Bu klasör, Sustainage projesinin Vue.js 3 tabanlı modern arayüzünü içerir.

## Gereksinimler
- Node.js (v18+)
- npm (v9+)

## Kurulum
Aşağıdaki komutları bu klasör içinde çalıştırın:

```bash
# Bağımlılıkları yükle
npm install
```

## Geliştirme (Local)
Frontend'i bağımsız olarak geliştirmek için:
```bash
npm run dev
```

## Build (Flask Entegrasyonu için)
Flask uygulaması ile birlikte çalışacak dosyaları üretmek için:
```bash
npm run build
```
Bu komut, derlenmiş dosyaları otomatik olarak projenin `static/vue` klasörüne aktarır.

## Flask Entegrasyonu
`vite.config.js` dosyası, çıktıları `../static/vue` dizinine verecek şekilde yapılandırılmıştır.
Flask tarafında `templates/vue_app.html` (veya benzeri) oluşturup, bu static dosyaları referans vermeniz gerekmektedir. 
Not: Vite build işlemi `index.html` dosyasını da `static/vue/index.html` olarak çıkarır. Flask'ın bunu template olarak kullanabilmesi için kopyalanması veya template klasörünün ayarlanması gerekebilir.
