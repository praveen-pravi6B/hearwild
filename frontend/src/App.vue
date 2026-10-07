<script setup>
import { ref } from 'vue'

import BrandHeader from './components/BrandHeader.vue'
import RecordButton from './components/RecordButton.vue'
import RecordingStatus from './components/RecordingStatus.vue'
import BirdResult from './components/BirdResult.vue'
import FlockView from './views/FlockView.vue'

import { identifyBird } from './services/birdApi'

const currentView = ref('discover')

const isRecording = ref(false)
const isIdentifying = ref(false)

const result = ref(null)
const errorMessage = ref('')

const showReward = ref(false)
const keepExploring = ref(false)

let mediaRecorder = null
let audioChunks = []
let transitionTimer = null

function clearTransitionTimer() {
  if (transitionTimer) {
    clearTimeout(transitionTimer)
    transitionTimer = null
  }
}

async function startRecording() {
  errorMessage.value = ''
  result.value = null
  showReward.value = false
  keepExploring.value = false

  clearTransitionTimer()

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true
    })

    audioChunks = []

    mediaRecorder = new MediaRecorder(stream)

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((track) => {
        track.stop()
      })

      const audioBlob = new Blob(audioChunks, {
        type: mediaRecorder.mimeType
      })

      await processRecording(audioBlob)
    }

    mediaRecorder.start()

    isRecording.value = true

    setTimeout(() => {
      if (
        mediaRecorder &&
        mediaRecorder.state === 'recording'
      ) {
        mediaRecorder.stop()

        isRecording.value = false
        isIdentifying.value = true
      }
    }, 6000)

  } catch (error) {
    console.error(error)

    errorMessage.value =
      'Microphone access is required to identify birds.'

    isRecording.value = false
    isIdentifying.value = false
  }
}

async function processRecording(audioBlob) {
  try {
    isIdentifying.value = true

    const identification = await identifyBird(audioBlob)

    result.value = identification

    const confidence =
      identification?.confidence ?? 0

    /*
     * ==========================================
     * CONFIDENT IDENTIFICATION
     * >= 70%
     * ==========================================
     *
     * Bird is added to the flock.
     * XP is awarded by the backend.
     *
     * Show reward for 6 seconds.
     * Then move to KEEP EXPLORING.
     */
    if (
      confidence >= 0.70 &&
      identification?.flock?.added === true
    ) {
      showReward.value = true
      keepExploring.value = false

      transitionTimer = setTimeout(() => {
        showReward.value = false
        keepExploring.value = true
        transitionTimer = null
      }, 6000)

      return
    }

    /*
     * ==========================================
     * VERY LOW CONFIDENCE
     * < 20%
     * ==========================================
     *
     * Don't add to flock.
     * Don't award XP.
     *
     * Show the result briefly, then return
     * directly to the normal Discover screen.
     */
    if (confidence < 0.20) {
      showReward.value = false
      keepExploring.value = false

      transitionTimer = setTimeout(() => {
        result.value = null
        showReward.value = false
        keepExploring.value = false
        transitionTimer = null
      }, 6000)

      return
    }

    /*
     * ==========================================
     * POSSIBLE IDENTIFICATION
     * 20% - 69%
     * ==========================================
     *
     * Don't add to flock.
     * Don't award XP.
     *
     * Show the result for 6 seconds,
     * then continue exploring.
     */
    showReward.value = false
    keepExploring.value = false

    transitionTimer = setTimeout(() => {
      result.value = null
      showReward.value = false
      keepExploring.value = true
      transitionTimer = null
    }, 6000)

  } catch (error) {
    console.error(error)

    errorMessage.value =
      'Unable to identify the recording. Please try again.'

  } finally {
    isIdentifying.value = false
  }
}

function goExplore() {
  clearTransitionTimer()

  result.value = null
  showReward.value = false
  keepExploring.value = false
  errorMessage.value = ''
}

function viewFlock() {
  clearTransitionTimer()

  result.value = null
  showReward.value = false
  keepExploring.value = false

  currentView.value = 'flock'
}

function backToDiscover() {
  clearTransitionTimer()

  currentView.value = 'discover'

  result.value = null
  showReward.value = false
  keepExploring.value = false
  errorMessage.value = ''
}
</script>

