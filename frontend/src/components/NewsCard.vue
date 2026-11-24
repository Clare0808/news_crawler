<script setup>
import AppIcon from "./AppIcon.vue";
import {
  companyById,
  sentimentLabels,
  shortDate,
} from "../services/newsService.js";
import { useWorkspace } from "../composables/useWorkspace.js";
defineProps({ article: { type: Object, required: true }, compact: Boolean });
const { isSaved, toggleSaved, openArticle } = useWorkspace();
</script>

<template>
  <article class="news-card" :class="{ compact }">
    <div class="news-card-main">
      <div class="article-meta">
        <span class="source-label"
          ><span
            class="source-square"
            :class="
              article.source === '中央社'
                ? 'source-cna'
                : article.source === '工商時報'
                ? 'source-ctee'
                : article.source === '經濟日報'
                ? 'source-edn'
                : 'source-wealth'
            "
          ></span
          >{{ article.source }}</span
        ><span class="meta-dot">·</span
        ><time :datetime="article.publishedAt">{{
          shortDate(article.publishedAt, true)
        }}</time
        ><span class="category-label">{{ article.category }}</span>
      </div>
      <h3>
        <button
          type="button"
          class="article-title-button"
          @click="openArticle(article)"
        >
          {{ article.title }}
        </button>
      </h3>
      <p v-if="!compact" class="article-excerpt">{{ article.excerpt }}</p>
      <div class="article-bottom">
        <div class="article-tags">
          <span class="sentiment-pill" :class="article.sentiment"
            ><span></span>{{ sentimentLabels[article.sentiment] }}</span
          ><span
            v-for="keyword in article.keywords.slice(0, compact ? 2 : 3)"
            :key="keyword"
            class="keyword-tag"
            >{{ keyword }}</span
          >
        </div>
        <span
          v-if="article.companyIds.length && !compact"
          class="article-company"
          >{{ companyById(article.companyIds[0])?.name }}</span
        >
      </div>
    </div>
    <button
      class="icon-button save-button"
      :class="{ 'is-saved': isSaved(article.id) }"
      type="button"
      :aria-label="`${isSaved(article.id) ? '取消收藏' : '收藏'}：${
        article.title
      }`"
      :aria-pressed="isSaved(article.id)"
      @click="toggleSaved(article.id)"
    >
      <AppIcon name="bookmark" :size="19" />
    </button>
  </article>
</template>
