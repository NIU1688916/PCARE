<template>
    <div>
        <h1>Datos del Sensor</h1>
        <div v-if="sensorData">
            <p><strong>Humedad:</strong> {{ sensorData.humedad }} Unidad</p>
            <p><strong>Luminosidad:</strong> {{ sensorData.luminocidad }} Unidad</p>
            <p><strong>Intensidad WiFi:</strong> {{ sensorData.intensidad_wifi }} dBm</p>
        </div>
        <div v-else>
            <p>Cargando datos del sensor...</p>
        </div>
    </div>
</template>

<script>
import { obtenerDatosSensor } from '../assets/functions.js';

export default {
    data() {
        return {
            sensorData: null,
        };
    },
    async created() {
        try {
            const response = await obtenerDatosSensor();
            this.sensorData = {
                humedad: response.humedad,
                luminocidad: response.luminocidad,
                intensidad_wifi: response.intensidad_wifi,
            };

        } catch (error) {
            console.error('Error al obtener los datos del sensor:', error);
        }
    },
};
</script>

<style scoped>
h1 {
    font-size: 1.5em;
    margin-bottom: 1em;
}
p {
    font-size: 1.2em;
    margin: 0.5em 0;
}
</style>