<template>
  <!-- ========================================
       MY FLOCK
  ========================================= -->
  <FlockView
    v-if="currentView === 'flock'"
    @back="backToDiscover"
  />

  <!-- ========================================
       DISCOVER
  ========================================= -->
  <main
    v-else
    class="app"
  >
    <section class="hero">

      <BrandHeader />

      <!-- ======================================
           DEFAULT DISCOVER / RECORDING / RESULT
      ======================================= -->
      <template
        v-if="!showReward && !keepExploring"
      >
        <RecordButton
          :is-recording="isRecording"
          :is-identifying="isIdentifying"
          @record="startRecording"
        />

        <RecordingStatus
          :is-recording="isRecording"
          :is-identifying="isIdentifying"
          :error-message="errorMessage"
        />

        <BirdResult
          :result="result"
          :show-reward="false"
        />

        <!-- View flock from the default screen -->
        <button
          v-if="
            !isRecording &&
            !isIdentifying &&
            !result
          "
          class="default-flock-button"
          type="button"
          @click="viewFlock"
        >
          View my flock
        </button>
      </template>

      <!-- ======================================
           REWARD
      ======================================= -->
      <template v-if="showReward">
        <BirdResult
          :result="result"
          :show-reward="true"
        />
      </template>

      <!-- ======================================
           KEEP EXPLORING
      ======================================= -->
      <section
        v-if="keepExploring"
        class="explore-card"
      >
        <p class="explore-icon">
          🌿
        </p>

        <p class="explore-label">
          KEEP EXPLORING
        </p>

        <h2>
          Listen for another bird
          to help your flock grow.
        </h2>

        <div class="actions">
          <button
            class="primary"
            type="button"
            @click="goExplore"
          >
            Go explore
          </button>

          <button
            class="secondary"
            type="button"
            @click="viewFlock"
          >
            View my flock
          </button>
        </div>
      </section>

    </section>
  </main>
</template>

<style scoped>
.app {
  width: 100%;
  min-height: 100vh;

  display: flex;
  align-items: center;
  justify-content: center;

  padding: 24px;

  background: #f4f1e8;
}

.hero {
  width: 100%;
  max-width: 680px;
}

/* ==========================================
   DEFAULT VIEW
========================================== */

.default-flock-button {
  display: block;

  margin: 18px auto 0;

  border: 1px solid #1d2a21;
  border-radius: 999px;

  padding: 13px 24px;

  background: transparent;
  color: #1d2a21;

  font-size: 14px;
  font-weight: 700;

  cursor: pointer;

  transition:
    transform 0.2s ease,
    background 0.2s ease,
    color 0.2s ease;
}

.default-flock-button:hover {
  transform: translateY(-2px);

  background: #1d2a21;
  color: white;
}

/* ==========================================
   KEEP EXPLORING
========================================== */

.explore-card {
  width: 100%;
  max-width: 500px;

  margin: 36px auto 0;
  padding: 40px 32px;

  border: 1px solid #ddd8ca;
  border-radius: 24px;

  background: #fffdf7;

  text-align: center;
}

.explore-icon {
  margin: 0 0 16px;

  font-size: 36px;
}

.explore-label {
  margin: 0 0 16px;

  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.15em;

  color: #59655c;
}

.explore-card h2 {
  max-width: 400px;

  margin: 0 auto;

  font-size: 28px;
  line-height: 1.25;
}

.actions {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;

  gap: 12px;

  margin-top: 32px;
}

.actions button {
  border-radius: 999px;

  padding: 14px 22px;

  font-size: 14px;
  font-weight: 700;

  cursor: pointer;

  transition:
    transform 0.2s ease,
    background 0.2s ease;
}

.primary {
  border: 0;

  background: #1d2a21;
  color: white;
}

.primary:hover {
  transform: translateY(-2px);
}

.secondary {
  border: 1px solid #1d2a21;

  background: transparent;
  color: #1d2a21;
}

.secondary:hover {
  transform: translateY(-2px);

  background: #1d2a21;
  color: white;
}

/* ==========================================
   MOBILE
========================================== */

@media (max-width: 600px) {
  .app {
    padding: 20px 16px;
  }

  .explore-card {
    padding: 32px 24px;
  }

  .explore-card h2 {
    font-size: 24px;
  }

  .actions {
    flex-direction: column;
  }

  .actions button {
    width: 100%;
  }
}
</style>
