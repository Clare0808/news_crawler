import { computed, ref } from "vue";
import { getNews } from "../services/newsService.js";

function readSaved() {
  try {
    const value = JSON.parse(localStorage.getItem("finsight:saved") || "[]");
    return Array.isArray(value)
      ? value.filter((id) => typeof id === "string")
      : [];
  } catch {
    return [];
  }
}

const articles = getNews();
const validIds = new Set(articles.map((article) => article.id));
const savedIds = ref(readSaved().filter((id) => validIds.has(id)));
const selectedArticle = ref(null);
const toast = ref("");
let toastTimer;

export function notify(message) {
  toast.value = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value = "";
  }, 3500);
}

export function useWorkspace() {
  function toggleSaved(id) {
    const next = savedIds.value.includes(id)
      ? savedIds.value.filter((value) => value !== id)
      : [...savedIds.value, id];
    savedIds.value = next;
    try {
      localStorage.setItem("finsight:saved", JSON.stringify(next));
      notify(next.includes(id) ? "已加入我的收藏" : "已從收藏移除");
    } catch {
      notify("收藏已更新；瀏覽器目前無法儲存，重新整理後不會保留。");
    }
  }
  return {
    articles,
    savedIds,
    selectedArticle,
    toast,
    savedArticles: computed(() =>
      articles.filter((article) => savedIds.value.includes(article.id))
    ),
    isSaved: (id) => savedIds.value.includes(id),
    toggleSaved,
    openArticle: (article) => {
      selectedArticle.value = article;
    },
    closeArticle: () => {
      selectedArticle.value = null;
    },
  };
}
