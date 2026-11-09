<script setup>
import LiveTrackingView from './components/LiveTrackingView.vue'
</script>

<template>
  <div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col font-sans">
    <header class="bg-white border-b border-slate-200/80 sticky top-0 z-30">
      <div class="max-w-[1440px] mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-2.5 text-sm">
          <div class="h-2.5 w-2.5 bg-blue-600"></div>
          <span class="font-semibold tracking-tight">CAP-28 Vision</span>
          <span class="text-slate-700">/</span>
          <span class="text-slate-700">Multi-Camera Re-ID</span>
        </div>

        <span class="text-sm text-slate-700">3 Cameras</span>
      </div>
    </header>
    <main class="flex-1 max-w-[1440px] w-full mx-auto px-6 py-6">
      <LiveTrackingView />
    </main>
  </div>
</template>
