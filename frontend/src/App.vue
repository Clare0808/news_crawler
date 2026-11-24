<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SiteNav from "./components/SiteNav.vue";
import AppIcon from "./components/AppIcon.vue";
import ArticleDetail from "./components/ArticleDetail.vue";
import { useWorkspace } from "./composables/useWorkspace.js";

const route = useRoute();
const router = useRouter();
const { selectedArticle, closeArticle, toast } = useWorkspace();
const query = ref("");
const searchInput = ref(null);
const mobileDialog = ref(null);
const helpDialog = ref(null);
const dark = ref(false);

function search() {
  router.push({
    path: "/news",
    query: query.value.trim() ? { q: query.value.trim() } : {},
  });
}
function closeMenu() {
  mobileDialog.value?.close();
}
function openHelp() {
  closeMenu();
  nextTick(() => helpDialog.value.showModal());
}
function toggleTheme() {
  dark.value = !dark.value;
  document.documentElement.dataset.theme = dark.value ? "dark" : "light";
  try {
    localStorage.setItem("finsight:theme", dark.value ? "dark" : "light");
  } catch {
    /* Theme still works without storage. */
  }
}
function keyboardSearch(event) {
  if (
    event.key === "/" &&
    !event.ctrlKey &&
    !event.metaKey &&
    !event.altKey &&
    !["INPUT", "TEXTAREA", "SELECT"].includes(
      document.activeElement?.tagName
    ) &&
    !document.activeElement?.isContentEditable &&
    !document.querySelector("dialog[open]")
  ) {
    event.preventDefault();
    searchInput.value?.focus();
  }
}
watch(
  () => route.query.q,
  (value) => {
    query.value = typeof value === "string" ? value : "";
  },
  { immediate: true }
);
watch(
  () => route.meta.title,
  (title) => {
    document.title = `${title} · FinSight 財經觀測`;
  },
  { immediate: true }
);
onMounted(() => {
  try {
    dark.value = localStorage.getItem("finsight:theme") === "dark";
  } catch {
    /* Use the default light theme. */
  }
  document.documentElement.dataset.theme = dark.value ? "dark" : "light";
  window.addEventListener("keydown", keyboardSearch);
});
onBeforeUnmount(() => window.removeEventListener("keydown", keyboardSearch));
</script>

<template>
  <a href="#main-content" class="skip-link">跳至主要內容</a>
  <div class="app-shell">
    <header class="site-header">
      <div class="topbar">
        <RouterLink to="/" class="brand" aria-label="FinSight 財經觀測首頁">
          <img src="/favicon.svg" alt="" width="35" height="35" />
          <span>FinSight <small>財經觀測</small></span>
        </RouterLink>
        <SiteNav class="desktop-nav" />
        <form class="global-search" role="search" @submit.prevent="search">
          <label for="global-search" class="sr-only">全站搜尋</label>
          <input
            id="global-search"
            ref="searchInput"
            v-model="query"
            type="search"
            placeholder="搜尋新聞或公司"
            autocomplete="off"
          />
          <button type="submit" aria-label="搜尋">
            <AppIcon name="search" :size="18" />
          </button>
        </form>
        <div class="topbar-actions">
          <button
            class="icon-button"
            type="button"
            :aria-label="dark ? '切換淺色模式' : '切換深色模式'"
            @click="toggleTheme"
          >
            <AppIcon :name="dark ? 'sun' : 'moon'" :size="19" />
          </button>
          <button
            class="icon-button"
            type="button"
            aria-label="使用說明"
            @click="openHelp"
          >
            <AppIcon name="help" :size="19" />
          </button>
          <button
            class="icon-button mobile-menu-button"
            type="button"
            aria-label="開啟導覽選單"
            aria-haspopup="dialog"
            @click="mobileDialog.showModal()"
          >
            <AppIcon name="menu" />
          </button>
        </div>
      </div>
    </header>
    <main id="main-content" class="page-content" tabindex="-1">
      <RouterView />
    </main>
    <footer class="page-footer">
      <strong>FinSight 財經觀測</strong>
      <span>自然語言處理期末專題</span>
      <button type="button" class="text-link" @click="openHelp">
        展示資料說明
      </button>
    </footer>
  </div>
  <dialog
    ref="mobileDialog"
    class="mobile-nav-dialog"
    aria-label="導覽選單"
    @click="
      (event) => {
        if (event.target === mobileDialog) closeMenu();
      }
    "
  >
    <div class="dialog-header">
      <strong>FinSight 財經觀測</strong>
      <button
        class="icon-button"
        type="button"
        aria-label="關閉導覽選單"
        @click="closeMenu"
      >
        <AppIcon name="close" />
      </button>
    </div>
    <SiteNav with-icons @navigate="closeMenu" />
  </dialog>
  <dialog
    ref="helpDialog"
    class="help-dialog"
    aria-labelledby="help-title"
    @click="
      (event) => {
        if (event.target === helpDialog) helpDialog.close();
      }
    "
  >
    <div class="dialog-header">
      <h2 id="help-title">使用說明</h2>
      <button
        class="icon-button"
        type="button"
        aria-label="關閉使用說明"
        @click="helpDialog.close()"
      >
        <AppIcon name="close" />
      </button>
    </div>
    <div class="help-note">
      <AppIcon name="layers" />
      <div>
        <strong>目前為前端展示模式</strong>
        <p>
          收錄既有 CSV 的 24 篇新聞樣本，日期為
          2026/11/17–11/21。公司標籤、情緒、關鍵詞與重點句均供前端展示。
        </p>
      </div>
    </div>
    <p>點選新聞標題可查看重點整理與原文連結。收藏會儲存在這個瀏覽器。</p>
    <p class="muted">新聞情緒描述文字傾向，不代表未來股價漲跌。</p>
    <button class="button primary" type="button" @click="helpDialog.close()">
      關閉
    </button>
  </dialog>
  <ArticleDetail :article="selectedArticle" @close="closeArticle" />
  <Transition name="toast"
    ><div v-if="toast" class="toast-message" role="status">
      <AppIcon name="check" :size="18" />{{ toast }}
    </div></Transition
  >
</template>
