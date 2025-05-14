
import { createApp } from 'vue'
import App from './App.vue'
import Toast, { POSITION } from 'vue-toastification';
import 'vuetify/styles';

import "vue-toastification/dist/index.css";
import vuetify from './modules_vue/vuetify'; 
const app = createApp(App);

app.use(Toast, { position: POSITION.TOP_RIGHT });
app.use(vuetify);

app.mount('#app');