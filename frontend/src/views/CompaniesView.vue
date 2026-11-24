<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppIcon from "../components/AppIcon.vue";
import NewsCard from "../components/NewsCard.vue";
import { useWorkspace } from "../composables/useWorkspace.js";
import { companies, sentimentLabels } from "../services/newsService.js";
const route = useRoute();
const router = useRouter();
const { articles } = useWorkspace();
const selected = computed(
  () =>
    companies.find((company) => company.id === route.query.company) ||
    companies[0]
);
const related = computed(() =>
  articles.filter((article) => article.companyIds.includes(selected.value.id))
);
const counts = (id) =>
  articles.filter((article) => article.companyIds.includes(id)).length;
const sentiments = computed(() =>
  ["positive", "neutral", "negative"].map((key) => ({
    key,
    label: sentimentLabels[key],
    count: related.value.filter((article) => article.sentiment === key).length,
  }))
);
</script>

<template>
  <div class="page-heading">
    <h1>公司觀測</h1>
  </div>
  <div class="company-grid">
    <button
      v-for="company in companies"
      :key="company.id"
      class="company-card"
      :class="{ selected: selected.id === company.id }"
      type="button"
      :aria-pressed="selected.id === company.id"
      @click="router.replace({ query: { company: company.id } })"
    >
      <span class="company-avatar" :class="company.color">{{
        company.initials
      }}</span
      ><span class="company-card-title"
        ><strong>{{ company.name }}</strong
        ><small>{{ company.code }} · {{ company.sector }}</small></span
      ><AppIcon
        v-if="selected.id === company.id"
        name="check"
        :size="17"
      /><span class="company-card-description">{{ company.description }}</span
      ><span class="company-card-footer"
        ><span>{{ counts(company.id) }} 篇相關新聞</span
        ><span>查看新聞<AppIcon name="chevron" :size="14" /></span
      ></span>
    </button>
  </div>
  <section class="panel company-detail">
    <div class="panel-heading">
      <div class="company-detail-title">
        <span class="company-avatar" :class="selected.color">{{
          selected.initials
        }}</span>
        <div>
          <h2>
            {{ selected.name
            }}<span class="company-code">{{ selected.code }}</span>
          </h2>
          <span class="panel-subtitle">相關新聞 {{ related.length }} 篇</span>
        </div>
      </div>
      <RouterLink
        :to="{ path: '/news', query: { company: selected.id } }"
        class="text-link"
        >全部新聞<AppIcon name="chevron" :size="15"
      /></RouterLink>
    </div>
    <div class="company-sentiments">
      <span class="muted">情緒示範</span
      ><span
        v-for="item in sentiments"
        :key="item.key"
        class="sentiment-pill"
        :class="item.key"
        ><span></span>{{ item.label }} {{ item.count }} 篇</span
      >
    </div>
    <NewsCard
      v-for="article in related.slice(0, 4)"
      :key="article.id"
      :article="article"
      compact
    />
    <div v-if="!related.length" class="empty-state">
      <p>目前沒有這家公司的展示新聞。</p>
    </div>
  </section>
</template>
