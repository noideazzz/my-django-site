<template>
  <div class="learning-progress-container" :class="{ 'loaded': isLoaded }">
    <!-- 顶部导航栏 -->
    <div class="header">
      <button class="back-button" @click="goBack">
        <i class="bi bi-arrow-left"></i>
        返回
      </button>
      <h1 class="page-title">学习成果分析</h1>
      <div class="placeholder"></div>
    </div>

    <!-- 统计概览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="card-icon">
          <i class="bi bi-clock"></i>
        </div>
        <div class="card-content">
          <p class="card-label">总学习时长</p>
          <p class="card-value">{{ totalStudyTime }} 小时</p>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon">
          <i class="bi bi-check-circle"></i>
        </div>
        <div class="card-content">
          <p class="card-label">平均正确率</p>
          <p class="card-value">{{ averageAccuracy }}%</p>
        </div>
      </div>
      <div class="overview-card">
        <div class="card-icon">
          <i class="bi bi-list-check"></i>
        </div>
        <div class="card-content">
          <p class="card-label">已完成章节</p>
          <p class="card-value">{{ completedChapters }} / {{ totalChapters }}</p>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 章节完成度 -->
      <div class="chart-card">
        <h3 class="chart-title">章节完成度</h3>
        <div class="chart-wrapper">
          <v-chart
            class="chart"
            :option="chapterProgressOption"
            autoresize
          />
        </div>
      </div>

      <!-- 正确率趋势 -->
      <div class="chart-card">
        <h3 class="chart-title">正确率趋势</h3>
        <div class="chart-wrapper">
          <v-chart
            class="chart"
            :option="accuracyTrendOption"
            autoresize
          />
        </div>
      </div>

      <!-- 学习时间分布 -->
      <div class="chart-card">
        <h3 class="chart-title">学习时间分布</h3>
        <div class="chart-wrapper">
          <v-chart
            class="chart"
            :option="studyTimeOption"
            autoresize
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VChart, registerChartOption } from 'vue-echarts'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册 ECharts 组件
registerChartOption(PieChart, LineChart, BarChart)
registerChartOption(TitleComponent, TooltipComponent, LegendComponent, GridComponent)
registerChartOption(CanvasRenderer)

const router = useRouter()
const isLoaded = ref(false)

// 模拟数据
const mockData = {
  chapterProgress: [
    { name: '电磁场基础理论', value: 100, status: 'completed' },
    { name: '麦克斯韦方程组', value: 75, status: 'in_progress' },
    { name: '电磁波传播', value: 0, status: 'not_started' },
    { name: '波导与谐振腔', value: 45, status: 'in_progress' },
    { name: '天线原理', value: 0, status: 'not_started' }
  ],
  accuracyTrend: [
    { date: '03-05', accuracy: 65 },
    { date: '03-06', accuracy: 72 },
    { date: '03-07', accuracy: 68 },
    { date: '03-08', accuracy: 75 },
    { date: '03-09', accuracy: 82 },
    { date: '03-10', accuracy: 78 },
    { date: '03-11', accuracy: 85 }
  ],
  studyTimeDistribution: [
    { name: '电磁场基础理论', minutes: 120 },
    { name: '麦克斯韦方程组', minutes: 90 },
    { name: '电磁波传播', minutes: 15 },
    { name: '波导与谐振腔', minutes: 45 },
    { name: '天线原理', minutes: 0 }
  ]
}

// 计算统计数据
const totalStudyTime = Math.round(mockData.studyTimeDistribution.reduce((sum, item) => sum + item.minutes, 0) / 60 * 10) / 10
const averageAccuracy = Math.round(mockData.accuracyTrend.reduce((sum, item) => sum + item.accuracy, 0) / mockData.accuracyTrend.length)
const completedChapters = mockData.chapterProgress.filter(item => item.status === 'completed').length
const totalChapters = mockData.chapterProgress.length

// 章节完成度图表配置
const chapterProgressOption = ref({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}% ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    textStyle: {
      color: '#ffffff'
    }
  },
  series: [
    {
      name: '章节完成度',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '18',
          fontWeight: 'bold',
          color: '#ffffff'
        }
      },
      labelLine: {
        show: false
      },
      data: mockData.chapterProgress.map(item => {
        let color = '#6b7280' // 未开始
        if (item.status === 'completed') {
          color = '#10b981' // 已完成
        } else if (item.status === 'in_progress') {
          color = '#f59e0b' // 进行中
        }
        return {
          value: item.value,
          name: item.name,
          itemStyle: {
            color: color
          }
        }
      })
    }
  ]
})

// 正确率趋势图表配置
const accuracyTrendOption = ref({
  tooltip: {
    trigger: 'axis',
    formatter: '{b}: {c}%'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: mockData.accuracyTrend.map(item => item.date),
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.3)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.7)'
    }
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.3)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.7)',
      formatter: '{value}%'
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  },
  series: [
    {
      name: '正确率',
      type: 'line',
      stack: 'Total',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3,
        color: '#ef4444'
      },
      itemStyle: {
        color: '#ef4444'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(239, 68, 68, 0.5)'
          }, {
            offset: 1, color: 'rgba(239, 68, 68, 0.1)'
          }]
        }
      },
      data: mockData.accuracyTrend.map(item => item.accuracy)
    }
  ]
})

// 学习时间分布图表配置
const studyTimeOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: '{b}: {c} 分钟'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.3)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.7)'
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  },
  yAxis: {
    type: 'category',
    data: mockData.studyTimeDistribution.map(item => item.name),
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.3)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.7)'
    }
  },
  series: [
    {
      name: '学习时长',
      type: 'bar',
      barWidth: '60%',
      itemStyle: {
        color: '#ef4444',
        borderRadius: [0, 4, 4, 0]
      },
      data: mockData.studyTimeDistribution.map(item => item.minutes)
    }
  ]
})

// 返回按钮功能
const goBack = () => {
  router.back()
}

// 页面加载动画
onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true
  }, 300)
})
</script>

<style scoped>
.learning-progress-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 2rem;
  color: #ffffff;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.learning-progress-container.loaded {
  opacity: 1;
  transform: translateY(0);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.75rem 1.5rem;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(16px);
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.page-title {
  font-size: 1.75rem;
  font-weight: bold;
  color: #ffffff;
}

.placeholder {
  width: 120px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(16px);
  transition: all 0.3s ease;
}

.overview-card:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.card-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  color: #ef4444;
  font-size: 1.25rem;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.25rem;
}

.card-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.chart-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(16px);
  transition: all 0.3s ease;
}

.chart-card:hover {
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.chart-title {
  font-size: 1.125rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 1rem;
}

.chart-wrapper {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

@media (max-width: 768px) {
  .learning-progress-container {
    padding: 1rem;
  }
  
  .header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .placeholder {
    display: none;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .chart-wrapper {
    height: 250px;
  }
}
</style>