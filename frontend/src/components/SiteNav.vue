<script setup>
import AppIcon from "./AppIcon.vue";
import { useWorkspace } from "../composables/useWorkspace.js";

defineProps({ withIcons: Boolean });
defineEmits(["navigate"]);
const { savedIds } = useWorkspace();
const links = [
  { to: "/", label: "新聞總覽", icon: "grid" },
  { to: "/news", label: "新聞探索", icon: "news" },
  { to: "/companies", label: "公司觀測", icon: "building" },
  { to: "/insights", label: "NLP 分析", icon: "chart" },
  { to: "/saved", label: "我的收藏", icon: "bookmark" },
];
</script>

<template>
  <nav class="main-nav" aria-label="主要導覽">
    <RouterLink
      v-for="link in links"
      :key="link.to"
      :to="link.to"
      @click="$emit('navigate')"
    >
      <AppIcon v-if="withIcons" :name="link.icon" :size="19" />
      <span>{{ link.label }}</span>
      <span v-if="link.to === '/saved' && savedIds.length" class="nav-count">
        {{ savedIds.length }}
      </span>
    </RouterLink>
  </nav>
</template>
