<script setup>
import { computed, ref, shallowRef, watch } from 'vue'
import CameraFeeds from './components/CameraFeeds.vue'

const videoExtension = /\.(avi|mp4|mov|mkv|webm|m4v|mpg|mpeg|wmv|mts|m2ts)$/i

const session = shallowRef(null)
const sessionVersion = ref(0)
const frame = ref(0)
const selectedId = ref(null)
const subjectSlots = shallowRef([])
const loading = ref(false)
const error = ref('')

const activeSubjects = computed((previous) => {
  const subjects = new Map()
  if (!session.value) return subjects

  const { cameras, fps, tracks } = session.value
  const lastFrame = frame.value
  const firstFrame = Math.max(0, lastFrame - Math.round(fps / 2))
  for (const { id } of cameras) {
    for (const [globalId, boxes] of Object.entries(tracks[id])) {
      for (let index = lastFrame; index >= firstFrame; index--) {
        if (!boxes[index]) continue
        const earlier = subjects.get(globalId)
        subjects.set(globalId, earlier ? `${earlier}, ${id}` : id)
        break
      }
    }
  }

  if (previous?.size === subjects.size &&
      [...subjects].every(([id, cameras]) => previous.get(id) === cameras)) return previous
  return subjects
})

watch([session, activeSubjects], ([, subjects]) => {
  const remaining = new Set([...subjects.keys()].sort((a, b) => Number(a) - Number(b)))
  const previous = subjectSlots.value
  const slots = previous.map((id) => remaining.delete(id) ? id : null)
  for (const id of remaining) {
    const vacant = slots.indexOf(null)
    if (vacant === -1) slots.push(id)
    else slots[vacant] = id
  }
  while (slots.at(-1) === null) slots.pop()
  while (slots[0] === null && slots[1] === null) slots.shift()
  if (slots.length !== previous.length || slots.some((id, index) => id !== previous[index])) {
    subjectSlots.value = slots
  }
})

async function openSession(event) {
  const files = [...event.target.files]
  event.target.value = ''
  if (!files.length) return

  error.value = ''
  const videos = files.filter(({ name }) => videoExtension.test(name))
    .sort((a, b) => a.webkitRelativePath.localeCompare(b.webkitRelativePath, undefined, { numeric: true }))
  if (videos.length < 2) {
    error.value = 'Choose a folder with at least two synchronized videos.'
    return
  }

  loading.value = true
  try {
    const metadata = videos.map(({ name, size }) => ({ size, extension: name.split('.').at(-1).toLowerCase() }))
    const response = await fetch('/api/reid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/octet-stream', 'X-ReID-Videos': JSON.stringify(metadata) },
      body: new Blob(videos)
    })
    if (!response.headers.get('content-type')?.includes('application/json')) {
      throw new Error('Run the local dashboard server to process videos.')
    }
    const result = await response.json()
    if (!response.ok) throw new Error(result.error)
    subjectSlots.value = []
    session.value = result
    sessionVersion.value++
    frame.value = 0
    selectedId.value = null
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main>
    <header>
      <h1>CAP-28 Multi-Camera Re-ID</h1>
      <label class="file-picker">
        {{ loading ? 'Processing…' : 'Open video folder' }}
        <input type="file" webkitdirectory :disabled="loading" @change="openSession" />
      </label>
    </header>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="loading" role="status">Running Re-ID. This can take a few minutes.</p>
    <p v-else-if="!session && !error">Choose a folder containing synchronized camera videos.</p>

    <template v-if="session">
      <CameraFeeds
        :key="sessionVersion"
        :session="session"
        :selected-id="selectedId"
        @frame="frame = $event"
      />
      <section aria-labelledby="active-subjects">
        <header>
          <h2 id="active-subjects">Active Subjects</h2>
          <button type="button" :disabled="!selectedId" @click="selectedId = null">Clear selection</button>
        </header>
        <div class="subjects">
          <p v-if="!activeSubjects.size" class="subjects-empty">No active subjects</p>
          <div v-for="(id, index) in subjectSlots" :key="index" class="subject-slot">
            <button
              v-if="id !== null"
              :key="id"
              type="button"
              :aria-pressed="selectedId === id"
              @click="selectedId = id"
            >
              <strong>Global ID {{ id }}</strong>
              <small>{{ activeSubjects.get(id) }}</small>
            </button>
          </div>
        </div>
      </section>
    </template>
  </main>
</template>
