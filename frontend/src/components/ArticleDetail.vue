<script setup>
import { nextTick, ref, watch } from "vue";
import AppIcon from "./AppIcon.vue";
import {
  companyById,
  sentimentLabels,
  shortDate,
} from "../services/newsService.js";
import { useWorkspace } from "../composables/useWorkspace.js";
const props = defineProps({ article: { type: Object, default: null } });
const emit = defineEmits(["close"]);
const dialog = ref(null);
const tab = ref("summary");
const { toggleSaved, isSaved } = useWorkspace();
function moveTab(event) {
  const tabs = ["summary", "content", "analysis"];
  const index = tabs.indexOf(tab.value);
  const next =
    event.key === "Home"
      ? 0
      : event.key === "End"
      ? 2
      : (index + (event.key === "ArrowLeft" ? -1 : 1) + 3) % 3;
  const list = event.currentTarget.parentElement;
  tab.value = tabs[next];
  nextTick(() => list.querySelector('[aria-selected="true"]')?.focus());
}
watch(
  () => props.article,
  async (value) => {
    if (value) {
      tab.value = "summary";
      await nextTick();
      if (!dialog.value.open) dialog.value.showModal();
    } else if (dialog.value?.open) dialog.value.close();
  }
);
</script>

<template>
  <dialog
    ref="dialog"
    class="article-dialog"
    aria-labelledby="article-detail-title"
    @close="emit('close')"
    @click="
      (event) => {
        if (event.target === dialog) dialog.close();
      }
    "
  >
    <template v-if="article">
      <div class="dialog-header">
        <span class="eyebrow"
          >NEWS READER <span class="inline-demo">分析示範</span></span
        ><button
          class="icon-button"
          type="button"
          aria-label="關閉新聞"
          @click="dialog.close()"
        >
          <AppIcon name="close" />
        </button>
      </div>
      <div class="article-meta">
        <span class="source-label">{{ article.source }}</span
        ><span>·</span
        ><time :datetime="article.publishedAt"
          >2026/{{ shortDate(article.publishedAt, true) }}</time
        ><span class="category-label">{{ article.category }}</span>
      </div>
      <h2 id="article-detail-title">{{ article.title }}</h2>
      <div class="reader-actions">
        <button
          class="button"
          type="button"
          :aria-pressed="isSaved(article.id)"
          @click="toggleSaved(article.id)"
        >
          <AppIcon name="bookmark" :size="17" />{{
            isSaved(article.id) ? "已收藏" : "收藏新聞"
          }}</button
        ><a
          class="button"
          :href="article.url"
          target="_blank"
          rel="noopener noreferrer"
          >閱讀來源原文<AppIcon name="external" :size="16"
        /></a>
      </div>
      <div class="reader-tabs" role="tablist" aria-label="新聞閱讀模式">
        <button
          v-for="item in [
            { id: 'summary', label: '重點整理' },
            { id: 'content', label: '新聞內容' },
            { id: 'analysis', label: 'NLP 分析' },
          ]"
          :id="`reader-tab-${item.id}`"
          :key="item.id"
          type="button"
          role="tab"
          :aria-selected="tab === item.id"
          :aria-controls="`reader-panel-${item.id}`"
          @click="tab = item.id"
          @keydown.right.prevent="moveTab"
          @keydown.left.prevent="moveTab"
          @keydown.home.prevent="moveTab"
          @keydown.end.prevent="moveTab"
          :tabindex="tab === item.id ? 0 : -1"
        >
          {{ item.label }}
        </button>
      </div>
      <div
        :id="`reader-panel-${tab}`"
        class="reader-content"
        role="tabpanel"
        :aria-labelledby="`reader-tab-${tab}`"
        tabindex="0"
      >
        <template v-if="tab === 'summary'"
          ><div class="section-label">
            <AppIcon name="spark" :size="17" />值得關注的重點
          </div>
          <ol class="summary-list">
            <li v-for="(sentence, index) in article.summary" :key="index">
              {{ sentence }}
            </li>
          </ol>
          <p class="reader-footnote">
            重點句為前端展示，尚未連接摘要模型。
          </p></template
        >
        <template v-else-if="tab === 'content'"
          ><div v-if="article.contentType === 'excerpt'" class="excerpt-notice">
            這筆來源資料可能只有截斷摘要，完整內容請前往原文。
          </div>
          <p
            v-for="(paragraph, index) in article.content
              .split(/\n+/)
              .filter(Boolean)"
            :key="index"
            class="reader-paragraph"
          >
            {{ paragraph }}
          </p></template
        >
        <template v-else
          ><div class="analysis-row">
            <strong>文字情緒</strong
            ><span class="sentiment-pill" :class="article.sentiment"
              ><span></span>{{ sentimentLabels[article.sentiment] }}</span
            >
          </div>
          <div class="analysis-row">
            <strong>關鍵詞</strong>
            <div class="article-tags">
              <span
                v-for="word in article.keywords"
                :key="word"
                class="keyword-tag"
                >{{ word }}</span
              >
            </div>
          </div>
          <div class="analysis-row">
            <strong>相關公司</strong>
            <div class="article-tags">
              <RouterLink
                v-for="id in article.companyIds"
                :key="id"
                :to="{ path: '/companies', query: { company: id } }"
                class="company-link"
                @click="dialog.close()"
                >{{ companyById(id)?.name }}</RouterLink
              ><span v-if="!article.companyIds.length" class="muted"
                >此展示樣本未標記公司</span
              >
            </div>
          </div>
          <p class="reader-footnote">
            情緒、關鍵詞與公司標籤皆為展示配置，並非模型判斷或股價預測。
          </p></template
        >
      </div>
    </template>
  </dialog>
</template>
