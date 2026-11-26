<script setup>
import { computed } from 'vue'

const props = defineProps({
  session: { type: Object, required: true },
  frame: { type: Number, required: true },
  graceFrames: { type: Number, required: true }
})

const statuses = ['New Person', 'Re-identified', 'Exited']
const eventLimit = 100

const events = computed(() => {
  const { cameras, tracks } = props.session
  const timeline = []
  for (const { id: cameraId, frameCount } of cameras) {
    for (const [id, boxes] of Object.entries(tracks[cameraId])) {
      const frames = Object.keys(boxes).map(Number).sort((a, b) => a - b)
      if (!frames.length) continue

      timeline.push({ cameraId, id, frame: frames[0] })
      for (let index = 0; index < frames.length; index++) {
        const exitFrame = frames[index] + props.graceFrames + 1
        const nextFrame = frames[index + 1] ?? frameCount
        if (exitFrame < nextFrame) {
          timeline.push({ cameraId, id, frame: exitFrame, status: 'Exited' })
        }
      }
    }
  }

  const seenIds = new Set()
  return timeline.sort((a, b) => a.frame - b.frame).map((event) => {
    if (event.status) return event

    const status = seenIds.has(event.id) ? 'Re-identified' : 'New Person'
    seenIds.add(event.id)
    return { ...event, status }
  })
})

const availableEvents = computed(() => events.value.filter((event) => event.frame <= props.frame))
const visibleEvents = computed(() => availableEvents.value.slice(-eventLimit))
const eventCounts = computed(() => statuses.map((status) => ({
  status,
  count: visibleEvents.value.filter((event) => event.status === status).length
})))

function formatTime(frame) {
  const hundredths = Math.round(frame * 100 / props.session.fps)
  const minutes = Math.floor(hundredths / 6000)
  const seconds = ((hundredths % 6000) / 100).toFixed(2).padStart(5, '0')
  return `${minutes}:${seconds}`
}
</script>

<template>
  <section aria-labelledby="tracking-events">
    <header>
      <h2 id="tracking-events">Detection &amp; Re-ID Events</h2>
      <small>Showing {{ visibleEvents.length }} of {{ availableEvents.length }} events</small>
    </header>

    <dl class="event-counts">
      <div v-for="{ status, count } in eventCounts" :key="status">
        <dt>{{ status }}</dt>
        <dd>{{ count }}</dd>
      </div>
    </dl>

    <div class="event-table">
      <table>
        <thead>
          <tr>
            <th scope="col">Time</th>
            <th scope="col">Camera</th>
            <th scope="col">ID</th>
            <th scope="col">Event</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!visibleEvents.length">
            <td colspan="4">No events yet</td>
          </tr>
          <tr v-for="event in visibleEvents" :key="event.cameraId + ':' + event.id + ':' + event.frame">
            <td>{{ formatTime(event.frame) }}</td>
            <td>{{ event.cameraId }}</td>
            <td>{{ event.id }}</td>
            <td>{{ event.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.event-counts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 8rem), 1fr));
  gap: 0.75rem;
}
.event-counts > div { padding: 0.625rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; }
.event-counts dt, header small { color: #475569; }
.event-counts dd { margin: 0.25rem 0 0; font-size: 1.25rem; font-weight: 600; }
.event-table { max-height: 24rem; overflow: auto; }
table { width: 100%; border-spacing: 0; text-align: left; font-size: 0.875rem; }
th, td { padding: 0.625rem 0.75rem; border-bottom: 1px solid #e2e8f0; }
th { position: sticky; top: 0; background: #f8fafc; }
td:first-child { font-variant-numeric: tabular-nums; }
</style>
