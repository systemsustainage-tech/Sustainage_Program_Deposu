<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import DashboardChart from '../components/DashboardChart.vue';
import DashboardDonutChart from '../components/DashboardDonutChart.vue';
import { useI18n } from 'vue-i18n';

const { t: $t } = useI18n();

const stats = ref(null);
const loading = ref(true);
const error = ref('');
const router = useRouter();
const theme = ref('light'); // 'light' or 'dark'

// Toggle Theme
const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light';
  document.body.setAttribute('data-bs-theme', theme.value);
};

// Define categories with icons
const categoryMap = {
  'environmental': {
    keys: ['carbon', 'energy', 'water', 'waste', 'biodiversity', 'product_technology'],
    icon: 'bi-tree-fill',
    color: 'success'
  },
  'social': {
    keys: ['social', 'human_rights', 'stakeholders'],
    icon: 'bi-people-fill',
    color: 'info'
  },
  'governance': {
    keys: ['governance', 'risk', 'compliance', 'ethics', 'supply_chain', 'economic'],
    icon: 'bi-bank2',
    color: 'primary'
  },
  'compliance': { // Renamed from reporting to match user intent better
    keys: ['sdg', 'gri', 'tcfd', 'tnfd', 'csrd', 'esrs', 'issb', 'cbam', 'cdp', 'unified_report', 'benchmark', 'regulation'],
    icon: 'bi-clipboard-check-fill',
    color: 'warning'
  }
};

const getCategoryDetails = (moduleKey) => {
  for (const [category, details] of Object.entries(categoryMap)) {
    if (details.keys.includes(moduleKey)) {
      return { id: category, ...details };
    }
  }
  return { id: 'other', icon: 'bi-box', color: 'secondary' };
};

const groupedModules = computed(() => {
  if (!stats.value || !stats.value.modules) return {};
  
  const groups = {
    'environmental': [],
    'social': [],
    'governance': [],
    'compliance': [],
    'other': []
  };
  
  stats.value.modules.forEach(module => {
    const key = module.key || module.name.toLowerCase().replace(/ /g, '_'); 
    module.uiKey = key; // Save for translation
    const catDetails = getCategoryDetails(key);
    if (groups[catDetails.id]) {
      groups[catDetails.id].push(module);
    } else {
      groups['other'].push(module);
    }
  });
  
  // Remove empty groups
  return Object.fromEntries(Object.entries(groups).filter(([_, v]) => v.length > 0));
});

// Summary Stats
const summaryStats = computed(() => {
  if (!stats.value) return { totalScore: 0, completedReports: 0, nextDeadline: '-' };
  
  const modules = stats.value.modules || [];
  const totalScore = modules.reduce((acc, m) => acc + m.score, 0);
  const avgScore = modules.length ? Math.round(totalScore / modules.length) : 0;
  
  return {
    avgScore,
    completedReports: stats.value.completed_reports || 0,
    nextDeadline: stats.value.next_deadline || '-'
  };
});

// Chart Data
const performanceChartData = computed(() => {
  if (!stats.value || !stats.value.modules) return { labels: [], datasets: [] }
  
  // Sort modules by score
  const sortedModules = [...stats.value.modules].sort((a, b) => b.score - a.score).slice(0, 10); // Top 10
  
  return {
    labels: sortedModules.map(m => $t(m.uiKey || m.name)),
    datasets: [
      {
        label: $t('performance_score'),
        backgroundColor: '#41B883',
        data: sortedModules.map(m => m.score)
      }
    ]
  }
});

const carbonChartData = computed(() => {
  if (!stats.value || !stats.value.carbon_data) return { labels: [], datasets: [] };
  
  return {
    labels: Object.keys(stats.value.carbon_data),
    datasets: [
      {
        backgroundColor: ['#41B883', '#E46651', '#00D8FF'],
        data: Object.values(stats.value.carbon_data)
      }
    ]
  };
});

const surveyChartData = computed(() => {
  if (!stats.value || !stats.value.survey_status) return { labels: [], datasets: [] };
  
  return {
    labels: Object.keys(stats.value.survey_status).map(k => $t('status_' + k.toLowerCase().replace(' ', '_'))),
    datasets: [
      {
        backgroundColor: ['#28a745', '#ffc107', '#6c757d'],
        data: Object.values(stats.value.survey_status)
      }
    ]
  };
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
  // Check system preference for theme
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    theme.value = 'dark';
    document.body.setAttribute('data-bs-theme', 'dark');
  }
});
</script>

