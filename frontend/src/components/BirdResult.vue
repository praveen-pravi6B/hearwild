<script setup>
defineProps({
  result: {
    type: Object,
    default: null
  }
})
</script>

<template>
  <div v-if="result" class="result-card">
    <!-- No prediction -->
    <template v-if="!result.bird">
      <p class="result-icon">🌿</p>

      <p class="result-label">
        NOTHING CLEAR YET
      </p>

      <h2>We couldn't identify that sound.</h2>

      <p class="message">
        Try recording again somewhere quieter
        where you can hear birds clearly.
      </p>
    </template>

    <!-- Low confidence -->
    <template
      v-else-if="result.confidence < 0.40"
    >
      <p class="result-icon">🌿</p>

      <p class="result-label">
        NOT SURE
      </p>

      <h2>We heard something...</h2>

      <p class="possible-bird">
        The model's best guess was
        <strong>{{ result.bird }}</strong>.
      </p>

      <p class="scientific">
        {{ result.scientific_name }}
      </p>

      <p class="confidence">
        {{ (result.confidence * 100).toFixed(1) }}%
        confidence
      </p>

      <p class="message">
        That's not confident enough to call it.
      </p>
    </template>

    <!-- Possible identification -->
    <template
      v-else-if="result.confidence < 0.70"
    >
      <p class="result-icon">🤔</p>

      <p class="result-label">
        POSSIBLE
      </p>

      <h2>{{ result.bird }}</h2>

      <p class="scientific">
        {{ result.scientific_name }}
      </p>

      <p class="confidence">
        {{ (result.confidence * 100).toFixed(1) }}%
        confidence
      </p>

      <p class="message">
        This might be what you heard.
      </p>
    </template>

    <!-- Confident identification -->
    <template v-else>
      <p class="result-icon">🐦</p>

      <p class="result-label">
        YOU HEARD
      </p>

      <h2>{{ result.bird }}</h2>

      <p class="scientific">
        {{ result.scientific_name }}
      </p>

      <p class="confidence">
        {{ (result.confidence * 100).toFixed(1) }}%
        confidence
      </p>

      <p class="message">
        That's a confident identification.
      </p>
    </template>
  </div>
</template>

<style scoped>
.result-card {
  margin: 36px auto 0;
  padding: 32px;
  max-width: 420px;
  border-radius: 24px;
  background: #fffdf7;
  border: 1px solid #ddd8ca;
  text-align: center;
}

.result-icon {
  margin: 0 0 16px;
  font-size: 32px;
}

.result-label {
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: #59655c;
}

.result-card h2 {
  margin: 0;
  font-size: 36px;
  line-height: 1.1;
}

.scientific {
  margin: 10px 0 20px;
  font-style: italic;
  color: #59655c;
}

.confidence {
  margin: 0;
  font-weight: 700;
}

.possible-bird {
  margin: 16px 0 0;
  color: #59655c;
  line-height: 1.5;
}

.message {
  margin: 16px 0 0;
  color: #59655c;
  line-height: 1.5;
}
</style>
