<template>
  <RouterView />
  <HelpModal />
</template>

<script setup>
import { RouterView } from 'vue-router'
import HelpModal from '@/components/HelpModal.vue'
</script>
