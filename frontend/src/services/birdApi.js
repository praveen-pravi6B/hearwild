const API_URL = 'http://127.0.0.1:8000'

export async function identifyBird(audioBlob) {
  const formData = new FormData()

  formData.append(
    'file',
    audioBlob,
    'recording.webm'
  )

  const response = await fetch(
    `${API_URL}/identify`,
    {
      method: 'POST',
      body: formData
    }
  )

  if (!response.ok) {
    throw new Error(
      `Bird identification failed: ${response.status}`
    )
  }

  return response.json()
}
