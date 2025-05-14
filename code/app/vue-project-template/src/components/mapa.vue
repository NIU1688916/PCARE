<template>
    <h1>Mapa Actual de SLAM</h1>
    <div>
        <v-btn color="primary" @click="fetchDataOnce">Coger datos 1 vez</v-btn>
        <v-btn color="secondary" @click="fetchDataContinuously">Coger datos constantemente</v-btn>
        <div v-if="imageData">
            <img :src="imageData" alt="Imagen recibida" />
        </div>
    </div>
</template>

<script>
import { obtenerMapaActual } from '../assets/functions.js';

export default {
    data() {
        return {
            imageData: null,
            intervalId: null,
        };
    },
    methods: {
        async fetchDataOnce() {
            try {
                const blob = await obtenerMapaActual();
                this.imageData = URL.createObjectURL(blob); // Convert blob to URL
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },
        fetchDataContinuously() {
            if (this.intervalId) return; // Prevent multiple intervals
            this.intervalId = setInterval(async () => {
                try {
                    const blob = await obtenerMapaActual();
                    this.imageData = URL.createObjectURL(blob); // Convert blob to URL
                } catch (error) {
                    console.error('Error fetching data:', error);
                }
            }, 1000); // Fetch data every second
        },
    },
    beforeDestroy() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        if (this.imageData) {
            URL.revokeObjectURL(this.imageData); // Clean up object URL
        }
    },
};
</script>

<style scoped>
button {
    margin: 5px;
}
img {
    margin-top: 10px;
    max-width: 100%;
    height: auto;
}
</style>