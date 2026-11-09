<script setup>
import { ref, computed } from 'vue'
import CameraFeeds from './CameraFeeds.vue'
import { eventLogs, identities } from '../data/mockReIdData.js'

const eventDisplayLimit = 100
const visibleEventLogs = eventLogs.slice(0, eventDisplayLimit)

const eventLabels = {
  NEW_PERSON: 'New Person',
  RE_IDENTIFIED: 'Re-identified',
  LOW_CONFIDENCE: 'Low Confidence',
  EXITED: 'Exited'
}

const eventCounts = Object.entries(eventLabels).map(([type, label]) => ({
  label,
  count: visibleEventLogs.filter((event) => event.eventType === type).length
}))

const selectedGlobalId = ref(identities[0]?.globalId)
const searchQuery = ref('')

const filteredIdentities = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return identities

  const id = Number(query)
  return identities.filter((person) =>
    person.globalId === id ||
    person.history.some((step) => step.localId === id) ||
    person.attributes.some((attribute) => attribute.toLowerCase().includes(query))
  )
})

const selectedIdentity = computed(() => findIdentity(selectedGlobalId.value) ?? identities[0])

function trackLabel(localId, globalId) {
  return `Local ID: ${localId} - Global ID: ${globalId ?? 'Pending'}`
}

function findIdentity(globalId) {
  return identities.find((person) => person.globalId === globalId)
}
</script>

<template>
  <CameraFeeds />

  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
    <div class="lg:col-span-8 space-y-6">
      <dl class="grid grid-cols-2 gap-3 sm:grid-cols-4">
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
            Showing {{ visibleEventLogs.length }} of {{ eventLogs.length }} events
          </span>
        </div>

        <div class="max-h-96 overflow-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 bg-slate-50">
              <tr class="border-b border-slate-100 text-sm font-medium text-slate-700 uppercase tracking-wider">
                <th class="py-2.5 pl-5 pr-3 w-24">Time</th>
                <th class="py-2.5 px-3 w-24">Camera</th>
                <th class="py-2.5 px-3 w-32">Subject</th>
                <th class="py-2.5 px-3">Event</th>
                <th class="py-2.5 px-3">Appearance Attributes</th>
                <th class="py-2.5 pl-3 pr-5 text-right w-24">Similarity</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="log in visibleEventLogs" :key="log.id">
                <td class="py-3 pl-5 pr-3 font-mono text-slate-700 whitespace-nowrap align-top">
                  {{ log.timestamp }}
                </td>
                <td class="py-3 px-3 whitespace-nowrap align-top">
                  <span class="text-slate-700 font-medium">{{ log.camera }}</span>
                </td>
                <td class="py-3 px-3 whitespace-nowrap align-top">
                  {{ trackLabel(log.localId, log.globalId) }}
                </td>
                <td class="py-3 px-3 text-slate-700 align-top">
                  {{ eventLabels[log.eventType] ?? log.eventType }}
                </td>
                <td class="py-3 px-3 align-top">
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="attr in log.attributes ?? findIdentity(log.globalId)?.attributes ?? []"
                      :key="attr"
                      class="px-2 py-0.5 rounded bg-slate-100 text-slate-700"
                    >
                      {{ attr }}
                    </span>
                  </div>
                </td>
                <td class="py-3 pl-3 pr-5 text-right font-mono font-medium text-slate-900 whitespace-nowrap align-top">
                  {{ log.confidence == null ? '—' : log.confidence + '%' }}
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
            {{ filteredIdentities.length }} tracked
          </span>
        </div>
        <div class="border-b border-slate-100 p-3">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by ID or Appearance Attributes"
            class="w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm"
          />
        </div>
        <div class="divide-y divide-slate-100 max-h-[380px] overflow-y-auto">
          <div
            v-for="person in filteredIdentities"
            :key="person.globalId"
            @click="selectedGlobalId = person.globalId"
            class="cursor-pointer px-5 py-3.5 transition-colors"
            :class="selectedGlobalId === person.globalId
              ? 'bg-blue-100'
              : 'hover:bg-slate-50'"
          >
            <div class="flex flex-wrap items-center justify-between gap-x-2 text-sm">
              <span class="font-semibold">{{ trackLabel(person.history.at(-1).localId, person.globalId) }}</span>
              <span class="text-slate-700">{{ person.history.at(-1).cameraId }}</span>
            </div>

            <p class="mt-1.5 text-sm text-slate-700 leading-relaxed">
              {{ person.attributes.join(', ') }}
            </p>
          </div>
        </div>
      </section>
      <section v-if="selectedIdentity" class="bg-white border border-slate-200/90 rounded-lg p-5">
        <h4 class="border-b border-slate-100 pb-3.5 text-base font-semibold">
          Global ID: {{ selectedIdentity.globalId }} History
        </h4>

        <div class="mt-4 space-y-4">
          <div
            v-for="(step, i) in selectedIdentity.history"
            :key="i"
          >
            <div class="flex flex-wrap justify-between gap-x-2 text-sm">
              <span class="font-semibold">{{ trackLabel(step.localId, selectedIdentity.globalId) }}</span>
              <span class="text-slate-700">{{ step.cameraId }}</span>
            </div>
            <p class="text-sm text-slate-700">{{ step.enterTime }} - {{ step.exitTime ?? 'Active' }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
