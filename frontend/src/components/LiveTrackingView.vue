<script setup>
import { computed, ref } from 'vue'
import CameraFeeds from './CameraFeeds.vue'
import { eventLogs, identities } from '../data/mockReIdData.js'

const playbackTime = ref(0)
const selectedGlobalId = ref(null)
const searchQuery = ref('')
const eventDisplayLimit = 100

const eventLabels = ['New Person', 'Re-identified', 'Exited']

const availableEvents = computed(() =>
  eventLogs.filter((event) => event.time <= playbackTime.value)
)
const visibleEventLogs = computed(() => availableEvents.value.slice(-eventDisplayLimit))
const eventCounts = computed(() => eventLabels.map((label) => ({
  label,
  count: visibleEventLogs.value.filter((event) => event.status === label).length
})))

const activeSubjects = computed(() => identities.map((person) => ({
  globalId: person.globalId,
  cameras: [...new Set(person.history
    .filter((visit) => visit.start <= playbackTime.value && playbackTime.value < visit.end)
    .map((visit) => visit.cameraId))]
})).filter((person) => person.cameras.length))

const filteredSubjects = computed(() => {
  const query = searchQuery.value.trim()
  return query
    ? activeSubjects.value.filter((person) => person.globalId === Number(query))
    : activeSubjects.value
})

const selectedIdentity = computed(() =>
  identities.find((person) => person.globalId === selectedGlobalId.value) ??
  identities.find((person) => person.globalId === activeSubjects.value[0]?.globalId)
)
const visibleHistory = computed(() =>
  selectedIdentity.value?.history.filter((visit) => visit.start <= playbackTime.value) ?? []
)

function formatTime(time) {
  const minutes = Math.floor(time / 60)
  const seconds = (time % 60).toFixed(2).padStart(5, '0')
  return `${minutes}:${seconds}`
}
</script>

<template>
  <CameraFeeds @time="playbackTime = $event" />

  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
    <div class="lg:col-span-8 space-y-6">
      <dl class="grid gap-3 sm:grid-cols-3">
        <div
          v-for="{ label, count } in eventCounts"
          :key="label"
          class="rounded-lg border border-slate-200 bg-white px-4 py-3"
        >
          <dt class="text-sm font-medium text-slate-700">{{ label }}</dt>
          <dd class="mt-1 text-2xl font-semibold tabular-nums">{{ count }}</dd>
        </div>
      </dl>
      <section class="bg-white border border-slate-200/90 rounded-lg overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <h3 class="text-base font-semibold text-slate-900">
            Detection & Re-ID Events
          </h3>
          <span class="text-sm text-slate-700">
            Showing {{ visibleEventLogs.length }} of {{ availableEvents.length }} events
          </span>
        </div>

        <div class="max-h-96 overflow-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 bg-slate-50">
              <tr class="border-b border-slate-100 text-sm font-medium text-slate-700 uppercase tracking-wider">
                <th class="py-2.5 pl-5 pr-3 w-24">Time</th>
                <th class="py-2.5 px-3 w-24">Camera</th>
                <th class="py-2.5 px-3 w-32">Global ID</th>
                <th class="py-2.5 px-3">Event</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="log in visibleEventLogs" :key="log.id">
                <td class="py-3 pl-5 pr-3 font-mono text-slate-700 whitespace-nowrap align-top">
                  {{ formatTime(log.time) }}
                </td>
                <td class="py-3 px-3 whitespace-nowrap align-top">
                  <span class="text-slate-700 font-medium">{{ log.cameraId }}</span>
                </td>
                <td class="py-3 px-3 whitespace-nowrap align-top">
                  {{ log.globalId }}
                </td>
                <td class="py-3 px-3 text-slate-700 align-top">
                  {{ log.status }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
    <div class="lg:col-span-4 space-y-6">
      <section class="bg-white border border-slate-200/90 rounded-lg overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <h3 class="text-base font-semibold text-slate-900">
            Active Subjects
          </h3>
          <span class="text-sm font-mono text-slate-700">
            {{ activeSubjects.length }} tracked
          </span>
        </div>
        <div class="border-b border-slate-100 p-3">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by Global ID"
            class="w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm"
          />
        </div>
        <div class="divide-y divide-slate-100 max-h-[380px] overflow-y-auto">
          <button
            v-for="person in filteredSubjects"
            :key="person.globalId"
            type="button"
            @click="selectedGlobalId = person.globalId"
            class="block w-full cursor-pointer px-5 py-3.5 text-left transition-colors"
            :class="selectedGlobalId === person.globalId
              ? 'bg-blue-100'
              : 'hover:bg-slate-50'"
          >
            <span class="text-sm font-semibold">Global ID: {{ person.globalId }}</span>
            <span class="mt-1.5 block text-sm text-slate-700">
              {{ person.cameras.join(', ') }}
            </span>
          </button>
          <p v-if="!filteredSubjects.length" class="px-5 py-3.5 text-sm text-slate-700">
            {{ searchQuery.trim() ? 'No matching Global ID' : 'No active subjects' }}
          </p>
        </div>
      </section>
      <section v-if="selectedIdentity" class="bg-white border border-slate-200/90 rounded-lg p-5">
        <h4 class="border-b border-slate-100 pb-3.5 text-base font-semibold">
          Global ID: {{ selectedIdentity.globalId }} History
        </h4>

        <div class="mt-4 space-y-4">
          <p v-if="!visibleHistory.length" class="text-sm text-slate-700">No sightings yet</p>
          <div v-for="visit in visibleHistory" :key="visit.cameraId + ':' + visit.start">
            <p class="text-sm font-semibold">{{ visit.cameraId }}</p>
            <p class="text-sm text-slate-700">
              {{ formatTime(visit.start) }} - {{ visit.end > playbackTime ? 'Active' : formatTime(visit.end) }}
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
