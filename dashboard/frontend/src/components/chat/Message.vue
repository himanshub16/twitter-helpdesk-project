<template>

  <v-layout
    row
    :reverse="isSent"
    >
    <v-flex md7>

      <v-card flat class="tweet-card"
              :color="card_color">
        <div class="tweet-userinfo">
          <v-icon small>person</v-icon>
          <span class="body-2">{{ msg.user.name }}</span>
        </div>

        <div class="tweet-body">
          {{ msg.full_text }}
        </div>

        <div class="tweet-stats">
          <span>
            <v-icon small>favorite_outline</v-icon>
            <small>{{ msg.favorite_count }}</small>
          </span>
          <span>
            <v-icon small>cached</v-icon>
            <small>{{ msg.retweet_count }}</small>
          </span>
          <span>
            <v-icon small>chat_bubble_outline</v-icon>
            <small>{{ msg.reply_count }}</small>
          </span>
          <span>
            <v-icon small>access_time</v-icon>
            <small>{{ parseDate(msg.created_at) }}</small>
          </span>
          <span>
            <a :href="tweetUrl" target="_blank">
              <v-icon small>open_in_new</v-icon>
              <small>Open in Twitter</small>
            </a>
          </span>
        </div>
      </v-card>

    </v-flex>

    <v-flex md5>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: 'Message',
  props: ['msg'],
  data() {
    return {
    };
  },
  methods: {
    parseDate(date) {
      const t = new Date();
      const d = new Date(date);
      const diff = {
        year: t.getUTCFullYear() - d.getUTCFullYear(),
        month: t.getUTCMonth() - d.getUTCMonth(),
        day: t.getUTCDate() - d.getUTCDate(),
      };
      if (diff.year > 0) {
        return `${diff.year} years`;
      } else if (diff.month > 0) {
        return `${diff.month} months`;
      }
      return `${diff.day} days`;
    },
  },
  computed: {
    isSent() {
      console.log(this.msg.sender);
      return this.msg.user.screen_name == this.$route.params.screenName;
    },
    card_color() {
      return (this.isSent) ? 'green lighten-5' : 'cyan lighten-5';
    },
    tweetUrl() {
      return `https://twitter.com/statuses/${this.msg.id_str}`;
    },
  },
};
</script>

<style scoped>
.tweet-card {
    border: 1px solid #ddd;
    border-radius: 5px;
}
.tweet-userinfo {
    padding: 2px 5px 0px;
}
.tweet-body {
    padding: 5px;
}
.tweet-stats {
    font-size: 0.8em;
    display: flex;
    border-top: 1px solid #dedede;
    flex-direction: row;
    font-size: smaller;
}
.tweet-stats span {
    margin: 2px 5px;
}
.tweet-stats span i {
    font-size: 1.2em;
}
.tweet-stats small {
    font-size: 1.1em;
    padding-left: 0.5ch;
}

</style>
