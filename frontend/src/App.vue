<script setup>
import { ref } from 'vue'

import BrandHeader from './components/BrandHeader.vue'
import RecordButton from './components/RecordButton.vue'
import RecordingStatus from './components/RecordingStatus.vue'
import BirdResult from './components/BirdResult.vue'

import { identifyBird } from './services/birdApi'

const isRecording = ref(false)
const isIdentifying = ref(false)
const result = ref(null)
const errorMessage = ref('')

let mediaRecorder = null
let audioChunks = []

async function startRecording() {
  errorMessage.value = ''
  result.value = null

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
      stream.getTracks().forEach((track) => track.stop())

      const audioBlob = new Blob(audioChunks, {
        type: mediaRecorder.mimeType
      })

      console.log('Recording complete')
      console.log('Audio type:', audioBlob.type)
      console.log('Audio size:', audioBlob.size, 'bytes')

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
  }
}

async function processRecording(audioBlob) {
  try {
    isIdentifying.value = true

    result.value = await identifyBird(audioBlob)

    console.log('BirdNET result:', result.value)
  } catch (error) {
    console.error(error)

    errorMessage.value =
      'Unable to identify the recording. Please try again.'
  } finally {
    isIdentifying.value = false
  }
}
</script>

<template>
  <main class="app">
    <section class="hero">
      <BrandHeader />

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

      <BirdResult :result="result" />
    </section>
  </main>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.hero {
  width: 100%;
  max-width: 680px;
}
</style>
