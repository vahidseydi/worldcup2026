<template>
  <div class="prob-bar-wrap">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  labels: { type: Array, required: true },
  actual: { type: Array, required: true },
  scenario: { type: Array, default: null },
})

const chartData = computed(() => {
  const datasets = [
    {
      label: 'Actual',
      data: props.actual.map(v => +(v * 100).toFixed(1)),
      backgroundColor: 'rgba(59, 130, 246, 0.7)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 1,
    },
  ]
  if (props.scenario) {
    datasets.push({
      label: 'Scenario',
      data: props.scenario.map(v => +(v * 100).toFixed(1)),
      backgroundColor: 'rgba(234, 179, 8, 0.7)',
      borderColor: 'rgba(234, 179, 8, 1)',
      borderWidth: 1,
    })
  }
  return { labels: props.labels, datasets }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      callbacks: {
        label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}%`,
      },
    },
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: { callback: v => `${v}%` },
    },
  },
}
</script>

<style scoped>
.prob-bar-wrap {
  position: relative;
  height: 220px;
}
</style>
