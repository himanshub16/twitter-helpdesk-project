<template>
  <v-card class="metric-card">
    <div class="display-3 value">
      {{ metric.count }}
    </div>
    <div class="subheading name">
      {{ metric.name }}
    </div>
  </v-card>
</template>

<script>
export default {
  props: ['metric'],
};
</script>

<style scoped>
.metric-card {
    padding: 5px 10px;
    text-align: center;
}
.metric-card .value {

}
.metric-card .name {
    text-transform: capitalize;
    border-top: 1px solid #ddd;
}
</style>
