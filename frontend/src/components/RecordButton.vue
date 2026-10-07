<script setup>
defineProps({
  isRecording: {
    type: Boolean,
    default: false
  },
  isIdentifying: {
    type: Boolean,
    default: false
  }
})

defineEmits(['record'])
</script>

<template>
  <button
    class="record-button"
    :class="{ recording: isRecording }"
    :disabled="isRecording || isIdentifying"
    @click="$emit('record')"
  >
    <span v-if="isRecording">
      🎙️ Listening...
    </span>

    <span v-else-if="isIdentifying">
      🧠 Identifying...
    </span>

    <span v-else>
      🎙️ Record a bird
    </span>
  </button>
</template>

<style scoped>
.record-button {
  border: 0;
  border-radius: 999px;
  padding: 18px 30px;
  background: #1d2a21;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.record-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.record-button:disabled {
  cursor: default;
  opacity: 0.8;
}

.record-button.recording {
  opacity: 0.8;
}
</style>
