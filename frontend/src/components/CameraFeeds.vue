<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  session: { type: Object, required: true },
  selectedId: { type: String, default: null }
})
const emit = defineEmits(['frame'])

const { cameras, fps, tracks } = props.session
const videos = []
const frameCallbacks = []
const frameIndexes = ref(cameras.map(() => null))

const selectedBoxes = computed(() => cameras.map((camera, index) => {
  const frame = frameIndexes.value[index]
  const box = tracks[camera.id][props.selectedId]?.[frame]
  if (!Array.isArray(box) || box.length !== 4) return null

  const { width, height } = camera
  const [left, top, right, bottom] = box
  return {
    left: `${left / width * 100}%`,
    top: `${top / height * 100}%`,
    width: `${(right - left) / width * 100}%`,
    height: `${(bottom - top) / height * 100}%`
  }
}))

onMounted(() => {
  videos.forEach((video, index) => {
    if (typeof video.requestVideoFrameCallback !== 'function') return

    function updateFrame(_now, { mediaTime }) {
      const frame = Math.round(mediaTime * fps)
      frameIndexes.value[index] = frame
      if (index === 0) emit('frame', frame)
      frameCallbacks[index] = video.requestVideoFrameCallback(updateFrame)
    }

    frameCallbacks[index] = video.requestVideoFrameCallback(updateFrame)
  })
})

onBeforeUnmount(() => {
  frameCallbacks.forEach((callback, index) => videos[index].cancelVideoFrameCallback(callback))
})

function handleTimeUpdate(event, index) {
  const video = event.currentTarget
  if (typeof video.requestVideoFrameCallback !== 'function') {
    frameIndexes.value[index] = Math.floor(video.currentTime * fps + 1e-6)
    if (index === 0) emit('frame', frameIndexes.value[index])
  }
  if (index === 0) synchronizePlayback(video.currentTime)
}

function synchronizePlayback(time) {
  for (const video of videos.slice(1)) {
    if (video?.readyState && Math.abs(video.currentTime - time) > 0.15) {
      video.currentTime = time
    }
  }
}
</script>

<template>
  <section aria-label="Camera feeds" class="cameras">
      <figure v-for="(camera, index) in cameras" :key="camera.id">
        <figcaption>{{ camera.id }}</figcaption>
        <div class="feed" :style="{ aspectRatio: camera.width + ' / ' + camera.height }">
          <video
            :ref="(video) => { videos[index] = video }"
            :src="camera.src"
            @loadeddata="handleTimeUpdate($event, index)"
            @timeupdate="handleTimeUpdate($event, index)"
            autoplay
            loop
            muted
            playsinline
          ></video>
          <div
            v-if="selectedBoxes[index]"
            class="box"
            :style="selectedBoxes[index]"
            aria-hidden="true"
          >
            <span>ID {{ selectedId }}</span>
          </div>
        </div>
      </figure>
  </section>
</template>
