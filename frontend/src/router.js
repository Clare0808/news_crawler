import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "./views/DashboardView.vue";
import NewsView from "./views/NewsView.vue";
import CompaniesView from "./views/CompaniesView.vue";
import InsightsView from "./views/InsightsView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: DashboardView, meta: { title: "新聞總覽" } },
    { path: "/news", component: NewsView, meta: { title: "新聞探索" } },
    {
      path: "/companies",
      component: CompaniesView,
      meta: { title: "公司觀測" },
    },
    { path: "/insights", component: InsightsView, meta: { title: "NLP 分析" } },
    {
      path: "/saved",
      component: NewsView,
      props: { savedOnly: true },
      meta: { title: "我的收藏" },
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || (to.path === from.path ? {} : { top: 0 });
  },
});
