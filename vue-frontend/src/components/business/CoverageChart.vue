<template>
  <div class="coverage-chart" ref="chartContainer">
    <div v-if="!hasData" class="empty-state">
      <el-empty description="暂无覆盖率数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  covered: {
    type: Number,
    default: 0
  },
  total: {
    type: Number,
    default: 0
  },
  uncoveredList: {
    type: Array,
    default: () => []
  },
  chartType: {
    type: String,
    default: 'pie',
    validator: (value) => ['pie', 'bar', 'ring'].includes(value)
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  height: {
    type: String,
    default: '300px'
  }
})

const emit = defineEmits(['click-item'])

const chartContainer = ref(null)
let chart = null

const hasData = computed(() => props.total > 0)

const coverageRate = computed(() => {
  if (props.total === 0) return 0
  return ((props.covered / props.total) * 100).toFixed(1)
})

const initChart = () => {
  if (!chartContainer.value || !hasData.value) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(chartContainer.value)

  const option = getChartOption()

  chart.setOption(option)

  chart.on('click', (params) => {
    emit('click-item', params)
  })
}

const getChartOption = () => {
  const uncovered = props.total - props.covered

  if (props.chartType === 'pie') {
    return {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: props.showLegend ? {
        orient: 'vertical',
        left: 'left'
      } : undefined,
      series: [
        {
          name: '需求覆盖',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}\n({d}%)'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
          data: [
            { value: props.covered, name: '已覆盖', itemStyle: { color: '#67C23A' } },
            { value: uncovered, name: '未覆盖', itemStyle: { color: '#F56C6C' } }
          ]
        }
      ]
    }
  }

  if (props.chartType === 'bar') {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['已覆盖', '未覆盖']
      },
      yAxis: {
        type: 'value',
        max: props.total
      },
      series: [
        {
          name: '需求数量',
          type: 'bar',
          barWidth: '50%',
          data: [
            { value: props.covered, itemStyle: { color: '#67C23A' } },
            { value: uncovered, itemStyle: { color: '#F56C6C' } }
          ],
          label: {
            show: true,
            position: 'top'
          }
        }
      ]
    }
  }

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: props.showLegend ? {
      orient: 'vertical',
      left: 'left'
    } : undefined,
    series: [
      {
        name: '需求覆盖',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 5,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: props.covered, name: '已覆盖', itemStyle: { color: '#67C23A' } },
          { value: uncovered, name: '未覆盖', itemStyle: { color: '#F56C6C' } }
        ]
      }
    ]
  }
}

const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

watch([() => props.covered, () => props.total], () => {
  if (chart) {
    chart.setOption(getChartOption())
  }
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.coverage-chart {
  width: 100%;
  min-height: 200px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}
</style>