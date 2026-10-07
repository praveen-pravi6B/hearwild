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
  <div class="record-button-wrapper">
    <button
      class="record-button"
      :class="{ recording: isRecording }"
      :disabled="isRecording || isIdentifying"
      @click="$emit('record')"
    >
      <svg
        class="microphone-icon"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <rect
          x="8"
          y="2"
          width="8"
          height="13"
          rx="4"
        />

        <path
          d="M5 11a7 7 0 0 0 14 0"
        />

        <path
          d="M12 18v4"
        />

        <path
          d="M8 22h8"
        />
      </svg>

      <span v-if="isRecording">
        Listening...
      </span>

      <span v-else-if="isIdentifying">
        Identifying...
      </span>

      <span v-else>
        Record a bird
      </span>
    </button>
  </div>
</template>

<style scoped>
.record-button-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.record-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  border: 0;
  border-radius: 999px;

  padding: 16px 28px;

  background: #1d2a21;
  color: white;

  font-size: 15px;
  font-weight: 700;

  cursor: pointer;

  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}

.microphone-icon {
  width: 20px;
  height: 20px;

  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;

  flex-shrink: 0;
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