<template>
  <div class="home container-fluid py-4">
    <!-- Header & Summary -->
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
      <div>
        <h1 class="h2">{{ $t('dashboard_title') }}</h1>
        <p class="text-muted">{{ $t('dashboard_welcome') }}</p>
      </div>
      <div class="btn-toolbar mb-2 mb-md-0">
        <button type="button" class="btn btn-sm btn-outline-secondary me-2" @click="toggleTheme">
          <i class="bi" :class="theme === 'light' ? 'bi-moon-stars' : 'bi-sun'"></i> {{ theme === 'light' ? $t('dark_mode') : $t('light_mode') }}
        </button>
        <div class="btn-group me-2">
          <button type="button" class="btn btn-sm btn-outline-secondary">{{ $t('share_button') }}</button>
          <button type="button" class="btn btn-sm btn-outline-secondary">{{ $t('export_button') }}</button>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="summaryStats" class="row mb-4 g-3">
      <div class="col-md-4">
        <div class="card border-start border-4 border-primary shadow-sm h-100">
          <div class="card-body d-flex align-items-center justify-content-between">
            <div>
              <h6 class="text-muted text-uppercase mb-1">{{ $t('average_score') }}</h6>
              <h2 class="mb-0 display-6 fw-bold">{{ summaryStats.avgScore }}%</h2>
            </div>
            <div class="icon-circle bg-primary bg-opacity-10 text-primary">
              <i class="bi bi-bar-chart-fill fs-3"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-start border-4 border-success shadow-sm h-100">
          <div class="card-body d-flex align-items-center justify-content-between">
            <div>
              <h6 class="text-muted text-uppercase mb-1">{{ $t('completed_reports') }}</h6>
              <h2 class="mb-0 display-6 fw-bold">{{ summaryStats.completedReports }}</h2>
            </div>
            <div class="icon-circle bg-success bg-opacity-10 text-success">
              <i class="bi bi-file-earmark-check-fill fs-3"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-start border-4 border-warning shadow-sm h-100">
          <div class="card-body d-flex align-items-center justify-content-between">
            <div>
              <h6 class="text-muted text-uppercase mb-1">{{ $t('next_deadline') }}</h6>
              <h3 class="mb-0 fw-bold">{{ summaryStats.nextDeadline }}</h3>
            </div>
            <div class="icon-circle bg-warning bg-opacity-10 text-warning">
              <i class="bi bi-calendar-event-fill fs-3"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('loading') }}</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
      <button class="btn btn-link" @click="fetchStats">{{ $t('retry_button') }}</button>
    </div>

    <div v-else>
      <!-- Charts Section -->
      <div class="row mb-4 g-3">
        <div class="col-lg-6">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="mb-0">{{ $t('top_performance_metrics') }}</h5>
            </div>
            <div class="card-body">
              <DashboardChart :chartData="performanceChartData" />
            </div>
          </div>
        </div>
        <div class="col-lg-3 col-md-6">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="mb-0">{{ $t('carbon_emissions') }}</h5>
            </div>
            <div class="card-body">
              <DashboardDonutChart :chartData="carbonChartData" />
            </div>
          </div>
        </div>
        <div class="col-lg-3 col-md-6">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-transparent border-0">
              <h5 class="mb-0">{{ $t('survey_status') }}</h5>
            </div>
            <div class="card-body">
              <DashboardDonutChart :chartData="surveyChartData" />
            </div>
          </div>
        </div>
      </div>

      <!-- System Notifications -->
      <div v-if="stats.alerts > 0" class="alert alert-warning shadow-sm d-flex align-items-center mb-4" role="alert">
        <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
        <div>
          <h6 class="alert-heading mb-1">{{ $t('system_alert_title') }}</h6>
          <p class="mb-0">{{ stats.alerts }} {{ $t('pending_alerts_suffix') }}</p>
        </div>
      </div>

      <!-- Modules by Category -->
      <div v-for="(modules, category) in groupedModules" :key="category" class="mb-5">
        <div class="d-flex align-items-center mb-3 pb-2 border-bottom">
          <i class="bi fs-3 me-2" :class="[(categoryMap[category]?.icon || 'bi-box'), 'text-' + (categoryMap[category]?.color || 'secondary')]"></i>
          <h3 class="mb-0 text-capitalize">{{ $t('category_' + category) }}</h3>
        </div>
        
        <div class="row g-4">
          <div class="col-md-4" v-for="module in modules" :key="module.name">
            <div class="card h-100 shadow-sm module-card border-top-0 border-end-0 border-bottom-0 border-3"
                 :class="'border-' + (categoryMap[category]?.color || 'secondary')">
              <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <h5 class="card-title fw-bold text-truncate" :title="$t(module.uiKey)">{{ $t(module.uiKey) }}</h5>
                  <span class="badge rounded-pill" :class="{'bg-success': module.status === 'Active', 'bg-secondary': module.status !== 'Active'}">
                    {{ module.status === 'Active' ? $t('status_active') : $t('status_pending') }}
                  </span>
                </div>
                
                <div class="mb-4">
                  <div class="d-flex justify-content-between mb-1">
                    <small class="text-muted">{{ $t('completion') }}</small>
                    <small class="fw-bold">{{ module.score }}%</small>
                  </div>
                  <div class="progress" style="height: 6px;">
                    <div class="progress-bar" role="progressbar" 
                         :class="'bg-' + (categoryMap[category]?.color || 'primary')"
                         :style="{width: module.score + '%'}" 
                         :aria-valuenow="module.score" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                </div>
                
                <div class="mt-auto d-grid gap-2">
                   <div class="btn-group" role="group">
                      <button type="button" class="btn btn-outline-primary btn-sm" :title="$t('action_enter_data')">
                        <i class="bi bi-pencil-square"></i> {{ $t('action_enter_data_short') }}
                      </button>
                      <button type="button" class="btn btn-outline-secondary btn-sm" :title="$t('action_view_details')">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button type="button" class="btn btn-outline-success btn-sm" :title="$t('action_create_report')">
                        <i class="bi bi-file-earmark-text"></i>
                      </button>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.module-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

/* Dark mode overrides if not handled by Bootstrap's data-bs-theme */
[data-bs-theme="dark"] .card {
  background-color: #2b3035;
  border-color: #495057;
}
</style>
