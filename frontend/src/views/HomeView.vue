<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import DashboardChart from '../components/DashboardChart.vue';
import { t as $t } from '../plugins/i18n';

const stats = ref(null);
const loading = ref(true);
const error = ref('');
const router = useRouter();

const chartData = computed(() => {
  if (!stats.value || !stats.value.modules) return { labels: [], datasets: [] }
  
  return {
    labels: stats.value.modules.map(m => m.name),
    datasets: [
      {
        label: $t('performance_score'),
        backgroundColor: '#41B883',
        data: stats.value.modules.map(m => m.score)
      }
    ]
  }
});

const fetchStats = async () => {
  try {
    const response = await fetch('/api/v1/dashboard-stats');
    
    if (response.status === 401) {
      router.push('/login');
      return;
    }
    
    if (!response.ok) {
      throw new Error($t('data_fetch_error'));
    }
    
    const data = await response.json();
    if (data.error) {
        throw new Error(data.error);
    }
    stats.value = data;
  } catch (err) {
    console.error('Dashboard error:', err);
    error.value = $t('dashboard_load_error');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<template>
  <div class="home">
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">{{ $t('dashboard_title') }}</h1>
      <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
          <button type="button" class="btn btn-sm btn-outline-secondary">{{ $t('share_button') }}</button>
          <button type="button" class="btn btn-sm btn-outline-secondary">{{ $t('export_button') }}</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('loading') }}</span>
      </div>
      <p class="mt-2">{{ $t('loading_data') }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
      <button class="btn btn-link" @click="fetchStats">{{ $t('retry_button') }}</button>
    </div>

    <div v-else class="dashboard-content">
      <!-- Alerts Section -->
      <div v-if="stats.alerts > 0" class="alert alert-warning d-flex align-items-center" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <div>
          {{ stats.alerts }} {{ $t('pending_alerts_suffix') }}
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row">
        <div class="col-md-4" v-for="module in stats.modules" :key="module.name">
          <div class="card mb-4 shadow-sm" :class="{'border-success': module.status === 'Active', 'border-warning': module.status === 'Pending'}">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="my-0 font-weight-normal">{{ module.name }}</h5>
              <span class="badge" :class="{'bg-success': module.status === 'Active', 'bg-warning text-dark': module.status === 'Pending'}">
                {{ module.status === 'Active' ? $t('status_active') : $t('status_pending') }}
              </span>
            </div>
            <div class="card-body">
              <h1 class="card-title pricing-card-title">{{ module.score }}<small class="text-muted">/100</small></h1>
              <ul class="list-unstyled mt-3 mb-4">
                <li>Son güncelleme: Bugün</li>
                <li>Veri girişi: %{{ module.score }} tamamlandı</li>
              </ul>
              <button type="button" class="btn btn-lg btn-block w-100" 
                :class="{'btn-outline-primary': module.status === 'Active', 'btn-primary': module.status === 'Pending'}">
                {{ module.status === 'Active' ? 'Detayları Gör' : 'Veri Gir' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Section -->
      <div class="row mt-4 mb-4">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="my-0">Modül Performans Analizi</h5>
            </div>
            <div class="card-body">
              <DashboardChart v-if="stats" :chartData="chartData" />
            </div>
          </div>
        </div>
      </div>

      <!-- Reports Section -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Rapor Durumu</h5>
            </div>
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <span>Sonraki Raporlama Tarihi:</span>
                <strong>{{ stats.next_deadline }}</strong>
              </div>
              <div class="progress" style="height: 20px;">
                <div class="progress-bar bg-success" role="progressbar" style="width: 75%;" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">Genel İlerleme %75</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: transform 0.2s;
}
.card:hover {
  transform: translateY(-5px);
}
</style>
