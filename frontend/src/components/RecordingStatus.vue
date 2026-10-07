<script setup>
defineProps({
  isRecording: {
    type: Boolean,
    default: false
  },
  isIdentifying: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="status-container">
    <p v-if="isRecording" class="status">
      Listen for 6 seconds...
    </p>

    <p v-if="isIdentifying" class="status">
      BirdNET is identifying the sound...
    </p>

    <p v-if="errorMessage" class="status error">
      {{ errorMessage }}
    </p>
  </div>
</template>

<style scoped>
.status-container {
  min-height: 44px;
}

.status {
  margin-top: 20px;
  color: #59655c;
  font-size: 14px;
}

.error {
  color: #a33a3a;
}
</style>
