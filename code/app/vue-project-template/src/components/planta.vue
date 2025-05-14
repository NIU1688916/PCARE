<template>
    <div class="planta">
        <h1>Control de Planta</h1>
        <div class="toggle-container">
            <label class="switch">
                <input type="checkbox" v-model="isAutomatic" />
                <span class="slider"></span>
            </label>
            <p>{{ isAutomatic ? "Modo Automático" : "Modo Manual" }}</p>
        </div>

        <div v-if="!isAutomatic" class="manual-mode">
            <h2>Modo Manual</h2>
            <v-form @submit.prevent="sendManualData" ref="form">
                <v-container>
                    <v-row>
                        <v-col cols="12" md="6">
                            <v-text-field
                                label="Nombre de la Planta"
                                v-model="manualData.plantName"
                                required
                            ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field
                                label="Humedad (Unidades)"
                                v-model="manualData.humidity"
                                type="number"
                                required
                            ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                            <v-text-field
                                label="Luz (Unidades)"
                                v-model="manualData.light"
                                type="number"
                                required
                            ></v-text-field>
                        </v-col>
                        <v-col cols="12">
                            <v-btn type="submit" color="success" :disabled="!$refs.form?.validate()">
                                Enviar Datos
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-container>
            </v-form>
        </div>

        <div v-else class="automatic-mode">
            <h2>Modo Automático</h2>
            <div>
                <label for="image">Subir o Tomar Foto:</label>
                <input type="file" id="image" @change="handleImageUpload" accept="image/*" />
            </div>
            <button @click="sendAutomaticData" :disabled="!image">Enviar Datos</button>
        </div>
    </div>
</template>

<script>
import { enviarDatosPlanta } from '../assets/functions.js';
import { useToast } from 'vue-toastification';
export default {
    data() {
        return {
            isAutomatic: false,
            manualData: {
                plantName: null,
                humidity: null,
                light: null,
            },
            image: null,
        };
    },
    methods: {
        sendData(nombre, humedad, luz) {
            const toast = useToast();
            const datos = {
            nombre: "Planta1",
            humedad_opt: humedad,
            luz_opt: luz,
            };
            enviarDatosPlanta(datos).then((text) => {
                toast.success(text);
            }).catch((error) => {
                toast.error(error);
            });
        
        },
        sendManualData() {
            console.log("Enviando datos manuales:", this.manualData);
            this.sendData(this.manualData.plantName, this.manualData.humidity, this.manualData.light)
        },
        handleImageUpload(event) {
            this.image = event.target.files[0];
            console.log("Imagen seleccionada:", this.image);
        },
        sendAutomaticData() {
            if (!this.image) return;
            console.log("Enviando datos automáticos con la imagen:", this.image);
            // Aquí puedes realizar una solicitud a tu API para procesar la imagen
            //Coger datos desde la iamgen y la  api, la imagen esta en this.image
            nombre = "prueba"
            humedad = 0
            luz = 0
            this.sendData(nombre, humedad, luz)
        },
    },
};
</script>

<style scoped>
.planta {
    font-family: Arial, sans-serif;
    padding: 20px;
}

.toggle-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 25px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.4s;
    border-radius: 25px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 19px;
    width: 19px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
}

input:checked + .slider {
    background-color: #4caf50;
}

input:checked + .slider:before {
    transform: translateX(25px);
}

.manual-mode,
.automatic-mode {
    margin-top: 20px;
}

form div {
    margin-bottom: 10px;
}

button {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    border-radius: 5px;
}

button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
</style>