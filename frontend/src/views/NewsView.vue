<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import NewsCard from "../components/NewsCard.vue";
import {
  categories,
  sources,
  companyById,
  exportNews,
} from "../services/newsService.js";
import { useWorkspace, notify } from "../composables/useWorkspace.js";

const props = defineProps({ savedOnly: Boolean });
const route = useRoute();
const router = useRouter();
const { articles, savedIds } = useWorkspace();
const page = ref(1);
const pageSize = 6;
const value = (key) =>
  typeof route.query[key] === "string" ? route.query[key] : "";
const query = computed(() => value("q"));
const category = computed(() =>
  categories.includes(value("category")) ? value("category") : "全部新聞"
);
function setFilter(key, next) {
  const updated = { ...route.query };
  if (!next || next === "全部新聞") delete updated[key];
  else updated[key] = next;
  router.replace({ query: updated });
}
function clearFilters() {
  router.replace({ query: {} });
}
function clearDates() {
  const updated = { ...route.query };
  delete updated.from;
  delete updated.to;
  router.replace({ query: updated });
}
const filtered = computed(() => {
  const needle = query.value.trim().toLocaleLowerCase();
  return articles
    .filter((article) => {
      const text = [
        article.title,
        article.content,
        ...article.keywords,
        ...article.companyIds.map(
          (id) => `${companyById(id)?.name} ${companyById(id)?.code}`
        ),
      ]
        .join(" ")
        .toLocaleLowerCase();
      return (
        (!props.savedOnly || savedIds.value.includes(article.id)) &&
        (!needle || text.includes(needle)) &&
        (category.value === "全部新聞" ||
          article.category === category.value) &&
        (!value("source") || article.source === value("source")) &&
        (!value("sentiment") || article.sentiment === value("sentiment")) &&
        (!value("company") || article.companyIds.includes(value("company"))) &&
        (!value("from") || article.publishedAt.slice(0, 10) >= value("from")) &&
        (!value("to") || article.publishedAt.slice(0, 10) <= value("to"))
      );
    })
    .sort((a, b) =>
      value("sort") === "oldest"
        ? a.publishedAt.localeCompare(b.publishedAt)
        : b.publishedAt.localeCompare(a.publishedAt)
    );
});
const pages = computed(() =>
  Math.max(1, Math.ceil(filtered.value.length / pageSize))
);
const visible = computed(() =>
  filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize)
);
const hasFilters = computed(() =>
  ["q", "category", "source", "sentiment", "company", "from", "to"].some(
    (key) => value(key)
  )
);
watch(
  () => route.fullPath,
  () => {
    page.value = 1;
  }
);
watch(pages, (count) => {
  page.value = Math.min(page.value, count);
});
function changePage(next) {
  page.value = next;
  document.getElementById("news-results")?.scrollIntoView({
    block: "start",
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "instant"
      : "smooth",
  });
}
function download() {
  exportNews(filtered.value);
  notify(`已匯出 ${filtered.value.length} 篇新聞`);
}
</script>

