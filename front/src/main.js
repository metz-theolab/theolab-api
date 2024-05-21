import "./assets/main.css";

import axios from 'axios'
import VueAxios from 'vue-axios'
import { createApp } from "vue";
import {createBootstrap} from 'bootstrap-vue-next'
import Keycloak from "keycloak-js";

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

import App from "./App.vue";
import router from "./router";

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const app = createApp(App)
const vuetify = createVuetify({
  components,
  directives,
})

app.use(createBootstrap({components: true, directives: true}))
app.use(VueAxios, axios);


const keycloak = new Keycloak({
    url: 'http://localhost:8024',
    realm: 'theolab',
    clientId: 'qwb-api'
})


// Axios
axios.defaults.baseURL = 'http://127.0.0.1:8000'

keycloak.init({
  onLoad: 'login-required',
}).then((authenticated) => {
  if (authenticated) {
    const token = keycloak.token;
    axios.defaults.headers.common['Authorization'] = 'Bearer ' + token;
    console.log(axios.defaults.headers.common['Authorization'])

    app.use(router);
    app.use(vuetify)
    app.mount("#app");
  }
}).catch((e) => {console.error(e)})




