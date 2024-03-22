import { createRouter, createWebHistory } from "vue-router";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:"/",
      name: "home",
      component: () => import("../views/HomePage.vue"),
    },
    {
      path: "/traditions",
      name: "traditions",
      component: () => import("../views/TraditionMenu.vue"),
    },
    { path: '/tradition/:tradition', component: () => import("../views/ManuscriptMenu.vue") },
    { path: '/tradition/:tradition/:manuscript', component: () => import("../views/FolioMenu.vue") },
    { path: '/tradition/:tradition/:manuscript/:folio', component: () => import("../views/FolioViewer.vue") }
  ],
});

export default router;
