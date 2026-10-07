<script setup>
import { onMounted, ref } from 'vue'

const emit = defineEmits(['back'])

const API_URL = 'http://127.0.0.1:8000'

const flock = ref(null)
const errorMessage = ref('')

async function loadFlock() {
  try {
    const response = await fetch(`${API_URL}/flock`)

    if (!response.ok) {
      throw new Error('Failed to load flock')
    }

    flock.value = await response.json()
  } catch (error) {
    console.error(error)
    errorMessage.value =
      'Unable to load your flock right now.'
  }
}

function birdLevel(xp) {
  return Math.floor(xp / 100) + 1
}

function goBack() {
  emit('back')
}

onMounted(loadFlock)
</script>

<template>
  <main class="flock-page">
    <header class="flock-header">
      <p class="eyebrow">HEARWILD</p>

      <h1>My Flock</h1>

      <p class="subtitle">
        Every bird you discover becomes part of your journey.
      </p>
    </header>

    <p v-if="errorMessage" class="error">
      {{ errorMessage }}
    </p>

    <template v-if="flock">

      <!-- Compact flock summary -->
      <section class="stats">
        <div class="stat">
          <span class="stat-value">
            {{ flock.total_birds }}
          </span>

          <span class="stat-label">
            Birds discovered
          </span>
        </div>

        <div class="stat">
          <span class="stat-value">
            ⭐ {{ flock.total_xp }}
          </span>

          <span class="stat-label">
            Total XP
          </span>
        </div>

        <div class="stat">
          <span class="stat-value">
            Level {{ flock.level }}
          </span>

          <span class="stat-label">
            Flock level
          </span>
        </div>
      </section>

      <!-- Birds -->
      <section
        v-if="flock.birds.length > 0"
        class="birds"
      >
        <article
          v-for="bird in flock.birds"
          :key="bird.id"
          class="bird-card"
        >
          <div class="bird-icon">
            <img
              v-if="bird.image_url"
              :src="bird.image_url"
              :alt="bird.common_name"
              class="bird-image"
              loading="lazy"
            />

            <span v-else>
              🐦
            </span>
          </div>

          <div class="bird-info">
            <p class="bird-name">
              {{ bird.common_name }}
            </p>

            <p class="scientific">
              {{ bird.scientific_name }}
            </p>

            <p
              v-if="bird.description"
              class="description"
            >
              {{ bird.description }}
            </p>

            <div class="bird-stats">
              <span>Level {{ birdLevel(bird.xp) }}</span>
              <span>·</span>
              <span>⭐ {{ bird.xp }} XP</span>
              <span>·</span>
              <span>Heard {{ bird.times_identified }}×</span>
            </div>
          </div>
        </article>
      </section>

      <!-- Empty state -->
      <section
        v-else
        class="empty"
      >
        <p class="empty-icon">🌿</p>

        <h2>Your flock is waiting.</h2>

        <p>
          Go outside and listen for your first bird.
        </p>
      </section>

      <button
        class="back-button"
        @click="goBack"
      >
        ← Back to exploring
      </button>
    </template>
  </main>
</template>

<style scoped>
.flock-page {
  width: 100%;
  min-height: 100vh;
  padding: 48px 24px;
  background: #f4f1e8;
}

.flock-header {
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
}

.eyebrow {
  margin: 0 0 20px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.2em;
}

h1 {
  margin: 0;
  font-size: clamp(42px, 8vw, 64px);
  line-height: 1;
  letter-spacing: -0.05em;
}

.subtitle {
  max-width: 480px;
  margin: 20px auto 32px;
  color: #59655c;
  line-height: 1.6;
}


/* --------------------------------
   Compact flock summary
-------------------------------- */

.stats {
  width: 100%;
  max-width: 760px;
  margin: 0 auto 28px;

  display: grid;
  grid-template-columns: repeat(3, 1fr);

  border: 1px solid #ddd8ca;
  border-radius: 20px;
  background: #fffdf7;

  overflow: hidden;
}

.stat {
  padding: 18px 12px;
  text-align: center;
}

.stat + .stat {
  border-left: 1px solid #ddd8ca;
}

.stat-value {
  display: block;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.2;
}

.stat-label {
  display: block;
  margin-top: 5px;
  color: #59655c;
  font-size: 12px;
}


/* --------------------------------
   Birds
-------------------------------- */

.birds {
  width: 100%;
  max-width: 760px;
  margin: 0 auto;

  display: grid;
  gap: 12px;
}

.bird-card {
  display: flex;
  gap: 20px;
  align-items: center;

  padding: 24px;

  border: 1px solid #ddd8ca;
  border-radius: 20px;

  background: #fffdf7;
}

.bird-icon {
  width: 96px;
  height: 96px;
  flex: 0 0 96px;

  overflow: hidden;
  border-radius: 18px;

  background: #f0eee4;

  display: grid;
  place-items: center;

  font-size: 30px;
}

.bird-image {
  width: 100%;
  height: 100%;

  display: block;

  object-fit: cover;
}

.bird-info {
  min-width: 0;
}

.bird-name {
  margin: 0;

  font-size: 22px;
  font-weight: 800;
}

.scientific {
  margin: 5px 0 8px;

  color: #59655c;
  font-style: italic;
}

.description {
  max-width: 520px;
  margin: 0 0 14px;

  color: #59655c;
  font-size: 14px;
  line-height: 1.5;
}

.bird-stats {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;

  color: #59655c;
  font-size: 13px;
  font-weight: 700;
}


/* --------------------------------
   Empty state
-------------------------------- */

.empty {
  max-width: 500px;

  margin: 40px auto;
  padding: 60px 24px;

  text-align: center;
}

.empty-icon {
  font-size: 40px;
}

.empty h2 {
  margin-bottom: 8px;
}

.empty p:last-child {
  color: #59655c;
}


/* --------------------------------
   Error
-------------------------------- */

.error {
  margin: 24px auto;

  text-align: center;

  color: #a33a3a;
}


/* --------------------------------
   Back button
-------------------------------- */

.back-button {
  display: block;

  margin: 28px auto 0;

  border: 1px solid #1d2a21;
  border-radius: 999px;

  padding: 14px 22px;

  background: transparent;
  color: #1d2a21;

  font-weight: 700;

  cursor: pointer;
}


/* --------------------------------
   Mobile
-------------------------------- */

@media (max-width: 600px) {
  .flock-page {
    padding: 36px 16px;
  }

  .stats {
    margin-bottom: 20px;
  }

  .stat {
    padding: 16px 6px;
  }

  .stat-value {
    font-size: 17px;
  }

  .stat-label {
    font-size: 10px;
  }

  .bird-card {
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
  }

  .bird-icon {
    width: 76px;
    height: 76px;
    flex-basis: 76px;
  }

  .bird-name {
    font-size: 20px;
  }

  .description {
    font-size: 13px;
  }
}
</style>
