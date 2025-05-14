<script setup>
import { ref } from 'vue'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import { VApp, VAppBar, VNavigationDrawer, VList, VListItem, VMain } from 'vuetify/components'

// Importa los componentes
import configuration from './components/configuration.vue'
import mapa from './components/mapa.vue'
import mapa_wifi from './components/mapa_wifi.vue'
import planta from './components/planta.vue'
import sensores from './components/sensores.vue'
import inicio from './components/inicio.vue'

const vuetify = createVuetify()

const drawer = ref(false)
const currentComponent = ref('inicio') // Componente actual por defecto
currentComponent.value = "inicio"
// Mapeo de nombres de componentes a sus importaciones
const componentsMap = {
  inicio,
  configuration,
  mapa,
  mapa_wifi,
  planta,
  sensores
}

function loadComponent(componentName) {
  currentComponent.value = componentName
}
</script>

<template>
  <v-app :vuetify="vuetify">
    <!-- Drawer -->
    <v-navigation-drawer v-model="drawer" app>
      <v-list>
        <v-list-item title="Inicio" @click="loadComponent('inicio')" />
        <v-list-item title="Configuración" @click="loadComponent('configuration')" />
        <v-list-item title="Mapa WiFi" @click="loadComponent('mapa_wifi')" />
        <v-list-item title="Mapa" @click="loadComponent('mapa')" />
        <v-list-item title="Planta" @click="loadComponent('planta')" />
        <v-list-item title="Sensores" @click="loadComponent('sensores')" />
      </v-list>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar app>
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <span class="title">Robot PCARE</span>
    </v-app-bar>

    <!-- Main Content -->
     
    <v-main>
            <component :is="componentsMap[currentComponent]" />
    </v-main>
  </v-app>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}

.title {
  font-size: 1.25rem;
  font-weight: bold;
}
</style>