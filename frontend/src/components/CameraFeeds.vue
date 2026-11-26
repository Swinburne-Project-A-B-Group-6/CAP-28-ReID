<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  session: { type: Object, required: true },
  selectedIds: { type: Set, required: true }
})
const emit = defineEmits(['frame'])

const { cameras, fps, tracks } = props.session
const videos = []
const frameCallbacks = []
const frameIndexes = ref(cameras.map(() => null))
const cameraSubjectIds = cameras.map(({ id }) => Object.keys(tracks[id]))

const visibleBoxes = computed(() => cameras.map((camera, index) => {
  const frame = frameIndexes.value[index]
  if (frame === null) return []

  const { width, height } = camera
  const cameraTracks = tracks[camera.id]
  const ids = props.selectedIds.size ? props.selectedIds : cameraSubjectIds[index]
  const boxes = []
  for (const id of ids) {
    const box = cameraTracks[id]?.[frame]
    if (!Array.isArray(box) || box.length !== 4) continue

    const [left, top, right, bottom] = box
    boxes.push({
      id,
      style: {
        left: `${left / width * 100}%`,
        top: `${top / height * 100}%`,
        width: `${(right - left) / width * 100}%`,
        height: `${(bottom - top) / height * 100}%`
      }
    })
  }
  return boxes
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
            v-for="box in visibleBoxes[index]"
            :key="box.id"
            class="box"
            :style="box.style"
            aria-hidden="true"
          >
            <span>ID {{ box.id }}</span>
          </div>
        </div>
      </figure>
  </section>
</template>