<template>
  <div class="page-heading">
    <h1>{{ savedOnly ? "我的收藏" : "新聞探索" }}</h1>
  </div>
  <section class="news-workspace" aria-label="新聞篩選與結果">
    <div class="news-toolbar">
      <label class="local-search"
        ><AppIcon name="search" :size="19" /><span class="sr-only"
          >篩選新聞、公司或關鍵詞</span
        ><input
          :value="query"
          type="search"
          placeholder="搜尋新聞、公司或關鍵詞…"
          @input="setFilter('q', $event.target.value)"
      /></label>
      <div class="toolbar-selects">
        <label class="select-control"
          ><AppIcon name="globe" :size="16" /><span class="sr-only"
            >新聞來源</span
          ><select
            :value="value('source')"
            @change="setFilter('source', $event.target.value)"
          >
            <option value="">所有來源</option>
            <option v-for="source in sources" :key="source" :value="source">
              {{ source }}
            </option></select
          ><AppIcon name="down" :size="14" /></label
        ><label class="select-control"
          ><span class="sr-only">新聞情緒</span
          ><select
            :value="value('sentiment')"
            @change="setFilter('sentiment', $event.target.value)"
          >
            <option value="">所有情緒</option>
            <option value="positive">正面</option>
            <option value="neutral">中性</option>
            <option value="negative">負面</option></select
          ><AppIcon name="down" :size="14"
        /></label>
        <details class="date-filter">
          <summary class="button">
            <AppIcon name="calendar" :size="16" />日期<AppIcon
              name="down"
              :size="13"
            />
          </summary>
          <div class="date-popover">
            <label
              >開始日期<input
                type="date"
                :value="value('from')"
                @change="setFilter('from', $event.target.value)" /></label
            ><label
              >結束日期<input
                type="date"
                :value="value('to')"
                @change="setFilter('to', $event.target.value)" /></label
            ><span class="muted">樣本期間：11/17–11/21</span
            ><button class="text-link" type="button" @click="clearDates">
              清除日期
            </button>
          </div>
        </details>
      </div>
    </div>
    <div class="category-tabs" aria-label="新聞主題">
      <button
        v-for="item in categories"
        :key="item"
        type="button"
        :class="{ active: category === item }"
        :aria-pressed="category === item"
        @click="setFilter('category', item)"
      >
        {{ item }}
      </button>
    </div>
    <div id="news-results" class="results-heading">
      <div>
        <strong>{{ filtered.length }}</strong> 篇{{ savedOnly ? "收藏" : "新聞"
        }}<span v-if="value('company')" class="active-filter"
          >{{ companyById(value("company"))?.name || value("company")
          }}<button
            type="button"
            aria-label="移除公司篩選"
            @click="setFilter('company', '')"
          >
            <AppIcon name="close" :size="12" /></button></span
        ><button
          v-if="hasFilters"
          class="clear-filters"
          type="button"
          @click="clearFilters"
        >
          清除篩選
        </button>
      </div>
      <div class="section-actions">
        <label class="sort-control">
          <span class="sr-only">新聞排序</span>
          <select
            :value="value('sort')"
            @change="setFilter('sort', $event.target.value)"
          >
            <option value="">最新發布</option>
            <option value="oldest">最早發布</option>
          </select>
          <AppIcon name="down" :size="13" />
        </label>
        <button
          class="button"
          type="button"
          :disabled="!filtered.length"
          @click="download"
        >
          <AppIcon name="download" :size="16" />匯出整理
        </button>
      </div>
    </div>
    <div class="article-grid news-results" aria-live="polite">
      <NewsCard
        v-for="article in visible"
        :key="article.id"
        :article="article"
      />
      <div v-if="!visible.length" class="empty-state">
        <AppIcon
          :name="savedOnly && !savedIds.length ? 'bookmark' : 'search'"
          :size="30"
        />
        <h2>
          {{
            savedOnly && !savedIds.length
              ? "還沒有收藏新聞"
              : "沒有符合條件的新聞"
          }}
        </h2>
        <p>
          {{
            savedOnly && !savedIds.length
              ? "在新聞旁點選收藏圖示，即可儲存到這裡。"
              : "試試其他關鍵詞，或調整來源與日期條件。"
          }}
        </p>
        <RouterLink
          v-if="savedOnly && !savedIds.length"
          to="/news"
          class="button primary"
          >探索新聞</RouterLink
        ><button v-else class="button" type="button" @click="clearFilters">
          清除篩選
        </button>
      </div>
    </div>
    <div v-if="filtered.length" class="pagination">
      <span
        >第 {{ (page - 1) * pageSize + 1 }}–{{
          Math.min(page * pageSize, filtered.length)
        }}
        篇，共 {{ filtered.length }} 篇</span
      >
      <nav aria-label="新聞分頁">
        <button
          class="page-button previous-page"
          type="button"
          aria-label="上一頁"
          :disabled="page === 1"
          @click="changePage(page - 1)"
        >
          <AppIcon name="chevron" :size="16" /></button
        ><button
          v-for="number in pages"
          :key="number"
          class="page-button"
          :class="{ active: page === number }"
          :aria-label="`第 ${number} 頁`"
          :aria-current="page === number ? 'page' : undefined"
          type="button"
          @click="changePage(number)"
        >
          {{ number }}</button
        ><button
          class="page-button"
          type="button"
          aria-label="下一頁"
          :disabled="page === pages"
          @click="changePage(page + 1)"
        >
          <AppIcon name="chevron" :size="16" />
        </button>
      </nav>
    </div>
  </section>
  <p class="below-note">
    {{
      savedOnly
        ? "收藏僅儲存在此瀏覽器。"
        : "目前顯示 24 篇展示樣本，並非即時新聞。"
    }}情緒與標籤為分析示範。
  </p>
</template>
