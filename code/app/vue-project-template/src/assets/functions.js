// Define a global variable for the base URL
function getBaseUrl() {
    return localStorage.getItem('BASE_URL') || "http://your-server-url.com"; // Default URL, put your NGrok URL
}

// Function to send plant data
async function enviarDatosPlanta(datos) {
    try {
        const response = await fetch(`${getBaseUrl()}/datos_planta`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });

        if (response.status !== 200) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al enviar los datos de la planta');
        }

        const responseData = await response.json();
        return responseData.message || 'Datos enviados correctamente';
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Function to get sensor data
async function obtenerDatosSensor() {
    try {
        const response = await fetch(`${getBaseUrl()}/datos_sensor`, {
            method: 'GET'
        });

        if (response.status !== 200) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al obtener datos de los sensores');
        }
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Function to get WiFi map
async function obtenerMapaWifi() {
    try {
        const response = await fetch(`${getBaseUrl()}/mapa_wifi`, {
            method: 'GET'
        });
            if (response.status !== 200) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al obtener el mapa wifi');
        }

        return await response.blob(); // Assuming the response is an image
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Function to get the current map
async function obtenerMapaActual() {
    try {
        const response = await fetch(`${getBaseUrl()}/mapa_actual`, {
            method: 'GET'
        });
        if (response.status !== 200) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al obtener el mapa');
        }
        return await response.blob(); // Assuming the response is an image
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

export { enviarDatosPlanta, obtenerDatosSensor, obtenerMapaWifi, obtenerMapaActual };
