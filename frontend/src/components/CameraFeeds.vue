<script setup>
import cam01 from '../assets/demo-videos/cam-01.mp4'
import cam02 from '../assets/demo-videos/cam-02.mp4'
import cam03 from '../assets/demo-videos/cam-03.mp4'

const cameras = [
  { id: 'CAM-01', src: cam01 },
  { id: 'CAM-02', src: cam02 },
  { id: 'CAM-03', src: cam03 }
]
</script>

<template>
  <section class="mb-6 overflow-hidden rounded-lg border border-slate-200/90 bg-white">
    <div class="border-b border-slate-100 px-4 py-3">
      <h2 class="text-base font-semibold text-slate-900">Camera Feeds</h2>
    </div>

    <div class="grid gap-3 p-3 md:grid-cols-3">
      <figure v-for="camera in cameras" :key="camera.id" class="min-w-0">
        <figcaption class="mb-2 text-sm font-medium text-slate-900">{{ camera.id }}</figcaption>
        <video
          :src="camera.src"
          autoplay
          loop
          muted
          class="block aspect-[5/4] w-full rounded bg-black object-contain"
        ></video>
      </figure>
    </div>
  </section>
</template>
