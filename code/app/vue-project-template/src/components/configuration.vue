<!-- filepath: /home/crugiente34/Documentos/robotica/practicas/proyecto/PCARE/code/app/vue-project-template/src/components/configuration.vue -->
<template>
  <div class="configuration">
    <h1>Configuración</h1>
    <form @submit.prevent="guardarUrl">
      <label for="base-url">URL Base:</label>
      <input
        id="base-url"
        type="text"
        v-model="baseUrl"
        placeholder="http://your-server-url.com"
      />
    <v-btn type="submit" color="primary" class="mt-3">Guardar</v-btn>
    </form>
    <p v-if="mensaje" class="mensaje">{{ mensaje }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      baseUrl: localStorage.getItem('BASE_URL') || '', // Cargar la URL desde localStorage
      mensaje: ''
    };
  },
  methods: {
    guardarUrl() {
      if (this.baseUrl.trim() === '') {
        this.mensaje = 'La URL no puede estar vacía.';
        return;
      }
      localStorage.setItem('BASE_URL', this.baseUrl.trim()); // Guardar en localStorage
      this.mensaje = 'URL guardada correctamente.';
    }
  }
};
</script>

<style scoped>
.configuration {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
}

button {
  padding: 0.5rem 1rem;
}

.mensaje {
  margin-top: 1rem;
  color: green;
}
</style>