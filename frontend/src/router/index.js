import { createRouter, createWebHistory } from "vue-router";
import OperadorasList from "../views/OperadorasList.vue";
import OperadoraDetail from "../views/OperadoraDetail.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "operadoras", component: OperadorasList },
    { path: "/operadoras/:cnpj", name: "operadora-detail", component: OperadoraDetail, props: true },
  ],
});
